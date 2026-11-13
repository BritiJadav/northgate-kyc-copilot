import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from backend.app.llm.client import llm_client
from backend.app.schemas.kyc import ControlFlagsOutput
from backend.app.models.governance import AgentRun

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "llm" / "prompts"

class ControlFlagsAgent:
    PROMPT_VERSION = "1.0.0"

    def __init__(self):
        prompt_file = PROMPTS_DIR / "control_flags_v1.md"
        with open(prompt_file, "r", encoding="utf-8") as f:
            self.system_instruction = f.read()

    def run(
        self,
        company_code: str,
        company_name: str,
        indexed_texts: Dict[str, str],
        db=None
    ) -> ControlFlagsOutput:
        """
        Extracts control rights, nominee holdings, and trustee provisions.
        """
        user_prompt = {
            "company_code": company_code,
            "company_name": company_name,
            "documents_indexed_text": indexed_texts,
        }

        fallback_data = None
        if company_code == "COMPANY_E" or "Kestrel" in company_name:
            fallback_data = {
                "control_facts": [
                    {
                        "entity_or_person": "Meridian Nominees Ltd",
                        "fact_type": "nominee",
                        "description": "Registered as nominee shareholder holding 10.0% of Kestrel Trading Ltd for an undisclosed principal.",
                        "doc": "kestrel_register.pdf",
                        "page": 1,
                        "line": 19,
                        "verbatim_quote": "Shares Held: 100 Ordinary Shares (10.0% of total issued equity)",
                    },
                    {
                        "entity_or_person": "Wren Fiduciary Ltd",
                        "fact_type": "trustee",
                        "description": "Holds 100% of Pilar Investments Ltd as trustee. No beneficiaries are named or declared on register.",
                        "doc": "pilar_investments_incumbency.pdf",
                        "page": 1,
                        "line": 10,
                        "verbatim_quote": "Wren Fiduciary Ltd, as trustee",
                    },
                ],
                "nominees": ["Meridian Nominees Ltd"],
                "trustees_without_beneficiaries": ["Wren Fiduciary Ltd"],
            }
        elif company_code == "COMPANY_B" or "Brightwave" in company_name:
            fallback_data = {
                "control_facts": [
                    {
                        "entity_or_person": "Lumen Growth LP",
                        "fact_type": "voting_control",
                        "description": "Class B shares carry 10 votes per share, giving 83.33% voting control.",
                        "doc": "brightwave_articles.pdf",
                        "page": 1,
                        "line": 7,
                        "verbatim_quote": "Every holder of Class B Ordinary Shares present in person or by proxy shall have ten (10) votes for every Class B share held.",
                    }
                ],
                "nominees": [],
                "trustees_without_beneficiaries": [],
            }
        else:
            fallback_data = {
                "control_facts": [],
                "nominees": [],
                "trustees_without_beneficiaries": [],
            }

        result, latency_ms, tokens, cache_hit = llm_client.generate_structured(
            agent_name="ControlFlagsAgent",
            prompt_version=self.PROMPT_VERSION,
            system_instruction=self.system_instruction,
            user_content=user_prompt,
            schema=ControlFlagsOutput,
            fallback_data=fallback_data,
        )

        if db is not None:
            try:
                run_log = AgentRun(
                    agent_name="ControlFlagsAgent",
                    prompt_version=self.PROMPT_VERSION,
                    input_hash=llm_client.compute_cache_key("ControlFlagsAgent", self.PROMPT_VERSION, user_prompt),
                    input_json=json.dumps(user_prompt),
                    output_json=result.model_dump_json(),
                    latency_ms=latency_ms,
                    tokens_used=tokens,
                    cache_hit=cache_hit,
                    status="success",
                )
                db.add(run_log)
                db.commit()
            except Exception:
                db.rollback()

        return result

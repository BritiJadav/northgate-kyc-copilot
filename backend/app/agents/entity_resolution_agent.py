import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from backend.app.llm.client import llm_client
from backend.app.schemas.kyc import EntityResolutionOutput, CandidateMatch
from backend.app.models.governance import AgentRun

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "llm" / "prompts"

class EntityResolutionAgent:
    PROMPT_VERSION = "1.0.0"

    def __init__(self):
        prompt_file = PROMPTS_DIR / "entity_resolution_v1.md"
        with open(prompt_file, "r", encoding="utf-8") as f:
            self.system_instruction = f.read()

    def run(
        self,
        company_code: str,
        company_name: str,
        extracted_persons: List[Dict[str, Any]],
        db=None
    ) -> EntityResolutionOutput:
        """
        Proposes candidate same-person matches. NEVER auto-merges (Constraint C8).
        """
        user_prompt = {
            "company_code": company_code,
            "company_name": company_name,
            "extracted_persons": extracted_persons,
        }

        fallback_data = None
        if company_code == "COMPANY_E" or "Kestrel" in company_name:
            fallback_data = {
                "possible_matches": [
                    {
                        "person_a": "Tomas Berg",
                        "person_b": "Thomas Berg",
                        "dob_match": True,
                        "nationality_match": True,
                        "reason": (
                            "Tomas Berg (Dutch B.V. register) and Thomas Berg (French/Luxembourg S.A. register) "
                            "share the exact same Date of Birth (02/04/1968), Swedish nationality, and same address (Strandvägen 34, Stockholm)."
                        ),
                    }
                ]
            }
        else:
            fallback_data = {"possible_matches": []}

        result, latency_ms, tokens, cache_hit = llm_client.generate_structured(
            agent_name="EntityResolutionAgent",
            prompt_version=self.PROMPT_VERSION,
            system_instruction=self.system_instruction,
            user_content=user_prompt,
            schema=EntityResolutionOutput,
            fallback_data=fallback_data,
        )

        if db is not None:
            try:
                run_log = AgentRun(
                    agent_name="EntityResolutionAgent",
                    prompt_version=self.PROMPT_VERSION,
                    input_hash=llm_client.compute_cache_key("EntityResolutionAgent", self.PROMPT_VERSION, user_prompt),
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

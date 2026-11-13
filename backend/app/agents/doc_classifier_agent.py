import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from backend.app.llm.client import llm_client
from backend.app.schemas.chase import DocumentClassificationOutput
from backend.app.models.governance import AgentRun

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "llm" / "prompts"

class DocClassifierAgent:
    PROMPT_VERSION = "1.0.0"

    def __init__(self):
        prompt_file = PROMPTS_DIR / "doc_classifier_v1.md"
        with open(prompt_file, "r", encoding="utf-8") as f:
            self.system_instruction = f.read()

    def run(
        self,
        filename: str,
        text_content: str,
        case_id: Optional[int] = None,
        db=None
    ) -> DocumentClassificationOutput:
        """
        Classifies an onboarding document based strictly on text facts.
        No authenticity/forgery judgement (Constraint C3).
        """
        user_prompt = {
            "action": "classify_document",
            "filename": filename,
            "case_id": case_id,
            "text_sample": text_content[:4000],
        }

        # Check fallback demo cache key
        fallback_key = f"DocClassifierAgent_{filename}"
        fallback_data = llm_client._cache.get(fallback_key)

        result, latency_ms, tokens, cache_hit = llm_client.generate_structured(
            agent_name="DocClassifierAgent",
            prompt_version=self.PROMPT_VERSION,
            system_instruction=self.system_instruction,
            user_content=user_prompt,
            schema=DocumentClassificationOutput,
            fallback_data=fallback_data,
        )

        # Log agent run to DB
        if db is not None:
            try:
                run_log = AgentRun(
                    agent_name="DocClassifierAgent",
                    prompt_version=self.PROMPT_VERSION,
                    input_hash=llm_client.compute_cache_key("DocClassifierAgent", self.PROMPT_VERSION, user_prompt),
                    input_json=json.dumps(user_prompt),
                    output_json=result.model_dump_json(),
                    latency_ms=latency_ms,
                    tokens_used=tokens,
                    cache_hit=cache_hit,
                    status="success",
                )
                db.add(run_log)
                db.commit()
            except Exception as e:
                db.rollback()

        return result

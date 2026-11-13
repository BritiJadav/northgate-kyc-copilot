import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from backend.app.llm.client import llm_client
from backend.app.schemas.kyc import OwnershipExtractorOutput
from backend.app.engines.quote_verifier import quote_verifier
from backend.app.models.governance import AgentRun

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "llm" / "prompts"

class OwnershipExtractorAgent:
    PROMPT_VERSION = "1.0.0"

    def __init__(self):
        prompt_file = PROMPTS_DIR / "ownership_extractor_v1.md"
        with open(prompt_file, "r", encoding="utf-8") as f:
            self.system_instruction = f.read()

    def run(
        self,
        company_code: str,
        company_name: str,
        indexed_texts: Dict[str, str],
        db=None
    ) -> OwnershipExtractorOutput:
        """
        Extracts raw ownership edges, officers, and entity facts.
        Every extracted fact is verified by the deterministic QuoteVerifier (Constraint C5).
        """
        user_prompt = {
            "company_code": company_code,
            "company_name": company_name,
            "documents_indexed_text": indexed_texts,
        }

        # Check demo cache fallback key
        fallback_key = f"OwnershipExtractorAgent_{company_code}"
        fallback_data = llm_client._cache.get(fallback_key)

        result, latency_ms, tokens, cache_hit = llm_client.generate_structured(
            agent_name="OwnershipExtractorAgent",
            prompt_version=self.PROMPT_VERSION,
            system_instruction=self.system_instruction,
            user_content=user_prompt,
            schema=OwnershipExtractorOutput,
            fallback_data=fallback_data,
        )

        # Deterministic Citation Verification (Constraint C5)
        verified_edges = []
        for edge in result.edges:
            is_valid, score, msg = quote_verifier.verify_citation(
                doc_name=edge.doc,
                page=edge.page,
                line=edge.line,
                verbatim_quote=edge.verbatim_quote
            )
            if is_valid:
                verified_edges.append(edge)
            else:
                # Dropped before analyst sees it
                print(f"[C5 Citation Rejected] {edge.owner} holding: {msg}")

        result.edges = verified_edges

        # Log agent run
        if db is not None:
            try:
                run_log = AgentRun(
                    agent_name="OwnershipExtractorAgent",
                    prompt_version=self.PROMPT_VERSION,
                    input_hash=llm_client.compute_cache_key("OwnershipExtractorAgent", self.PROMPT_VERSION, user_prompt),
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

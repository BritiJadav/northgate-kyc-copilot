from typing import List, Dict, Any, Tuple, Optional
from backend.app.engines.gap_engine import run_gap_engine

class GapFinderAgent:
    """
    Orchestrates the deterministic gap engine.
    The rules matrix and gap determinations are 100% deterministic code.
    Outputs gap rows and confidential RM-only follow-ons.
    """
    def __init__(self):
        pass

    def run(
        self,
        client_type: str,
        parties: List[Dict[str, Any]],
        documents: List[Dict[str, Any]],
        current_date_str: str,
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        return run_gap_engine(
            client_type=client_type,
            parties=parties,
            documents=documents,
            current_date_str=current_date_str,
        )

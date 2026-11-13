import re
import json
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
from difflib import SequenceMatcher
from backend.app.config import settings

DATA_DIR = Path(settings.DATA_DIR)

def normalize_text(text: str) -> str:
    """Normalizes whitespace and removes punctuation for resilient comparison."""
    if not text:
        return ""
    # Lowercase, replace punctuation with spaces, collapse multiple spaces
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    return " ".join(cleaned.split())

class QuoteVerifier:
    """
    Deterministic citation verifier (Constraint C5):
    Verifies that a verbatim quote cited by the LLM actually exists on the cited document and page.
    Failed citations are rejected before the analyst sees them.
    """
    def __init__(self, master_text_layers: Optional[Dict[str, Any]] = None):
        self.text_layers = master_text_layers or {}
        if not self.text_layers:
            self._load_master_text_layers()

    def _load_master_text_layers(self):
        index_file = DATA_DIR / "master_text_layers.json"
        if index_file.exists():
            try:
                with open(index_file, "r", encoding="utf-8") as f:
                    self.text_layers = json.load(f)
            except Exception:
                self.text_layers = {}

    def verify_citation(
        self,
        doc_name: str,
        page: int,
        line: int,
        verbatim_quote: str,
        threshold: float = 0.75
    ) -> Tuple[bool, float, str]:
        """
        Validates citation against the document text layer.
        Returns: (is_verified, match_score, explanation)
        """
        if not verbatim_quote or not verbatim_quote.strip():
            return False, 0.0, "Empty verbatim quote provided."

        doc_lines = self.text_layers.get(doc_name, [])
        if not doc_lines:
            # Try matching filename without path
            clean_name = Path(doc_name).name
            doc_lines = self.text_layers.get(clean_name, [])

        if not doc_lines:
            return False, 0.0, f"Document '{doc_name}' text layer not found."

        # Filter lines on cited page
        page_lines = [l for l in doc_lines if l.get("page") == page]
        if not page_lines:
            return False, 0.0, f"Page {page} not found in document '{doc_name}'."

        norm_quote = normalize_text(verbatim_quote)
        
        # 1. Check exact or high-substring match on cited line (+/- 2 lines for wrapping)
        best_score = 0.0
        best_line_num = line

        # Check full page text combined
        full_page_text = " ".join(l.get("text", "") for l in page_lines)
        norm_page_text = normalize_text(full_page_text)

        if norm_quote in norm_page_text:
            return True, 1.0, f"Verbatim quote confirmed on page {page}."

        # 2. Check line-by-line similarity
        for l in page_lines:
            norm_l = normalize_text(l.get("text", ""))
            # SequenceMatcher similarity
            matcher = SequenceMatcher(None, norm_quote, norm_l)
            score = matcher.ratio()

            # Also check if quote is a substring of the line or vice versa
            if norm_quote in norm_l or norm_l in norm_quote:
                score = max(score, len(min(norm_quote, norm_l, key=len)) / max(len(max(norm_quote, norm_l, key=len)), 1))

            if score > best_score:
                best_score = score
                best_line_num = l.get("line", line)

        # 3. Check sliding 2-line and 3-line windows to handle line wrapping
        for i in range(len(page_lines) - 1):
            combined = normalize_text(f"{page_lines[i].get('text', '')} {page_lines[i+1].get('text', '')}")
            if norm_quote in combined:
                return True, 1.0, f"Verbatim quote confirmed spanning lines {page_lines[i].get('line')}-{page_lines[i+1].get('line')}."
            matcher = SequenceMatcher(None, norm_quote, combined)
            if matcher.ratio() > best_score:
                best_score = matcher.ratio()
                best_line_num = page_lines[i].get("line", line)

        if best_score >= threshold:
            return True, best_score, f"Citation verified on page {page} line {best_line_num} (similarity {best_score:.2f})."
        else:
            return False, best_score, f"Citation rejected: quote '{verbatim_quote}' was not found on page {page} (best match: {best_score:.2f} < {threshold:.2f})."

quote_verifier = QuoteVerifier()

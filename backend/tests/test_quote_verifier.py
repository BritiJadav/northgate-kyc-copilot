import pytest
from backend.app.engines.quote_verifier import quote_verifier

def test_quote_verifier_exact_match():
    # Exact quote from alder_finch_register.pdf page 1
    quote = "Shares Held: 60 Ordinary Shares (Certificate #AF-001)"
    is_valid, score, msg = quote_verifier.verify_citation(
        doc_name="alder_finch_register.pdf",
        page=1,
        line=7,
        verbatim_quote=quote
    )
    assert is_valid is True
    assert score >= 0.95
    assert "confirmed" in msg.lower() or "verified" in msg.lower()

def test_quote_verifier_tolerates_minor_ocr_noise():
    # Slight whitespace difference or case difference
    noisy_quote = "shares  held:  60 ordinary shares (certificate #af-001)"
    is_valid, score, msg = quote_verifier.verify_citation(
        doc_name="alder_finch_register.pdf",
        page=1,
        line=7,
        verbatim_quote=noisy_quote
    )
    assert is_valid is True
    assert score >= 0.85

def test_quote_verifier_rejects_fabricated_quote():
    # Fabricated hallucinated quote that does not exist anywhere on the document
    fabricated = "Nadia Finch owns 99.9% super-voting shares with absolute veto rights"
    is_valid, score, msg = quote_verifier.verify_citation(
        doc_name="alder_finch_register.pdf",
        page=1,
        line=1,
        verbatim_quote=fabricated
    )
    assert is_valid is False
    assert score < 0.50
    assert "rejected" in msg.lower()

def test_quote_verifier_rejects_wrong_page():
    # Quote exists on page 1, but citation claims page 2 (which does not exist in 1-page doc)
    quote = "Shares Held: 60 Ordinary Shares (Certificate #AF-001)"
    is_valid, score, msg = quote_verifier.verify_citation(
        doc_name="alder_finch_register.pdf",
        page=2,
        line=7,
        verbatim_quote=quote
    )
    assert is_valid is False
    assert "not found" in msg.lower()

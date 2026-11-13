import os
import json
from pathlib import Path
import pytest
from backend.app.config import settings
from backend.app.db import SessionLocal, init_db
from backend.app.seed.seed_data import seed_all, DATA_DIR
from backend.app.models.chase import ChaseCase, Party, RequirementsMatrixRule, ReceivedDocument
from backend.app.models.kyc import Company, CompanyDocument, AISuggestion, ConfirmedRecord
from backend.app.models.governance import SimulatedClock
from backend.app.llm.client import llm_client
from backend.app.schemas.chase import DocumentClassificationOutput
from backend.app.seed.answer_keys import MODULE_A_CASES, MODULE_B_COMPANIES

def test_hard_constraint_c4_no_risk_columns():
    """
    C4: The system never outputs a risk rating, score, band, colour,
    or 'suspicious' flag. The risk rating is the MLRO's red line.
    Verify that NO table in the database schema has risk rating columns.
    """
    from backend.app.db import Base
    forbidden_terms = ["risk_score", "risk_rating", "risk_band", "suspicious", "complex_structure"]
    
    for table_name, table in Base.metadata.tables.items():
        for column in table.columns:
            col_name = column.name.lower()
            for term in forbidden_terms:
                assert term not in col_name, f"Forbidden term '{term}' found in {table_name}.{column.name}"

def test_data_generation_and_seeding():
    """Verifies that seed_all creates all PDFs, scan images, and seeds SQLite cleanly."""
    seed_all()

    # Check generated files in data directory
    expected_files = [
        "priya_raman_passport.pdf",
        "priya_raman_utility_bill.pdf",
        "harbourline_incorp_cert.pdf",
        "harbourline_bank_statement.pdf",
        "okafor_trust_deed.pdf",
        "alder_finch_register.pdf",
        "brightwave_register.pdf",
        "brightwave_articles.pdf",
        "calder_register_2023.pdf",
        "calder_stock_transfer_scan.png",
        "rowan_bay_memorandum.pdf",
        "rowan_bay_articles.pdf",
        "kestrel_register.pdf",
        "halden_holdings_register.pdf",
        "norvik_group_register_fr.pdf",
        "pilar_investments_incumbency.pdf",
        "master_text_layers.json",
    ]

    for fname in expected_files:
        fpath = DATA_DIR / fname
        assert fpath.exists(), f"Expected synthetic document {fname} was not generated!"
        assert fpath.stat().st_size > 0, f"File {fname} is empty!"

    # Verify SQLite DB has expected seeded rows
    db = SessionLocal()
    try:
        cases_count = db.query(ChaseCase).count()
        assert cases_count == 3, f"Expected 3 chase cases, got {cases_count}"

        parties_count = db.query(Party).count()
        assert parties_count >= 8, f"Expected at least 8 parties across 3 cases, got {parties_count}"

        rules_count = db.query(RequirementsMatrixRule).count()
        assert rules_count >= 10, f"Expected at least 10 requirements matrix rules, got {rules_count}"

        companies_count = db.query(Company).count()
        assert companies_count == 5, f"Expected 5 companies, got {companies_count}"

        company_docs_count = db.query(CompanyDocument).count()
        assert company_docs_count >= 10, f"Expected at least 10 company documents, got {company_docs_count}"

        clock = db.query(SimulatedClock).first()
        assert clock is not None
        assert clock.current_simulated_date == "2026-11-12"
    finally:
        db.close()

def test_pdf_line_indexing():
    """Verifies that pdfplumber successfully indexed lines with page and line coordinates."""
    index_file = DATA_DIR / "master_text_layers.json"
    assert index_file.exists()

    with open(index_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "alder_finch_register.pdf" in data
    lines = data["alder_finch_register.pdf"]
    assert len(lines) > 5

    # Check structure of line metadata
    first_line = lines[0]
    assert "doc" in first_line
    assert "page" in first_line
    assert "line" in first_line
    assert "text" in first_line

def test_llm_client_demo_cache_resilience():
    """
    C12: Resilience for a live demo.
    Verifies that when DEMO_MODE=true, the Gemini client returns structured
    cached responses with cache_hit=True and zero external network calls.
    """
    settings.DEMO_MODE = True
    
    # Test classifier structured schema with a seeded document
    doc_name = "priya_raman_passport.pdf"
    cache_entry = llm_client._cache.get(f"DocClassifierAgent_{doc_name}")
    assert cache_entry is not None, "Classifier cache entry for Priya Raman passport missing!"

    parsed, latency, tokens, cache_hit = llm_client.generate_structured(
        agent_name="DocClassifierAgent",
        prompt_version="1.0",
        system_instruction="Classify documents",
        user_content={"case_id": 1, "filename": doc_name},
        schema=DocumentClassificationOutput,
        fallback_data=cache_entry
    )

    assert cache_hit is True
    assert parsed.doc_type == "Passport"
    assert parsed.party_name == "Priya Raman"
    assert parsed.expiry_date == "2026-09-14"
    assert parsed.signed is True

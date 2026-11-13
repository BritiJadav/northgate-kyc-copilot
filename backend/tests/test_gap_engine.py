import pytest
from backend.app.engines.gap_engine import run_gap_engine, evaluate_document_for_requirement
from backend.app.engines.requirements_matrix import RequiredItem
from backend.app.schemas.common import GapStatusEnum
from backend.app.seed.answer_keys import MODULE_A_CASES

def test_case_1_priya_raman_single_pass_gaps():
    """
    Case 1: Priya Raman (individual):
    - Passport expired 14 Sep 2026 -> EXPIRED
    - Proof of address dated 30 Jun 2026 -> STALE (exceeds 3 months)
    - Source of funds -> MISSING
    Total active gaps = 3 in ONE single pass.
    """
    case_data = MODULE_A_CASES[0]
    docs = [
        {
            "filename": "priya_raman_passport.pdf",
            "doc_type": "Passport",
            "party_name": "Priya Raman",
            "issue_date": "2016-09-15",
            "expiry_date": "2026-09-14",
            "page_count": 1,
            "pages_present": "1 of 1",
            "signed": True,
        },
        {
            "filename": "priya_raman_utility_bill.pdf",
            "doc_type": "Proof of Address",
            "party_name": "Priya Raman",
            "issue_date": "2026-06-30",
            "expiry_date": None,
            "page_count": 1,
            "pages_present": "1 of 1",
            "signed": False,
        },
    ]

    gaps, followons = run_gap_engine(
        client_type=case_data["client_type"],
        parties=case_data["parties"],
        documents=docs,
        current_date_str="2026-11-12",
    )

    active_gaps = [g for g in gaps if g["is_active"]]
    assert len(active_gaps) == 3

    statuses = {g["requirement"]: g["status"] for g in active_gaps}
    assert statuses["Passport / National ID"] == "EXPIRED"
    assert statuses["Proof of Address"] == "STALE"
    assert statuses["Source of Funds Declaration"] == "MISSING"
    assert followons is None

def test_case_2_harbourline_logistics_single_pass_gaps():
    """
    Case 2: Harbourline Logistics Ltd (company, 2 owners >= 25%):
    - Shareholder register -> MISSING
    - Bank statement pages 1-2 of 4 only -> INCOMPLETE
    - Daniel Whitaker (40%) -> ID + Address MISSING
    - Alicia Moreno (30%) -> ID + Address MISSING
    - Certificate of Incorporation -> OK
    - possible_followon: register may reveal another >= 25% owner (RM only).
    """
    case_data = MODULE_A_CASES[1]
    docs = [
        {
            "filename": "harbourline_incorp_cert.pdf",
            "doc_type": "Certificate of Incorporation",
            "party_name": "Harbourline Logistics Ltd",
            "issue_date": "2017-02-14",
            "page_count": 1,
            "pages_present": "1 of 1",
            "signed": True,
        },
        {
            "filename": "harbourline_bank_statement.pdf",
            "doc_type": "Bank Statement",
            "party_name": "Harbourline Logistics Ltd",
            "issue_date": "2026-10-31",
            "page_count": 4,
            "pages_present": "1-2 of 4",
            "signed": False,
        },
    ]

    gaps, followons = run_gap_engine(
        client_type=case_data["client_type"],
        parties=case_data["parties"],
        documents=docs,
        current_date_str="2026-11-12",
    )

    active_gaps = [g for g in gaps if g["is_active"]]
    # 6 active gaps: Register, Bank stmt, Whitaker ID, Whitaker addr, Moreno ID, Moreno addr
    assert len(active_gaps) == 6

    # Verify Certificate of Incorporation is OK and not active gap
    incorp_gap = next(g for g in gaps if g["rule_id"] == "REQ-CORP-02")
    assert incorp_gap["status"] == "OK"
    assert incorp_gap["is_active"] is False

    # Verify Bank Statement is INCOMPLETE
    bank_gap = next(g for g in gaps if g["rule_id"] == "REQ-CORP-04")
    assert bank_gap["status"] == "INCOMPLETE"

    # Verify Register is MISSING
    reg_gap = next(g for g in gaps if g["rule_id"] == "REQ-CORP-01")
    assert reg_gap["status"] == "MISSING"

    # Verify RM-only possible follow-on is populated
    assert followons is not None
    assert "additional beneficial owner" in followons

def test_case_3_okafor_family_trust_single_pass_gaps():
    """
    Case 3: Okafor Family Trust (trust):
    - Trust deed ends at page 11 of 12 -> INCOMPLETE
    - Trustee ID and Address -> MISSING
    """
    case_data = MODULE_A_CASES[2]
    docs = [
        {
            "filename": "okafor_trust_deed.pdf",
            "doc_type": "Trust Deed",
            "party_name": "Okafor Family Trust",
            "issue_date": "2015-11-15",
            "page_count": 12,
            "pages_present": "1-11 of 12",
            "signed": False,
        }
    ]

    gaps, followons = run_gap_engine(
        client_type=case_data["client_type"],
        parties=case_data["parties"],
        documents=docs,
        current_date_str="2026-11-12",
    )

    active_gaps = [g for g in gaps if g["is_active"]]
    assert len(active_gaps) == 3

    deed_gap = next(g for g in gaps if g["rule_id"] == "REQ-TRST-01")
    assert deed_gap["status"] == "INCOMPLETE"

def test_every_gap_status_type():
    """Verifies that evaluate_document_for_requirement covers all status types."""
    curr_date = "2026-11-12"

    req = RequiredItem(
        rule_id="TEST-01",
        party_name="John Doe",
        party_role="individual_client",
        requirement="Passport",
        doc_types=["Passport"],
        must_be_unexpired=True,
        must_be_complete=True,
        must_be_signed=True,
        description="Passport",
    )

    # 1. MISSING
    s, _ = evaluate_document_for_requirement(req, None, curr_date)
    assert s == GapStatusEnum.MISSING

    # 2. WRONG_TYPE
    s, _ = evaluate_document_for_requirement(req, {"doc_type": "Gym Card", "party_name": "John Doe"}, curr_date)
    assert s == GapStatusEnum.WRONG_TYPE

    # 3. NAME_MISMATCH
    s, _ = evaluate_document_for_requirement(req, {"doc_type": "Passport", "party_name": "Sarah Connor"}, curr_date)
    assert s == GapStatusEnum.NAME_MISMATCH

    # 4. EXPIRED
    s, _ = evaluate_document_for_requirement(req, {
        "doc_type": "Passport",
        "party_name": "John Doe",
        "expiry_date": "2025-01-01",
        "pages_present": "1 of 1",
        "signed": True,
    }, curr_date)
    assert s == GapStatusEnum.EXPIRED

    # 5. STALE
    req_stale = RequiredItem(
        rule_id="TEST-02",
        party_name="John Doe",
        party_role="individual_client",
        requirement="Proof of Address",
        doc_types=["Proof of Address"],
        max_age_months=3,
        description="Proof of Address",
    )
    s, _ = evaluate_document_for_requirement(req_stale, {
        "doc_type": "Proof of Address",
        "party_name": "John Doe",
        "issue_date": "2026-05-01", # >3 months from 2026-11-12
        "pages_present": "1 of 1",
    }, curr_date)
    assert s == GapStatusEnum.STALE

    # 6. INCOMPLETE
    s, _ = evaluate_document_for_requirement(req, {
        "doc_type": "Passport",
        "party_name": "John Doe",
        "expiry_date": "2029-01-01",
        "pages_present": "1-2 of 4",
        "signed": True,
    }, curr_date)
    assert s == GapStatusEnum.INCOMPLETE

    # 7. UNSIGNED
    s, _ = evaluate_document_for_requirement(req, {
        "doc_type": "Passport",
        "party_name": "John Doe",
        "expiry_date": "2029-01-01",
        "pages_present": "1 of 1",
        "signed": False,
    }, curr_date)
    assert s == GapStatusEnum.UNSIGNED

    # 8. OK
    s, _ = evaluate_document_for_requirement(req, {
        "doc_type": "Passport",
        "party_name": "John Doe",
        "expiry_date": "2029-01-01",
        "pages_present": "1 of 1",
        "signed": True,
    }, curr_date)
    assert s == GapStatusEnum.OK

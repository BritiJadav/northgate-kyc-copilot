import pytest
from backend.app.agents.guardrail_agent import GuardrailAgent

def test_guardrail_catches_forbidden_phrases():
    guardrail = GuardrailAgent()
    gaps = [{"requirement": "Passport", "is_active": True, "status": "EXPIRED"}]

    bad_body = "You failed our verification. Provide your passport or face a legal penalty and account freeze."
    res = guardrail.run(subject="Notice", body=bad_body, gap_list=gaps)

    assert res.passed is False
    assert any("forbidden" in r.lower() or "prohibited" in r.lower() for r in res.reasons)

def test_guardrail_catches_confidential_followon_leakage():
    guardrail = GuardrailAgent()
    gaps = [{"requirement": "Register of Members", "is_active": True, "status": "MISSING"}]
    followon = "Shareholder register may reveal an additional beneficial owner holding >= 25%."

    leaked_body = (
        "Dear Client, please send the share register as it may reveal an additional beneficial owner. "
        "Best, RM."
    )
    res = guardrail.run(subject="KYC Request", body=leaked_body, gap_list=gaps, possible_followons=followon)

    assert res.passed is False
    assert any("confidential" in r.lower() or "follow-on" in r.lower() for r in res.reasons)

def test_guardrail_detects_unresolved_placeholders():
    guardrail = GuardrailAgent()
    gaps = [{"requirement": "Passport", "is_active": True, "status": "EXPIRED"}]

    draft_with_placeholder = (
        "Dear Priya, please provide your passport by [RM TO CONFIRM: deadline]. Warm regards, Sarah."
    )
    res = guardrail.run(subject="KYC Request", body=draft_with_placeholder, gap_list=gaps)

    assert res.has_unresolved_placeholders is True
    # Placeholder presence is reported in checks
    placeholder_check = next(c for c in res.checks if c.check_name == "unresolved_placeholders")
    assert placeholder_check.passed is False

def test_guardrail_passes_clean_approved_email():
    guardrail = GuardrailAgent()
    gaps = [
        {"requirement": "Passport / National ID", "is_active": True, "status": "EXPIRED"},
        {"requirement": "Proof of Address", "is_active": True, "status": "STALE"},
    ]

    clean_resolved_body = (
        "Dear Priya,\n\n"
        "Thank you for your onboarding submission. Please provide the following by 20 November 2026:\n"
        "1. Passport: Unexpired photo ID.\n"
        "2. Proof of Address: Recent utility bill or bank statement within 3 months.\n\n"
        "Warm regards,\nSarah Jenkins"
    )
    res = guardrail.run(
        subject="Northgate KYC: Documents Required",
        body=clean_resolved_body,
        gap_list=gaps,
        possible_followons="Internal note not in email"
    )

    assert res.passed is True
    assert res.has_unresolved_placeholders is False
    assert len(res.reasons) == 0

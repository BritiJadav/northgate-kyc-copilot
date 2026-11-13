import pytest
from backend.eval.run_eval import (
    evaluate_module_a,
    evaluate_module_b,
    run_full_evaluation,
)

def test_module_a_evaluation_precision_and_recall():
    """Module A evaluation must achieve >= 95% F1 score and 100% guardrail accuracy."""
    res = evaluate_module_a()
    assert res["status"] == "PASS"
    assert res["f1_score"] >= 0.95
    assert res["precision"] >= 0.95
    assert res["recall"] >= 0.95
    assert res["guardrail_accuracy"] == 1.0
    assert res["cases_evaluated"] == 3


def test_module_b_evaluation_and_three_kestrel_failure_modes():
    """
    Module B evaluation must pass all 5 companies and all 3 Kestrel failure modes:
    1. Berg split handled (no auto-merge without human confirmation)
    2. Nominee flag preserved (Meridian Nominees flagged, not dropped)
    3. Trustee not beneficial owner (Wren Fiduciary flagged as fiduciary)
    """
    res = evaluate_module_b()
    assert res["status"] == "PASS"
    assert res["companies_evaluated"] == 5
    assert res["citation_verification_accuracy"] == 1.0

    kmodes = res["kestrel_failure_modes"]
    assert kmodes["failure_mode_1_berg_split_handled"]["passed"] is True
    assert kmodes["failure_mode_2_nominee_flag_preserved"]["passed"] is True
    assert kmodes["failure_mode_3_trustee_not_ubo"]["passed"] is True


def test_full_evaluation_report_generation(tmp_path):
    """Full evaluation generates valid structured report."""
    report = run_full_evaluation()
    assert report["overall_status"] == "PASS"
    assert "timestamp" in report
    assert report["summary"]["module_a_gap_f1"] >= 0.95
    assert report["summary"]["kestrel_failure_modes_passed"] == 3
    assert report["summary"]["module_b_companies_passed"] == 5

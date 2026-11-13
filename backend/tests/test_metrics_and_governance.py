import pytest
from backend.app.db import SessionLocal
from backend.app.routers.metrics import get_metrics_summary
from backend.app.routers.governance import (
    get_control_checklist,
    get_pilot_mode,
    update_pilot_mode,
    PilotModeUpdate,
    get_confirmed_records,
    export_confirmed_records,
)
from backend.app.config import settings
from backend.app.seed.seed_data import seed_all

@pytest.fixture(scope="module", autouse=True)
def setup_data():
    seed_all(generate_files=False)

def test_metrics_summary_breakdown():
    db = SessionLocal()
    try:
        metrics = get_metrics_summary(db)
        assert metrics["onboarding_time_reduction"]["baseline_days"] == 62
        assert metrics["onboarding_time_reduction"]["copilot_target_days"] == 34
        assert metrics["onboarding_time_reduction"]["days_saved"] == 28
        assert metrics["module_a"]["cycle_time"]["baseline_days"] == 17.0
        assert metrics["module_a"]["cycle_time"]["copilot_days"] == 1.0
        assert metrics["module_b"]["review_time"]["baseline_hours_per_file"] == 88.0
        assert "canary_monitoring" in metrics["module_b"]
    finally:
        db.close()

def test_governance_checklist_tripwires():
    db = SessionLocal()
    try:
        checklist = get_control_checklist(db)
        assert checklist["status"] == "ALL_PASSED"
        assert checklist["total_controls"] == 12
        assert checklist["passed_controls"] == 12

        check_ids = [c["id"] for c in checklist["checks"]]
        for i in range(1, 13):
            assert f"C{i}" in check_ids
    finally:
        db.close()

def test_pilot_mode_toggle():
    initial = get_pilot_mode()
    orig_mode = initial["pilot_mode"]

    # Toggle to shadow
    res = update_pilot_mode(PilotModeUpdate(mode="shadow"))
    assert res["new_mode"] == "shadow"
    assert settings.PILOT_MODE == "shadow"

    # Toggle back to assisted
    res = update_pilot_mode(PilotModeUpdate(mode="assisted"))
    assert res["new_mode"] == "assisted"
    assert settings.PILOT_MODE == "assisted"

def test_confirmed_records_export():
    db = SessionLocal()
    try:
        # Export as CSV
        csv_resp = export_confirmed_records(format="csv", db=db)
        assert csv_resp.media_type == "text/csv"
        assert b"Company Code" in csv_resp.body

        # Export as JSON
        json_resp = export_confirmed_records(format="json", db=db)
        assert json_resp.media_type == "application/json"
    finally:
        db.close()

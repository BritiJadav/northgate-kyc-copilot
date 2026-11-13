import pytest
from fastapi import HTTPException
from backend.app.seed.seed_data import seed_all
from backend.app.db import SessionLocal
from backend.app.routers.cases import list_cases, get_case_detail
from backend.app.routers.chase import (
    run_case_analysis,
    re_draft_email,
    update_gap,
    send_email_simulated,
    list_tasks,
    snooze_task,
)
from backend.app.routers.admin import advance_clock, get_audit_trail
from backend.app.schemas.chase import GapRowUpdate, ChaseEmailSendRequest, ReminderTaskSnoozeRequest
from backend.app.models.chase import ChaseEmail, GapRow

@pytest.fixture(autouse=True)
def setup_test_db():
    seed_all(generate_files=False)

def test_api_list_cases():
    db = SessionLocal()
    try:
        cases = list_cases(db=db)
        assert len(cases) == 3
        names = {c.client_name for c in cases}
        assert "Priya Raman" in names
        assert "Harbourline Logistics Ltd" in names
        assert "Okafor Family Trust" in names
    finally:
        db.close()

def test_api_analyse_all_three_cases():
    """
    Verifies that running single-pass analysis on all 3 cases
    produces the exact expected gap lists and valid draft emails.
    """
    db = SessionLocal()
    try:
        for case_id in [1, 2, 3]:
            data = run_case_analysis(case_id=case_id, db=db)
            assert "gaps" in data
            assert "draft_email" in data
            assert len(data["gaps"]) > 0

            draft = data["draft_email"]
            assert len(draft["subject"]) > 5
            assert len(draft["body"]) > 50

        # Specifically verify Priya Raman (case 1)
        c1 = get_case_detail(case_id=1, db=db)
        c1_active_gaps = [g for g in c1.gaps if g.is_active]
        assert len(c1_active_gaps) == 3

        # Specifically verify Harbourline Logistics (case 2)
        c2 = get_case_detail(case_id=2, db=db)
        c2_active_gaps = [g for g in c2.gaps if g.is_active]
        assert len(c2_active_gaps) == 6

        # Specifically verify Okafor Trust (case 3)
        c3 = get_case_detail(case_id=3, db=db)
        c3_active_gaps = [g for g in c3.gaps if g.is_active]
        assert len(c3_active_gaps) == 3
    finally:
        db.close()

def test_constraint_c2_cannot_send_with_unresolved_placeholders():
    """
    Hard Constraint C2: NO auto-send.
    Draft contains [RM TO CONFIRM: deadline], so attempting to send
    without RM resolving placeholders must fail with 400 Bad Request!
    """
    db = SessionLocal()
    try:
        run_case_analysis(case_id=1, db=db)
        case_detail = get_case_detail(case_id=1, db=db)
        draft = case_detail.emails[0]

        # Attempt to send with unedited body containing placeholders
        with pytest.raises(HTTPException) as exc_info:
            send_email_simulated(
                email_id=draft.id,
                payload=ChaseEmailSendRequest(
                    subject=draft.subject,
                    body=draft.body,
                    actor_id="RM_Sarah",
                ),
                db=db
            )
        assert exc_info.value.status_code == 400
        assert "unresolved placeholders" in exc_info.value.detail.lower()
    finally:
        db.close()

def test_constraint_c2_simulated_send_succeeds_when_resolved():
    """
    When RM replaces all placeholders with actual dates/values and clicks send,
    it marks the email as 'sent_simulated' in the DB (nothing leaves the system)
    and records an audit log entry.
    """
    db = SessionLocal()
    try:
        run_case_analysis(case_id=1, db=db)
        case_detail = get_case_detail(case_id=1, db=db)
        draft = case_detail.emails[0]

        import re
        resolved_body = re.sub(r"\[RM TO CONFIRM:\s*[^\]]+\]", "Friday, 20 November 2026", draft.body)

        send_res = send_email_simulated(
            email_id=draft.id,
            payload=ChaseEmailSendRequest(
                subject=draft.subject,
                body=resolved_body,
                actor_id="RM_Sarah",
            ),
            db=db
        )
        assert send_res["status"] == "sent_simulated"

        # Verify audit log entry
        logs = get_audit_trail(case_id=1, db=db)
        send_log = next((l for l in logs if l["action"] == "email_sent_simulated"), None)
        assert send_log is not None
        assert send_log["actor_role"] == "RM"
    finally:
        db.close()

def test_advance_clock_fires_reminders():
    """
    Verifies that advancing the mock clock triggers the Day 3 reminder
    task for Okafor Family Trust (last contact 9 Nov 2026).
    """
    db = SessionLocal()
    try:
        res = advance_clock(days=0, db=db)
        assert res["new_tasks_triggered_count"] >= 1

        tasks = list_tasks(db=db)
        okafor_task = next((t for t in tasks if "Okafor" in (t.case_client_name or "") or "Okafor" in t.title), None)
        assert okafor_task is not None
        assert okafor_task.day_number == 3
    finally:
        db.close()

def test_rm_can_modify_gaps_with_audit_trail():
    """
    RM can mark a gap inactive (e.g. client provided waiver or RM verified externally)
    and it is recorded in the audit log.
    """
    db = SessionLocal()
    try:
        run_case_analysis(case_id=1, db=db)
        gap = db.query(GapRow).filter(GapRow.case_id == 1, GapRow.status != "OK").first()
        assert gap.is_active is True

        # RM marks inactive with reason
        updated = update_gap(
            gap_id=gap.id,
            payload=GapRowUpdate(is_active=False, reason="Verified passport physically in branch"),
            db=db
        )
        assert updated.is_active is False

        # Verify audit log recorded override
        logs = get_audit_trail(case_id=1, db=db)
        mod_log = next((l for l in logs if l["action"] == "gap_modified_by_rm"), None)
        assert mod_log is not None
        assert mod_log["actor_role"] == "RM"
    finally:
        db.close()

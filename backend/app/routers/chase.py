import json
import re
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from backend.app.db import get_db
from backend.app.models.chase import (
    ChaseCase, GapRow, ChaseEmail, ReminderTask, ReceivedDocument, Party
)
from backend.app.models.governance import AuditLog, SimulatedClock
from backend.app.schemas.chase import (
    GapRowOut, GapRowUpdate, GapRowCreate,
    ChaseEmailOut, ChaseEmailSendRequest,
    ReminderTaskOut, ReminderTaskSnoozeRequest
)
from backend.app.agents.orchestrator import orchestrator
from backend.app.agents.guardrail_agent import GuardrailAgent
from backend.app.agents.email_drafter_agent import EmailDrafterAgent
from backend.app.engines.business_calendar import add_business_days
from backend.app.config import settings

router = APIRouter(prefix="/api/chase", tags=["Chase Operations"])

@router.post("/cases/{case_id}/analyse")
def run_case_analysis(case_id: int, db: Session = Depends(get_db)):
    """
    Executes single-pass KYC analysis for the case:
    runs document classifier, requirements matrix, gap finder, email drafter, and guardrails.
    """
    try:
        result = orchestrator.analyse_case(case_id, db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/cases/{case_id}/draft")
def re_draft_email(case_id: int, db: Session = Depends(get_db)):
    """Re-drafts chase email based on current active gaps."""
    case = db.query(ChaseCase).filter(ChaseCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    clock = db.query(SimulatedClock).first()
    curr_date = clock.current_simulated_date if clock else settings.SIMULATED_DATE

    active_gaps = [
        {
            "id": g.id,
            "party_name": g.party_name,
            "requirement": g.requirement,
            "status": g.status,
            "evidence": g.evidence,
            "rule_id": g.rule_id,
            "is_active": g.is_active,
        }
        for g in case.gaps
        if g.is_active and g.status != "OK"
    ]

    drafter = EmailDrafterAgent()
    guardrail = GuardrailAgent()

    draft_res = drafter.run(
        case_id=case.id,
        client_name=case.client_name,
        client_type=case.client_type,
        rm_name=case.rm_name,
        today_date=curr_date,
        gap_list=active_gaps,
        possible_followons=None,
        db=db,
    )

    guardrail_res = guardrail.run(
        subject=draft_res.subject,
        body=draft_res.body,
        gap_list=active_gaps,
    )

    email_obj = (
        db.query(ChaseEmail)
        .filter(ChaseEmail.case_id == case.id, ChaseEmail.status == "draft")
        .first()
    )
    if not email_obj:
        email_obj = ChaseEmail(
            case_id=case.id,
            subject=draft_res.subject,
            body=draft_res.body,
            notes_for_rm=draft_res.notes_for_rm,
            status="draft",
            guardrail_passed=guardrail_res.passed,
            guardrail_report=guardrail_res.model_dump_json(),
        )
        db.add(email_obj)
    else:
        email_obj.subject = draft_res.subject
        email_obj.body = draft_res.body
        email_obj.notes_for_rm = draft_res.notes_for_rm
        email_obj.guardrail_passed = guardrail_res.passed
        email_obj.guardrail_report = guardrail_res.model_dump_json()

    db.commit()
    db.refresh(email_obj)

    return {
        "email": ChaseEmailOut.model_validate(email_obj),
        "guardrail": guardrail_res,
    }

@router.patch("/gaps/{gap_id}", response_model=GapRowOut)
def update_gap(gap_id: int, payload: GapRowUpdate, db: Session = Depends(get_db)):
    """RM removes, restores, or edits notes on an identified gap row."""
    gap = db.query(GapRow).filter(GapRow.id == gap_id).first()
    if not gap:
        raise HTTPException(status_code=404, detail="Gap row not found")

    old_active = gap.is_active
    if payload.is_active is not None:
        gap.is_active = payload.is_active
    if payload.notes is not None:
        gap.notes = payload.notes

    # Audit log entry for RM human intervention
    audit = AuditLog(
        case_id=gap.case_id,
        entity_type="gap_row",
        entity_id=gap.id,
        action="gap_modified_by_rm",
        actor_role="RM",
        actor_id="RM_current",
        details_json=json.dumps({
            "requirement": gap.requirement,
            "party_name": gap.party_name,
            "old_active": old_active,
            "new_active": gap.is_active,
            "reason": payload.reason or "RM manual override",
        }),
    )
    db.add(audit)
    db.commit()
    db.refresh(gap)
    return gap

@router.post("/cases/{case_id}/gaps", response_model=GapRowOut)
def add_custom_gap(case_id: int, payload: GapRowCreate, db: Session = Depends(get_db)):
    """Allows RM to manually add a missing document requirement."""
    case = db.query(ChaseCase).filter(ChaseCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    new_gap = GapRow(
        case_id=case.id,
        party_name=payload.party_name,
        requirement=payload.requirement,
        status=payload.status.value,
        evidence=payload.evidence or "Manually added by RM",
        rule_id=payload.rule_id,
        is_active=True,
        notes=payload.notes,
    )
    db.add(new_gap)
    db.flush()

    audit = AuditLog(
        case_id=case.id,
        entity_type="gap_row",
        entity_id=new_gap.id,
        action="gap_added_by_rm",
        actor_role="RM",
        actor_id="RM_current",
        details_json=json.dumps({
            "requirement": new_gap.requirement,
            "party_name": new_gap.party_name,
            "notes": new_gap.notes,
        }),
    )
    db.add(audit)
    db.commit()
    db.refresh(new_gap)
    return new_gap

@router.post("/emails/{email_id}/send")
def send_email_simulated(
    email_id: int,
    payload: ChaseEmailSendRequest,
    db: Session = Depends(get_db)
):
    """
    Simulated Send Action (Constraint C2):
    NO auto-send. Sending requires explicit human RM action.
    Strictly verifies that NO '[RM TO CONFIRM: ...]' placeholders remain in the text!
    Updates email status to 'sent_simulated' and logs edits diff in audit trail.
    """
    email = db.query(ChaseEmail).filter(ChaseEmail.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    case = db.query(ChaseCase).filter(ChaseCase.id == email.case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Associated case not found")

    # Use updated body and subject if RM edited in the UI before clicking send
    final_subject = payload.subject or email.subject
    final_body = payload.body or email.body

    # Check for unresolved placeholders
    placeholder_matches = re.findall(r"\[RM TO CONFIRM:\s*([^\]]+)\]", final_body, re.IGNORECASE)
    if placeholder_matches:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot send email with unresolved placeholders: {placeholder_matches}. Please replace all [RM TO CONFIRM: ...] placeholders with verified values."
        )

    # Calculate edits diff
    edits_diff = None
    if final_body != email.body:
        edits_diff = f"RM modified {abs(len(final_body) - len(email.body))} characters prior to sending."

    # Mark as sent_simulated
    email.subject = final_subject
    email.body = final_body
    email.status = "sent_simulated"
    email.edits_diff = edits_diff
    email.sent_at = datetime.now(timezone.utc)

    # Update case status and contact date
    clock = db.query(SimulatedClock).first()
    curr_date = clock.current_simulated_date if clock else settings.SIMULATED_DATE
    case.last_contact_date = curr_date
    case.status = "awaiting_docs"

    # Append to append-only audit trail
    audit = AuditLog(
        case_id=case.id,
        entity_type="chase_email",
        entity_id=email.id,
        action="email_sent_simulated",
        actor_role="RM",
        actor_id=payload.actor_id,
        details_json=json.dumps({
            "subject": final_subject,
            "recipient": case.client_email,
            "edits_diff": edits_diff,
            "sent_at": email.sent_at.isoformat(),
        }),
    )
    db.add(audit)
    db.commit()

    return {
        "status": "sent_simulated",
        "message": "Email successfully marked as sent in simulated outbox (nothing left the system).",
        "email_id": email.id,
        "case_id": case.id,
        "sent_at": email.sent_at,
        "last_contact_date": case.last_contact_date,
    }

@router.post("/cases/{case_id}/simulate-reply")
def simulate_client_reply(
    case_id: int,
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Simulates a client reply (partial or full):
    Receives documents, re-runs gap check, updates list, restarts the 3-day clock
    for remaining items only, and increments rounds_count.
    """
    case = db.query(ChaseCase).filter(ChaseCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    clock = db.query(SimulatedClock).first()
    curr_date = clock.current_simulated_date if clock else settings.SIMULATED_DATE

    # New documents provided in the payload
    # e.g. [{"filename": "updated_passport.pdf", "doc_type": "Passport", "expiry_date": "2032-10-01", "signed": True}]
    new_docs = payload.get("documents", [])
    for doc_item in new_docs:
        rec_doc = ReceivedDocument(
            case_id=case.id,
            filename=doc_item.get("filename", "client_submission.pdf"),
            file_path=str(settings.DATA_DIR + "/" + doc_item.get("filename", "client_submission.pdf")),
            doc_type=doc_item.get("doc_type"),
            party_name=doc_item.get("party_name", case.client_name),
            issue_date=doc_item.get("issue_date", curr_date),
            expiry_date=doc_item.get("expiry_date"),
            page_count=doc_item.get("page_count", 1),
            pages_present=doc_item.get("pages_present", "1 of 1"),
            signed=doc_item.get("signed", True),
        )
        db.add(rec_doc)
    db.flush()

    # Restart contact date to today (Day 0 of new round)
    case.last_contact_date = curr_date
    case.rounds_count += 1

    # Re-run full analysis
    analysis = orchestrator.analyse_case(case.id, db)

    # Log audit entry
    audit = AuditLog(
        case_id=case.id,
        entity_type="chase_case",
        entity_id=case.id,
        action="client_reply_received_partial_or_full",
        actor_role="System",
        actor_id="client_portal_simulated",
        details_json=json.dumps({
            "documents_received_count": len(new_docs),
            "new_rounds_count": case.rounds_count,
            "new_contact_date": case.last_contact_date,
        }),
    )
    db.add(audit)
    db.commit()

    return {
        "case_id": case.id,
        "rounds_count": case.rounds_count,
        "last_contact_date": case.last_contact_date,
        "analysis": analysis,
    }

@router.get("/tasks", response_model=List[ReminderTaskOut])
def list_tasks(db: Session = Depends(get_db)):
    """RM Task inbox: returns all reminder tasks due (Day 3/6/9)."""
    tasks = db.query(ReminderTask).filter(ReminderTask.status != "completed").all()
    results = []
    for t in tasks:
        client_name = t.case.client_name if t.case else None
        out = ReminderTaskOut.model_validate(t)
        out.case_client_name = client_name
        results.append(out)
    return results

@router.post("/tasks/{task_id}/snooze", response_model=ReminderTaskOut)
def snooze_task(
    task_id: int,
    payload: ReminderTaskSnoozeRequest,
    db: Session = Depends(get_db)
):
    """Allows RM to snooze a reminder task with a reason."""
    task = db.query(ReminderTask).filter(ReminderTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    clock = db.query(SimulatedClock).first()
    curr_date = clock.current_simulated_date if clock else settings.SIMULATED_DATE

    snoozed_until_date = add_business_days(curr_date, payload.snooze_days)
    task.status = "snoozed"
    task.snoozed_until = snoozed_until_date
    task.snooze_reason = payload.reason

    audit = AuditLog(
        case_id=task.case_id,
        entity_type="reminder_task",
        entity_id=task.id,
        action="task_snoozed_by_rm",
        actor_role="RM",
        actor_id="RM_current",
        details_json=json.dumps({
            "snoozed_until": snoozed_until_date,
            "reason": payload.reason,
        }),
    )
    db.add(audit)
    db.commit()
    db.refresh(task)
    return task

@router.post("/tasks/{task_id}/complete")
def complete_task(task_id: int, db: Session = Depends(get_db)):
    """Marks a reminder task as completed."""
    task = db.query(ReminderTask).filter(ReminderTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = "completed"
    task.completed_at = datetime.now(timezone.utc)

    audit = AuditLog(
        case_id=task.case_id,
        entity_type="reminder_task",
        entity_id=task.id,
        action="task_completed_by_rm",
        actor_role="RM",
        actor_id="RM_current",
        details_json=json.dumps({"task_title": task.title}),
    )
    db.add(audit)
    db.commit()
    return {"status": "completed", "task_id": task.id}

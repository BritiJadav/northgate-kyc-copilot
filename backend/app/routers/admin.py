from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from backend.app.db import get_db
from backend.app.models.governance import SimulatedClock, AuditLog, AgentRun
from backend.app.engines.business_calendar import add_business_days
from backend.app.agents.orchestrator import orchestrator
from backend.app.seed.seed_data import seed_all
from backend.app.config import settings

router = APIRouter(prefix="/api/admin", tags=["Admin & Demo Controls"])

@router.get("/clock")
def get_clock(db: Session = Depends(get_db)):
    """Returns current simulated clock date."""
    clock = db.query(SimulatedClock).first()
    curr_date = clock.current_simulated_date if clock else settings.SIMULATED_DATE
    return {"simulated_date": curr_date}

@router.post("/advance-clock")
def advance_clock(
    days: int = Query(default=1, description="Number of business days to advance"),
    db: Session = Depends(get_db)
):
    """
    Advances mock business clock and immediately triggers follow-up cadence rules (Day 3 / 6 / 9)
    so the guide can see reminder tasks fire in real-time.
    """
    clock = db.query(SimulatedClock).first()
    if not clock:
        clock = SimulatedClock(current_simulated_date=settings.SIMULATED_DATE)
        db.add(clock)
        db.flush()

    old_date = clock.current_simulated_date
    new_date = add_business_days(old_date, days)
    clock.current_simulated_date = new_date
    db.commit()

    # Trigger follow-up checks across all cases with the new simulated date
    created_tasks = orchestrator.check_all_case_reminders(db)

    audit = AuditLog(
        entity_type="simulated_clock",
        entity_id=clock.id,
        action="advance_clock",
        actor_role="Admin",
        actor_id="demo_operator",
        details_json=f'{{"old_date": "{old_date}", "new_date": "{new_date}", "tasks_created": {len(created_tasks)}}}',
    )
    db.add(audit)
    db.commit()

    return {
        "old_date": old_date,
        "new_date": new_date,
        "advanced_business_days": days,
        "new_tasks_triggered_count": len(created_tasks),
        "triggered_tasks": [
            {
                "id": t.id,
                "case_id": t.case_id,
                "day_number": t.day_number,
                "task_type": t.task_type,
                "title": t.title,
            }
            for t in created_tasks
        ],
    }

@router.post("/reset-demo")
def reset_demo():
    """Resets database and re-seeds all synthetic data and baseline caches."""
    try:
        seed_all()
        return {"status": "success", "message": "Demo data reset successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")

@router.get("/audit")
def get_audit_trail(
    case_id: Optional[int] = None,
    company_id: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Retrieves immutable append-only audit trail."""
    query = db.query(AuditLog)
    if case_id is not None:
        query = query.filter(AuditLog.case_id == case_id)
    if company_id is not None:
        query = query.filter(AuditLog.company_id == company_id)
    
    logs = query.order_by(AuditLog.id.desc()).limit(limit).all()
    return [
        {
            "id": l.id,
            "case_id": l.case_id,
            "company_id": l.company_id,
            "entity_type": l.entity_type,
            "entity_id": l.entity_id,
            "action": l.action,
            "actor_role": l.actor_role,
            "actor_id": l.actor_id,
            "details": l.details_json,
            "created_at": l.created_at,
        }
        for l in logs
    ]

@router.get("/agent-runs")
def get_agent_runs(limit: int = 20, db: Session = Depends(get_db)):
    """Retrieves agent run trace history for the UI agent trace drawer."""
    runs = db.query(AgentRun).order_by(AgentRun.id.desc()).limit(limit).all()
    return [
        {
            "id": r.id,
            "agent_name": r.agent_name,
            "prompt_version": r.prompt_version,
            "input_hash": r.input_hash,
            "latency_ms": r.latency_ms,
            "tokens_used": r.tokens_used,
            "cache_hit": r.cache_hit,
            "status": r.status,
            "created_at": r.created_at,
        }
        for r in runs
    ]

import json
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from backend.app.db import get_db
from backend.app.models.kyc import (
    Company, AISuggestion, AnalystDecision, PossibleMatch, ConfirmedRecord
)
from backend.app.models.governance import AuditLog
from backend.app.schemas.kyc import (
    AnalystDecisionCreate,
    AnalystDecisionOut,
    PossibleMatchResolveRequest,
    AddPartyRequest,
    ConfirmedRecordOut,
)
from backend.app.services.confirm_workflow import confirm_workflow

router = APIRouter(prefix="/api/kyc", tags=["Analyst Operations"])

@router.post("/files/{company_id}/extract")
def extract_file_data(company_id: int, db: Session = Depends(get_db)):
    """
    Runs Module B extraction pipeline:
    Extractor -> Quote Verifier (C5) -> Control Flags -> Entity Resolution -> Look-through & Voting (C6).
    """
    try:
        res = confirm_workflow.extract_and_generate_suggestions(company_id=company_id, db=db)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

@router.get("/files/{company_id}/suggestions")
def get_file_suggestions(company_id: int, db: Session = Depends(get_db)):
    """
    Returns ordered confirm rows for analyst review (hardest first, no accept-all).
    """
    return confirm_workflow.get_ordered_confirm_rows(company_id=company_id, db=db)

@router.post("/suggestions/{suggestion_id}/decision", response_model=AnalystDecisionOut)
def record_suggestion_decision(
    suggestion_id: int,
    payload: AnalystDecisionCreate,
    db: Session = Depends(get_db)
):
    """
    Analyst accepts, edits, or rejects an individual AI suggestion row with reason code.
    NO accept-all (Constraint C8/C9).
    """
    sugg = db.query(AISuggestion).filter(AISuggestion.id == suggestion_id).first()
    if not sugg:
        raise HTTPException(status_code=404, detail="Suggestion not found")

    decision = confirm_workflow.record_decision(
        company_id=sugg.company_id,
        suggestion_id=sugg.id,
        field_name=sugg.field_name,
        action=payload.action.value,
        final_value=payload.final_value,
        reason_code=payload.reason_code.value if payload.reason_code else None,
        rationale=payload.rationale,
        time_spent_ms=payload.time_spent_ms,
        source_opened=payload.source_opened,
        analyst_id=payload.analyst_id,
        db=db,
    )
    return decision

@router.post("/files/{company_id}/add-party", response_model=AnalystDecisionOut)
def add_missed_party(
    company_id: int,
    payload: AddPartyRequest,
    db: Session = Depends(get_db)
):
    """Allows analyst to manually add a party or holding the AI missed."""
    comp = db.query(Company).filter(Company.id == company_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Company not found")

    final_val = f"{payload.party_name} ({payload.role})"
    if payload.ownership_pct is not None:
        final_val += f" - {payload.ownership_pct:.1f}% equity"
    if payload.voting_pct is not None:
        final_val += f" - {payload.voting_pct:.1f}% votes"

    decision = confirm_workflow.record_decision(
        company_id=comp.id,
        suggestion_id=None,
        field_name=f"Manual Party Addition: {payload.party_name}",
        action="add",
        final_value=final_val,
        reason_code="missed_party",
        rationale=payload.notes or "Analyst identified party omitted by AI",
        analyst_id=payload.analyst_id,
        db=db,
    )
    return decision

@router.post("/files/{company_id}/resolve-match")
def resolve_entity_match(
    company_id: int,
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Analyst confirms or separates candidate same-person match (Constraint C8).
    'confirm_same' triggers deterministic recompute of merged look-through percentage!
    """
    match_id = payload.get("match_id")
    action = payload.get("action") # "confirm_same" | "confirm_different"
    analyst_id = payload.get("analyst_id", "analyst_1")

    if not match_id or not action:
        raise HTTPException(status_code=400, detail="match_id and action required")

    res = confirm_workflow.resolve_match(
        company_id=company_id,
        match_id=match_id,
        action=action,
        analyst_id=analyst_id,
        db=db,
    )
    return res

@router.post("/files/{company_id}/submit")
def submit_kyc_file(
    company_id: int,
    payload: Dict[str, Any] = Body(default={"analyst_id": "analyst_1"}),
    db: Session = Depends(get_db)
):
    """
    Submits file:
    Enforces that EVERY suggestion row has an explicit decision and all matches are resolved.
    Populates confirmed_records table.
    """
    analyst_id = payload.get("analyst_id", "analyst_1")
    return confirm_workflow.submit_file(
        company_id=company_id,
        analyst_id=analyst_id,
        db=db,
    )

@router.get("/files/{company_id}/confirmed", response_model=List[ConfirmedRecordOut])
def get_confirmed_records_for_downstream(
    company_id: int,
    db: Session = Depends(get_db)
):
    """
    Constraint C9 (Data Separation):
    Downstream systems, reporting tools, and exports read ONLY from this confirmed_records endpoint.
    They never read from ai_suggestions directly.
    """
    records = (
        db.query(ConfirmedRecord)
        .filter(ConfirmedRecord.company_id == company_id)
        .order_by(ConfirmedRecord.id.asc())
        .all()
    )
    return records

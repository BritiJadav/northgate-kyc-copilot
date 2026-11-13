from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.app.db import get_db
from backend.app.models.chase import ChaseCase, GapRow
from backend.app.models.governance import SimulatedClock
from backend.app.schemas.chase import ChaseCaseSummary, ChaseCaseDetail
from backend.app.engines.business_calendar import business_days_between
from backend.app.config import settings

router = APIRouter(prefix="/api/chase", tags=["Chase Cases"])

@router.get("/cases", response_model=List[ChaseCaseSummary])
def list_cases(db: Session = Depends(get_db)):
    """Lists all KYC onboarding chase cases with current gap counts and timelines."""
    cases = db.query(ChaseCase).all()
    results = []
    
    clock = db.query(SimulatedClock).first()
    curr_date = clock.current_simulated_date if clock else settings.SIMULATED_DATE

    for c in cases:
        gap_count = (
            db.query(GapRow)
            .filter(GapRow.case_id == c.id, GapRow.is_active == True, GapRow.status != "OK")
            .count()
        )
        days_since = business_days_between(c.last_contact_date, curr_date) if c.last_contact_date else 0
        
        results.append(ChaseCaseSummary(
            id=c.id,
            case_number=c.case_number,
            client_name=c.client_name,
            client_type=c.client_type,
            status=c.status,
            rm_name=c.rm_name,
            deadline=c.deadline,
            last_contact_date=c.last_contact_date,
            rounds_count=c.rounds_count,
            gap_count=gap_count,
            created_at=c.created_at,
        ))
    return results

@router.get("/cases/{case_id}", response_model=ChaseCaseDetail)
def get_case_detail(case_id: int, db: Session = Depends(get_db)):
    """Retrieves full case details including parties, received documents, gaps, drafts, and reminders."""
    case = db.query(ChaseCase).filter(ChaseCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    gap_count = (
        db.query(GapRow)
        .filter(GapRow.case_id == case.id, GapRow.is_active == True, GapRow.status != "OK")
        .count()
    )

    # Find latest draft email possible follow-ons
    latest_email = (
        db.query(ChaseCase)
        .filter(ChaseCase.id == case_id)
        .first()
    )
    possible_followons = None
    if case.emails:
        possible_followons = case.emails[-1].possible_followons

    return ChaseCaseDetail(
        id=case.id,
        case_number=case.case_number,
        client_name=case.client_name,
        client_type=case.client_type,
        status=case.status,
        rm_name=case.rm_name,
        deadline=case.deadline,
        last_contact_date=case.last_contact_date,
        rounds_count=case.rounds_count,
        gap_count=gap_count,
        created_at=case.created_at,
        parties=case.parties,
        documents=case.documents,
        gaps=case.gaps,
        emails=case.emails,
        reminders=case.reminders,
        possible_followons=possible_followons,
    )

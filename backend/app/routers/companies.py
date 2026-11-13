from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.app.db import get_db
from backend.app.models.kyc import Company, AISuggestion, AnalystDecision
from backend.app.schemas.kyc import CompanySummary, CompanyDetail

router = APIRouter(prefix="/api/kyc", tags=["KYC Files"])

@router.get("/files", response_model=List[CompanySummary])
def list_companies(db: Session = Depends(get_db)):
    """Lists all KYC corporate files with status and pending review counts."""
    companies = db.query(Company).all()
    results = []

    for c in companies:
        suggestions_count = db.query(AISuggestion).filter(AISuggestion.company_id == c.id).count()
        decisions_count = db.query(AnalystDecision).filter(AnalystDecision.company_id == c.id).count()
        pending = max(0, suggestions_count - decisions_count)

        results.append(CompanySummary(
            id=c.id,
            name=c.name,
            code=c.code,
            jurisdiction=c.jurisdiction,
            registration_number=c.registration_number,
            incorporation_date=c.incorporation_date,
            status=c.status,
            pending_decisions_count=pending,
        ))
    return results

@router.get("/files/{company_id}", response_model=CompanyDetail)
def get_company_detail(company_id: int, db: Session = Depends(get_db)):
    """Retrieves full company detail including registered documents and confirmed status."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    suggestions_count = db.query(AISuggestion).filter(AISuggestion.company_id == company.id).count()
    decisions_count = db.query(AnalystDecision).filter(AnalystDecision.company_id == company.id).count()
    all_decided = (suggestions_count > 0) and (suggestions_count == decisions_count)

    return CompanyDetail(
        id=company.id,
        name=company.name,
        code=company.code,
        jurisdiction=company.jurisdiction,
        registration_number=company.registration_number,
        incorporation_date=company.incorporation_date,
        status=company.status,
        pending_decisions_count=max(0, suggestions_count - decisions_count),
        documents=company.documents,
        suggestions=company.suggestions,
        possible_matches=company.possible_matches,
        decisions=company.decisions,
        confirmed_records=company.confirmed_records,
        all_decided=all_decided,
    )

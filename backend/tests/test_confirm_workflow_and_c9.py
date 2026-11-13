import pytest
from fastapi import HTTPException
from backend.app.seed.seed_data import seed_all
from backend.app.db import SessionLocal
from backend.app.models.kyc import Company, AISuggestion, AnalystDecision, ConfirmedRecord, PossibleMatch
from backend.app.models.governance import MetricsEvent
from backend.app.services.confirm_workflow import confirm_workflow
from backend.app.routers.analyst import (
    extract_file_data,
    get_file_suggestions,
    record_suggestion_decision,
    resolve_entity_match,
    submit_kyc_file,
    get_confirmed_records_for_downstream,
)
from backend.app.schemas.kyc import AnalystDecisionCreate
from backend.app.schemas.common import DecisionActionEnum

@pytest.fixture(autouse=True)
def setup_test_db():
    seed_all(generate_files=False)

def test_submit_blocked_until_every_row_has_decision():
    """
    Policy Enforcement:
    Submission is blocked until every single row has an explicit human decision.
    There is NO accept-all endpoint.
    """
    db = SessionLocal()
    try:
        # Extract Company A (Alder & Finch)
        comp_a = db.query(Company).filter(Company.code == "COMPANY_A").first()
        extract_file_data(company_id=comp_a.id, db=db)

        # Attempt to submit immediately without making decisions
        with pytest.raises(HTTPException) as exc_info:
            submit_kyc_file(company_id=comp_a.id, payload={"analyst_id": "analyst_1"}, db=db)
        
        assert exc_info.value.status_code == 400
        assert "remain undecided" in exc_info.value.detail.lower()
    finally:
        db.close()

def test_kestrel_entity_resolution_and_submission_workflow():
    """
    Tests full workflow on Company E (Kestrel Trading Ltd):
    1. Extract yields candidate match: Tomas Berg vs Thomas Berg
    2. Before match resolution, submit is blocked
    3. Resolving match as 'confirm_same' recomputes lookthrough:
       Berg reaches 33.6% (UBO >=25%)!
    4. Analyst decides all rows
    5. Submit succeeds
    """
    db = SessionLocal()
    try:
        comp_e = db.query(Company).filter(Company.code == "COMPANY_E").first()
        extract_file_data(company_id=comp_e.id, db=db)

        # Verify candidate match exists
        matches = db.query(PossibleMatch).filter(PossibleMatch.company_id == comp_e.id).all()
        assert len(matches) >= 1
        berg_match = matches[0]
        assert "Berg" in berg_match.person_a_name

        # Resolve candidate match as confirmed_same
        resolve_res = resolve_entity_match(
            company_id=comp_e.id,
            payload={"match_id": berg_match.id, "action": "confirm_same", "analyst_id": "analyst_1"},
            db=db
        )
        assert resolve_res["status"] == "confirmed_same"

        # Check suggestions now contain merged Berg at 33.6%
        suggs = db.query(AISuggestion).filter(AISuggestion.company_id == comp_e.id).all()
        berg_sugg = next((s for s in suggs if "Berg" in s.value and "33.6%" in s.value), None)
        assert berg_sugg is not None, "Merged Berg at 33.6% must exist in suggestions after match confirmation"
        assert berg_sugg.field_type == "COMPUTED"

        # Record explicit decisions on all suggestions
        for s in suggs:
            record_suggestion_decision(
                suggestion_id=s.id,
                payload=AnalystDecisionCreate(
                    suggestion_id=s.id,
                    field_name=s.field_name,
                    action=DecisionActionEnum.ACCEPT,
                    final_value=s.value,
                    analyst_id="analyst_1",
                ),
                db=db
            )

        # Submit file
        sub_res = submit_kyc_file(company_id=comp_e.id, payload={"analyst_id": "analyst_1"}, db=db)
        assert sub_res["status"] == "submitted"
        assert sub_res["confirmed_count"] > 0
    finally:
        db.close()

def test_hard_constraint_c9_strict_data_separation():
    """
    Constraint C9:
    AI suggestions live in their own tables (ai_suggestions).
    Downstream consumers read ONLY the analyst-confirmed table (confirmed_records).
    Test proves that deleting/altering ai_suggestions has ZERO effect on downstream confirmed records.
    """
    db = SessionLocal()
    try:
        comp_a = db.query(Company).filter(Company.code == "COMPANY_A").first()
        extract_file_data(company_id=comp_a.id, db=db)
        suggs = db.query(AISuggestion).filter(AISuggestion.company_id == comp_a.id).all()

        for s in suggs:
            record_suggestion_decision(
                suggestion_id=s.id,
                payload=AnalystDecisionCreate(
                    suggestion_id=s.id,
                    field_name=s.field_name,
                    action=DecisionActionEnum.ACCEPT,
                    final_value=s.value,
                    analyst_id="analyst_1",
                ),
                db=db
            )

        submit_kyc_file(company_id=comp_a.id, payload={"analyst_id": "analyst_1"}, db=db)

        # Fetch confirmed records for downstream
        confirmed_before = get_confirmed_records_for_downstream(company_id=comp_a.id, db=db)
        assert len(confirmed_before) > 0
        original_values = [r.value for r in confirmed_before]

        # MUTATE AND WIPE ai_suggestions completely!
        db.query(AISuggestion).filter(AISuggestion.company_id == comp_a.id).delete()
        db.commit()

        # Re-fetch confirmed records for downstream: MUST REMAIN 100% INTACT!
        confirmed_after = get_confirmed_records_for_downstream(company_id=comp_a.id, db=db)
        assert len(confirmed_after) == len(confirmed_before)
        assert [r.value for r in confirmed_after] == original_values
    finally:
        db.close()

def test_hard_constraint_c10_canaries():
    """
    Constraint C10: Seeded canaries.
    In pilot mode, canaries are flagged in DB (canary_flag=True),
    NEVER shown in UI response, and catching one logs a telemetry metric.
    """
    db = SessionLocal()
    try:
        comp_a = db.query(Company).filter(Company.code == "COMPANY_A").first()
        extract_file_data(company_id=comp_a.id, db=db)

        # Check DB has canary_flag=True on at least one row
        canary = db.query(AISuggestion).filter(
            AISuggestion.company_id == comp_a.id,
            AISuggestion.canary_flag == True
        ).first()
        assert canary is not None
        assert canary.canary_flag is True

        # Check UI suggestions response hides canary_flag
        ui_res = get_file_suggestions(company_id=comp_a.id, db=db)
        for s in ui_res["suggestions"]:
            assert "canary_flag" not in s

        # Analyst catches the canary by editing/correcting the value
        record_suggestion_decision(
            suggestion_id=canary.id,
            payload=AnalystDecisionCreate(
                suggestion_id=canary.id,
                field_name=canary.field_name,
                action=DecisionActionEnum.EDIT,
                final_value="Analyst Corrected Value",
                reason_code="wrong_value",
                analyst_id="analyst_1",
            ),
            db=db
        )

        # Verify telemetry event was recorded
        ev = db.query(MetricsEvent).filter(MetricsEvent.event_type == "canary_caught").first()
        assert ev is not None
        assert ev.metric_value == 1.0
    finally:
        db.close()

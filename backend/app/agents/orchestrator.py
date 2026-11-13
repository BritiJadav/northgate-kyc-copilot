import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.app.models.chase import (
    ChaseCase, Party, ReceivedDocument, GapRow, ChaseEmail, ReminderTask
)
from backend.app.models.governance import SimulatedClock, AuditLog
from backend.app.agents.doc_classifier_agent import DocClassifierAgent
from backend.app.agents.gap_finder_agent import GapFinderAgent
from backend.app.agents.email_drafter_agent import EmailDrafterAgent
from backend.app.agents.guardrail_agent import GuardrailAgent
from backend.app.agents.followup_agent import FollowUpAgent
from backend.app.config import settings

class CaseOrchestrator:
    def __init__(self):
        self.classifier = DocClassifierAgent()
        self.gap_finder = GapFinderAgent()
        self.drafter = EmailDrafterAgent()
        self.guardrail = GuardrailAgent()
        self.followup = FollowUpAgent()

    def get_current_date(self, db: Session) -> str:
        clock = db.query(SimulatedClock).first()
        return clock.current_simulated_date if clock else settings.SIMULATED_DATE

    def analyse_case(self, case_id: int, db: Session) -> Dict[str, Any]:
        """
        Runs complete Module A analysis pipeline in one pass:
        1. Classifies received documents if not already classified
        2. Evaluates requirements matrix & detects all gaps
        3. Drafts single consolidated email with placeholders
        4. Verifies draft against safety guardrails
        """
        case = db.query(ChaseCase).filter(ChaseCase.id == case_id).first()
        if not case:
            raise ValueError(f"Case with id {case_id} not found")

        current_date_str = self.get_current_date(db)

        # 1. Classify received documents
        parties = [
            {
                "id": p.id,
                "name": p.name,
                "role": p.role,
                "ownership_pct": p.ownership_pct,
                "dob": p.dob,
                "nationality": p.nationality,
            }
            for p in case.parties
        ]

        doc_dicts = []
        for doc in case.documents:
            # If doc attributes are empty, classify via agent
            if not doc.doc_type:
                # Read sample text if file exists
                fpath = Path(doc.file_path)
                txt_content = ""
                indexed_txt = fpath.parent / f"{fpath.stem}_indexed.txt"
                if indexed_txt.exists():
                    with open(indexed_txt, "r", encoding="utf-8") as f:
                        txt_content = f.read()

                classified = self.classifier.run(
                    filename=doc.filename,
                    text_content=txt_content,
                    case_id=case.id,
                    db=db,
                )
                doc.doc_type = classified.doc_type
                doc.party_name = classified.party_name or doc.party_name
                doc.issue_date = classified.issue_date
                doc.expiry_date = classified.expiry_date
                doc.page_count = classified.page_count
                doc.pages_present = classified.pages_present
                doc.signed = classified.signed
                db.flush()

            doc_dicts.append({
                "id": doc.id,
                "filename": doc.filename,
                "doc_type": doc.doc_type,
                "party_name": doc.party_name,
                "issue_date": doc.issue_date,
                "expiry_date": doc.expiry_date,
                "page_count": doc.page_count,
                "pages_present": doc.pages_present,
                "signed": doc.signed,
            })

        # 2. Run deterministic Gap Finder
        gap_rows_data, possible_followons = self.gap_finder.run(
            client_type=case.client_type,
            parties=parties,
            documents=doc_dicts,
            current_date_str=current_date_str,
        )

        # Clear existing gap rows for this case and persist new ones
        db.query(GapRow).filter(GapRow.case_id == case.id).delete()
        persisted_gaps = []
        for g in gap_rows_data:
            gap_obj = GapRow(
                case_id=case.id,
                party_name=g["party_name"],
                requirement=g["requirement"],
                status=g["status"],
                evidence=g["evidence"],
                rule_id=g["rule_id"],
                is_active=g["is_active"],
            )
            db.add(gap_obj)
            persisted_gaps.append(gap_obj)
        db.flush()

        # 3. Draft single consolidated email
        draft_result = self.drafter.run(
            case_id=case.id,
            client_name=case.client_name,
            client_type=case.client_type,
            rm_name=case.rm_name,
            today_date=current_date_str,
            gap_list=gap_rows_data,
            possible_followons=possible_followons,
            db=db,
        )

        # 4. Run Guardrail checks
        guardrail_result = self.guardrail.run(
            subject=draft_result.subject,
            body=draft_result.body,
            gap_list=gap_rows_data,
            possible_followons=possible_followons,
        )

        # Save or update draft email
        email_obj = (
            db.query(ChaseEmail)
            .filter(ChaseEmail.case_id == case.id, ChaseEmail.status == "draft")
            .first()
        )
        if not email_obj:
            email_obj = ChaseEmail(
                case_id=case.id,
                subject=draft_result.subject,
                body=draft_result.body,
                notes_for_rm=draft_result.notes_for_rm,
                possible_followons=possible_followons,
                status="draft",
                guardrail_passed=guardrail_result.passed,
                guardrail_report=guardrail_result.model_dump_json(),
            )
            db.add(email_obj)
        else:
            email_obj.subject = draft_result.subject
            email_obj.body = draft_result.body
            email_obj.notes_for_rm = draft_result.notes_for_rm
            email_obj.possible_followons = possible_followons
            email_obj.guardrail_passed = guardrail_result.passed
            email_obj.guardrail_report = guardrail_result.model_dump_json()

        db.commit()

        return {
            "case_id": case.id,
            "case_number": case.case_number,
            "client_name": case.client_name,
            "current_simulated_date": current_date_str,
            "gaps": [
                {
                    "id": g.id,
                    "party_name": g.party_name,
                    "requirement": g.requirement,
                    "status": g.status,
                    "evidence": g.evidence,
                    "rule_id": g.rule_id,
                    "is_active": g.is_active,
                }
                for g in persisted_gaps
            ],
            "possible_followons": possible_followons,
            "draft_email": {
                "id": email_obj.id,
                "subject": email_obj.subject,
                "body": email_obj.body,
                "notes_for_rm": email_obj.notes_for_rm,
                "guardrail_passed": email_obj.guardrail_passed,
                "guardrail_report": json.loads(email_obj.guardrail_report or "{}"),
            },
        }

    def check_all_case_reminders(self, db: Session) -> List[ReminderTask]:
        """
        Evaluates business calendar rules across all cases and creates tasks where due.
        """
        current_date_str = self.get_current_date(db)
        cases = db.query(ChaseCase).all()
        created_tasks = []

        for case in cases:
            existing_tasks = [
                {
                    "id": t.id,
                    "day_number": t.day_number,
                    "task_type": t.task_type,
                    "status": t.status,
                    "snoozed_until": t.snoozed_until,
                    "triggered_at": t.triggered_at,
                }
                for t in case.reminders
            ]

            trigger = self.followup.run(
                last_contact_date_str=case.last_contact_date,
                current_date_str=current_date_str,
                existing_tasks=existing_tasks,
                client_name=case.client_name,
                rm_name=case.rm_name,
            )

            if trigger:
                task = ReminderTask(
                    case_id=case.id,
                    day_number=trigger["day_number"],
                    task_type=trigger["task_type"],
                    title=trigger["title"],
                    pre_drafted_text=trigger["pre_drafted_text"],
                    triggered_at=trigger["triggered_at"],
                    status="pending",
                )
                db.add(task)
                
                if trigger["task_type"] == "manager_flag":
                    case.status = "stalled"
                    
                created_tasks.append(task)

        if created_tasks:
            db.commit()

        return created_tasks

orchestrator = CaseOrchestrator()

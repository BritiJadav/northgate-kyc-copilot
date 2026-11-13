from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.db import Base
from backend.app.models.base import TimestampMixin

class ChaseCase(Base, TimestampMixin):
    __tablename__ = "chase_cases"

    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String(50), unique=True, index=True, nullable=False)
    client_name = Column(String(200), nullable=False)
    client_type = Column(String(50), nullable=False)  # individual, company, trust
    status = Column(String(50), default="in_progress") # in_progress, awaiting_docs, completed, stalled
    rm_name = Column(String(100), nullable=False)
    rm_email = Column(String(100), nullable=False)
    client_email = Column(String(100), nullable=False)
    deadline = Column(String(50), nullable=True)
    last_contact_date = Column(String(50), nullable=True) # YYYY-MM-DD
    rounds_count = Column(Integer, default=1)
    
    # Relationships
    parties = relationship("Party", back_populates="case", cascade="all, delete-orphan")
    documents = relationship("ReceivedDocument", back_populates="case", cascade="all, delete-orphan")
    gaps = relationship("GapRow", back_populates="case", cascade="all, delete-orphan")
    emails = relationship("ChaseEmail", back_populates="case", cascade="all, delete-orphan")
    reminders = relationship("ReminderTask", back_populates="case", cascade="all, delete-orphan")

class Party(Base, TimestampMixin):
    __tablename__ = "parties"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("chase_cases.id"), nullable=False)
    name = Column(String(200), nullable=False)
    role = Column(String(100), nullable=False) # individual_client, director, owner_25_plus, trustee, settlor
    ownership_pct = Column(Float, nullable=True)
    dob = Column(String(50), nullable=True)
    nationality = Column(String(50), nullable=True)

    case = relationship("ChaseCase", back_populates="parties")
    documents = relationship("ReceivedDocument", back_populates="party")

class RequirementsMatrixRule(Base, TimestampMixin):
    __tablename__ = "requirements_matrix_rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_code = Column(String(50), unique=True, nullable=False)
    client_type = Column(String(50), nullable=False) # individual, company, trust, all
    target_role = Column(String(100), nullable=False) # individual_client, director, owner_25_plus, trustee, company_entity
    document_type = Column(String(100), nullable=False)
    max_age_months = Column(Integer, nullable=True) # e.g. 3 for proof of address
    must_be_unexpired = Column(Boolean, default=False)
    must_be_complete = Column(Boolean, default=True) # all pages
    must_be_signed = Column(Boolean, default=False)
    description = Column(Text, nullable=False)

class ReceivedDocument(Base, TimestampMixin):
    __tablename__ = "received_documents"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("chase_cases.id"), nullable=False)
    party_id = Column(Integer, ForeignKey("parties.id"), nullable=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    doc_type = Column(String(100), nullable=True)
    party_name = Column(String(200), nullable=True)
    issue_date = Column(String(50), nullable=True)
    expiry_date = Column(String(50), nullable=True)
    page_count = Column(Integer, default=1)
    pages_present = Column(String(50), nullable=True) # e.g. "1-2 of 4"
    signed = Column(Boolean, nullable=True) # True, False, None
    raw_text = Column(Text, nullable=True)

    case = relationship("ChaseCase", back_populates="documents")
    party = relationship("Party", back_populates="documents")

class GapRow(Base, TimestampMixin):
    __tablename__ = "gap_rows"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("chase_cases.id"), nullable=False)
    party_name = Column(String(200), nullable=False)
    requirement = Column(String(200), nullable=False)
    status = Column(String(50), nullable=False) # OK, MISSING, EXPIRED, STALE, INCOMPLETE, WRONG_TYPE, UNSIGNED, NAME_MISMATCH
    evidence = Column(Text, nullable=True)
    rule_id = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)

    case = relationship("ChaseCase", back_populates="gaps")

class ChaseEmail(Base, TimestampMixin):
    __tablename__ = "chase_emails"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("chase_cases.id"), nullable=False)
    subject = Column(String(300), nullable=False)
    body = Column(Text, nullable=False)
    notes_for_rm = Column(Text, nullable=True)
    possible_followons = Column(Text, nullable=True) # RM-only notes
    status = Column(String(50), default="draft") # draft, approved, sent_simulated
    guardrail_passed = Column(Boolean, default=False)
    guardrail_report = Column(Text, nullable=True) # JSON report of check details
    edits_diff = Column(Text, nullable=True) # Diff between AI draft and RM final
    sent_at = Column(DateTime, nullable=True)

    case = relationship("ChaseCase", back_populates="emails")

class ReminderTask(Base, TimestampMixin):
    __tablename__ = "reminder_tasks"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("chase_cases.id"), nullable=False)
    day_number = Column(Integer, nullable=False) # 3, 6, 9
    task_type = Column(String(50), nullable=False) # email_reminder, phone_call, manager_flag
    title = Column(String(255), nullable=False)
    pre_drafted_text = Column(Text, nullable=True)
    status = Column(String(50), default="pending") # pending, completed, snoozed
    snoozed_until = Column(String(50), nullable=True) # YYYY-MM-DD
    snooze_reason = Column(Text, nullable=True)
    triggered_at = Column(String(50), nullable=False) # YYYY-MM-DD
    completed_at = Column(DateTime, nullable=True)

    case = relationship("ChaseCase", back_populates="reminders")

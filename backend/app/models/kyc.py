from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.db import Base
from backend.app.models.base import TimestampMixin

class Company(Base, TimestampMixin):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    code = Column(String(50), unique=True, index=True, nullable=False) # e.g. "COMPANY_A", "COMPANY_E"
    jurisdiction = Column(String(100), nullable=False)
    registration_number = Column(String(100), nullable=False)
    incorporation_date = Column(String(50), nullable=True) # YYYY-MM-DD
    status = Column(String(50), default="pending_review") # pending_review, in_review, submitted

    documents = relationship("CompanyDocument", back_populates="company", cascade="all, delete-orphan")
    suggestions = relationship("AISuggestion", back_populates="company", cascade="all, delete-orphan")
    possible_matches = relationship("PossibleMatch", back_populates="company", cascade="all, delete-orphan")
    decisions = relationship("AnalystDecision", back_populates="company", cascade="all, delete-orphan")
    confirmed_records = relationship("ConfirmedRecord", back_populates="company", cascade="all, delete-orphan")

class CompanyDocument(Base, TimestampMixin):
    __tablename__ = "company_documents"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    doc_hash = Column(String(64), nullable=False) # SHA-256
    page_count = Column(Integer, default=1)
    low_legibility = Column(Boolean, default=False)
    text_layer_json = Column(Text, nullable=True) # JSON list of {page, line, text}

    company = relationship("Company", back_populates="documents")

class AISuggestion(Base, TimestampMixin):
    __tablename__ = "ai_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    field_name = Column(String(200), nullable=False)
    value = Column(String(500), nullable=False)
    field_type = Column(String(50), nullable=False) # EXTRACTED, COMPUTED, NOT_FOUND
    formula = Column(Text, nullable=True) # e.g. "50% x 60% x 48% = 14.4%"
    inputs_json = Column(Text, nullable=True) # JSON list of edges or dependencies
    confidence = Column(Float, default=1.0)
    doc_source = Column(String(255), nullable=True)
    page = Column(Integer, nullable=True)
    line = Column(Integer, nullable=True)
    verbatim_quote = Column(Text, nullable=True)
    citation_verified = Column(Boolean, default=True) # C5: Deterministic verifier output
    canary_flag = Column(Boolean, default=False) # C10: Seeded canary indicator (hidden in UI)
    as_at = Column(String(100), default="current") # "current" or "at incorporation" or "2023-05-10"

    company = relationship("Company", back_populates="suggestions")

class PossibleMatch(Base, TimestampMixin):
    __tablename__ = "possible_matches"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    person_a_name = Column(String(200), nullable=False)
    person_b_name = Column(String(200), nullable=False)
    person_a_dob = Column(String(50), nullable=True)
    person_b_dob = Column(String(50), nullable=True)
    reason = Column(Text, nullable=False)
    status = Column(String(50), default="pending") # pending, confirmed_same, confirmed_different
    resolved_at = Column(DateTime, nullable=True)
    analyst_id = Column(String(100), nullable=True)

    company = relationship("Company", back_populates="possible_matches")

class AnalystDecision(Base, TimestampMixin):
    __tablename__ = "analyst_decisions"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    suggestion_id = Column(Integer, ForeignKey("ai_suggestions.id"), nullable=True)
    field_name = Column(String(200), nullable=False)
    action = Column(String(50), nullable=False) # accept, edit, reject, add
    original_value = Column(String(500), nullable=True)
    final_value = Column(String(500), nullable=False)
    reason_code = Column(String(100), nullable=True) # wrong_value, wrong_source, missed_party, stale_document, name_match_error, other
    rationale = Column(Text, nullable=True)
    time_spent_ms = Column(Integer, default=0)
    source_opened = Column(Boolean, default=False)
    analyst_id = Column(String(100), default="analyst_1")

    company = relationship("Company", back_populates="decisions")

class ConfirmedRecord(Base, TimestampMixin):
    """
    C9: Downstream consumers read ONLY this confirmed_records table.
    Data is populated solely from verified analyst decisions upon file submission.
    """
    __tablename__ = "confirmed_records"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    field_name = Column(String(200), nullable=False)
    value = Column(String(500), nullable=False)
    field_type = Column(String(50), nullable=False) # EXTRACTED, COMPUTED, NOT_FOUND
    formula = Column(Text, nullable=True)
    source_citation = Column(Text, nullable=True)
    confirmed_by = Column(String(100), nullable=False)
    as_at = Column(String(100), default="current")

    company = relationship("Company", back_populates="confirmed_records")

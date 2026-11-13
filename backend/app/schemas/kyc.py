from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from backend.app.schemas.common import (
    FieldTypeEnum,
    DecisionActionEnum,
    ReasonCodeEnum,
    MatchStatusEnum
)

class CompanyDocumentOut(BaseModel):
    id: int
    company_id: int
    filename: str
    file_path: str
    doc_hash: str
    page_count: int
    low_legibility: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AISuggestionOut(BaseModel):
    id: int
    company_id: int
    field_name: str
    value: str
    field_type: FieldTypeEnum
    formula: Optional[str] = None
    inputs_json: Optional[str] = None
    confidence: float
    doc_source: Optional[str] = None
    page: Optional[int] = None
    line: Optional[int] = None
    verbatim_quote: Optional[str] = None
    citation_verified: bool
    as_at: str
    decision: Optional[Dict[str, Any]] = None # Attached analyst decision if already decided
    model_config = ConfigDict(from_attributes=True)

class PossibleMatchOut(BaseModel):
    id: int
    company_id: int
    person_a_name: str
    person_b_name: str
    person_a_dob: Optional[str] = None
    person_b_dob: Optional[str] = None
    reason: str
    status: MatchStatusEnum
    resolved_at: Optional[datetime] = None
    analyst_id: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class PossibleMatchResolveRequest(BaseModel):
    action: str # "confirm_same" or "confirm_different"
    analyst_id: str = "analyst_1"

class AnalystDecisionCreate(BaseModel):
    suggestion_id: Optional[int] = None
    field_name: str
    action: DecisionActionEnum # accept, edit, reject, add
    final_value: str
    reason_code: Optional[ReasonCodeEnum] = None
    rationale: Optional[str] = None
    time_spent_ms: int = 0
    source_opened: bool = False
    analyst_id: str = "analyst_1"

class AnalystDecisionOut(BaseModel):
    id: int
    company_id: int
    suggestion_id: Optional[int] = None
    field_name: str
    action: str
    original_value: Optional[str] = None
    final_value: str
    reason_code: Optional[str] = None
    rationale: Optional[str] = None
    time_spent_ms: int
    source_opened: bool
    analyst_id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AddPartyRequest(BaseModel):
    party_name: str
    role: str
    ownership_pct: Optional[float] = None
    voting_pct: Optional[float] = None
    notes: Optional[str] = None
    analyst_id: str = "analyst_1"

class ConfirmedRecordOut(BaseModel):
    id: int
    company_id: int
    field_name: str
    value: str
    field_type: str
    formula: Optional[str] = None
    source_citation: Optional[str] = None
    confirmed_by: str
    as_at: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CompanySummary(BaseModel):
    id: int
    name: str
    code: str
    jurisdiction: str
    registration_number: str
    incorporation_date: Optional[str] = None
    status: str
    pending_decisions_count: int = 0
    model_config = ConfigDict(from_attributes=True)

class CompanyDetail(CompanySummary):
    documents: List[CompanyDocumentOut] = []
    suggestions: List[AISuggestionOut] = []
    possible_matches: List[PossibleMatchOut] = []
    decisions: List[AnalystDecisionOut] = []
    confirmed_records: List[ConfirmedRecordOut] = []
    all_decided: bool = False

# Structured Output Schemas for Agent LLM calls
class ExtractedEdge(BaseModel):
    owner: str = Field(description="Name of the shareholder/owner or holder entity")
    owned: str = Field(description="Name of company or entity held")
    shares_count: Optional[float] = Field(default=None, description="Number of shares held if stated")
    percentage: Optional[float] = Field(default=None, description="Direct percentage if explicitly stated in text")
    share_class: Optional[str] = Field(default="Ordinary", description="e.g. Ordinary, Class A, Class B")
    votes_per_share: Optional[float] = Field(default=None, description="Explicit voting rights per share if stated")
    as_at_date: str = Field(default="current", description="'current', specific date, or 'at incorporation'")
    doc: str = Field(description="Document filename")
    page: int = Field(description="Page number where fact appears")
    line: int = Field(description="Line number where fact appears")
    verbatim_quote: str = Field(description="Exact verbatim quote from the page")

class ExtractedOfficer(BaseModel):
    name: str
    role: str # Director, Secretary, CEO
    doc: str
    page: int
    line: int
    verbatim_quote: str

class OwnershipExtractorOutput(BaseModel):
    edges: List[ExtractedEdge] = []
    officers: List[ExtractedOfficer] = []
    entity_facts: List[str] = []
    has_share_register: bool = True
    notes: Optional[str] = None

class CandidateMatch(BaseModel):
    person_a: str
    person_b: str
    dob_match: bool
    nationality_match: bool
    reason: str

class EntityResolutionOutput(BaseModel):
    possible_matches: List[CandidateMatch] = []

class ControlFact(BaseModel):
    entity_or_person: str
    fact_type: str # nominee, trustee, appointment_rights, voting_control, shareholder_agreement
    description: str
    doc: str
    page: int
    line: int
    verbatim_quote: str

class ControlFlagsOutput(BaseModel):
    control_facts: List[ControlFact] = []
    nominees: List[str] = []
    trustees_without_beneficiaries: List[str] = []

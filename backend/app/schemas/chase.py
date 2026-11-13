from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from backend.app.schemas.common import GapStatusEnum

class PartyBase(BaseModel):
    name: str
    role: str
    ownership_pct: Optional[float] = None
    dob: Optional[str] = None
    nationality: Optional[str] = None

class PartyOut(PartyBase):
    id: int
    case_id: int
    model_config = ConfigDict(from_attributes=True)

class ReceivedDocumentOut(BaseModel):
    id: int
    case_id: int
    party_id: Optional[int] = None
    filename: str
    file_path: str
    doc_type: Optional[str] = None
    party_name: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    page_count: int
    pages_present: Optional[str] = None
    signed: Optional[bool] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class GapRowOut(BaseModel):
    id: int
    case_id: int
    party_name: str
    requirement: str
    status: GapStatusEnum
    evidence: Optional[str] = None
    rule_id: str
    is_active: bool
    notes: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class GapRowUpdate(BaseModel):
    is_active: Optional[bool] = None
    notes: Optional[str] = None
    reason: Optional[str] = None

class GapRowCreate(BaseModel):
    party_name: str
    requirement: str
    status: GapStatusEnum = GapStatusEnum.MISSING
    evidence: Optional[str] = None
    rule_id: str = "MANUAL_RM"
    notes: Optional[str] = None

class ChaseEmailOut(BaseModel):
    id: int
    case_id: int
    subject: str
    body: str
    notes_for_rm: Optional[str] = None
    possible_followons: Optional[str] = None
    status: str
    guardrail_passed: bool
    guardrail_report: Optional[str] = None
    edits_diff: Optional[str] = None
    sent_at: Optional[datetime] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ChaseEmailSendRequest(BaseModel):
    subject: Optional[str] = None
    body: Optional[str] = None
    actor_id: str = "RM_default"

class ReminderTaskOut(BaseModel):
    id: int
    case_id: int
    day_number: int
    task_type: str
    title: str
    pre_drafted_text: Optional[str] = None
    status: str
    snoozed_until: Optional[str] = None
    snooze_reason: Optional[str] = None
    triggered_at: str
    case_client_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class ReminderTaskSnoozeRequest(BaseModel):
    snooze_days: int = 1
    reason: str

class ChaseCaseSummary(BaseModel):
    id: int
    case_number: str
    client_name: str
    client_type: str
    status: str
    rm_name: str
    deadline: Optional[str] = None
    last_contact_date: Optional[str] = None
    rounds_count: int
    gap_count: int = 0
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ChaseCaseDetail(ChaseCaseSummary):
    parties: List[PartyOut] = []
    documents: List[ReceivedDocumentOut] = []
    gaps: List[GapRowOut] = []
    emails: List[ChaseEmailOut] = []
    reminders: List[ReminderTaskOut] = []
    possible_followons: Optional[str] = None

# Structured Output Schemas for Agents
class DocumentClassificationOutput(BaseModel):
    doc_type: str = Field(description="Normalized type e.g. Passport, Proof of Address, Shareholder Register, Bank Statement, Trust Deed")
    party_name: Optional[str] = Field(default=None, description="Name of party this document belongs to")
    issue_date: Optional[str] = Field(default=None, description="Date document was issued, YYYY-MM-DD or readable date")
    expiry_date: Optional[str] = Field(default=None, description="Date document expires, YYYY-MM-DD or readable date")
    page_count: int = Field(default=1, description="Total pages stated or counted")
    pages_present: str = Field(default="1 of 1", description="e.g. '1-2 of 4', 'all', '1-11 of 12'")
    signed: Optional[bool] = Field(default=None, description="Whether signature is present if required")

class EmailDraftOutput(BaseModel):
    subject: str = Field(description="Professional email subject line")
    body: str = Field(description="Consolidated email body covering all gaps with placeholders [RM TO CONFIRM: field]")
    notes_for_rm: str = Field(description="Internal RM operational notes")
    possible_followons: Optional[str] = Field(default=None, description="Confidential RM-only notes on what may follow")

class GuardrailCheckItem(BaseModel):
    check_name: str
    passed: bool
    details: str

class GuardrailOutput(BaseModel):
    passed: bool
    checks: List[GuardrailCheckItem]
    reasons: List[str]
    has_unresolved_placeholders: bool

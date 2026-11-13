from pydantic import BaseModel, ConfigDict
from typing import Optional, Any, List
from enum import Enum
from datetime import datetime

class FieldTypeEnum(str, Enum):
    EXTRACTED = "EXTRACTED"
    COMPUTED = "COMPUTED"
    NOT_FOUND = "NOT_FOUND"

class GapStatusEnum(str, Enum):
    OK = "OK"
    MISSING = "MISSING"
    EXPIRED = "EXPIRED"
    STALE = "STALE"
    INCOMPLETE = "INCOMPLETE"
    WRONG_TYPE = "WRONG_TYPE"
    UNSIGNED = "UNSIGNED"
    NAME_MISMATCH = "NAME_MISMATCH"

class DecisionActionEnum(str, Enum):
    ACCEPT = "accept"
    EDIT = "edit"
    REJECT = "reject"
    ADD = "add"

class ReasonCodeEnum(str, Enum):
    WRONG_VALUE = "wrong_value"
    WRONG_SOURCE = "wrong_source"
    MISSED_PARTY = "missed_party"
    STALE_DOCUMENT = "stale_document"
    NAME_MATCH_ERROR = "name_match_error"
    OTHER = "other"

class MatchStatusEnum(str, Enum):
    PENDING = "pending"
    CONFIRMED_SAME = "confirmed_same"
    CONFIRMED_DIFFERENT = "confirmed_different"

class PilotModeEnum(str, Enum):
    SHADOW = "shadow"
    ASSISTED = "assisted"

class CitationSchema(BaseModel):
    doc: str
    page: int
    line: int
    verbatim_quote: str

    model_config = ConfigDict(from_attributes=True)

class AgentRunOut(BaseModel):
    id: int
    agent_name: str
    prompt_version: str
    input_hash: str
    latency_ms: int
    tokens_used: int
    cache_hit: bool
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

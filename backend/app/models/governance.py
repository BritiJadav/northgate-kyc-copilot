from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float
from datetime import datetime, timezone
from backend.app.db import Base
from backend.app.models.base import TimestampMixin, utc_now

class AuditLog(Base):
    """
    Append-only audit trail for all human decisions, emails sent, and state transitions.
    """
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, nullable=True)
    company_id = Column(Integer, nullable=True)
    entity_type = Column(String(100), nullable=False) # e.g. "chase_email", "analyst_decision", "gap_row"
    entity_id = Column(Integer, nullable=True)
    action = Column(String(100), nullable=False) # e.g. "email_sent_simulated", "accepted", "edited", "rejected"
    actor_role = Column(String(50), nullable=False) # RM, Analyst, MLRO, Ops, System
    actor_id = Column(String(100), nullable=False)
    details_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

class AgentRun(Base):
    """
    Detailed log of every LLM agent execution for governance, trace visualization, and evaluation.
    """
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String(100), nullable=False)
    prompt_version = Column(String(50), nullable=False)
    input_hash = Column(String(64), nullable=False, index=True)
    input_json = Column(Text, nullable=True)
    output_json = Column(Text, nullable=True)
    latency_ms = Column(Integer, default=0)
    tokens_used = Column(Integer, default=0)
    cache_hit = Column(Boolean, default=False)
    status = Column(String(50), default="success") # success, failed, cached
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

class MetricsEvent(Base):
    """
    Telemetry events for pilot analytics and baseline comparison.
    """
    __tablename__ = "metrics_events"

    id = Column(Integer, primary_key=True, index=True)
    module = Column(String(50), nullable=False) # "chaser" or "analyst"
    event_type = Column(String(100), nullable=False) # "case_completed", "decision_made", "canary_caught", "canary_missed"
    metric_key = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

class SimulatedClock(Base):
    """
    Single-row table holding the simulated business clock date for time-travel demos.
    """
    __tablename__ = "simulated_clock"

    id = Column(Integer, primary_key=True)
    current_simulated_date = Column(String(50), nullable=False, default="2026-11-12")
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

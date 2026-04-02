"""Pydantic data models for the application."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AttackType(str, Enum):
    """Enumeration of possible attack types."""

    BRUTE_FORCE = "brute_force"
    PORT_SCAN = "port_scan"
    DOS = "denial_of_service"
    SQL_INJECTION = "sql_injection"
    NORMAL = "normal_traffic"
    UNKNOWN = "unknown"


class SeverityLevel(str, Enum):
    """Enumeration of severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class RecommendedAction(str, Enum):
    """Enumeration of recommended actions."""

    BLOCK_IP = "block_ip"
    ALERT_ADMIN = "alert_admin"
    MONITOR = "monitor"
    IGNORE = "ignore"
    QUARANTINE = "quarantine"


class LogEvent(BaseModel):
    """Model representing an incoming raw log event."""

    timestamp: str = Field(description="ISO format timestamp")
    source_ip: str = Field(description="Source IP address")
    destination_ip: str = Field(description="Destination IP address")
    destination_port: int = Field(description="Destination port number")
    protocol: str = Field(description="Network protocol (e.g., TCP, UDP, ICMP)")
    event_type: str = Field(description="Type of the event")
    raw_log: str = Field(description="The full raw log string")
    metadata: dict = Field(default_factory=dict, description="Optional extra fields")


class ResponsePlan(BaseModel):
    """Model representing the response agent's containment playbook."""

    response_steps: list[str] = Field(description="Step-by-step containment actions")
    estimated_impact: str = Field(description="One sentence on blast radius")
    escalate_to_tier2: bool = Field(description="Whether this needs a human SOC analyst")


class IncidentReport(BaseModel):
    """Model representing the structured output incident report."""

    event_id: str = Field(description="UUID for the event")
    timestamp: str = Field(description="Timestamp of when analysis happened")
    source_ip: str = Field(description="Source IP address of the potential attacker")
    attack_type: AttackType = Field(description="Classified attack type")
    severity: SeverityLevel = Field(description="Assessed severity level")
    confidence_score: float = Field(description="Confidence score from 0.0 to 1.0")
    recommended_action: RecommendedAction = Field(description="Recommended mitigation action")
    reasoning: str = Field(description="LLM's explanation of its classification (1-2 sentences)")
    indicators: list[str] = Field(description="List of suspicious signals found in the log")
    processing_time_ms: int = Field(description="Time taken to process the event in milliseconds")
    response_plan: Optional[ResponsePlan] = Field(default=None, description="Playbook from response agent, if triggered")
    needs_human_review: bool = Field(default=False, description="Flagged when confidence is too low for automation")
    human_review_message: Optional[str] = Field(default=None, description="Message for the analyst when flagged")
    graph_path: list[str] = Field(default_factory=list, description="Nodes traversed during graph execution")

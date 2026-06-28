"""Pydantic data models for the application — V2 Production."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AttackType(str, Enum):
    """Enumeration of possible attack types."""

    BRUTE_FORCE = "brute_force"
    PORT_SCAN = "port_scan"
    DOS = "denial_of_service"
    SQL_INJECTION = "sql_injection"
    XSS = "cross_site_scripting"
    COMMAND_INJECTION = "command_injection"
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


# ── V2: Tool Call Record ──────────────────────────────────────────────


class ToolCallRecord(BaseModel):
    """Record of a single tool invocation by an agent."""

    tool_name: str = Field(description="Name of the tool called")
    arguments: dict = Field(default_factory=dict, description="Arguments passed to the tool")
    result: dict = Field(default_factory=dict, description="Result returned by the tool")
    duration_ms: int = Field(default=0, description="Time taken for tool execution in ms")
    called_by: str = Field(default="", description="Which agent called this tool")


# ── V2: IP Investigation ──────────────────────────────────────────────


class IPInvestigation(BaseModel):
    """Result of investigating an IP address."""

    ip_address: str = ""
    country: str = ""
    city: str = ""
    isp: str = ""
    org: str = ""
    is_proxy: bool = False
    is_tor: bool = False
    abuse_score: int = Field(default=0, ge=0, le=100)
    is_known_malicious: bool = False
    threat_type: str = ""
    references: list[str] = Field(default_factory=list)


# ── V2: Port Scan Result ──────────────────────────────────────────────


class PortInfo(BaseModel):
    """Information about a single port."""

    port: int
    service: str = ""
    state: str = "closed"


class PortScanResult(BaseModel):
    """Result of a port scan on a target IP."""

    target_ip: str = ""
    open_ports: list[PortInfo] = Field(default_factory=list)
    os_guess: str = ""
    scan_time_ms: int = 0


# ── V2: Execution Trace ──────────────────────────────────────────────


class TraceStep(BaseModel):
    """A single step in the execution trace."""

    node_name: str = Field(description="Name of the graph node")
    display_name: str = Field(default="", description="Human-readable node name")
    started_at: str = Field(default="", description="ISO timestamp when step started")
    completed_at: str = Field(default="", description="ISO timestamp when step completed")
    duration_ms: int = Field(default=0, description="Duration of this step in ms")
    input_summary: str = Field(default="", description="Brief summary of input to this step")
    output_summary: str = Field(default="", description="Brief summary of output from this step")
    tools_called: list[ToolCallRecord] = Field(default_factory=list)
    decision: str = Field(default="", description="Rationale for decisions made in this step")


class ExecutionTrace(BaseModel):
    """Full execution trace for a single event analysis."""

    event_id: str = Field(default="", description="UUID for the event")
    started_at: str = Field(default="", description="ISO timestamp when execution started")
    completed_at: str = Field(default="", description="ISO timestamp when execution completed")
    total_duration_ms: int = Field(default=0, description="Total pipeline duration in ms")
    steps: list[TraceStep] = Field(default_factory=list)
    final_decision: str = Field(default="", description="Summary of final decision")


# ── V2: Memory Context ──────────────────────────────────────────────


class HistoricalMatch(BaseModel):
    """A single match from the vector memory system."""

    timestamp: str = ""
    attack_type: str = ""
    severity: str = ""
    source_ip: str = ""
    raw_log_snippet: str = ""
    similarity_score: float = Field(default=0.0, ge=0.0, le=1.0)


# ── Main Incident Report ─────────────────────────────────────────────


class IncidentReport(BaseModel):
    """Model representing the structured output incident report — V2."""

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

    # ── V2 Fields ──
    ip_investigation: Optional[IPInvestigation] = Field(default=None, description="GeoIP and threat intel results for the source IP")
    port_scan: Optional[PortScanResult] = Field(default=None, description="Port scan results for the source IP")
    tools_called: list[ToolCallRecord] = Field(default_factory=list, description="Record of all tool invocations")
    blocked: bool = Field(default=False, description="Whether the IP was actively blocked")
    blocked_until: Optional[str] = Field(default=None, description="ISO timestamp until which IP is blocked")
    historical_context: list[HistoricalMatch] = Field(default_factory=list, description="Similar past attacks from vector memory")
    execution_trace: Optional[ExecutionTrace] = Field(default=None, description="Full execution trace for observability")

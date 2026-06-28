"""Triage Agent V2 — Classifies incoming log events with tool use and memory context.

V2 Upgrades:
    - Integrates historical context from FAISS vector memory into the prompt
    - The graph's investigation_node runs tools before this agent is called
    - Enriched system prompt with memory-aware reasoning instructions
"""

from __future__ import annotations

import logging

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from src.core.config import settings
from src.models.schemas import AttackType, LogEvent, RecommendedAction, SeverityLevel, HistoricalMatch

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert Security Operations Center (SOC) analyst with 10 years of experience in network intrusion detection.
Analyze the provided network log event and classify it accurately into a structured incident report.
Be concise but thorough in your reasoning. Look for indicators of compromise (IoC) and anomalous patterns.
Your output must perfectly map to the requested structured JSON schema.

{memory_context}

{investigation_context}"""


class LLMOutput(BaseModel):
    """Model representing the structured output from the LLM."""

    attack_type: AttackType
    severity: SeverityLevel
    confidence_score: float = Field(ge=0.0, le=1.0)
    recommended_action: RecommendedAction
    reasoning: str
    indicators: list[str]


def _build_memory_prompt(historical_matches: list[HistoricalMatch]) -> str:
    """Build a memory context string from historical matches.

    Args:
        historical_matches: List of similar past incidents from FAISS.

    Returns:
        Formatted string for prompt injection, or empty string if no matches.
    """
    if not historical_matches:
        return ""

    lines = ["HISTORICAL CONTEXT (from attack memory database):"]
    for match in historical_matches[:5]:
        lines.append(
            f"  - [{match.timestamp}] {match.source_ip} → {match.attack_type} "
            f"(severity: {match.severity}, similarity: {match.similarity_score:.0%})"
        )
    lines.append(
        "Consider this history when assessing the current event. "
        "Repeated activity from the same IP suggests a multi-stage or persistent attack."
    )
    return "\n".join(lines)


def _build_investigation_prompt(ip_investigation: dict | None, threat_intel: dict | None) -> str:
    """Build an investigation context string from tool results.

    Args:
        ip_investigation: GeoIP/reputation data from investigate_ip tool.
        threat_intel: Threat intelligence feed data from check_threat_intel tool.

    Returns:
        Formatted string for prompt injection.
    """
    parts = []

    if ip_investigation:
        parts.append(
            f"IP INVESTIGATION RESULTS:\n"
            f"  Country: {ip_investigation.get('country', 'Unknown')}, "
            f"City: {ip_investigation.get('city', 'Unknown')}\n"
            f"  ISP: {ip_investigation.get('isp', 'Unknown')}, "
            f"Org: {ip_investigation.get('org', 'Unknown')}\n"
            f"  Proxy: {ip_investigation.get('is_proxy', False)}, "
            f"Tor: {ip_investigation.get('is_tor', False)}\n"
            f"  Abuse Score: {ip_investigation.get('abuse_score', 0)}/100"
        )

    if threat_intel:
        is_mal = threat_intel.get("is_known_malicious", False)
        parts.append(
            f"THREAT INTELLIGENCE:\n"
            f"  Known Malicious: {'YES' if is_mal else 'No'}\n"
            f"  Threat Type: {threat_intel.get('threat_type', 'None')}\n"
            f"  Sources: {', '.join(threat_intel.get('sources', [])) or 'None'}"
        )

    return "\n\n".join(parts) if parts else ""


def analyze_log_event(
    log_event: LogEvent,
    historical_matches: list[HistoricalMatch] | None = None,
    ip_investigation: dict | None = None,
    threat_intel: dict | None = None,
) -> dict:
    """Analyze a log event using an LLM triage agent with enriched context.

    Args:
        log_event: The raw log event to analyze.
        historical_matches: Similar past incidents from vector memory (optional).
        ip_investigation: GeoIP/reputation data from IP investigation tool (optional).
        threat_intel: Threat intel data from check_threat_intel tool (optional).

    Returns:
        Dict with analysis results (attack_type, severity, confidence_score, etc.).
    """
    logger.info("Triage agent analyzing log from %s", log_event.source_ip)

    # Build context strings
    memory_ctx = _build_memory_prompt(historical_matches or [])
    investigation_ctx = _build_investigation_prompt(ip_investigation, threat_intel)

    # Smart provider selection: Use Groq if available, fallback to OpenAI
    if settings.GROQ_API_KEY:
        from langchain_groq import ChatGroq
        llm = ChatGroq(
            model=settings.GROQ_MODEL,
            temperature=0,
            api_key=settings.GROQ_API_KEY,
        )
        logger.info("Using Groq model: %s", settings.GROQ_MODEL)
    else:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0,
            api_key=settings.OPENAI_API_KEY,
        )
        logger.info("Using OpenAI model: %s", settings.OPENAI_MODEL)

    structured_llm = llm.with_structured_output(LLMOutput)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "Log Event to analyze:\n{log_json}"),
        ]
    )

    chain = prompt | structured_llm
    result = chain.invoke({
        "log_json": log_event.model_dump_json(),
        "memory_context": memory_ctx,
        "investigation_context": investigation_ctx,
    })

    logger.info(
        "Triage result: %s (severity=%s, confidence=%.2f)",
        result.attack_type.value,
        result.severity.value,
        result.confidence_score,
    )
    return result.model_dump()

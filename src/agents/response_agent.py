"""Response Agent V2 — Generates containment playbooks and executes blocking actions.

V2 Upgrades:
    - After generating the playbook, calls block_ip() tool if recommended action is BLOCK_IP
    - Returns block status and tool call records for tracing
"""

from __future__ import annotations

import logging

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from src.core.config import settings
from src.models.schemas import IncidentReport

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a senior SOC incident responder with deep expertise in network defense and containment.
Given a triaged security incident, write a precise, actionable response playbook.
Focus on practical containment steps that a junior analyst could execute immediately.
Be specific — reference the actual IPs, ports, and attack vectors from the incident."""


class LLMResponseOutput(BaseModel):
    """Structured output from the response LLM."""

    response_steps: list[str] = Field(description="Step-by-step containment actions")
    estimated_impact: str = Field(description="One sentence on blast radius")
    escalate_to_tier2: bool = Field(description="Whether this needs a human SOC analyst")


def generate_response_plan(incident: IncidentReport) -> dict:
    """Generate a response playbook for a triaged incident.

    V2: Also executes the block_ip tool if the recommended action is BLOCK_IP.

    Args:
        incident: The triaged incident report.

    Returns:
        Dict with response plan data + optional block result and tool records.
    """
    logger.info("Response agent generating playbook for %s attack", incident.attack_type.value)

    if settings.GROQ_API_KEY:
        from langchain_groq import ChatGroq
        llm = ChatGroq(
            model=settings.GROQ_MODEL,
            temperature=0,
            api_key=settings.GROQ_API_KEY,
        )
    else:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0,
            api_key=settings.OPENAI_API_KEY,
        )

    structured_llm = llm.with_structured_output(LLMResponseOutput)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "Triaged Incident Report:\n{incident_json}"),
        ]
    )

    chain = prompt | structured_llm
    result = chain.invoke({"incident_json": incident.model_dump_json()})

    response_data = result.model_dump()

    # V2: Execute block_ip tool if recommended action is BLOCK_IP
    tool_records: list[dict] = []
    block_result = None

    if settings.TOOLS_ENABLED and incident.recommended_action.value == "block_ip":
        try:
            from src.tools.security_toolkit import block_ip

            block_res, block_record = block_ip(
                ip_address=incident.source_ip,
                reason=f"Automated: {incident.attack_type.value} attack (confidence {incident.confidence_score:.0%})",
                duration_hours=24,
            )
            block_result = block_res
            tool_records.append(block_record.model_dump())

            logger.info("IP %s blocked by response agent", incident.source_ip)

        except Exception as e:
            logger.error("Failed to execute block_ip: %s", e)

    response_data["_block_result"] = block_result
    response_data["_tool_records"] = tool_records

    return response_data

"""Response agent for generating containment playbooks from triaged incidents."""

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
    """Generate a response playbook for a triaged incident using Groq or OpenAI."""
    logger.info("Response agent generating playbook for %s attack", incident.attack_type.value)

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

    structured_llm = llm.with_structured_output(LLMResponseOutput)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "Triaged Incident Report:\n{incident_json}"),
        ]
    )

    chain = prompt | structured_llm
    result = chain.invoke({"incident_json": incident.model_dump_json()})

    return result.model_dump()

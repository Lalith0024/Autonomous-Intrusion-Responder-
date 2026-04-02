"""Triage agent for classifying incoming log events."""

import logging

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from src.core.config import settings
from src.models.schemas import AttackType, LogEvent, RecommendedAction, SeverityLevel

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert Security Operations Center (SOC) analyst with 10 years of experience in network intrusion detection.
Analyze the provided network log event and classify it accurately into a structured incident report.
Be concise but thorough in your reasoning. Look for indicators of compromise (IoC) and anomalous patterns.
Your output must perfectly map to the requested structured JSON schema."""


class LLMOutput(BaseModel):
    """Model representing the structured output from the LLM."""

    attack_type: AttackType
    severity: SeverityLevel
    confidence_score: float = Field(ge=0.0, le=1.0)
    recommended_action: RecommendedAction
    reasoning: str
    indicators: list[str]


def analyze_log_event(log_event: LogEvent) -> dict:
    """Analyze a log event using an LLM triage agent (Groq or OpenAI)."""
    logger.info("Initializing triage agent for log event from %s", log_event.source_ip)

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
    result = chain.invoke({"log_json": log_event.model_dump_json()})

    return result.model_dump()

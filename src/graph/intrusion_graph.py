"""LangGraph state graph for multi-agent intrusion detection and response."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, TypedDict

from langgraph.graph import END, START, StateGraph

from src.agents.response_agent import generate_response_plan
from src.agents.triage_agent import analyze_log_event
from src.models.schemas import IncidentReport, LogEvent, ResponsePlan

logger = logging.getLogger(__name__)


class GraphState(TypedDict):
    """The state used across the graph nodes."""

    log_event: LogEvent
    incident_report: Optional[IncidentReport]
    error: Optional[str]


def triage_node(state: GraphState) -> GraphState:
    """Classify the raw log event into a structured incident report.

    Args:
        state (GraphState): The current state of the graph.

    Returns:
        GraphState: State with incident report populated.
    """
    log_event = state["log_event"]
    logger.info("Triage node executing for source IP: %s", log_event.source_ip)

    try:
        analysis_data = analyze_log_event(log_event)

        report = IncidentReport(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            source_ip=log_event.source_ip,
            attack_type=analysis_data["attack_type"],
            severity=analysis_data["severity"],
            confidence_score=analysis_data["confidence_score"],
            recommended_action=analysis_data["recommended_action"],
            reasoning=analysis_data["reasoning"],
            indicators=analysis_data["indicators"],
            processing_time_ms=0,
            graph_path=["triage_node"],
        )

        return {"log_event": log_event, "incident_report": report, "error": None}

    except Exception as e:
        logger.error("Error in triage node: %s", str(e), exc_info=True)
        return {"log_event": log_event, "incident_report": None, "error": str(e)}


def severity_router(state: GraphState) -> str:
    """Route based on confidence and severity — the guardrail decision point.

    Args:
        state (GraphState): Current graph state with triage results.

    Returns:
        str: Next node name to route to.
    """
    report = state.get("incident_report")
    if not report or state.get("error"):
        return END

    confidence = report.confidence_score
    severity = report.severity.value

    if confidence < 0.7:
        logger.info("Low confidence (%.2f) — routing to human review", confidence)
        return "human_review_node"

    if severity in ("high", "critical"):
        logger.info("High-severity %s attack — routing to response agent", report.attack_type.value)
        return "response_agent"

    # Low/Medium severity with good confidence — triage is sufficient
    logger.info("Low-severity incident — triage output is final")
    report.graph_path.append("severity_router")
    return END


def response_agent_node(state: GraphState) -> GraphState:
    """Generate a containment playbook for high-severity incidents.

    Args:
        state (GraphState): Current state with triage results.

    Returns:
        GraphState: State with response plan attached.
    """
    report = state["incident_report"]
    report.graph_path.append("severity_router")

    try:
        plan_data = generate_response_plan(report)
        report.response_plan = ResponsePlan(**plan_data)
        report.graph_path.append("response_agent")

    except Exception as e:
        logger.error("Error in response agent: %s", str(e), exc_info=True)
        return {"log_event": state["log_event"], "incident_report": report, "error": str(e)}

    return {"log_event": state["log_event"], "incident_report": report, "error": None}


def human_review_node(state: GraphState) -> GraphState:
    """Flag low-confidence detections for analyst review — no LLM call.

    Args:
        state (GraphState): Current state with low-confidence triage.

    Returns:
        GraphState: State with human review flag set.
    """
    report = state["incident_report"]
    report.graph_path.append("severity_router")
    report.needs_human_review = True
    report.human_review_message = "Low confidence detection. Flagged for analyst review."
    report.graph_path.append("human_review_node")

    logger.info("Incident flagged for human review (confidence: %.2f)", report.confidence_score)

    return {"log_event": state["log_event"], "incident_report": report, "error": None}


def build_graph() -> StateGraph:
    """Build and compile the multi-agent execution graph.

    Returns:
        StateGraph: Compiled LangGraph instance.
    """
    workflow = StateGraph(GraphState)

    workflow.add_node("triage_node", triage_node)
    workflow.add_node("response_agent", response_agent_node)
    workflow.add_node("human_review_node", human_review_node)

    workflow.add_edge(START, "triage_node")

    # Conditional routing after triage — the core orchestration logic
    workflow.add_conditional_edges(
        "triage_node",
        severity_router,
        {
            "response_agent": "response_agent",
            "human_review_node": "human_review_node",
            END: END,
        },
    )

    workflow.add_edge("response_agent", END)
    workflow.add_edge("human_review_node", END)

    app = workflow.compile()
    return app


# The compiled graph instance to be used by the API
intrusion_app = build_graph()

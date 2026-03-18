"""LangGraph state graph for intrusion detection."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, TypedDict

from langgraph.graph import END, START, StateGraph

from src.agents.triage_agent import analyze_log_event
from src.models.schemas import IncidentReport, LogEvent

logger = logging.getLogger(__name__)

# FEATURE 2 EXTENSION POINT:
# Add forensics_node and threat_intel_node here as parallel branches
# using LangGraph's Send() API for fan-out parallelism


class GraphState(TypedDict):
    """The state used across the graph nodes."""

    log_event: LogEvent
    incident_report: Optional[IncidentReport]
    error: Optional[str]


def triage_node(state: GraphState) -> GraphState:
    """Node that executes the triage agent on the log event.

    Args:
        state (GraphState): The current state of the graph.

    Returns:
        GraphState: Evaluated state with incident report populated.
    """
    log_event = state["log_event"]
    logger.info("Triage node executing for source IP: %s", log_event.source_ip)

    try:
        # Get LLM analysis
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
            processing_time_ms=0,  # To be filled by API route
        )

        return {"log_event": log_event, "incident_report": report, "error": None}

    except Exception as e:
        logger.error("Error in triage node: %s", str(e), exc_info=True)
        return {"log_event": log_event, "incident_report": None, "error": str(e)}


def build_graph() -> StateGraph:
    """Build and compile the execution graph.

    Returns:
        StateGraph: Compiled LangGraph instance.
    """
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("triage_node", triage_node)

    # Add edges
    workflow.add_edge(START, "triage_node")
    workflow.add_edge("triage_node", END)

    # Compile the graph
    app = workflow.compile()
    return app


# The compiled graph instance to be used by the API
intrusion_app = build_graph()

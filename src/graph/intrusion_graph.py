"""LangGraph V2 — Multi-agent execution graph with tools, memory, and tracing.

V2 Architecture:
    START → investigation_node → triage_node → severity_router →
        → response_agent (high/critical + confidence ≥ 0.7)
        → human_review_node (confidence < 0.7)
        → END (low/medium severity)
    → memory_persist_node → END

New Nodes:
    - investigation_node: Runs security tools (IP lookup, port scan, threat intel)
    - memory_persist_node: Stores the incident in FAISS vector memory

Enhanced:
    - Full execution tracing via TraceCollector
    - Historical context injection from vector memory
    - Tool call recording at every step
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, TypedDict

from langgraph.graph import END, START, StateGraph

from src.agents.response_agent import generate_response_plan
from src.agents.triage_agent import analyze_log_event
from src.core.config import settings
from src.core.tracer import TraceCollector
from src.models.schemas import (
    HistoricalMatch,
    IPInvestigation,
    IncidentReport,
    LogEvent,
    PortScanResult,
    ResponsePlan,
    ToolCallRecord,
)

logger = logging.getLogger(__name__)


class GraphState(TypedDict):
    """The state used across the graph nodes — V2."""

    log_event: LogEvent
    incident_report: Optional[IncidentReport]
    error: Optional[str]

    # V2: Enrichment data
    ip_investigation: Optional[dict]
    threat_intel: Optional[dict]
    port_scan: Optional[dict]
    historical_matches: Optional[list[dict]]
    tool_records: list[dict]
    tracer: Optional[TraceCollector]


def investigation_node(state: GraphState) -> GraphState:
    """Run security investigation tools before triage.

    Calls investigate_ip, scan_ports, and check_threat_intel to gather
    intelligence about the source IP. Also queries vector memory for
    historical context.

    Args:
        state: Current graph state with log_event.

    Returns:
        State enriched with investigation results.
    """
    log_event = state["log_event"]
    tracer: TraceCollector | None = state.get("tracer")
    tool_records = list(state.get("tool_records", []))

    if tracer:
        tracer.start_step("investigation_node", input_summary=f"Investigating IP {log_event.source_ip}")

    ip_investigation = None
    threat_intel = None
    port_scan = None
    historical_matches = None

    # Tool 1: IP Investigation
    if settings.TOOLS_ENABLED:
        try:
            from src.tools.security_toolkit import investigate_ip, scan_ports, check_threat_intel

            ip_result, ip_record = investigate_ip(log_event.source_ip)
            ip_investigation = ip_result.model_dump()
            tool_records.append(ip_record.model_dump())
            if tracer:
                tracer.add_tool_call(ip_record)

            # Tool 2: Port Scan
            port_result, port_record = scan_ports(log_event.source_ip)
            port_scan = port_result.model_dump()
            tool_records.append(port_record.model_dump())
            if tracer:
                tracer.add_tool_call(port_record)

            # Tool 3: Threat Intel
            ti_result, ti_record = check_threat_intel(log_event.source_ip)
            threat_intel = ti_result
            tool_records.append(ti_record.model_dump())
            if tracer:
                tracer.add_tool_call(ti_record)

        except Exception as e:
            logger.warning("Tool execution failed: %s. Continuing without tools.", e)

    # Memory: Query for historical context
    if settings.MEMORY_ENABLED:
        try:
            from src.memory import vector_store

            similar = vector_store.search_similar(log_event.raw_log, k=3)
            ip_history = vector_store.search_by_ip(log_event.source_ip)

            # Combine and deduplicate
            all_matches = {m.timestamp + m.source_ip: m for m in similar + ip_history}
            historical_matches = [m.model_dump() for m in all_matches.values()][:5]

        except Exception as e:
            logger.warning("Memory query failed: %s. Continuing without history.", e)

    if tracer:
        tool_count = len(tool_records) - len(state.get("tool_records", []))
        history_count = len(historical_matches) if historical_matches else 0
        tracer.end_step(
            output_summary=f"Ran {tool_count} tools, found {history_count} historical matches",
            decision="Investigation complete, forwarding to triage",
        )

    return {
        **state,
        "ip_investigation": ip_investigation,
        "threat_intel": threat_intel,
        "port_scan": port_scan,
        "historical_matches": historical_matches,
        "tool_records": tool_records,
    }


def triage_node(state: GraphState) -> GraphState:
    """Classify the raw log event into a structured incident report.

    V2: Receives investigation results and historical context
    which are injected into the LLM prompt for better analysis.

    Args:
        state: Current graph state with log_event and enrichment data.

    Returns:
        State with incident report populated.
    """
    log_event = state["log_event"]
    tracer: TraceCollector | None = state.get("tracer")
    tool_records = list(state.get("tool_records", []))

    if tracer:
        tracer.start_step("triage_node", input_summary=f"Classifying log from {log_event.source_ip}")

    try:
        # Build historical matches for memory context
        hist_matches = None
        if state.get("historical_matches"):
            hist_matches = [HistoricalMatch(**m) for m in state["historical_matches"]]

        analysis_data = analyze_log_event(
            log_event,
            historical_matches=hist_matches,
            ip_investigation=state.get("ip_investigation"),
            threat_intel=state.get("threat_intel"),
        )

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
            graph_path=["investigation_node", "triage_node"],
            # V2 fields
            ip_investigation=IPInvestigation(**state["ip_investigation"]) if state.get("ip_investigation") else None,
            port_scan=PortScanResult(**state["port_scan"]) if state.get("port_scan") else None,
            tools_called=[ToolCallRecord(**r) for r in tool_records],
            historical_context=[HistoricalMatch(**m) for m in (state.get("historical_matches") or [])],
        )

        if tracer:
            tracer.end_step(
                output_summary=f"Classified as {report.attack_type.value} (severity={report.severity.value}, confidence={report.confidence_score:.0%})",
                decision=report.reasoning[:150],
            )

        return {
            **state,
            "incident_report": report,
            "error": None,
            "tool_records": tool_records,
        }

    except Exception as e:
        logger.error("Error in triage node: %s", str(e), exc_info=True)
        if tracer:
            tracer.end_step(output_summary=f"ERROR: {str(e)}", decision="Triage failed")
        return {**state, "incident_report": None, "error": str(e)}


def severity_router(state: GraphState) -> str:
    """Route based on confidence and severity — the guardrail decision point.

    Args:
        state: Current graph state with triage results.

    Returns:
        Next node name to route to.
    """
    report = state.get("incident_report")
    tracer: TraceCollector | None = state.get("tracer")

    if not report or state.get("error"):
        return END

    confidence = report.confidence_score
    severity = report.severity.value

    if tracer:
        tracer.start_step("severity_router", input_summary=f"Routing: confidence={confidence:.2f}, severity={severity}")

    if confidence < 0.7:
        decision = f"Low confidence ({confidence:.2f}) — routing to human review"
        logger.info(decision)
        report.graph_path.append("severity_router")
        if tracer:
            tracer.end_step(output_summary="→ Human Review", decision=decision)
        return "human_review_node"

    if severity in ("high", "critical"):
        decision = f"High-severity {report.attack_type.value} attack with confidence {confidence:.2f} — routing to response agent"
        logger.info(decision)
        report.graph_path.append("severity_router")
        if tracer:
            tracer.end_step(output_summary="→ Response Agent", decision=decision)
        return "response_agent"

    # Low/Medium severity with good confidence — triage is sufficient
    decision = f"Low-severity incident ({severity}) — triage output is final"
    logger.info(decision)
    report.graph_path.append("severity_router")
    if tracer:
        tracer.end_step(output_summary="→ End (Low Severity)", decision=decision)
    return "memory_persist_node"


def response_agent_node(state: GraphState) -> GraphState:
    """Generate a containment playbook for high-severity incidents.

    V2: Also executes the block_ip tool if the action is BLOCK_IP.

    Args:
        state: Current state with triage results.

    Returns:
        State with response plan attached.
    """
    report = state["incident_report"]
    tracer: TraceCollector | None = state.get("tracer")
    tool_records = list(state.get("tool_records", []))

    report.graph_path.append("severity_router")

    if tracer:
        tracer.start_step("response_agent", input_summary=f"Generating playbook for {report.attack_type.value}")

    try:
        plan_data = generate_response_plan(report)

        # Extract V2 tool records from response agent
        response_tools = plan_data.pop("_tool_records", [])
        block_result = plan_data.pop("_block_result", None)

        report.response_plan = ResponsePlan(**plan_data)
        report.graph_path.append("response_agent")

        # V2: Record blocking action
        if block_result:
            report.blocked = block_result.get("success", False)
            report.blocked_until = block_result.get("blocked_until")
            for tr in response_tools:
                tool_records.append(tr)
                if tracer:
                    tracer.add_tool_call(ToolCallRecord(**tr))

        report.tools_called = [ToolCallRecord(**r) for r in tool_records]

        if tracer:
            step_count = len(report.response_plan.response_steps)
            blocked_msg = ", IP BLOCKED" if report.blocked else ""
            tracer.end_step(
                output_summary=f"Generated {step_count} containment steps{blocked_msg}",
                decision=f"Playbook created. Escalate to Tier 2: {report.response_plan.escalate_to_tier2}",
            )

    except Exception as e:
        logger.error("Error in response agent: %s", str(e), exc_info=True)
        if tracer:
            tracer.end_step(output_summary=f"ERROR: {str(e)}", decision="Response generation failed")
        return {**state, "incident_report": report, "error": str(e), "tool_records": tool_records}

    return {**state, "incident_report": report, "error": None, "tool_records": tool_records}


def human_review_node(state: GraphState) -> GraphState:
    """Flag low-confidence detections for analyst review — no LLM call.

    Args:
        state: Current state with low-confidence triage.

    Returns:
        State with human review flag set.
    """
    report = state["incident_report"]
    tracer: TraceCollector | None = state.get("tracer")

    if tracer:
        tracer.start_step("human_review_node", input_summary=f"Confidence {report.confidence_score:.2f} below threshold")

    report.graph_path.append("severity_router")
    report.needs_human_review = True
    report.human_review_message = (
        f"Low confidence detection ({report.confidence_score:.0%}). "
        f"Flagged for analyst review. Autonomous response blocked."
    )
    report.graph_path.append("human_review_node")

    logger.info("Incident flagged for human review (confidence: %.2f)", report.confidence_score)

    if tracer:
        tracer.end_step(
            output_summary="Flagged for human review",
            decision=f"Confidence {report.confidence_score:.2f} < 0.70 threshold — human intervention required",
        )

    return {**state, "incident_report": report, "error": None}


def memory_persist_node(state: GraphState) -> GraphState:
    """Store the processed incident in vector memory for future reference.

    Args:
        state: Current state with finalized incident report.

    Returns:
        State unchanged (memory side-effect only).
    """
    report = state.get("incident_report")
    tracer: TraceCollector | None = state.get("tracer")

    if tracer:
        tracer.start_step("memory_persist_node", input_summary="Persisting incident to vector memory")

    if report and settings.MEMORY_ENABLED:
        try:
            from src.memory import vector_store
            vector_store.add_incident(report)
            logger.info("Incident %s persisted to vector memory", report.event_id)
            if tracer:
                tracer.end_step(output_summary="Incident stored in FAISS index", decision="Memory updated")
        except Exception as e:
            logger.warning("Failed to persist to memory: %s", e)
            if tracer:
                tracer.end_step(output_summary=f"Memory persist failed: {e}", decision="Non-critical failure")
    else:
        if tracer:
            tracer.end_step(output_summary="Memory disabled or no report", decision="Skipped")

    return state


def build_graph() -> StateGraph:
    """Build and compile the V2 multi-agent execution graph.

    Returns:
        Compiled LangGraph instance.
    """
    workflow = StateGraph(GraphState)

    # V2: Add all nodes including new investigation and memory nodes
    workflow.add_node("investigation_node", investigation_node)
    workflow.add_node("triage_node", triage_node)
    workflow.add_node("response_agent", response_agent_node)
    workflow.add_node("human_review_node", human_review_node)
    workflow.add_node("memory_persist_node", memory_persist_node)

    # V2: Investigation runs first, then triage
    workflow.add_edge(START, "investigation_node")
    workflow.add_edge("investigation_node", "triage_node")

    # Conditional routing after triage — the core orchestration logic
    workflow.add_conditional_edges(
        "triage_node",
        severity_router,
        {
            "response_agent": "response_agent",
            "human_review_node": "human_review_node",
            "memory_persist_node": "memory_persist_node",
            END: END,
        },
    )

    # V2: All paths lead to memory persist, then END
    workflow.add_edge("response_agent", "memory_persist_node")
    workflow.add_edge("human_review_node", "memory_persist_node")
    workflow.add_edge("memory_persist_node", END)

    app = workflow.compile()
    return app


# The compiled graph instance to be used by the API
intrusion_app = build_graph()

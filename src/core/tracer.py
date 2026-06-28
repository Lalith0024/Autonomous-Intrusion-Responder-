"""Execution Trace System — Full observability for every pipeline run.

Every decision the AI makes gets recorded into a structured trace that shows:
- Which nodes were executed and in what order
- How long each step took
- What tools were called and what they returned
- Why the router made its routing decision
- Total pipeline cost estimate

The trace gets attached to the IncidentReport and rendered in the Streamlit dashboard.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from src.models.schemas import ExecutionTrace, ToolCallRecord, TraceStep

logger = logging.getLogger(__name__)

# Node name → human-readable label
NODE_DISPLAY_NAMES = {
    "investigation_node": "🔍 Investigation",
    "triage_node": "🧠 Triage Agent",
    "severity_router": "🔀 Policy Router",
    "response_agent": "⚔️ Response Agent",
    "human_review_node": "👤 Human Review",
    "memory_persist_node": "💾 Memory Persist",
}


class TraceCollector:
    """Collects trace steps during a single pipeline execution.

    Usage:
        tracer = TraceCollector(event_id="abc-123")
        tracer.start_step("triage_node", input_summary="Analyzing log from 45.33.32.156")
        # ... do work ...
        tracer.end_step(output_summary="Classified as brute_force (95%)", decision="High confidence threat")
        trace = tracer.finalize()
    """

    def __init__(self, event_id: str = ""):
        self.event_id = event_id
        self.started_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self._start_time = time.perf_counter()
        self.steps: list[TraceStep] = []
        self._current_step: TraceStep | None = None
        self._step_start: float = 0.0

    def start_step(
        self,
        node_name: str,
        input_summary: str = "",
    ) -> None:
        """Begin timing a new trace step.

        Args:
            node_name: Internal name of the graph node.
            input_summary: Brief description of input to this step.
        """
        self._current_step = TraceStep(
            node_name=node_name,
            display_name=NODE_DISPLAY_NAMES.get(node_name, node_name),
            started_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            input_summary=input_summary,
        )
        self._step_start = time.perf_counter()
        logger.debug("Trace: started step '%s'", node_name)

    def add_tool_call(self, record: ToolCallRecord) -> None:
        """Add a tool call record to the current step.

        Args:
            record: The ToolCallRecord from a tool invocation.
        """
        if self._current_step is not None:
            self._current_step.tools_called.append(record)

    def end_step(
        self,
        output_summary: str = "",
        decision: str = "",
    ) -> None:
        """Finalize the current trace step with output and timing.

        Args:
            output_summary: Brief description of what this step produced.
            decision: Rationale for any decisions made (especially routing).
        """
        if self._current_step is None:
            return

        elapsed = time.perf_counter() - self._step_start
        self._current_step.completed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self._current_step.duration_ms = int(elapsed * 1000)
        self._current_step.output_summary = output_summary
        self._current_step.decision = decision
        self.steps.append(self._current_step)

        logger.debug(
            "Trace: completed step '%s' in %dms",
            self._current_step.node_name,
            self._current_step.duration_ms,
        )
        self._current_step = None

    def finalize(self, final_decision: str = "") -> ExecutionTrace:
        """Finalize the execution trace and return the complete trace object.

        Args:
            final_decision: Summary of the final pipeline decision.

        Returns:
            Complete ExecutionTrace object.
        """
        total_duration = int((time.perf_counter() - self._start_time) * 1000)

        trace = ExecutionTrace(
            event_id=self.event_id,
            started_at=self.started_at,
            completed_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            total_duration_ms=total_duration,
            steps=self.steps,
            final_decision=final_decision,
        )

        logger.info(
            "Trace finalized: %s — %d steps in %dms",
            self.event_id,
            len(self.steps),
            total_duration,
        )
        return trace

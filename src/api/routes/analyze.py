"""API routes for the analysis endpoint."""

import logging
import time
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request

from src.core.config import settings
from src.graph.intrusion_graph import intrusion_app
from src.models.schemas import IncidentReport, LogEvent

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/analyze", response_model=IncidentReport)
async def analyze_endpoint(request: Request, log_event: LogEvent):
    """Analyze a network log event and return an incident report.

    Args:
        request (Request): The incoming HTTP request.
        log_event (LogEvent): The log event payload.

    Returns:
        IncidentReport: Structured analysis of the log event.

    Raises:
        HTTPException: If the analysis fails.
    """
    start_time = time.perf_counter()
    event_id = str(uuid.uuid4())
    logger.info("Received analyze request %s for IP %s", event_id, log_event.source_ip)

    # Prepare initial state for LangGraph
    initial_state = {
        "log_event": log_event,
        "incident_report": None,
        "error": None,
    }

    # Run graph execution
    try:
        final_state = await intrusion_app.ainvoke(initial_state)
    except Exception as e:
        logger.error("Graph execution failed: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during analysis") from e

    if final_state.get("error"):
        logger.error("Analysis error: %s", final_state["error"])
        raise HTTPException(status_code=500, detail=f"Analysis failed: {final_state['error']}")

    report = final_state.get("incident_report")
    if not report:
        logger.error("No incident report returned from graph")
        raise HTTPException(status_code=500, detail="Failed to generate incident report")

    # Calculate processing time and update report
    end_time = time.perf_counter()
    processing_time_ms = int((end_time - start_time) * 1000)

    # Update properties set by API layer
    report.event_id = event_id
    report.timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    report.processing_time_ms = processing_time_ms

    logger.info("Analysis complete for %s. Result: %s", event_id, report.attack_type)
    return report


@router.get("/health")
async def health_check():
    """Health check endpoint.

    Returns:
        dict: Status and version information.
    """
    return {"status": "ok", "version": settings.APP_VERSION}

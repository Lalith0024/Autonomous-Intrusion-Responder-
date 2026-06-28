"""API routes V2 — Analysis, ingestion, blocking, and queue management endpoints.

V2 Endpoints:
    POST /analyze         — Synchronous single-event analysis (V1 compatible)
    POST /ingest          — Async: push to Redis queue, return 202 + event_id
    GET  /result/{id}     — Poll for async processing result
    GET  /blocked         — List all currently blocked IPs
    POST /block/{ip}      — Manually block an IP
    DELETE /block/{ip}    — Unblock an IP
    GET  /queue/stats     — Queue depth and processing stats
    GET  /memory/stats    — Vector memory statistics
    GET  /health          — Health check
"""

from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request

from src.core.config import settings
from src.core.tracer import TraceCollector
from src.graph.intrusion_graph import intrusion_app
from src.models.schemas import IncidentReport, LogEvent

logger = logging.getLogger(__name__)

router = APIRouter()


# ── V1 Compatible: Synchronous Analysis ────────────────────────────


@router.post("/analyze", response_model=IncidentReport)
async def analyze_endpoint(request: Request, log_event: LogEvent):
    """Analyze a network log event and return an incident report.

    This is the synchronous endpoint — waits for the full pipeline
    to complete before returning. Use /ingest for async processing.

    Args:
        request: The incoming HTTP request.
        log_event: The log event payload.

    Returns:
        IncidentReport: Structured analysis of the log event.

    Raises:
        HTTPException: If the analysis fails.
    """
    start_time = time.perf_counter()
    event_id = str(uuid.uuid4())
    logger.info("Received analyze request %s for IP %s", event_id, log_event.source_ip)

    # V2: Create tracer for full observability
    tracer = TraceCollector(event_id=event_id)

    # Prepare initial state for LangGraph (V2 schema)
    initial_state = {
        "log_event": log_event,
        "incident_report": None,
        "error": None,
        "ip_investigation": None,
        "threat_intel": None,
        "port_scan": None,
        "historical_matches": None,
        "tool_records": [],
        "tracer": tracer,
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

    report.event_id = event_id
    report.timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    report.processing_time_ms = processing_time_ms

    # V2: Attach execution trace
    trace = tracer.finalize(
        final_decision=f"{report.attack_type.value} → {report.recommended_action.value}"
    )
    report.execution_trace = trace

    logger.info("Analysis complete for %s. Result: %s (%dms)", event_id, report.attack_type, processing_time_ms)
    return report


# ── V2: Async Ingestion (Redis Queue) ──────────────────────────────


@router.post("/ingest", status_code=202)
async def ingest_endpoint(log_event: LogEvent):
    """Async log ingestion: push to Redis queue for background processing.

    Returns immediately with an event_id that can be polled via GET /result/{id}.

    Args:
        log_event: The log event payload.

    Returns:
        Dict with event_id and queue status.

    Raises:
        HTTPException: If Redis queue is unavailable.
    """
    from src.queue import redis_client

    if not redis_client.is_connected():
        raise HTTPException(
            status_code=503,
            detail="Redis queue is not available. Use POST /analyze for synchronous processing.",
        )

    event_id = await redis_client.enqueue_log(log_event.model_dump())
    if event_id is None:
        raise HTTPException(status_code=500, detail="Failed to enqueue log event")

    depth = await redis_client.get_queue_depth()

    return {
        "status": "queued",
        "event_id": event_id,
        "queue_depth": depth,
        "message": f"Event {event_id} queued for processing. Poll GET /result/{event_id} for results.",
    }


@router.get("/result/{event_id}")
async def get_result_endpoint(event_id: str):
    """Poll for the result of an async analysis.

    Args:
        event_id: The event ID returned by POST /ingest.

    Returns:
        The incident report if processing is complete, or a pending status.
    """
    from src.queue import redis_client

    if not redis_client.is_connected():
        raise HTTPException(status_code=503, detail="Redis queue is not available")

    result = await redis_client.get_result(event_id)
    if result is None:
        return {"status": "processing", "event_id": event_id, "message": "Still processing. Try again shortly."}

    return {"status": "complete", "event_id": event_id, "incident_report": result}


# ── V2: IP Blocking Management ────────────────────────────────────


@router.get("/blocked")
async def get_blocked_ips():
    """List all currently blocked IPs.

    Returns:
        List of active blocked IP entries with timestamps and reasons.
    """
    from src.tools.security_toolkit import get_blocked_ips

    blocked = get_blocked_ips()
    return {"total": len(blocked), "blocked_ips": blocked}


@router.post("/block/{ip_address}")
async def block_ip_endpoint(ip_address: str, duration_hours: int = 24, reason: str = "Manual block via API"):
    """Manually block an IP address.

    Args:
        ip_address: The IP to block.
        duration_hours: How long to block (default 24h).
        reason: Human-readable reason for the block.

    Returns:
        Block confirmation with details.
    """
    from src.tools.security_toolkit import block_ip

    result, _ = block_ip(ip_address, reason=reason, duration_hours=duration_hours)
    return result


@router.delete("/block/{ip_address}")
async def unblock_ip_endpoint(ip_address: str):
    """Unblock an IP address.

    Args:
        ip_address: The IP to unblock.

    Returns:
        Unblock confirmation.
    """
    from src.tools.security_toolkit import unblock_ip

    return unblock_ip(ip_address)


# ── V2: Queue Stats ───────────────────────────────────────────────


@router.get("/queue/stats")
async def queue_stats():
    """Return queue depth and processing statistics.

    Returns:
        Queue depth, connection status, and processing rate.
    """
    from src.queue import redis_client

    return await redis_client.get_processing_stats()


# ── V2: Memory Stats ──────────────────────────────────────────────


@router.get("/memory/stats")
async def memory_stats():
    """Return vector memory statistics.

    Returns:
        Total incidents stored, unique IPs, attack type distribution.
    """
    try:
        from src.memory import vector_store
        return vector_store.get_stats()
    except Exception as e:
        return {"error": str(e), "index_initialized": False}


# ── Health Check ──────────────────────────────────────────────────


@router.get("/health")
async def health_check():
    """Health check endpoint with system status.

    Returns:
        Status, version, and component health.
    """
    from src.queue import redis_client

    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "components": {
            "api": "healthy",
            "redis": "connected" if redis_client.is_connected() else "disconnected",
            "tools": "enabled" if settings.TOOLS_ENABLED else "disabled",
            "memory": "enabled" if settings.MEMORY_ENABLED else "disabled",
        },
    }

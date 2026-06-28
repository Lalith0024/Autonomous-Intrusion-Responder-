"""Background Worker — Pulls logs from Redis queue and processes through LangGraph.

Usage:
    python -m src.queue.worker

This runs as a separate process from the FastAPI server. It continuously
polls the Redis queue for new logs and processes them through the full
agent pipeline (investigation → triage → routing → response).

Results are stored back in Redis for the API to serve.
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from pathlib import Path

# Fix import path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from dotenv import load_dotenv
load_dotenv()

from src.core.config import settings  # noqa: E402
from src.core.tracer import TraceCollector  # noqa: E402
from src.graph.intrusion_graph import intrusion_app  # noqa: E402
from src.models.schemas import LogEvent  # noqa: E402
from src.queue import redis_client  # noqa: E402

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def process_event(event_data: dict) -> dict | None:
    """Process a single event through the LangGraph pipeline.

    Args:
        event_data: Dict with 'event_id' and 'log_event' keys.

    Returns:
        The incident report dict, or None on failure.
    """
    event_id = event_data.get("event_id", "unknown")
    log_data = event_data.get("log_event", {})

    try:
        log_event = LogEvent(**log_data)
        tracer = TraceCollector(event_id=event_id)

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

        final_state = await intrusion_app.ainvoke(initial_state)

        report = final_state.get("incident_report")
        if report:
            report.event_id = event_id
            trace = tracer.finalize(
                final_decision=f"{report.attack_type.value} → {report.recommended_action.value}"
            )
            report.execution_trace = trace
            return json.loads(report.model_dump_json())

        return None

    except Exception as e:
        logger.error("Failed to process event %s: %s", event_id, e, exc_info=True)
        return None


async def worker_loop() -> None:
    """Main worker loop — continuously pull from Redis and process."""
    logger.info("=" * 60)
    logger.info("  AIR Worker Starting...")
    logger.info("=" * 60)

    connected = await redis_client.connect()
    if not connected:
        logger.error("Cannot connect to Redis. Worker cannot start.")
        return

    logger.info("Worker connected to Redis. Waiting for events...")
    processed = 0

    try:
        while True:
            event_data = await redis_client.dequeue_log()

            if event_data is None:
                continue  # brpop timed out, just retry

            event_id = event_data.get("event_id", "?")
            logger.info("[%d] Processing event: %s", processed + 1, event_id)

            result = await process_event(event_data)

            if result:
                await redis_client.store_result(event_id, result)
                processed += 1
                logger.info("[%d] Event %s processed successfully", processed, event_id)
            else:
                logger.warning("Event %s produced no result", event_id)

    except KeyboardInterrupt:
        logger.info("Worker shutting down (Ctrl+C)...")
    except Exception as e:
        logger.error("Worker crashed: %s", e, exc_info=True)
    finally:
        await redis_client.disconnect()
        logger.info("Worker stopped. Total processed: %d", processed)


if __name__ == "__main__":
    asyncio.run(worker_loop())

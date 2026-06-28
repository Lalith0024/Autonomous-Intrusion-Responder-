"""Redis Queue Client — Async log ingestion and result storage.

Implements a Producer-Consumer pattern for high-throughput log processing:
    - FastAPI (Producer): Receives log → pushes to Redis queue → returns 202 Accepted
    - Worker (Consumer): Pulls from queue → processes through LangGraph → stores result

Queue: 'air:log_queue' (Redis List, FIFO via LPUSH/BRPOP)
Results: 'air:results:{event_id}' (Redis String, 24h TTL)
Blocked IPs: 'air:blocked_ips' (Redis Set)

Graceful Degradation:
    - If Redis is unavailable, all methods return None/empty without raising.
    - The API falls back to synchronous processing when Redis is disabled.
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import Optional

from src.core.config import settings

logger = logging.getLogger(__name__)

# Lazy-loaded Redis connection
_redis = None
_connected = False

QUEUE_KEY = "air:log_queue"
RESULT_PREFIX = "air:results:"
BLOCKED_SET = "air:blocked_ips"
STATS_KEY = "air:stats"


async def connect() -> bool:
    """Initialize the async Redis connection.

    Returns:
        True if connection was successful.
    """
    global _redis, _connected

    if not settings.REDIS_ENABLED:
        logger.info("Redis is disabled (REDIS_ENABLED=false)")
        return False

    try:
        import redis.asyncio as aioredis

        _redis = aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_timeout=5.0,
            socket_connect_timeout=5.0,
        )
        # Test connection
        await _redis.ping()
        _connected = True
        logger.info("Redis connected: %s", settings.REDIS_URL)
        return True

    except ImportError:
        logger.warning("redis package not installed. Queue disabled.")
        return False
    except Exception as e:
        logger.warning("Redis connection failed: %s. Queue disabled.", e)
        _connected = False
        return False


async def disconnect() -> None:
    """Close the Redis connection."""
    global _redis, _connected
    if _redis is not None:
        await _redis.close()
        _connected = False
        logger.info("Redis disconnected")


def is_connected() -> bool:
    """Check if Redis is connected and available."""
    return _connected


async def enqueue_log(log_event: dict) -> Optional[str]:
    """Push a log event to the processing queue.

    Args:
        log_event: The log event dict to queue.

    Returns:
        Event ID for tracking, or None if queue is unavailable.
    """
    if not _connected or _redis is None:
        return None

    event_id = str(uuid.uuid4())
    payload = json.dumps({"event_id": event_id, "log_event": log_event})

    try:
        await _redis.lpush(QUEUE_KEY, payload)
        logger.info("Enqueued log %s (queue depth: pending)", event_id)
        return event_id
    except Exception as e:
        logger.error("Failed to enqueue log: %s", e)
        return None


async def dequeue_log() -> Optional[dict]:
    """Pop the next log from the queue (blocking, 5s timeout).

    Returns:
        Dict with event_id and log_event, or None if queue is empty/unavailable.
    """
    if not _connected or _redis is None:
        return None

    try:
        result = await _redis.brpop(QUEUE_KEY, timeout=5)
        if result:
            _, payload = result
            return json.loads(payload)
        return None
    except Exception as e:
        logger.error("Failed to dequeue log: %s", e)
        return None


async def store_result(event_id: str, result: dict, ttl: int = 86400) -> bool:
    """Store a processed result with TTL.

    Args:
        event_id: The event ID to store under.
        result: The processed incident report dict.
        ttl: Time-to-live in seconds (default 24h).

    Returns:
        True if stored successfully.
    """
    if not _connected or _redis is None:
        return False

    try:
        key = f"{RESULT_PREFIX}{event_id}"
        await _redis.set(key, json.dumps(result), ex=ttl)
        logger.info("Result stored: %s (TTL: %ds)", event_id, ttl)
        return True
    except Exception as e:
        logger.error("Failed to store result: %s", e)
        return False


async def get_result(event_id: str) -> Optional[dict]:
    """Retrieve a processed result by event ID.

    Args:
        event_id: The event ID to look up.

    Returns:
        The incident report dict, or None if not found.
    """
    if not _connected or _redis is None:
        return None

    try:
        key = f"{RESULT_PREFIX}{event_id}"
        data = await _redis.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        logger.error("Failed to get result: %s", e)
        return None


async def get_queue_depth() -> int:
    """Return the current number of unprocessed logs in the queue."""
    if not _connected or _redis is None:
        return 0

    try:
        return await _redis.llen(QUEUE_KEY)
    except Exception:
        return 0


async def get_processing_stats() -> dict:
    """Return queue and processing statistics."""
    depth = await get_queue_depth()

    return {
        "queue_depth": depth,
        "redis_connected": _connected,
        "redis_url": settings.REDIS_URL if _connected else None,
    }

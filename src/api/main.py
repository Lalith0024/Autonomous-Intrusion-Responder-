"""FastAPI application entrypoint — V2 Production."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.analyze import router as analyze_router
from src.core.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events.

    V2: Initializes Redis connection and vector memory on startup.

    Args:
        app: The running FastAPI instance.
    """
    logger.info("=" * 60)
    logger.info("  Starting Autonomous Intrusion Responder API v%s", settings.APP_VERSION)
    logger.info("=" * 60)

    # V2: Initialize Redis if enabled
    if settings.REDIS_ENABLED:
        from src.queue import redis_client
        connected = await redis_client.connect()
        if connected:
            logger.info("✓ Redis queue initialized")
        else:
            logger.warning("✗ Redis connection failed — async ingestion disabled")
    else:
        logger.info("○ Redis queue disabled (REDIS_ENABLED=false)")

    # V2: Initialize vector memory if enabled
    if settings.MEMORY_ENABLED:
        try:
            from src.memory import vector_store
            if vector_store.initialize(settings.VECTOR_INDEX_DIR):
                stats = vector_store.get_stats()
                logger.info("✓ Vector memory initialized (%d incidents in index)", stats["total_incidents"])
            else:
                logger.warning("✗ Vector memory initialization failed — memory disabled")
        except Exception as e:
            logger.warning("✗ Vector memory setup error: %s", e)
    else:
        logger.info("○ Vector memory disabled (MEMORY_ENABLED=false)")

    # V2: Log tools status
    if settings.TOOLS_ENABLED:
        logger.info("✓ Security tools enabled (investigate_ip, scan_ports, check_threat_intel, block_ip)")
    else:
        logger.info("○ Security tools disabled (TOOLS_ENABLED=false)")

    logger.info("=" * 60)
    logger.info("  API ready at http://127.0.0.1:8000")
    logger.info("=" * 60)

    yield

    # Shutdown
    logger.info("Shutting down Autonomous Intrusion Responder API...")
    if settings.REDIS_ENABLED:
        from src.queue import redis_client
        await redis_client.disconnect()


app = FastAPI(
    title="Autonomous Intrusion Responder",
    description="Multi-agent AI pipeline for network security: log analysis, threat classification, and automated response.",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# V2: CORS middleware for Streamlit dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analyze_router)

"""FastAPI application entrypoint."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

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
    
    Args:
        app (FastAPI): The running FastAPI instance.
    """
    logger.info("Starting up Autonomous Intrusion Responder API...")
    yield
    logger.info("Shutting down Autonomous Intrusion Responder API...")


app = FastAPI(
    title="Autonomous Intrusion Responder",
    description="Network Security AI Agent for log analysis and incident triage.",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Include routers
app.include_router(analyze_router)

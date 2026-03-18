"""Script to run the FastAPI application."""

import uvicorn

from src.core.config import settings


def main():
    """Start the Uvicorn ASGI server."""
    uvicorn.run(
        "src.api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level=settings.LOG_LEVEL.lower(),
    )


if __name__ == "__main__":
    main()

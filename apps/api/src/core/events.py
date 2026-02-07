"""Application lifecycle events."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger
from sqlalchemy import text

from src import __version__
from src.core.database import async_engine
from src.core.logging import setup_logging
from src.core.settings import settings


def print_banner() -> None:
    """Print application banner on startup."""
    separator = "═" * 67
    logger.info(separator)
    logger.info(f"  {settings.app_name.upper():^63}")
    logger.info(separator)
    logger.info(f"  Version      │  {__version__}")
    logger.info(f"  Environment  │  {settings.env}")
    logger.info(f"  Debug Mode   │  {'✓ enabled' if settings.debug else '✗ disabled'}")
    logger.info(f"  Log Level    │  {settings.log_level}")
    logger.info(separator)
    if settings.debug:
        logger.info("  Docs         │  http://localhost:8000/docs")
        logger.info("  Health       │  http://localhost:8000/v1/health")
        logger.info(separator)


async def startup_event() -> None:
    """Run on application startup."""
    setup_logging()

    # Print banner
    print_banner()

    # Log startup info
    logger.info("Starting application")
    logger.info(f"App Name: {settings.app_name}")
    logger.info(f"Environment: {settings.env}")
    logger.info(f"Debug Mode: {settings.debug}")
    logger.info(f"Log Level: {settings.log_level}")

    # Test database connection
    try:
        async with async_engine.connect() as conn:
            _ = await conn.execute(text("SELECT 1"))
        logger.success("Database connection established successfully")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

    logger.success("Application started successfully")


async def shutdown_event() -> None:
    """Run on application shutdown."""
    logger.info("Shutting down application")

    # Close database connections
    await async_engine.dispose()
    logger.info("Database connections closed")

    logger.success("Application shutdown complete")


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Application lifespan context manager.

    Handles startup and shutdown events.
    """
    # Startup
    await startup_event()

    yield

    # Shutdown
    await shutdown_event()

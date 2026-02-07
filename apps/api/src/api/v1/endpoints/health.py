"""Health check endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src import __version__
from src.api.deps import get_db_session
from src.core.settings import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check(db: Annotated[AsyncSession, Depends(get_db_session)]):
    """
    Health check endpoint with database status.

    Returns:
        Health status including database connection
    """
    db_status = "unknown"
    try:
        result = await db.execute(text("SELECT 1"))
        _ = result.scalar()
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "app": settings.app_name,
        "env": settings.env,
        "version": __version__,
        "database": db_status,
    }


@router.get("/")
async def root():
    """
    Root endpoint with API info.

    Returns:
        Basic API information and available endpoints
    """
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": __version__,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/v1/health",
    }

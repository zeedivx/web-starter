"""Database engine configuration."""

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

from src.core.settings import settings

# Async engine
async_engine = create_async_engine(
    settings.async_database_url,
    echo=settings.debug,
    future=True,
    pool_pre_ping=True,
    poolclass=NullPool if settings.env == "test" else None,
)

# Sync engine
engine = create_engine(
    settings.async_database_url.replace("+asyncpg", ""),
    echo=settings.debug,
    future=True,
    pool_pre_ping=True,
)

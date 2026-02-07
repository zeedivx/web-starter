"""FastAPI dependencies."""

from collections.abc import AsyncGenerator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db


async def get_db_session(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[AsyncSession]:
    """
    Get database session dependency.

    Usage:
        ```python
        @router.get("/users")
        async def list_users(db: AsyncSession = Depends(get_db_session)):
            result = await db.execute(select(User))
            return result.scalars().all()
        ```
    """
    yield db


def get_request_id(request: Request) -> str:
    """
    Get request ID from request state.

    Usage:
        ```python
        @router.get("/example")
        async def example(request_id: str = Depends(get_request_id)):
            logger.info(f"Processing request {request_id}")
        ```
    """
    return getattr(request.state, "request_id", "unknown")

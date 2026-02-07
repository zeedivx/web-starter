"""Base service layer for business logic."""

from typing import TypeVar
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.database import RecordNotFoundException
from src.db.repositories.base import BaseRepository
from src.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseService[ModelType: Base]:
    """
    Base service with common business logic operations.

    Usage:
        ```python
        class UserService(BaseService[User]):
            def __init__(self, session: AsyncSession):
                repository = UserRepository(session)
                super().__init__(repository, session)
        ```
    """

    def __init__(
        self,
        repository: BaseRepository[ModelType],
        session: AsyncSession,
    ) -> None:
        """
        Initialize service with repository and session.

        Args:
            repository: Repository instance for data access
            session: Database session for transactions
        """
        self.repository = repository  # pyright: ignore[reportUnannotatedClassAttribute]
        self.session: AsyncSession = session

    async def get_by_id(self, id: UUID) -> ModelType | None:
        """Get entity by ID."""
        return await self.repository.get(id)

    async def get_by_id_or_fail(self, id: UUID) -> ModelType:
        """Get entity by ID or raise exception."""
        entity = await self.repository.get(id)
        if not entity:
            raise RecordNotFoundException(
                f"{self.repository.model.__name__} with id {id} not found"
            )
        return entity

    async def get_many(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
    ) -> list[ModelType]:
        """Get multiple entities with pagination."""
        return await self.repository.get_multi(skip=skip, limit=limit, order_by=order_by)

    async def create(self, entity: ModelType) -> ModelType:
        """Create new entity."""
        created = await self.repository.create(entity)
        await self.session.commit()
        return created

    async def update(self, entity: ModelType) -> ModelType:
        """Update existing entity."""
        updated = await self.repository.update(entity)
        await self.session.commit()
        return updated

    async def delete(self, id: UUID) -> bool:
        """Delete entity by ID."""
        deleted = await self.repository.delete(id)
        await self.session.commit()
        return deleted

    async def exists(self, id: UUID) -> bool:
        """Check if entity exists by ID."""
        return await self.repository.exists(id)

    async def count(self) -> int:
        """Count total entities."""
        return await self.repository.count()

    async def get_by_field(self, field: str, value: object) -> ModelType | None:
        """Get entity by field value."""
        return await self.repository.get_by_field(field, value)

    async def get_many_by_field(
        self,
        field: str,
        value: object,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ModelType]:
        """Get multiple entities by field value."""
        return await self.repository.get_multi_by_field(field, value, skip=skip, limit=limit)

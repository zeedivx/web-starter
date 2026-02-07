"""Base repository for database operations."""

from typing import TYPE_CHECKING, TypeVar
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from src.models.base import Base

if TYPE_CHECKING:
    from sqlalchemy.sql import Select
    from sqlalchemy.sql.elements import UnaryExpression

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository[ModelType: Base]:
    """
    Base repository with common CRUD operations.

    Usage:
        ```python
        class UserRepository(BaseRepository[User]):
            def __init__(self, session: AsyncSession):
                super().__init__(User, session)

            # Add custom methods here
            async def get_by_email(self, email: str) -> User | None:
                result = await self.session.execute(
                    select(User).where(User.email == email)
                )
                return result.scalar_one_or_none()
        ```
    """

    def __init__(self, model: type[ModelType], session: AsyncSession) -> None:
        """
        Initialize repository.

        Args:
            model: SQLAlchemy model class
            session: Async database session
        """
        self.model: type[ModelType] = model
        self.session: AsyncSession = session

    async def get(self, id: UUID) -> ModelType | None:
        """
        Get a single record by ID.

        Args:
            id: Record UUID

        Returns:
            Model instance or None if not found
        """
        return await self.session.get(self.model, id)

    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: UnaryExpression[object] | str | None = None,
    ) -> list[ModelType]:
        """
        Get multiple records with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Column expression or column name to order by (optional)

        Returns:
            List of model instances
        """
        query = select(self.model).offset(skip).limit(limit)

        if order_by is not None:
            if isinstance(order_by, str):
                query = query.order_by(getattr(self.model, order_by, None))
            else:
                query = query.order_by(order_by)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, obj: ModelType) -> ModelType:
        """
        Create a new record.

        Args:
            obj: Model instance to create

        Returns:
            Created model instance with ID populated
        """
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, obj: ModelType) -> ModelType:
        """
        Update an existing record.

        Args:
            obj: Model instance to update

        Returns:
            Updated model instance
        """
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, id: UUID) -> bool:
        """
        Delete a record by ID.

        Args:
            id: Record UUID

        Returns:
            True if deleted, False if not found
        """
        obj = await self.get(id)
        if obj:
            await self.session.delete(obj)
            await self.session.flush()
            return True
        return False

    async def exists(self, id: UUID) -> bool:
        """
        Check if a record exists by ID.

        Args:
            id: Record UUID

        Returns:
            True if exists, False otherwise
        """
        id_column = self.__get_column("id")
        result = await self.session.execute(select(id_column).where(id_column == id))
        return result.scalar_one_or_none() is not None

    async def count(self, query: Select[tuple[object, ...]] | None = None) -> int:
        """
        Count records.

        Args:
            query: Optional SQLAlchemy select query to count (if None, counts all records)

        Returns:
            Number of records
        """
        if query is None:
            count_query = select(func.count()).select_from(self.model)
        else:
            count_query = select(func.count()).select_from(query.subquery())

        result = await self.session.execute(count_query)
        return result.scalar_one()

    async def get_by_field(self, field: str, value: object) -> ModelType | None:
        """
        Get a single record by field value.

        Args:
            field: Field name
            value: Field value

        Returns:
            Model instance or None if not found
        """
        field_column = self.__get_column(field)
        result = await self.session.execute(select(self.model).where(field_column == value))
        return result.scalar_one_or_none()

    async def get_multi_by_field(
        self, field: str, value: object, *, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        """
        Get multiple records by field value.

        Args:
            field: Field name
            value: Field value
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of model instances
        """
        field_column = self.__get_column(field)

        result = await self.session.execute(
            select(self.model).where(field_column == value).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def delete_by_field(self, field: str, value: object) -> int:
        """
        Delete records by field value.

        Args:
            field: Field name
            value: Field value

        Returns:
            Number of deleted records
        """
        field_column = self.__get_column(field)
        result = await self.session.execute(delete(self.model).where(field_column == value))
        await self.session.flush()
        return getattr(result, "rowcount", 0) or 0

    def __get_column(self, column: str) -> InstrumentedAttribute[object]:
        """
        Get a column from the model.

        Args:
            column: Column name

        Returns:
            Column
        """
        col = getattr(self.model, column, None)
        if col is None or not isinstance(col, InstrumentedAttribute):
            raise ValueError(f"Model does not have a column named {column}")
        return col

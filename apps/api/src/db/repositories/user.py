"""User repository."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repositories.base import BaseRepository
from src.models.user import User


class UserRepository(BaseRepository[User]):
    """
    Repository for User model with user-specific queries.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize user repository.

        Args:
            session: Async database session
        """
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> User | None:
        """
        Get user by email address.

        Args:
            email: User's email address

        Returns:
            User instance or None if not found
        """
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """
        Get user by username.

        Args:
            username: User's username

        Returns:
            User instance or None if not found
        """
        result = await self.session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_active_users(self, *, skip: int = 0, limit: int = 100) -> list[User]:
        """
        Get all active users (is_active=True).

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of active users
        """
        result = await self.session.execute(
            select(User)
            .where(User.is_active.is_(True))
            .where(User.deleted_at.is_(None))  # Exclude soft-deleted
            .offset(skip)
            .limit(limit)
            .order_by(User.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_superusers(self, *, skip: int = 0, limit: int = 100) -> list[User]:
        """
        Get all superusers (is_superuser=True).

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of superusers
        """
        result = await self.session.execute(
            select(User)
            .where(User.is_superuser.is_(True))
            .where(User.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
            .order_by(User.created_at.desc())
        )
        return list(result.scalars().all())

    async def email_exists(self, email: str) -> bool:
        """
        Check if email already exists in the database.

        Args:
            email: Email address to check

        Returns:
            True if email exists, False otherwise
        """
        result = await self.session.execute(select(User.id).where(User.email == email))
        return result.scalar_one_or_none() is not None

    async def username_exists(self, username: str) -> bool:
        """
        Check if username already exists in the database.

        Args:
            username: Username to check

        Returns:
            True if username exists, False otherwise
        """
        result = await self.session.execute(select(User.id).where(User.username == username))
        return result.scalar_one_or_none() is not None

    async def count_active_users(self) -> int:
        """
        Count all active users.

        Returns:
            Number of active users
        """
        result = await self.session.execute(
            select(func.count())
            .select_from(User)
            .where(User.is_active.is_(True))
            .where(User.deleted_at.is_(None))
        )
        return result.scalar_one()

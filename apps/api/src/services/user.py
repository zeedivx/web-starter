"""User service for business logic."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.database import DuplicateRecordException
from src.core.security import hash_password, verify_password
from src.db.repositories.user import UserRepository
from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate
from src.services.base import BaseService


class UserService(BaseService[User]):
    """User service with user-specific business logic."""

    repository: UserRepository

    def __init__(self, session: AsyncSession) -> None:
        """Initialize user service."""
        repository = UserRepository(session)
        super().__init__(repository, session)
        self.repository = repository

    async def create_user(self, data: UserCreate) -> User:
        """Create a new user with password hashing and validation."""
        if await self.repository.email_exists(data.email):
            raise DuplicateRecordException(f"Email {data.email} already exists")

        if data.username and await self.repository.username_exists(data.username):
            raise DuplicateRecordException(f"Username {data.username} already exists")

        user = User(
            email=data.email,
            username=data.username,
            hashed_password=hash_password(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
            is_active=data.is_active,
            is_superuser=data.is_superuser,
        )

        return await self.create(user)

    async def update_user(self, user_id: str, data: UserUpdate) -> User:
        """Update an existing user."""
        from uuid import UUID

        user = await self.get_by_id_or_fail(UUID(user_id))

        if data.email and data.email != user.email:
            if await self.repository.email_exists(data.email):
                raise DuplicateRecordException(f"Email {data.email} already exists")
            user.email = data.email

        if data.username and data.username != user.username:
            if await self.repository.username_exists(data.username):
                raise DuplicateRecordException(f"Username {data.username} already exists")
            user.username = data.username

        if data.password:
            user.hashed_password = hash_password(data.password)

        if data.first_name is not None:
            user.first_name = data.first_name
        if data.last_name is not None:
            user.last_name = data.last_name
        if data.is_active is not None:
            user.is_active = data.is_active
        if data.is_superuser is not None:
            user.is_superuser = data.is_superuser

        return await self.update(user)

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        return await self.repository.get_by_email(email)

    async def get_by_username(self, username: str) -> User | None:
        """Get user by username."""
        return await self.repository.get_by_username(username)

    async def get_active_users(self, *, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all active users."""
        return await self.repository.get_active_users(skip=skip, limit=limit)

    async def authenticate(self, email: str, password: str) -> User | None:
        """Authenticate user by email and password."""
        user = await self.get_by_email(email)
        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        if not user.is_active:
            return None

        return user

    async def deactivate_user(self, user_id: str) -> User:
        """Deactivate user account."""
        from uuid import UUID

        user = await self.get_by_id_or_fail(UUID(user_id))
        user.is_active = False
        return await self.update(user)

    async def activate_user(self, user_id: str) -> User:
        """Activate user account."""
        from uuid import UUID

        user = await self.get_by_id_or_fail(UUID(user_id))
        user.is_active = True
        return await self.update(user)

    async def soft_delete_user(self, user_id: str) -> User:
        """Soft delete user."""
        from uuid import UUID

        user = await self.get_by_id_or_fail(UUID(user_id))
        user.soft_delete()
        return await self.update(user)

"""Session service for user authentication."""

import secrets
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repositories.session import SessionRepository
from src.models.session import Session
from src.models.user import User
from src.services.base import BaseService


class SessionService(BaseService[Session]):
    """
    Session service for managing user sessions.
    """

    repository: SessionRepository

    def __init__(self, session: AsyncSession) -> None:
        """Initialize session service."""
        self.repository = SessionRepository(session)
        super().__init__(self.repository, session)

    async def create_session(
        self,
        user: User,
        *,
        expires_hours: int = 24,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> Session:
        """
        Create a new session for a user.

        Args:
            user: User to create session for
            expires_hours: Session expiration in hours (default: 24)
            ip_address: Optional IP address of client
            user_agent: Optional user agent string

        Returns:
            Created session
        """
        token = secrets.token_urlsafe(32)

        session_obj = Session(
            user_id=user.id,
            token=token,
            expires_at=Session.create_expiration(expires_hours),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return await self.create(session_obj)

    async def get_by_token(self, token: str) -> Session | None:
        """
        Get session by token.

        Args:
            token: Session token

        Returns:
            Session or None if not found
        """
        return await self.repository.get_by_token(token)

    async def get_active_session(self, token: str) -> Session | None:
        """
        Get active session by token.

        Args:
            token: Session token

        Returns:
            Session or None if not found or invalid
        """
        return await self.repository.get_active_session_by_token(token)

    async def validate_session(self, token: str) -> Session | None:
        """
        Validate session and return it if valid.

        Args:
            token: Session token

        Returns:
            Session if valid, None otherwise
        """
        session_obj = await self.get_active_session(token)
        if not session_obj:
            return None

        return session_obj if session_obj.is_valid else None

    async def revoke_session(self, token: str) -> bool:
        """
        Revoke a session.

        Args:
            token: Session token

        Returns:
            True if revoked, False if not found
        """
        revoked = await self.repository.revoke_session(token)
        if revoked:
            await self.session.commit()
        return revoked

    async def revoke_user_sessions(self, user_id: UUID) -> int:
        """
        Revoke all active sessions for a user.

        Args:
            user_id: User UUID

        Returns:
            Number of sessions revoked
        """
        count = await self.repository.revoke_user_sessions(user_id)
        await self.session.commit()
        return count

    async def get_user_sessions(
        self,
        user_id: UUID,
        *,
        include_expired: bool = False,
        include_revoked: bool = False,
    ) -> list[Session]:
        """
        Get all sessions for a user.

        Args:
            user_id: User UUID
            include_expired: Include expired sessions
            include_revoked: Include revoked sessions

        Returns:
            List of sessions
        """
        return await self.repository.get_user_sessions(
            user_id,
            include_expired=include_expired,
            include_revoked=include_revoked,
        )

    async def cleanup_expired_sessions(self) -> int:
        """
        Delete expired and revoked sessions.

        Returns:
            Number of sessions deleted
        """
        count = await self.repository.cleanup_expired_sessions()
        await self.session.commit()
        return count

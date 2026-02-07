"""Session repository."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repositories.base import BaseRepository
from src.models.session import Session


class SessionRepository(BaseRepository[Session]):
    """
    Repository for Session model with session-specific queries.

    Handles database operations for user sessions.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize session repository."""
        super().__init__(Session, session)

    async def get_by_token(self, token: str) -> Session | None:
        """
        Get session by token.

        Args:
            token: Session token

        Returns:
            Session or None if not found
        """
        result = await self.session.execute(select(Session).where(Session.token == token))
        return result.scalar_one_or_none()

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
            include_expired: Include expired sessions (default: False)
            include_revoked: Include revoked sessions (default: False)

        Returns:
            List of sessions
        """
        query = select(Session).where(Session.user_id == user_id)

        if not include_expired:
            query = query.where(Session.expires_at > datetime.now(UTC))

        if not include_revoked:
            query = query.where(Session.revoked_at.is_(None))

        query = query.order_by(Session.created_at.desc())

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_active_session_by_token(self, token: str) -> Session | None:
        """
        Get active (valid, not expired, not revoked) session by token.

        Args:
            token: Session token

        Returns:
            Session or None if not found or invalid
        """
        result = await self.session.execute(
            select(Session)
            .where(Session.token == token)
            .where(Session.expires_at > datetime.now(UTC))
            .where(Session.revoked_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def revoke_session(self, token: str) -> bool:
        """
        Revoke a session by token.

        Args:
            token: Session token

        Returns:
            True if session was revoked, False if not found
        """
        session_obj = await self.get_by_token(token)
        if not session_obj:
            return False

        session_obj.revoke()
        await self.session.flush()
        return True

    async def revoke_user_sessions(self, user_id: UUID) -> int:
        """
        Revoke all active sessions for a user.

        Args:
            user_id: User UUID

        Returns:
            Number of sessions revoked
        """
        sessions = await self.get_user_sessions(
            user_id, include_expired=False, include_revoked=False
        )

        for session_obj in sessions:
            session_obj.revoke()

        await self.session.flush()
        return len(sessions)

    async def cleanup_expired_sessions(self) -> int:
        """
        Delete expired and revoked sessions from database.

        Returns:
            Number of sessions deleted
        """
        now = datetime.now(UTC)

        result = await self.session.execute(
            delete(Session).where((Session.expires_at < now) | (Session.revoked_at.is_not(None)))
        )

        await self.session.flush()
        return getattr(result, "rowcount", 0) or 0

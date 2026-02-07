"""Session model for user authentication."""

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, override
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.models.user import User


class Session(Base, UUIDMixin, TimestampMixin):
    """
    User session model for authentication.
    """

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    token: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
    )

    user_agent: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Relationship to user
    user: Mapped[User] = relationship("User", back_populates="sessions")

    @override
    def __repr__(self) -> str:
        """String representation of Session."""
        return f"<Session(id={self.id}, user_id={self.user_id}, expires_at={self.expires_at})>"

    @property
    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.now(UTC) > self.expires_at

    @property
    def is_revoked(self) -> bool:
        """Check if session is revoked."""
        return self.revoked_at is not None

    @property
    def is_valid(self) -> bool:
        """Check if session is valid (not expired and not revoked)."""
        return not self.is_expired and not self.is_revoked

    def revoke(self) -> None:
        """Revoke this session."""
        self.revoked_at = datetime.now(UTC)

    @staticmethod
    def create_expiration(hours: int = 24) -> datetime:
        """
        Create expiration datetime.

        Args:
            hours: Number of hours until expiration (default: 24)

        Returns:
            Expiration datetime
        """
        return datetime.now(UTC) + timedelta(hours=hours)

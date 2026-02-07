"""User model."""

from typing import TYPE_CHECKING, override

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.mixins import FullModelMixin

if TYPE_CHECKING:
    from src.models.session import Session


class User(Base, FullModelMixin):
    """
    User model with authentication and profile information.
    """

    # Authentication
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    username: Mapped[str | None] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=True,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Permissions
    is_active: Mapped[bool] = mapped_column(
        default=True,
        server_default="true",
        nullable=False,
    )
    is_superuser: Mapped[bool] = mapped_column(
        default=False,
        server_default="false",
        nullable=False,
    )

    # Profile
    first_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    last_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Relationships
    sessions: Mapped[list[Session]] = relationship(
        "Session",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    @override
    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, email={self.email})>"

    @property
    def full_name(self) -> str | None:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name

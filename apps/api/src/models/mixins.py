"""Reusable model mixins."""

from datetime import UTC, datetime
from uuid import UUID, uuid7

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class UUIDMixin:
    """
    Mixin that adds UUID v7 primary key.

    UUID v7 features:
    - Sortable by creation time
    - Contains timestamp information
    - Better for database indexes than UUID v4

    Attributes:
        id: UUID v7 primary key (auto-generated)
    """

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid7,
        sort_order=-100,  # Ensure id is first column
    )


class TimestampMixin:
    """
    Mixin that adds created_at and updated_at timestamps.

    Attributes:
        created_at: Timestamp when record was created (auto-set)
        updated_at: Timestamp when record was last updated (auto-updated)
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
        nullable=False,
        sort_order=100,  # Place at end
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
        onupdate=lambda: datetime.now(UTC),
        server_onupdate=func.now(),
        nullable=False,
        sort_order=101,  # Place at end
    )


class SoftDeleteMixin:
    """
    Mixin that adds soft delete functionality.

    Attributes:
        deleted_at: Timestamp when record was soft deleted (NULL if not deleted)
    """

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None,
        nullable=True,
        sort_order=102,  # Place at end
    )

    @property
    def is_deleted(self) -> bool:
        """Check if record is soft deleted."""
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        """Soft delete this record."""
        self.deleted_at = datetime.now(UTC)

    def restore(self) -> None:
        """Restore soft deleted record."""
        self.deleted_at = None


class BaseModelMixin(UUIDMixin, TimestampMixin):
    """
    Combines common mixins for most models.

    Includes:
    - UUID primary key
    - Timestamp fields (created_at, updated_at)

    Usage:
        class User(Base, BaseModelMixin):
            name: Mapped[str]
            email: Mapped[str]
    """

    __abstract__: bool = True


class FullModelMixin(UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Combines all mixins including soft delete.

    Includes:
    - UUID primary key
    - Timestamp fields (created_at, updated_at)
    - Soft delete (deleted_at)

    Usage:
        class User(Base, FullModelMixin):
            name: Mapped[str]
            email: Mapped[str]
    """

    __abstract__: bool = True

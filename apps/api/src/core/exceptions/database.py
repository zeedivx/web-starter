"""Database-related exceptions."""

from src.core.exceptions.base import AppException
from src.core.exceptions.codes import ErrorCode


class DatabaseException(AppException):
    """
    Base exception for database-related errors.

    Raised when a database operation fails.
    """

    def __init__(
        self,
        message: str = "Database error",
        code: ErrorCode | str | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        """Initialize exception."""
        super().__init__(message=message, code=code or ErrorCode.DATABASE_ERROR, details=details)


class RecordNotFoundException(DatabaseException):
    """
    Exception raised when a database record is not found.

    Usage:
        ```python
        user = await db.get(User, user_id)
        if not user:
            raise RecordNotFoundException(f"User with id {user_id} not found")
        ```
    """

    def __init__(
        self,
        message: str = "Record not found",
        code: ErrorCode | str | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        """Initialize exception."""
        super().__init__(message=message, code=code or ErrorCode.RECORD_NOT_FOUND, details=details)


class DuplicateRecordException(DatabaseException):
    """
    Exception raised when trying to create a duplicate record.

    Usually raised on unique constraint violations.

    Usage:
        ```python
        try:
            await db.add(user)
            await db.commit()
        except IntegrityError:
            raise DuplicateRecordException("User with this email already exists")
        ```
    """

    def __init__(
        self,
        message: str = "Record already exists",
        code: ErrorCode | str | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        """Initialize exception."""
        super().__init__(message=message, code=code or ErrorCode.DUPLICATE_RECORD, details=details)

"""HTTP-related exceptions."""

from src.core.exceptions.base import AppException
from src.core.exceptions.codes import ErrorCode


class BadRequestException(AppException):
    """
    Exception for 400 Bad Request errors.

    Raised when the request is malformed or invalid.
    """

    def __init__(
        self,
        message: str = "Bad request",
        code: ErrorCode | str | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        """Initialize exception."""
        super().__init__(message=message, code=code or ErrorCode.BAD_REQUEST, details=details)


class UnauthorizedException(AppException):
    """
    Exception for 401 Unauthorized errors.

    Raised when authentication is required but not provided or invalid.
    """

    def __init__(
        self,
        message: str = "Unauthorized",
        code: ErrorCode | str | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        """Initialize exception."""
        super().__init__(message=message, code=code or ErrorCode.UNAUTHORIZED, details=details)


class ForbiddenException(AppException):
    """
    Exception for 403 Forbidden errors.

    Raised when the user is authenticated but doesn't have permission.
    """

    def __init__(
        self,
        message: str = "Forbidden",
        code: ErrorCode | str | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        """Initialize exception."""
        super().__init__(message=message, code=code or ErrorCode.FORBIDDEN, details=details)


class NotFoundException(AppException):
    """
    Exception for 404 Not Found errors.

    Raised when a requested resource is not found.
    """

    def __init__(
        self,
        message: str = "Resource not found",
        code: ErrorCode | str | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        """Initialize exception."""
        super().__init__(message=message, code=code or ErrorCode.NOT_FOUND, details=details)

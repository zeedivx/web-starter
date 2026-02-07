"""Base exception classes."""

from typing import override

from src.core.exceptions.codes import ErrorCode


class AppException(Exception):
    """
    Base exception for all application exceptions.

    Attributes:
        message: Error message
        code: Error code from ErrorCode enum
        details: Additional error details (optional)
    """

    def __init__(
        self,
        message: str,
        code: ErrorCode | str | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        """Initialize exception."""
        self.message: str = message
        self.code: ErrorCode | str = code or ErrorCode(self.__class__.__name__)
        self.details: dict[str, object] | None = details or {}
        super().__init__(self.message)

    @override
    def __str__(self) -> str:
        """String representation."""
        if self.details:
            return f"{self.message} (code: {self.code}, details: {self.details})"
        return f"{self.message} (code: {self.code})"

    def to_dict(self) -> dict[str, object]:
        """Convert exception to dictionary."""
        return {
            "error": str(self.code),
            "message": self.message,
            "details": self.details,
        }

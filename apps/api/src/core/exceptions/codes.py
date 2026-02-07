"""Error codes enum."""

from enum import StrEnum


class ErrorCode(StrEnum):
    """
    Enumeration of all error codes used in the application.

    Inherits from StrEnum to make it JSON serializable.
    """

    # HTTP errors (4xx)
    BAD_REQUEST = "BAD_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"

    # Database errors (5xx)
    DATABASE_ERROR = "DATABASE_ERROR"
    RECORD_NOT_FOUND = "RECORD_NOT_FOUND"
    DUPLICATE_RECORD = "DUPLICATE_RECORD"

    # Authentication errors (401)
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    INVALID_TOKEN = "INVALID_TOKEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"

    # Generic errors
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"

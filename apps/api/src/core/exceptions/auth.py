"""Authentication and authorization exceptions."""

from src.core.exceptions.base import AppException
from src.core.exceptions.codes import ErrorCode


class AuthenticationException(AppException):
    """
    Base exception for authentication-related errors.

    Raised when authentication fails.
    """

    def __init__(
        self,
        message: str = "Authentication failed",
        code: ErrorCode | str | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        """Initialize exception."""
        super().__init__(
            message=message, code=code or ErrorCode.AUTHENTICATION_ERROR, details=details
        )


class InvalidCredentialsException(AuthenticationException):
    """
    Exception raised when credentials are invalid.

    Usage:
        ```python
        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsException()
        ```
    """

    def __init__(
        self,
        message: str = "Invalid credentials",
        code: ErrorCode | str | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        """Initialize exception."""
        super().__init__(
            message=message, code=code or ErrorCode.INVALID_CREDENTIALS, details=details
        )


class InvalidTokenException(AuthenticationException):
    """
    Exception raised when authentication token is invalid.

    Usage:
        ```python
        try:
            payload = decode_token(token)
        except JWTError:
            raise InvalidTokenException()
        ```
    """

    def __init__(
        self,
        message: str = "Invalid token",
        code: ErrorCode | str | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        """Initialize exception."""
        super().__init__(message=message, code=code or ErrorCode.INVALID_TOKEN, details=details)


class TokenExpiredException(AuthenticationException):
    """
    Exception raised when authentication token has expired.

    Usage:
        ```python
        if token_exp < datetime.now():
            raise TokenExpiredException()
        ```
    """

    def __init__(
        self,
        message: str = "Token has expired",
        code: ErrorCode | str | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        """Initialize exception."""
        super().__init__(message=message, code=code or ErrorCode.TOKEN_EXPIRED, details=details)

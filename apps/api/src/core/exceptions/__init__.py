"""Custom exceptions for the application."""

from src.core.exceptions.auth import (
    AuthenticationException,
    InvalidCredentialsException,
    InvalidTokenException,
    TokenExpiredException,
)
from src.core.exceptions.base import AppException
from src.core.exceptions.codes import ErrorCode
from src.core.exceptions.database import (
    DatabaseException,
    DuplicateRecordException,
    RecordNotFoundException,
)
from src.core.exceptions.http import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
)

__all__ = [
    "AppException",
    "AuthenticationException",
    "BadRequestException",
    "DatabaseException",
    "DuplicateRecordException",
    "ErrorCode",
    "ForbiddenException",
    "InvalidCredentialsException",
    "InvalidTokenException",
    "NotFoundException",
    "RecordNotFoundException",
    "TokenExpiredException",
    "UnauthorizedException",
]

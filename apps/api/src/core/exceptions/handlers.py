"""Exception handlers for FastAPI."""

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.core.exceptions.auth import AuthenticationException
from src.core.exceptions.base import AppException
from src.core.exceptions.codes import ErrorCode
from src.core.exceptions.database import DatabaseException, RecordNotFoundException
from src.core.exceptions.http import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    Handle custom application exceptions.

    Maps exception types to appropriate HTTP status codes.
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    if isinstance(exc, (BadRequestException, RequestValidationError)):
        status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, (UnauthorizedException, AuthenticationException)):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, ForbiddenException):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, (NotFoundException, RecordNotFoundException)):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, DatabaseException):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    logger.error(
        f"Exception: {exc.__class__.__name__} - {exc.message}",
        extra={
            "exception_type": exc.__class__.__name__,
            "status_code": status_code,
            "path": request.url.path,
            "method": request.method,
            "details": exc.details,
        },
    )

    return JSONResponse(
        status_code=status_code,
        content=exc.to_dict(),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError | ValidationError
) -> JSONResponse:
    """
    Handle Pydantic validation errors.

    Returns structured validation error response.
    """
    logger.warning(
        f"Validation error on {request.method} {request.url.path}",
        extra={
            "errors": exc.errors(),
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": ErrorCode.VALIDATION_ERROR,
            "message": "Validation failed",
            "details": {
                "errors": exc.errors(),
            },
        },
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handle Starlette HTTP exceptions (routing 404s, etc).

    Maps status codes to appropriate error codes and messages.
    """
    error_map = {
        status.HTTP_400_BAD_REQUEST: (ErrorCode.BAD_REQUEST, "Invalid request"),
        status.HTTP_401_UNAUTHORIZED: (ErrorCode.UNAUTHORIZED, "Authentication required"),
        status.HTTP_403_FORBIDDEN: (ErrorCode.FORBIDDEN, "Access forbidden"),
        status.HTTP_404_NOT_FOUND: (
            ErrorCode.NOT_FOUND,
            f"Endpoint '{request.url.path}' not found",
        ),
        status.HTTP_405_METHOD_NOT_ALLOWED: (
            ErrorCode.BAD_REQUEST,
            f"Method {request.method} not allowed",
        ),
    }

    error_code, default_message = error_map.get(
        exc.status_code, (ErrorCode.INTERNAL_SERVER_ERROR, "An unexpected error occurred")
    )

    message = exc.detail if exc.detail and exc.detail != "Not Found" else default_message

    logger.warning(
        f"HTTP {exc.status_code} on {request.method} {request.url.path}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": error_code,
            "message": message,
            "details": {},
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions.

    Logs the error and returns a generic error response.
    """
    logger.exception(
        f"Unexpected error on {request.method} {request.url.path}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "exception_type": exc.__class__.__name__,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": ErrorCode.INTERNAL_SERVER_ERROR,
            "message": "An unexpected error occurred",
            "details": {},
        },
    )

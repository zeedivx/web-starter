"""Request/response logging middleware."""

import time
from collections.abc import Awaitable, Callable
from typing import override
from uuid import uuid4

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.

    Adds request ID to each request and logs request/response details.
    """

    @override
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process request and log details."""
        request_id = str(uuid4())
        request.state.request_id = request_id

        logger.info(
            f"→ {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query": str(request.query_params),
                "client": request.client.host if request.client else None,
            },
        )

        start_time = time.time()
        try:
            response: Response = await call_next(request)
            process_time = time.time() - start_time

            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.4f}"

            logger.info(
                f"← {request.method} {request.url.path} - {response.status_code} ({process_time:.4f}s)",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "process_time": process_time,
                },
            )

            return response

        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"✗ {request.method} {request.url.path} - ERROR ({process_time:.4f}s): {e}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                    "process_time": process_time,
                },
            )
            raise

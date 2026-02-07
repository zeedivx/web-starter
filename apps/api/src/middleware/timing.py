"""Request timing middleware."""

import time
from collections.abc import Awaitable, Callable
from typing import override

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class TimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for tracking request timing.

    Logs slow requests (> 1 second).
    """

    @override
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process request and track timing."""
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time

        if process_time > 1.0:
            logger.warning(
                f"Slow request detected: {request.method} {request.url.path} took {process_time:.2f}s",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "duration": process_time,
                    "slow_request": True,
                },
            )

        return response

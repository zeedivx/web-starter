"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from src import __version__
from src.api.v1.router import api_router
from src.core.events import lifespan
from src.core.settings import settings
from src.middleware import LoggingMiddleware, TimingMiddleware


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        description="Web Starter API built with FastAPI",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan,
    )

    if not settings.debug:
        app.add_middleware(
            TrustedHostMiddleware,  # type: ignore[arg-type]
            allowed_hosts=["*"],
        )

    app.add_middleware(
        CORSMiddleware,  # type: ignore[arg-type]
        allow_origins=["*"] if settings.debug else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(TimingMiddleware)  # type: ignore[arg-type]
    app.add_middleware(LoggingMiddleware)  # type: ignore[arg-type]

    app.include_router(api_router, prefix="/v1")

    return app


app = create_app()

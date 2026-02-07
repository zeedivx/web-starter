"""Logging configuration using loguru."""

import sys
from pathlib import Path

from loguru import logger

from src.core.settings import settings


def setup_logging() -> None:
    """
    Configure loguru logging.

    """
    logger.remove()

    _ = logger.add(
        sys.stderr,
        format=settings.log_format,
        level=settings.log_level,
        colorize=True,
        backtrace=True,
        diagnose=settings.debug,
    )

    if settings.env != "test":
        log_path = Path(settings.log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        _ = logger.add(
            settings.log_file_path,
            format=settings.log_format,
            level=settings.log_level,
            rotation=settings.log_rotation,
            retention=settings.log_retention,
            compression="zip",
            backtrace=True,
            diagnose=settings.debug,
        )

        if settings.env == "production":
            _ = logger.add(
                log_path.parent / "app.json",
                format="{message}",
                level=settings.log_level,
                rotation=settings.log_rotation,
                retention=settings.log_retention,
                compression="zip",
                serialize=True,
            )

    logger.info(f"Logging configured: level={settings.log_level}, env={settings.env}")


def get_logger(name: str):
    """
    Get a logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance

    Usage:
        ```python
        from core.logging import get_logger

        logger = get_logger(__name__)
        logger.info("Something happened")
        ```
    """
    return logger.bind(name=name)

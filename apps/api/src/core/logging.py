"""Logging configuration using loguru."""

import logging
import sys
from pathlib import Path
from typing import override

from loguru import logger

from src.core.settings import settings


class InterceptHandler(logging.Handler):
    """
    Intercept standard logging messages and redirect to loguru.

    This allows third-party libraries (SQLAlchemy, uvicorn, etc.)
    to use loguru's formatting.
    """

    @override
    def emit(self, record: logging.LogRecord) -> None:
        """Emit a record using loguru."""
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame = logging.currentframe()
        depth = 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


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

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    loggers_config = {
        "uvicorn": logging.INFO,
        "uvicorn.access": logging.INFO,
        "uvicorn.error": logging.ERROR,
        "sqlalchemy.engine": logging.WARNING,
    }

    for logger_name, level in loggers_config.items():
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.setLevel(level)
        logging_logger.propagate = False

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

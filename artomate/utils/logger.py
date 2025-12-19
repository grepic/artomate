"""Centralized logging configuration with rotation and structured output."""

import sys
from pathlib import Path
from typing import Optional

from loguru import logger

from artomate.core.config import Config


def setup_logging(config: Optional[Config] = None) -> None:
    """Setup centralized logging with rotation and formatting.

    Features:
    - Console output with colors for development
    - File output with rotation (100MB files, 30 days retention)
    - Separate error log file (90 days retention)
    - Compression of rotated files
    - Structured format with timestamps

    Args:
        config: Application configuration
    """
    if config is None:
        from artomate.core.config import get_config
        config = get_config()

    # Remove default handler
    logger.remove()

    # Console output (colorized for readability)
    logger.add(
        sys.stderr,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        level=config.log_level,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    # Main log file with rotation
    logger.add(
        config.log_file,
        rotation="100 MB",  # Rotate when file reaches 100MB
        retention="30 days",  # Keep logs for 30 days
        compression="zip",  # Compress rotated files
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level: <8} | "
            "{name}:{function}:{line} | "
            "{extra[job_id]!s:>6} | "
            "{message}"
        ),
        level="DEBUG",
        enqueue=True,  # Async logging for better performance
        backtrace=True,
        diagnose=True,
    )

    # Separate error log file (easier to find issues)
    error_log_file = config.log_file.parent / "errors.log"
    logger.add(
        error_log_file,
        rotation="50 MB",
        retention="90 days",  # Keep errors longer
        compression="zip",
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level: <8} | "
            "{name}:{function}:{line} | "
            "{extra[job_id]!s:>6} | "
            "{message}"
        ),
        level="ERROR",
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

    logger.configure(extra={"job_id": "N/A"})

    logger.info(
        f"Logging configured: level={config.log_level}, "
        f"log_file={config.log_file}, error_log={error_log_file}"
    )


def get_logger_with_context(job_id: Optional[int] = None, **kwargs):
    """Get logger with context (job_id, etc.).

    Usage:
        log = get_logger_with_context(job_id=123)
        log.info("Processing job")
        # Output: ... | job_id=123 | Processing job

    Args:
        job_id: Job ID for correlation
        **kwargs: Additional context fields

    Returns:
        Logger with context bound
    """
    context = {}

    if job_id is not None:
        context["job_id"] = job_id

    context.update(kwargs)

    return logger.bind(**context)


def log_function_call(func):
    """Decorator to log function entry/exit.

    Usage:
        @log_function_call
        def my_function(arg1, arg2):
            return result
    """
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"→ Entering {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"← Exiting {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"✗ {func.__name__} failed: {e}")
            raise

    return wrapper


# Example usage:
# from artomate.utils.logger import setup_logging, get_logger_with_context
#
# # At application startup
# setup_logging(config)
#
# # In workers
# log = get_logger_with_context(job_id=job.id)
# log.info("Starting image generation")
# log.error("API call failed", api="openai", attempt=3)

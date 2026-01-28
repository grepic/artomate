"""Centralized logging configuration with rotation and structured output."""

import sys
import uuid
from pathlib import Path
from typing import Optional
from contextvars import ContextVar

from loguru import logger

from artomate.core.config import Config

# Context variable for correlation ID tracking across threads/async
correlation_id_var: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)


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
            "job_id={extra[job_id]!s:>6} | "
            "correlation_id={extra[correlation_id]!s} | "
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
            "job_id={extra[job_id]!s:>6} | "
            "correlation_id={extra[correlation_id]!s} | "
            "{message}"
        ),
        level="ERROR",
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

    logger.configure(extra={"job_id": "N/A", "correlation_id": "N/A"})

    logger.info(
        f"Logging configured: level={config.log_level}, "
        f"log_file={config.log_file}, error_log={error_log_file}"
    )


def get_logger_with_context(job_id: Optional[int] = None, correlation_id: Optional[str] = None, **kwargs):
    """Get logger with context (job_id, correlation_id, etc.).

    Usage:
        log = get_logger_with_context(job_id=123, correlation_id="abc-123")
        log.info("Processing job")
        # Output: ... | job_id=123 | correlation_id=abc-123 | Processing job

    Args:
        job_id: Job ID for correlation
        correlation_id: Unique ID for tracking request across services
        **kwargs: Additional context fields

    Returns:
        Logger with context bound
    """
    context = {}

    if job_id is not None:
        context["job_id"] = job_id

    # Get correlation_id from context var if not provided
    if correlation_id is None:
        correlation_id = correlation_id_var.get()
    
    if correlation_id is not None:
        context["correlation_id"] = correlation_id

    context.update(kwargs)

    return logger.bind(**context)


def set_correlation_id(correlation_id: Optional[str] = None) -> str:
    """Set correlation ID for current context.
    
    Args:
        correlation_id: Correlation ID to set, or None to generate new one
        
    Returns:
        The correlation ID that was set
    """
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())
    
    correlation_id_var.set(correlation_id)
    return correlation_id


def get_correlation_id() -> Optional[str]:
    """Get current correlation ID from context.
    
    Returns:
        Current correlation ID or None
    """
    return correlation_id_var.get()


def clear_correlation_id() -> None:
    """Clear correlation ID from current context."""
    correlation_id_var.set(None)


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

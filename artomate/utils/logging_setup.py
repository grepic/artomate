"""Enhanced logging system with rotation, correlation IDs, and structured output."""

import sys
import contextvars
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from loguru import logger


# Context variable for correlation ID (thread-safe)
correlation_id_var = contextvars.ContextVar('correlation_id', default=None)


class LogConfig:
    """Centralized logging configuration."""
    
    # Log levels per environment
    DEV_LEVEL = "DEBUG"
    PROD_LEVEL = "INFO"
    
    # Log formats
    CONSOLE_FORMAT = (
        "<green>{time:HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{extra[correlation_id]}</cyan> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    FILE_FORMAT = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{extra[correlation_id]} | "
        "{name}:{function}:{line} | "
        "{message}"
    )
    
    JSON_FORMAT = (
        '{{' 
        '"timestamp": "{time:YYYY-MM-DD HH:mm:ss.SSS}", '
        '"level": "{level}", '
        '"correlation_id": "{extra[correlation_id]}", '
        '"module": "{name}", '
        '"function": "{function}", '
        '"line": {line}, '
        '"message": "{message}"'
        '}}'
    )
    
    # Rotation settings
    ROTATION_SIZE = "100 MB"
    RETENTION_DAYS = "30 days"
    COMPRESSION = "zip"
    
    # Error log retention
    ERROR_RETENTION_DAYS = "90 days"


def setup_logging(
    log_dir: Path,
    environment: str = "dev",
    console_level: Optional[str] = None,
    enable_json: bool = False
):
    """
    Setup centralized logging with rotation and formatting.
    
    Args:
        log_dir: Directory for log files
        environment: Environment name (dev/prod)
        console_level: Override console log level
        enable_json: Enable JSON structured logging
    """
    # Remove default handler
    logger.remove()
    
    # Ensure log directory exists
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine log level
    if console_level:
        level = console_level
    elif environment.lower() in ("prod", "production"):
        level = LogConfig.PROD_LEVEL
    else:
        level = LogConfig.DEV_LEVEL
    
    # Add console handler with colors
    logger.add(
        sys.stderr,
        format=LogConfig.CONSOLE_FORMAT,
        level=level,
        colorize=True,
        filter=lambda record: add_correlation_id(record)
    )
    
    # Add main log file with rotation
    logger.add(
        log_dir / "artomate.log",
        format=LogConfig.FILE_FORMAT if not enable_json else LogConfig.JSON_FORMAT,
        level="DEBUG",
        rotation=LogConfig.ROTATION_SIZE,
        retention=LogConfig.RETENTION_DAYS,
        compression=LogConfig.COMPRESSION,
        filter=lambda record: add_correlation_id(record)
    )
    
    # Add error-only log file
    logger.add(
        log_dir / "errors.log",
        format=LogConfig.FILE_FORMAT,
        level="ERROR",
        rotation="50 MB",
        retention=LogConfig.ERROR_RETENTION_DAYS,
        compression=LogConfig.COMPRESSION,
        filter=lambda record: add_correlation_id(record)
    )
    
    # Add worker-specific log file
    logger.add(
        log_dir / "workers.log",
        format=LogConfig.FILE_FORMAT,
        level="DEBUG",
        rotation=LogConfig.ROTATION_SIZE,
        retention=LogConfig.RETENTION_DAYS,
        compression=LogConfig.COMPRESSION,
        filter=lambda record: add_correlation_id(record) and "workers" in record["name"]
    )
    
    # Add API-specific log file
    logger.add(
        log_dir / "api.log",
        format=LogConfig.FILE_FORMAT,
        level="INFO",
        rotation=LogConfig.ROTATION_SIZE,
        retention=LogConfig.RETENTION_DAYS,
        compression=LogConfig.COMPRESSION,
        filter=lambda record: add_correlation_id(record) and "api" in record["name"]
    )
    
    logger.info(
        f"Logging initialized",
        environment=environment,
        level=level,
        log_dir=str(log_dir)
    )


def add_correlation_id(record: Dict[str, Any]) -> bool:
    """Add correlation ID to log record."""
    corr_id = correlation_id_var.get()
    record["extra"]["correlation_id"] = corr_id if corr_id else "no-correlation"
    return True


def set_correlation_id(correlation_id: str):
    """Set correlation ID for current context."""
    correlation_id_var.set(correlation_id)


def get_correlation_id() -> Optional[str]:
    """Get current correlation ID."""
    return correlation_id_var.get()


def clear_correlation_id():
    """Clear correlation ID."""
    correlation_id_var.set(None)


class CorrelationContext:
    """Context manager for correlation ID."""
    
    def __init__(self, correlation_id: str):
        self.correlation_id = correlation_id
        self.previous_id = None
    
    def __enter__(self):
        self.previous_id = get_correlation_id()
        set_correlation_id(self.correlation_id)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.previous_id:
            set_correlation_id(self.previous_id)
        else:
            clear_correlation_id()


def log_function_call(func):
    """Decorator to log function entry and exit."""
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"Entering {func.__name__}", args=args, kwargs=kwargs)
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Exiting {func.__name__}", result=type(result).__name__)
            return result
        except Exception as e:
            logger.error(f"Exception in {func.__name__}", error=str(e), exc_info=True)
            raise
    
    return wrapper


class StructuredLogger:
    """Structured logger with consistent field names."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logger.bind(component=name)
    
    def log_job_start(self, job_id: int, job_type: str, **kwargs):
        """Log job start."""
        self.logger.info(
            "Job started",
            job_id=job_id,
            job_type=job_type,
            **kwargs
        )
    
    def log_job_complete(self, job_id: int, duration: float, **kwargs):
        """Log job completion."""
        self.logger.info(
            "Job completed",
            job_id=job_id,
            duration_seconds=duration,
            **kwargs
        )
    
    def log_job_failed(self, job_id: int, error: Exception, **kwargs):
        """Log job failure."""
        self.logger.error(
            "Job failed",
            job_id=job_id,
            error_type=type(error).__name__,
            error_message=str(error),
            **kwargs,
            exc_info=True
        )
    
    def log_api_call(self, service: str, endpoint: str, status: int, duration: float):
        """Log API call."""
        self.logger.info(
            "API call",
            service=service,
            endpoint=endpoint,
            status_code=status,
            duration_ms=duration * 1000
        )
    
    def log_api_error(self, service: str, endpoint: str, error: Exception):
        """Log API error."""
        self.logger.error(
            "API error",
            service=service,
            endpoint=endpoint,
            error_type=type(error).__name__,
            error_message=str(error),
            exc_info=True
        )
    
    def log_metric(self, metric_name: str, value: float, unit: str = None, **tags):
        """Log metric."""
        self.logger.info(
            "Metric",
            metric_name=metric_name,
            value=value,
            unit=unit,
            **tags
        )


# Usage examples:
#
# 1. Setup logging at application start:
#    setup_logging(Path("logs"), environment="prod")
#
# 2. Use correlation ID for tracking requests:
#    with CorrelationContext(f"job-{job_id}"):
#        logger.info("Processing job")
#        # All logs in this block will have the correlation ID
#
# 3. Structured logging:
#    struct_logger = StructuredLogger("image_generator")
#    struct_logger.log_job_start(job_id=123, job_type="generate_image")
#
# 4. Function logging:
#    @log_function_call
#    def my_function():
#        pass

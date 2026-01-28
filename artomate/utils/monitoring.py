"""Monitoring, metrics, and health checks."""

import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict

from loguru import logger


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    name: str
    status: str  # "healthy", "degraded", "unhealthy"
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }


class MetricsCollector:
    """Collect and store application metrics."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Counters
        self.counters = defaultdict(int)
        
        # Gauges (current values)
        self.gauges = {}
        
        # Histograms (timing data)
        self.histograms = defaultdict(list)
        
        # Start time
        self.start_time = datetime.utcnow()
        
        self._initialized = True
        self._lock_internal = threading.Lock()
    
    def increment_counter(self, name: str, value: int = 1, tags: Dict[str, str] = None):
        """Increment a counter metric."""
        with self._lock_internal:
            key = self._make_key(name, tags)
            self.counters[key] += value
    
    def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Set a gauge metric."""
        with self._lock_internal:
            key = self._make_key(name, tags)
            self.gauges[key] = value
    
    def record_histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a histogram value (e.g., timing)."""
        with self._lock_internal:
            key = self._make_key(name, tags)
            self.histograms[key].append({
                "value": value,
                "timestamp": datetime.utcnow()
            })
            
            # Keep only last 1000 values per metric
            if len(self.histograms[key]) > 1000:
                self.histograms[key] = self.histograms[key][-1000:]
    
    def _make_key(self, name: str, tags: Optional[Dict[str, str]] = None) -> str:
        """Create metric key with tags."""
        if not tags:
            return name
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}{{{tag_str}}}"
    
    def get_metrics(self) -> Dict:
        """Get all metrics."""
        with self._lock_internal:
            return {
                "counters": dict(self.counters),
                "gauges": dict(self.gauges),
                "histograms": {
                    key: {
                        "count": len(values),
                        "min": min(v["value"] for v in values) if values else 0,
                        "max": max(v["value"] for v in values) if values else 0,
                        "avg": sum(v["value"] for v in values) / len(values) if values else 0
                    }
                    for key, values in self.histograms.items()
                },
                "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds()
            }
    
    def reset(self):
        """Reset all metrics."""
        with self._lock_internal:
            self.counters.clear()
            self.gauges.clear()
            self.histograms.clear()


class Timer:
    """Context manager for timing operations."""
    
    def __init__(self, metric_name: str, tags: Dict[str, str] = None):
        self.metric_name = metric_name
        self.tags = tags
        self.start_time = None
        self.duration = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.duration = time.time() - self.start_time
        
        metrics = MetricsCollector()
        metrics.record_histogram(
            f"{self.metric_name}_duration_seconds",
            self.duration,
            tags=self.tags
        )
        
        # Also increment counter
        status = "error" if exc_type else "success"
        metrics.increment_counter(
            f"{self.metric_name}_total",
            tags={**(self.tags or {}), "status": status}
        )


def timed(metric_name: str = None, tags: Dict[str, str] = None):
    """Decorator to time function execution."""
    def decorator(func):
        from functools import wraps
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            name = metric_name or func.__name__
            with Timer(name, tags):
                return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


class HealthChecker:
    """Health check manager."""
    
    def __init__(self):
        self.checks: Dict[str, callable] = {}
    
    def register(self, name: str, check_func: callable):
        """Register a health check."""
        self.checks[name] = check_func
        logger.info(f"Health check registered: {name}")
    
    def run_check(self, name: str) -> HealthCheckResult:
        """Run a single health check."""
        if name not in self.checks:
            return HealthCheckResult(
                name=name,
                status="unhealthy",
                message=f"Health check '{name}' not found"
            )
        
        try:
            return self.checks[name]()
        except Exception as e:
            logger.error(f"Health check '{name}' failed", error=str(e), exc_info=True)
            return HealthCheckResult(
                name=name,
                status="unhealthy",
                message=f"Health check failed: {str(e)}"
            )
    
    def run_all_checks(self) -> Dict[str, HealthCheckResult]:
        """Run all registered health checks."""
        results = {}
        for name in self.checks:
            results[name] = self.run_check(name)
        return results
    
    def get_overall_status(self) -> str:
        """Get overall health status."""
        results = self.run_all_checks()
        
        if not results:
            return "unknown"
        
        statuses = [r.status for r in results.values()]
        
        if all(s == "healthy" for s in statuses):
            return "healthy"
        elif any(s == "unhealthy" for s in statuses):
            return "unhealthy"
        else:
            return "degraded"


# Built-in health checks

def check_database(db_session_factory) -> HealthCheckResult:
    """Check database connectivity."""
    try:
        from sqlalchemy import text
        session = db_session_factory()
        session.execute(text("SELECT 1"))
        session.close()
        
        return HealthCheckResult(
            name="database",
            status="healthy",
            message="Database connection OK"
        )
    except Exception as e:
        return HealthCheckResult(
            name="database",
            status="unhealthy",
            message=f"Database connection failed: {str(e)}"
        )


def check_disk_space(min_free_gb: float = 1.0) -> HealthCheckResult:
    """Check available disk space."""
    try:
        usage = psutil.disk_usage('/')
        free_gb = usage.free / (1024 ** 3)
        
        if free_gb < min_free_gb:
            return HealthCheckResult(
                name="disk_space",
                status="degraded",
                message=f"Low disk space: {free_gb:.2f}GB free",
                details={"free_gb": free_gb, "total_gb": usage.total / (1024 ** 3)}
            )
        
        return HealthCheckResult(
            name="disk_space",
            status="healthy",
            message=f"Disk space OK: {free_gb:.2f}GB free",
            details={"free_gb": free_gb, "total_gb": usage.total / (1024 ** 3)}
        )
    except Exception as e:
        return HealthCheckResult(
            name="disk_space",
            status="unhealthy",
            message=f"Failed to check disk space: {str(e)}"
        )


def check_memory() -> HealthCheckResult:
    """Check memory usage."""
    try:
        mem = psutil.virtual_memory()
        
        if mem.percent > 90:
            return HealthCheckResult(
                name="memory",
                status="degraded",
                message=f"High memory usage: {mem.percent:.1f}%",
                details={
                    "percent": mem.percent,
                    "available_gb": mem.available / (1024 ** 3),
                    "total_gb": mem.total / (1024 ** 3)
                }
            )
        
        return HealthCheckResult(
            name="memory",
            status="healthy",
            message=f"Memory usage OK: {mem.percent:.1f}%",
            details={
                "percent": mem.percent,
                "available_gb": mem.available / (1024 ** 3),
                "total_gb": mem.total / (1024 ** 3)
            }
        )
    except Exception as e:
        return HealthCheckResult(
            name="memory",
            status="unhealthy",
            message=f"Failed to check memory: {str(e)}"
        )


def check_api_keys(config) -> HealthCheckResult:
    """Check if required API keys are configured."""
    missing = []
    
    if not config.openai_api_key and config.default_image_provider == "openai":
        missing.append("OPENAI_API_KEY")
    if not config.printify_api_token:
        missing.append("PRINTIFY_API_TOKEN")
    
    if missing:
        return HealthCheckResult(
            name="api_keys",
            status="unhealthy",
            message=f"Missing API keys: {', '.join(missing)}",
            details={"missing_keys": missing}
        )
    
    return HealthCheckResult(
        name="api_keys",
        status="healthy",
        message="All required API keys configured"
    )


# Setup function
def setup_monitoring(config, db_session_factory=None):
    """Setup monitoring, metrics, and health checks."""
    
    # Initialize metrics collector
    metrics = MetricsCollector()
    logger.info("Metrics collector initialized")
    
    # Setup health checks
    health = HealthChecker()
    
    # Register built-in health checks
    if db_session_factory:
        health.register("database", lambda: check_database(db_session_factory))
    
    health.register("disk_space", lambda: check_disk_space())
    health.register("memory", lambda: check_memory())
    health.register("api_keys", lambda: check_api_keys(config))
    
    logger.info("Health checks registered")
    
    return health


# Usage examples:
#
# 1. Setup monitoring:
#    from artomate.core.config import get_config
#    from artomate.db.session import SessionLocal
#    health = setup_monitoring(get_config(), SessionLocal)
#
# 2. Use timer:
#    with Timer("api_call", tags={"service": "openai"}):
#        result = api.call()
#
# 3. Use timed decorator:
#    @timed("image_generation")
#    def generate_image():
#        pass
#
# 4. Manual metrics:
#    metrics = MetricsCollector()
#    metrics.increment_counter("jobs_created")
#    metrics.set_gauge("active_jobs", 5)
#
# 5. Run health checks:
#    health = HealthChecker()
#    results = health.run_all_checks()
#    status = health.get_overall_status()

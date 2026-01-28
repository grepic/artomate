"""Health check endpoints."""

import shutil
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter
from sqlalchemy import text

from artomate.core.config import get_config
from artomate.db.database import get_db
from artomate.workers.queue import get_queue
from artomate.integrations.telegram_notifier import get_telegram_notifier
from artomate.utils.monitoring import HealthChecker, MetricsCollector, check_disk_space, check_memory, check_api_keys
from artomate.utils.rate_limiter import RateLimitManager

router = APIRouter()


@router.get("")
async def health_check() -> Dict[str, Any]:
    """Comprehensive health check endpoint.

    Checks:
    - API status
    - Database connectivity
    - Storage availability and disk space
    - Redis/Queue availability
    - Telegram bot connectivity
    - Configuration status

    Returns:
        Dict with health status and component checks
    """
    config = get_config()
    health_status = {
        "status": "healthy",
        "service": "artomate",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {},
    }

    # 1. Database check
    try:
        with get_db().session_scope() as session:
            session.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {
            "status": "ok",
            "message": "Connected",
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {
            "status": "error",
            "message": str(e),
        }

    # 2. Storage check
    try:
        # Check if directories exist
        if not config.assets_dir.exists():
            raise FileNotFoundError(f"Assets directory not found: {config.assets_dir}")

        # Check disk space
        stat = shutil.disk_usage(config.assets_dir)
        free_gb = stat.free / (1024 ** 3)
        total_gb = stat.total / (1024 ** 3)
        used_percent = (stat.used / stat.total) * 100

        if free_gb < 1.0:
            health_status["status"] = "degraded"
            storage_status = "warning"
            storage_message = f"Low disk space: {free_gb:.2f}GB free"
        else:
            storage_status = "ok"
            storage_message = f"{free_gb:.2f}GB free of {total_gb:.2f}GB ({used_percent:.1f}% used)"

        health_status["checks"]["storage"] = {
            "status": storage_status,
            "message": storage_message,
            "free_gb": round(free_gb, 2),
            "total_gb": round(total_gb, 2),
            "used_percent": round(used_percent, 1),
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["storage"] = {
            "status": "error",
            "message": str(e),
        }

    # 3. Redis/Queue check
    try:
        queue = get_queue()
        if queue.is_available():
            queue_stats = queue.get_stats()
            health_status["checks"]["queue"] = {
                "status": "ok",
                "message": "Redis connected",
                "stats": queue_stats,
            }
        else:
            health_status["checks"]["queue"] = {
                "status": "unavailable",
                "message": "Redis not connected (queue disabled)",
            }
    except Exception as e:
        health_status["checks"]["queue"] = {
            "status": "error",
            "message": str(e),
        }

    # 4. Telegram bot check
    try:
        notifier = get_telegram_notifier()
        if notifier.is_available():
            health_status["checks"]["telegram"] = {
                "status": "ok",
                "message": "Bot configured",
            }
        else:
            health_status["checks"]["telegram"] = {
                "status": "unavailable",
                "message": "Bot not configured",
            }
    except Exception as e:
        health_status["checks"]["telegram"] = {
            "status": "error",
            "message": str(e),
        }

    # 5. Configuration check
    try:
        config_checks = {
            "openai_api_key": bool(config.openai_api_key),
            "printify_api_token": bool(config.printify_api_token),
            "etsy_api_key": bool(config.etsy_api_key),
        }

        required_missing = []
        if not config.openai_api_key:
            required_missing.append("OPENAI_API_KEY")
        if not config.printify_api_token:
            required_missing.append("PRINTIFY_API_TOKEN")

        if required_missing:
            config_status = "incomplete"
            config_message = f"Missing required keys: {', '.join(required_missing)}"
        else:
            config_status = "ok"
            config_message = "All required keys configured"

        health_status["checks"]["configuration"] = {
            "status": config_status,
            "message": config_message,
            "keys_configured": config_checks,
        }
    except Exception as e:
        health_status["checks"]["configuration"] = {
            "status": "error",
            "message": str(e),
        }

    return health_status


@router.get("/readiness")
async def readiness_check() -> Dict[str, str]:
    """Readiness check for Kubernetes/Docker.

    Returns 200 if service is ready to accept requests.
    """
    # Quick check - just database
    try:
        with get_db().session_scope() as session:
            session.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not ready", "error": str(e)}


@router.get("/liveness")
async def liveness_check() -> Dict[str, str]:
    """Liveness check for Kubernetes/Docker.

    Returns 200 if service is alive (even if not fully functional).
    """
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}


@router.get("/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with system metrics."""
    config = get_config()
    
    # Run all health checks
    result = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # Memory check
    memory_check = check_memory()
    result["checks"]["memory"] = memory_check.to_dict()
    if memory_check.status != "healthy":
        result["status"] = memory_check.status
    
    # Disk space check
    disk_check = check_disk_space()
    result["checks"]["disk_space"] = disk_check.to_dict()
    if disk_check.status != "healthy":
        result["status"] = disk_check.status
    
    # API keys check
    api_keys_check = check_api_keys(config)
    result["checks"]["api_keys"] = api_keys_check.to_dict()
    if api_keys_check.status != "healthy":
        result["status"] = api_keys_check.status
    
    # Rate limiter stats
    try:
        rate_manager = RateLimitManager()
        result["checks"]["rate_limiters"] = {
            "status": "healthy",
            "stats": rate_manager.get_all_stats()
        }
    except Exception as e:
        result["checks"]["rate_limiters"] = {
            "status": "error",
            "message": str(e)
        }
    
    return result


@router.get("/metrics/summary")
async def metrics_summary() -> Dict[str, Any]:
    """Get metrics summary."""
    try:
        metrics = MetricsCollector()
        return metrics.get_metrics()
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}

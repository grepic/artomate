"""Initialize all production-ready components."""

from pathlib import Path
from loguru import logger

from artomate.core.config import get_config
from artomate.utils.logging_setup import setup_logging
from artomate.utils.rate_limiter import setup_rate_limiters
from artomate.utils.cache import CacheManager, warm_up_cache
from artomate.utils.monitoring import setup_monitoring, MetricsCollector


def initialize_system():
    """
    Initialize all system components.
    
    This should be called at application startup to ensure all
    production-ready components are properly configured.
    """
    logger.info("🚀 Initializing Artomate system...")
    
    # 1. Load configuration
    config = get_config()
    logger.info(f"✓ Configuration loaded (environment: {config.env})")
    
    # 2. Setup logging
    log_dir = config.log_file.parent
    setup_logging(
        log_dir=log_dir,
        environment=config.env,
        enable_json=(config.env == "production")
    )
    logger.info(f"✓ Logging configured (directory: {log_dir})")
    
    # 3. Validate configuration
    try:
        config.print_validation_status()
        logger.info("✓ Configuration validated")
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        raise
    
    # 4. Ensure directories exist
    config.ensure_directories()
    logger.info("✓ Directories verified")
    
    # 5. Setup rate limiters
    setup_rate_limiters(config)
    logger.info("✓ Rate limiters initialized")
    
    # 6. Setup cache
    cache_mgr = CacheManager()
    logger.info("✓ Cache manager initialized")
    
    # Optional: Setup Redis if available
    try:
        import redis
        redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=False
        )
        # Test connection
        redis_client.ping()
        cache_mgr.setup_redis(redis_client)
        logger.info("✓ Redis cache backend connected")
    except Exception as e:
        logger.warning(f"Redis not available, using memory cache: {e}")
    
    # 7. Warm up cache (optional)
    try:
        warm_up_cache()
        logger.info("✓ Cache warmed up")
    except Exception as e:
        logger.warning(f"Cache warm-up skipped: {e}")
    
    # 8. Setup monitoring
    try:
        from artomate.db.database import SessionLocal
        health = setup_monitoring(config, SessionLocal)
        logger.info("✓ Monitoring and health checks configured")
    except Exception as e:
        logger.warning(f"Monitoring setup incomplete: {e}")
    
    # 9. Initialize metrics
    metrics = MetricsCollector()
    metrics.increment_counter("system.startup")
    logger.info("✓ Metrics collector initialized")
    
    logger.info("✅ System initialization complete!")
    
    return {
        "config": config,
        "cache": cache_mgr,
        "metrics": metrics
    }


def validate_system_health():
    """
    Validate system health after initialization.
    
    Returns:
        Dict with health status
    """
    logger.info("🔍 Running system health check...")
    
    config = get_config()
    health_report = {
        "status": "healthy",
        "checks": {}
    }
    
    # Check configuration
    try:
        config.validate_for_image_generation()
        health_report["checks"]["image_generation"] = "OK"
    except ValueError as e:
        health_report["checks"]["image_generation"] = f"FAILED: {e}"
        health_report["status"] = "degraded"
    
    try:
        config.validate_for_printify()
        health_report["checks"]["printify"] = "OK"
    except ValueError as e:
        health_report["checks"]["printify"] = f"FAILED: {e}"
        health_report["status"] = "degraded"
    
    try:
        config.validate_for_storage()
        health_report["checks"]["storage"] = "OK"
    except ValueError as e:
        health_report["checks"]["storage"] = f"FAILED: {e}"
        health_report["status"] = "unhealthy"
    
    try:
        config.validate_for_database()
        health_report["checks"]["database"] = "OK"
    except ValueError as e:
        health_report["checks"]["database"] = f"FAILED: {e}"
        health_report["status"] = "unhealthy"
    
    # Log results
    if health_report["status"] == "healthy":
        logger.info("✅ System health check passed")
    elif health_report["status"] == "degraded":
        logger.warning("⚠️  System health check: degraded")
    else:
        logger.error("❌ System health check: unhealthy")
    
    for check, result in health_report["checks"].items():
        status_icon = "✓" if result == "OK" else "✗"
        logger.info(f"  {status_icon} {check}: {result}")
    
    return health_report


def shutdown_system():
    """Graceful shutdown of system components."""
    logger.info("🛑 Shutting down Artomate system...")
    
    try:
        # Cleanup cache
        from artomate.utils.cache import cleanup_cache
        cleanup_cache()
        logger.info("✓ Cache cleaned up")
    except Exception as e:
        logger.warning(f"Cache cleanup failed: {e}")
    
    try:
        # Get final metrics
        metrics = MetricsCollector()
        metrics.increment_counter("system.shutdown")
        final_metrics = metrics.get_metrics()
        logger.info(f"✓ Final metrics: {final_metrics.get('uptime_seconds', 0):.0f}s uptime")
    except Exception as e:
        logger.warning(f"Metrics finalization failed: {e}")
    
    logger.info("✅ Shutdown complete")


# CLI command for system check
def run_system_check():
    """Run comprehensive system check (CLI command)."""
    print("\n" + "=" * 60)
    print("🔧 Artomate System Check")
    print("=" * 60 + "\n")
    
    try:
        # Initialize
        init_result = initialize_system()
        print("\n✅ System initialized successfully\n")
        
        # Health check
        health = validate_system_health()
        print("\n" + "=" * 60)
        print(f"System Status: {health['status'].upper()}")
        print("=" * 60)
        
        return health["status"] != "unhealthy"
        
    except Exception as e:
        print(f"\n❌ System check failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run system check when executed directly
    import sys
    success = run_system_check()
    sys.exit(0 if success else 1)

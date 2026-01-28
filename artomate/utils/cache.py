"""Caching system with memory and Redis support."""

import json
import hashlib
import pickle
from typing import Any, Optional, Callable
from datetime import datetime, timedelta
from functools import wraps
import threading

from loguru import logger


class MemoryCache:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self):
        self._cache = {}
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self._lock:
            if key not in self._cache:
                return None
            
            value, expiry = self._cache[key]
            
            # Check if expired
            if expiry and datetime.utcnow() > expiry:
                del self._cache[key]
                return None
            
            return value
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        """Set value in cache with optional TTL."""
        with self._lock:
            expiry = None
            if ttl_seconds:
                expiry = datetime.utcnow() + timedelta(seconds=ttl_seconds)
            
            self._cache[key] = (value, expiry)
    
    def delete(self, key: str):
        """Delete key from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
    
    def clear(self):
        """Clear all cache."""
        with self._lock:
            self._cache.clear()
    
    def size(self) -> int:
        """Get cache size."""
        with self._lock:
            return len(self._cache)
    
    def cleanup_expired(self):
        """Remove expired entries."""
        now = datetime.utcnow()
        with self._lock:
            expired_keys = [
                key for key, (_, expiry) in self._cache.items()
                if expiry and now > expiry
            ]
            for key in expired_keys:
                del self._cache[key]


class RedisCache:
    """Redis-based cache."""
    
    def __init__(self, redis_client=None, prefix: str = "artomate:"):
        """
        Initialize Redis cache.
        
        Args:
            redis_client: Redis client instance (if None, falls back to memory cache)
            prefix: Key prefix for namespacing
        """
        self.redis = redis_client
        self.prefix = prefix
        self._fallback = MemoryCache()
    
    def _make_key(self, key: str) -> str:
        """Create prefixed key."""
        return f"{self.prefix}{key}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.redis:
            return self._fallback.get(key)
        
        try:
            value = self.redis.get(self._make_key(key))
            if value is None:
                return None
            return pickle.loads(value)
        except Exception as e:
            logger.warning(f"Redis get error: {e}, falling back to memory")
            return self._fallback.get(key)
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        """Set value in cache with optional TTL."""
        if not self.redis:
            return self._fallback.set(key, value, ttl_seconds)
        
        try:
            serialized = pickle.dumps(value)
            if ttl_seconds:
                self.redis.setex(self._make_key(key), ttl_seconds, serialized)
            else:
                self.redis.set(self._make_key(key), serialized)
        except Exception as e:
            logger.warning(f"Redis set error: {e}, falling back to memory")
            self._fallback.set(key, value, ttl_seconds)
    
    def delete(self, key: str):
        """Delete key from cache."""
        if not self.redis:
            return self._fallback.delete(key)
        
        try:
            self.redis.delete(self._make_key(key))
        except Exception as e:
            logger.warning(f"Redis delete error: {e}")
            self._fallback.delete(key)
    
    def clear(self, pattern: str = "*"):
        """Clear cache matching pattern."""
        if not self.redis:
            return self._fallback.clear()
        
        try:
            keys = self.redis.keys(f"{self.prefix}{pattern}")
            if keys:
                self.redis.delete(*keys)
        except Exception as e:
            logger.warning(f"Redis clear error: {e}")


class CacheManager:
    """Centralized cache manager with multiple backends."""
    
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
        
        self.memory = MemoryCache()
        self.redis = None  # Will be set if Redis is available
        self.default_ttl = 300  # 5 minutes
        self._initialized = True
    
    def setup_redis(self, redis_client, prefix: str = "artomate:"):
        """Setup Redis cache backend."""
        try:
            self.redis = RedisCache(redis_client, prefix)
            logger.info("Redis cache backend initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Redis cache: {e}")
    
    def get_cache(self, use_redis: bool = True):
        """Get cache backend."""
        if use_redis and self.redis:
            return self.redis
        return self.memory


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from function arguments."""
    # Create a string representation of all arguments
    key_data = {
        "args": args,
        "kwargs": sorted(kwargs.items())
    }
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    
    # Hash for consistent length
    return hashlib.md5(key_str.encode()).hexdigest()


def cached(
    ttl_seconds: int = 300,
    key_prefix: Optional[str] = None,
    use_redis: bool = True
):
    """
    Decorator to cache function results.
    
    Args:
        ttl_seconds: Time to live in seconds
        key_prefix: Optional key prefix (defaults to function name)
        use_redis: Use Redis if available, otherwise memory
        
    Example:
        @cached(ttl_seconds=600, key_prefix="product")
        def get_product(product_id: int):
            return fetch_from_api(product_id)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            prefix = key_prefix or func.__name__
            arg_key = cache_key(*args, **kwargs)
            full_key = f"{prefix}:{arg_key}"
            
            # Try to get from cache
            cache_mgr = CacheManager()
            cache_backend = cache_mgr.get_cache(use_redis)
            
            cached_value = cache_backend.get(full_key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {prefix}")
                return cached_value
            
            # Cache miss - execute function
            logger.debug(f"Cache miss: {prefix}")
            result = func(*args, **kwargs)
            
            # Store in cache
            cache_backend.set(full_key, result, ttl_seconds)
            
            return result
        
        return wrapper
    
    return decorator


# Specific caches for common use cases

class PrintifyCatalogCache:
    """Cache for Printify catalog data."""
    
    CACHE_KEY = "printify:catalog"
    CACHE_TTL = 86400  # 24 hours
    
    @staticmethod
    def get():
        """Get cached catalog."""
        cache = CacheManager().get_cache()
        return cache.get(PrintifyCatalogCache.CACHE_KEY)
    
    @staticmethod
    def set(catalog_data: dict):
        """Set cached catalog."""
        cache = CacheManager().get_cache()
        cache.set(
            PrintifyCatalogCache.CACHE_KEY,
            catalog_data,
            PrintifyCatalogCache.CACHE_TTL
        )
        logger.info("Printify catalog cached")
    
    @staticmethod
    def clear():
        """Clear catalog cache."""
        cache = CacheManager().get_cache()
        cache.delete(PrintifyCatalogCache.CACHE_KEY)
        logger.info("Printify catalog cache cleared")


class ProductCache:
    """Cache for product data."""
    
    @staticmethod
    @cached(ttl_seconds=3600, key_prefix="product")
    def get_product(product_id: int):
        """Get cached product (decorator example)."""
        pass
    
    @staticmethod
    def invalidate_product(product_id: int):
        """Invalidate specific product cache."""
        cache = CacheManager().get_cache()
        key = f"product:{cache_key(product_id)}"
        cache.delete(key)


class ImageCache:
    """Cache for generated images metadata."""
    
    @staticmethod
    @cached(ttl_seconds=7200, key_prefix="image")
    def get_image_metadata(image_hash: str):
        """Get cached image metadata."""
        pass


def warm_up_cache():
    """Pre-populate cache with frequently accessed data."""
    logger.info("Warming up cache...")
    
    try:
        # Example: Cache Printify catalog on startup
        # from artomate.workers.printify_worker import PrintifyWorker
        # worker = PrintifyWorker()
        # catalog = worker.get_catalog()
        # PrintifyCatalogCache.set(catalog)
        
        logger.info("Cache warmed up successfully")
    except Exception as e:
        logger.warning(f"Cache warm-up failed: {e}")


def cleanup_cache():
    """Periodic cleanup of expired cache entries."""
    cache_mgr = CacheManager()
    cache_mgr.memory.cleanup_expired()
    logger.debug("Cache cleanup completed")


# Usage examples:
#
# 1. Setup cache manager:
#    cache_mgr = CacheManager()
#    # Optional: add Redis
#    import redis
#    redis_client = redis.Redis(host='localhost', port=6379, db=0)
#    cache_mgr.setup_redis(redis_client)
#
# 2. Use cached decorator:
#    @cached(ttl_seconds=600)
#    def expensive_operation(param):
#        # ... expensive operation
#        return result
#
# 3. Manual cache operations:
#    cache = CacheManager().get_cache()
#    cache.set("my_key", "my_value", ttl_seconds=300)
#    value = cache.get("my_key")
#
# 4. Use specific caches:
#    PrintifyCatalogCache.set(catalog_data)
#    catalog = PrintifyCatalogCache.get()

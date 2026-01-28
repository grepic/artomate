"""Rate limiting and throttling for API calls."""

import time
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, Callable
from collections import deque
from functools import wraps

from loguru import logger


class RateLimiter:
    """Token bucket rate limiter for API calls."""
    
    def __init__(
        self,
        name: str,
        requests_per_minute: int = 60,
        requests_per_hour: Optional[int] = None,
        requests_per_day: Optional[int] = None
    ):
        """
        Initialize rate limiter.
        
        Args:
            name: Name of the rate limiter (for logging)
            requests_per_minute: Maximum requests per minute
            requests_per_hour: Maximum requests per hour (optional)
            requests_per_day: Maximum requests per day (optional)
        """
        self.name = name
        self.rpm = requests_per_minute
        self.rph = requests_per_hour
        self.rpd = requests_per_day
        
        # Token buckets for different time windows
        self.minute_tokens = deque(maxlen=requests_per_minute)
        self.hour_tokens = deque(maxlen=requests_per_hour) if requests_per_hour else None
        self.day_tokens = deque(maxlen=requests_per_day) if requests_per_day else None
        
        self.lock = threading.Lock()
    
    def _clean_old_tokens(self):
        """Remove tokens older than their time window."""
        now = datetime.now()
        
        # Clean minute tokens (older than 60 seconds)
        while self.minute_tokens and (now - self.minute_tokens[0]) > timedelta(seconds=60):
            self.minute_tokens.popleft()
        
        # Clean hour tokens (older than 1 hour)
        if self.hour_tokens:
            while self.hour_tokens and (now - self.hour_tokens[0]) > timedelta(hours=1):
                self.hour_tokens.popleft()
        
        # Clean day tokens (older than 24 hours)
        if self.day_tokens:
            while self.day_tokens and (now - self.day_tokens[0]) > timedelta(days=1):
                self.day_tokens.popleft()
    
    def _get_wait_time(self) -> float:
        """Calculate how long to wait before making next request."""
        self._clean_old_tokens()
        
        wait_times = []
        now = datetime.now()
        
        # Check minute limit
        if len(self.minute_tokens) >= self.rpm:
            oldest = self.minute_tokens[0]
            wait_until = oldest + timedelta(seconds=60)
            wait_times.append((wait_until - now).total_seconds())
        
        # Check hour limit
        if self.hour_tokens and len(self.hour_tokens) >= self.rph:
            oldest = self.hour_tokens[0]
            wait_until = oldest + timedelta(hours=1)
            wait_times.append((wait_until - now).total_seconds())
        
        # Check day limit
        if self.day_tokens and len(self.day_tokens) >= self.rpd:
            oldest = self.day_tokens[0]
            wait_until = oldest + timedelta(days=1)
            wait_times.append((wait_until - now).total_seconds())
        
        return max(wait_times) if wait_times else 0
    
    def acquire(self, blocking: bool = True) -> bool:
        """
        Acquire permission to make a request.
        
        Args:
            blocking: If True, wait for token. If False, return immediately.
            
        Returns:
            True if acquired, False if rate limited and not blocking
        """
        with self.lock:
            wait_time = self._get_wait_time()
            
            if wait_time > 0:
                if not blocking:
                    logger.warning(
                        f"Rate limit exceeded for {self.name}",
                        wait_time=wait_time
                    )
                    return False
                
                logger.info(
                    f"Rate limit throttling for {self.name}",
                    wait_time=wait_time
                )
                time.sleep(wait_time)
            
            # Add token
            now = datetime.now()
            self.minute_tokens.append(now)
            if self.hour_tokens is not None:
                self.hour_tokens.append(now)
            if self.day_tokens is not None:
                self.day_tokens.append(now)
            
            return True
    
    def get_usage_stats(self) -> Dict[str, any]:
        """Get current usage statistics."""
        with self.lock:
            self._clean_old_tokens()
            
            stats = {
                "name": self.name,
                "requests_last_minute": len(self.minute_tokens),
                "requests_per_minute_limit": self.rpm,
                "minute_usage_percent": (len(self.minute_tokens) / self.rpm) * 100
            }
            
            if self.hour_tokens is not None:
                stats.update({
                    "requests_last_hour": len(self.hour_tokens),
                    "requests_per_hour_limit": self.rph,
                    "hour_usage_percent": (len(self.hour_tokens) / self.rph) * 100
                })
            
            if self.day_tokens is not None:
                stats.update({
                    "requests_last_day": len(self.day_tokens),
                    "requests_per_day_limit": self.rpd,
                    "day_usage_percent": (len(self.day_tokens) / self.rpd) * 100
                })
            
            return stats


class RateLimitManager:
    """Centralized rate limit management for all services."""
    
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
        
        self.limiters: Dict[str, RateLimiter] = {}
        self._initialized = True
    
    def get_limiter(self, name: str) -> Optional[RateLimiter]:
        """Get rate limiter by name."""
        return self.limiters.get(name)
    
    def add_limiter(
        self,
        name: str,
        requests_per_minute: int,
        requests_per_hour: Optional[int] = None,
        requests_per_day: Optional[int] = None
    ):
        """Add a new rate limiter."""
        self.limiters[name] = RateLimiter(
            name=name,
            requests_per_minute=requests_per_minute,
            requests_per_hour=requests_per_hour,
            requests_per_day=requests_per_day
        )
        logger.info(
            f"Rate limiter '{name}' initialized",
            rpm=requests_per_minute,
            rph=requests_per_hour,
            rpd=requests_per_day
        )
    
    def get_all_stats(self) -> Dict[str, Dict]:
        """Get usage statistics for all limiters."""
        return {
            name: limiter.get_usage_stats()
            for name, limiter in self.limiters.items()
        }


def rate_limited(limiter_name: str):
    """
    Decorator to rate limit function calls.
    
    Args:
        limiter_name: Name of the rate limiter to use
        
    Example:
        @rate_limited("openai")
        def call_openai_api():
            return openai.images.generate(...)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            manager = RateLimitManager()
            limiter = manager.get_limiter(limiter_name)
            
            if limiter is None:
                logger.warning(
                    f"No rate limiter found for '{limiter_name}', "
                    "proceeding without rate limiting"
                )
            else:
                limiter.acquire(blocking=True)
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


# Initialize default rate limiters
def setup_rate_limiters(config=None):
    """Setup rate limiters for all services."""
    manager = RateLimitManager()
    
    # OpenAI - 50 requests per minute (default tier)
    # Adjust based on your actual limits
    manager.add_limiter(
        "openai",
        requests_per_minute=getattr(config, 'openai_rpm', 50) if config else 50,
        requests_per_hour=3000  # Typical OpenAI limit
    )
    
    # Printify - 120 requests per minute
    manager.add_limiter(
        "printify",
        requests_per_minute=getattr(config, 'printify_rpm', 120) if config else 120,
        requests_per_hour=7200
    )
    
    # Etsy - 10,000 requests per day
    manager.add_limiter(
        "etsy",
        requests_per_minute=100,
        requests_per_hour=1000,
        requests_per_day=getattr(config, 'etsy_rpd', 10000) if config else 10000
    )
    
    # Stability AI - varies by tier
    manager.add_limiter(
        "stability",
        requests_per_minute=50,
        requests_per_hour=3000
    )
    
    logger.info("Rate limiters initialized for all services")


# Usage examples:
#
# 1. Setup rate limiters at application start:
#    from artomate.core.config import get_config
#    setup_rate_limiters(get_config())
#
# 2. Use decorator:
#    @rate_limited("openai")
#    def generate_image():
#        return openai.images.generate(...)
#
# 3. Manual usage:
#    manager = RateLimitManager()
#    limiter = manager.get_limiter("printify")
#    if limiter.acquire():
#        # Make API call
#        pass
#
# 4. Check usage:
#    manager = RateLimitManager()
#    stats = manager.get_all_stats()
#    print(stats)

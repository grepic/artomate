"""
Circuit breaker pattern for protecting against cascading failures.

Prevents repeated calls to a failing service, allowing it time to recover.
"""

import time
from enum import Enum
from functools import wraps
from typing import Callable, Optional, Type, Tuple
from loguru import logger
import threading


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation, requests pass through
    OPEN = "open"          # Circuit is open, requests fail immediately
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open."""
    pass


class CircuitBreaker:
    """
    Circuit breaker implementation for protecting against cascading failures.
    
    States:
        CLOSED: Normal operation, all requests pass through
        OPEN: Too many failures, requests fail immediately for recovery_timeout
        HALF_OPEN: Testing if service recovered, allows limited requests
    
    Transitions:
        CLOSED -> OPEN: After failure_threshold failures
        OPEN -> HALF_OPEN: After recovery_timeout seconds
        HALF_OPEN -> CLOSED: If test request succeeds
        HALF_OPEN -> OPEN: If test request fails
    
    Args:
        failure_threshold: Number of failures before opening circuit (default: 5)
        recovery_timeout: Seconds to wait before testing recovery (default: 60)
        expected_exception: Exception type that counts as failure (default: Exception)
        name: Optional name for logging (default: function name)
    
    Example:
        # Create circuit breaker for OpenAI API
        openai_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=30,
            expected_exception=openai.APIError,
            name="OpenAI"
        )
        
        @openai_breaker
        def generate_image(prompt):
            return openai.images.generate(prompt=prompt)
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception,
        name: Optional[str] = None,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.name = name or "CircuitBreaker"
        
        # State tracking
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: Optional[float] = None
        self._lock = threading.Lock()
        
        logger.info(
            f"Circuit breaker '{self.name}' initialized",
            extra={
                "breaker_name": self.name,
                "failure_threshold": failure_threshold,
                "recovery_timeout": recovery_timeout,
            }
        )
    
    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        with self._lock:
            return self._state
    
    @property
    def failure_count(self) -> int:
        """Get current failure count."""
        with self._lock:
            return self._failure_count
    
    def _transition_to_open(self):
        """Transition circuit to OPEN state."""
        with self._lock:
            self._state = CircuitState.OPEN
            self._last_failure_time = time.time()
            
        logger.error(
            f"Circuit breaker '{self.name}' OPENED after {self._failure_count} failures",
            extra={
                "breaker_name": self.name,
                "state": "OPEN",
                "failure_count": self._failure_count,
                "recovery_timeout": self.recovery_timeout,
            }
        )
    
    def _transition_to_half_open(self):
        """Transition circuit to HALF_OPEN state."""
        with self._lock:
            self._state = CircuitState.HALF_OPEN
            
        logger.info(
            f"Circuit breaker '{self.name}' entering HALF_OPEN state (testing recovery)",
            extra={
                "breaker_name": self.name,
                "state": "HALF_OPEN",
            }
        )
    
    def _transition_to_closed(self):
        """Transition circuit to CLOSED state."""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._last_failure_time = None
            
        logger.info(
            f"Circuit breaker '{self.name}' CLOSED (service recovered)",
            extra={
                "breaker_name": self.name,
                "state": "CLOSED",
            }
        )
    
    def _record_failure(self):
        """Record a failure and potentially open the circuit."""
        with self._lock:
            self._failure_count += 1
            
            if self._state == CircuitState.HALF_OPEN:
                # If we fail in HALF_OPEN, go back to OPEN
                self._transition_to_open()
            elif self._failure_count >= self.failure_threshold:
                # If we reach threshold in CLOSED, open circuit
                self._transition_to_open()
    
    def _record_success(self):
        """Record a success and potentially close the circuit."""
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                # Success in HALF_OPEN means service recovered
                self._transition_to_closed()
            elif self._state == CircuitState.CLOSED:
                # Reset failure count on success
                self._failure_count = 0
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        if self._state != CircuitState.OPEN:
            return False
        
        if self._last_failure_time is None:
            return False
        
        elapsed = time.time() - self._last_failure_time
        return elapsed >= self.recovery_timeout
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator to wrap function with circuit breaker."""
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use function name if breaker name not set
            if self.name == "CircuitBreaker":
                self.name = func.__name__
            
            # Check if circuit is open
            if self._state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._transition_to_half_open()
                else:
                    # Circuit is open and not ready to retry
                    time_remaining = self.recovery_timeout - (time.time() - self._last_failure_time)
                    error_msg = (
                        f"Circuit breaker '{self.name}' is OPEN. "
                        f"Service unavailable. Retry in {time_remaining:.1f}s"
                    )
                    logger.warning(
                        error_msg,
                        extra={
                            "breaker_name": self.name,
                            "state": "OPEN",
                            "time_remaining": time_remaining,
                        }
                    )
                    raise CircuitBreakerError(error_msg)
            
            # Attempt the call
            try:
                result = func(*args, **kwargs)
                self._record_success()
                return result
                
            except self.expected_exception as e:
                self._record_failure()
                logger.warning(
                    f"Circuit breaker '{self.name}' recorded failure",
                    extra={
                        "breaker_name": self.name,
                        "state": self._state.value,
                        "failure_count": self._failure_count,
                        "error": str(e),
                    }
                )
                raise
        
        return wrapper
    
    def reset(self):
        """Manually reset the circuit breaker to CLOSED state."""
        self._transition_to_closed()
        logger.info(
            f"Circuit breaker '{self.name}' manually reset",
            extra={"breaker_name": self.name}
        )


# Pre-configured circuit breakers for common services
openai_breaker = CircuitBreaker(
    failure_threshold=3,
    recovery_timeout=30.0,
    name="OpenAI",
)

printify_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60.0,
    name="Printify",
)

etsy_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60.0,
    name="Etsy",
)

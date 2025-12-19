"""Retry decorator with exponential backoff for resilient API calls."""

import time
from functools import wraps
from typing import Callable, Type, Tuple, Optional

from loguru import logger


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 2.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int, float], None]] = None,
):
    """Retry decorator with exponential backoff.

    Retries a function call with exponential backoff when specified exceptions occur.
    Useful for API calls that may fail due to network issues or rate limiting.

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        base_delay: Initial delay in seconds (default: 2.0)
        backoff: Backoff multiplier (default: 2.0)
                 Delay formula: base_delay * (backoff ** attempt)
                 Example with defaults: 2s, 4s, 8s
        exceptions: Tuple of exception types to catch and retry
        on_retry: Optional callback function(exception, attempt, delay)

    Returns:
        Decorator function

    Example:
        @retry_with_backoff(max_retries=3, base_delay=2, exceptions=(requests.RequestException,))
        def call_api():
            response = requests.get("https://api.example.com")
            return response.json()

        # Retry behavior:
        # Attempt 1 fails -> wait 2s
        # Attempt 2 fails -> wait 4s
        # Attempt 3 fails -> wait 8s
        # Attempt 4 fails -> raise exception
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):  # +1 for initial attempt
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e

                    # If this was the last attempt, raise the exception
                    if attempt == max_retries:
                        logger.error(
                            f"❌ {func.__name__} failed after {max_retries + 1} attempts: {e}"
                        )
                        raise

                    # Calculate delay with exponential backoff
                    delay = base_delay * (backoff ** attempt)

                    logger.warning(
                        f"⚠️  {func.__name__} attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )

                    # Call optional retry callback
                    if on_retry:
                        try:
                            on_retry(e, attempt + 1, delay)
                        except Exception as callback_error:
                            logger.warning(f"Retry callback failed: {callback_error}")

                    # Wait before retrying
                    time.sleep(delay)

            # This should never be reached, but just in case
            if last_exception:
                raise last_exception

        return wrapper

    return decorator


def retry_on_rate_limit(
    max_retries: int = 5,
    base_delay: float = 5.0,
    backoff: float = 2.0,
):
    """Specialized retry decorator for rate limit errors.

    Uses longer delays suitable for API rate limiting.
    Default: 5s, 10s, 20s, 40s, 80s

    Args:
        max_retries: Maximum number of retry attempts (default: 5)
        base_delay: Initial delay in seconds (default: 5.0)
        backoff: Backoff multiplier (default: 2.0)

    Example:
        @retry_on_rate_limit()
        def call_rate_limited_api():
            return api.make_request()
    """
    return retry_with_backoff(
        max_retries=max_retries,
        base_delay=base_delay,
        backoff=backoff,
        exceptions=(Exception,),  # Catch all, filter in implementation
    )


class RetryConfig:
    """Configuration for retry behavior per service."""

    # OpenAI API
    OPENAI_MAX_RETRIES = 3
    OPENAI_BASE_DELAY = 2.0
    OPENAI_BACKOFF = 2.0

    # Printify API
    PRINTIFY_MAX_RETRIES = 3
    PRINTIFY_BASE_DELAY = 1.0
    PRINTIFY_BACKOFF = 2.0

    # Etsy API
    ETSY_MAX_RETRIES = 3
    ETSY_BASE_DELAY = 3.0
    ETSY_BACKOFF = 2.0

    # Network requests (general)
    NETWORK_MAX_RETRIES = 4
    NETWORK_BASE_DELAY = 2.0
    NETWORK_BACKOFF = 2.0

    @classmethod
    def for_openai(cls):
        """Get retry decorator configured for OpenAI API."""
        return retry_with_backoff(
            max_retries=cls.OPENAI_MAX_RETRIES,
            base_delay=cls.OPENAI_BASE_DELAY,
            backoff=cls.OPENAI_BACKOFF,
        )

    @classmethod
    def for_printify(cls):
        """Get retry decorator configured for Printify API."""
        return retry_with_backoff(
            max_retries=cls.PRINTIFY_MAX_RETRIES,
            base_delay=cls.PRINTIFY_BASE_DELAY,
            backoff=cls.PRINTIFY_BACKOFF,
        )

    @classmethod
    def for_etsy(cls):
        """Get retry decorator configured for Etsy API."""
        return retry_with_backoff(
            max_retries=cls.ETSY_MAX_RETRIES,
            base_delay=cls.ETSY_BASE_DELAY,
            backoff=cls.ETSY_BACKOFF,
        )

    @classmethod
    def for_network(cls):
        """Get retry decorator configured for general network requests."""
        return retry_with_backoff(
            max_retries=cls.NETWORK_MAX_RETRIES,
            base_delay=cls.NETWORK_BASE_DELAY,
            backoff=cls.NETWORK_BACKOFF,
        )


# Example usage:
#
# Option 1: Use decorator directly
# @retry_with_backoff(max_retries=3, base_delay=2, exceptions=(requests.RequestException,))
# def my_api_call():
#     return requests.get("https://api.example.com").json()
#
# Option 2: Use service-specific decorator
# @RetryConfig.for_openai()
# def generate_image():
#     return openai.images.generate(...)
#
# Option 3: With custom callback
# def on_retry_callback(exception, attempt, delay):
#     logger.warning(f"Retry {attempt}: {exception}")
#
# @retry_with_backoff(max_retries=3, on_retry=on_retry_callback)
# def my_function():
#     ...

"""Tests for retry decorator."""

import time
import pytest
from artomate.utils.retry import retry_with_backoff


class TestRetryDecorator:
    """Test retry_with_backoff decorator."""

    def test_retry_succeeds_on_first_attempt(self):
        """Test that function succeeds on first attempt without retry."""
        call_count = 0

        @retry_with_backoff(max_retries=3, base_delay=0.1)
        def success_function():
            nonlocal call_count
            call_count += 1
            return "success"

        result = success_function()

        assert result == "success"
        assert call_count == 1

    def test_retry_succeeds_after_failures(self):
        """Test that function retries and eventually succeeds."""
        call_count = 0

        @retry_with_backoff(max_retries=3, base_delay=0.1, exceptions=(ValueError,))
        def eventually_succeeds():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Not yet")
            return "success"

        result = eventually_succeeds()

        assert result == "success"
        assert call_count == 3

    def test_retry_exhausts_attempts(self):
        """Test that retry gives up after max_retries."""
        call_count = 0

        @retry_with_backoff(max_retries=2, base_delay=0.01, exceptions=(ValueError,))
        def always_fails():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")

        with pytest.raises(ValueError, match="Always fails"):
            always_fails()

        # max_retries=2 means 1 initial + 2 retries = 3 total attempts
        assert call_count == 3

    def test_retry_with_exponential_backoff(self):
        """Test that delays follow exponential backoff pattern."""
        call_times = []

        @retry_with_backoff(
            max_retries=3, base_delay=0.1, backoff=2.0, exceptions=(ValueError,)
        )
        def record_times():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise ValueError("Fail")
            return "success"

        record_times()

        # Check delays: ~0.1s, ~0.2s
        assert len(call_times) == 3
        delay1 = call_times[1] - call_times[0]
        delay2 = call_times[2] - call_times[1]

        # Allow some tolerance
        assert 0.08 < delay1 < 0.15  # ~0.1s delay
        assert 0.15 < delay2 < 0.30  # ~0.2s delay

    def test_retry_only_catches_specified_exceptions(self):
        """Test that only specified exceptions trigger retry."""
        call_count = 0

        @retry_with_backoff(max_retries=3, base_delay=0.01, exceptions=(ValueError,))
        def raises_different_exception():
            nonlocal call_count
            call_count += 1
            raise TypeError("Wrong exception")

        with pytest.raises(TypeError, match="Wrong exception"):
            raises_different_exception()

        # Should fail immediately, no retries
        assert call_count == 1

    def test_retry_with_callback(self):
        """Test that on_retry callback is called."""
        retry_info = []

        def on_retry(exception, attempt, delay):
            retry_info.append((str(exception), attempt, delay))

        @retry_with_backoff(
            max_retries=2,  # 1 initial + 2 retries = 3 total
            base_delay=0.1,
            backoff=2.0,
            exceptions=(ValueError,),
            on_retry=on_retry,
        )
        def fails_twice():
            if len(retry_info) < 2:
                raise ValueError(f"Attempt {len(retry_info) + 1}")
            return "success"

        result = fails_twice()

        assert result == "success"
        assert len(retry_info) == 2
        assert retry_info[0][1] == 1  # First retry
        assert retry_info[1][1] == 2  # Second retry

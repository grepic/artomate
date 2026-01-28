"""Tests for circuit breaker."""

import time
import pytest
from artomate.utils.circuit_breaker import CircuitBreaker, CircuitState, CircuitBreakerError


class TestCircuitBreaker:
    """Test CircuitBreaker pattern."""

    def test_circuit_starts_closed(self):
        """Test that circuit breaker starts in CLOSED state."""
        breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=0.5)

        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0

    def test_circuit_allows_success_when_closed(self):
        """Test that successful calls pass through when circuit is closed."""
        breaker = CircuitBreaker(failure_threshold=3)

        @breaker
        def success_function():
            return "success"

        result = success_function()

        assert result == "success"
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0

    def test_circuit_opens_after_threshold_failures(self):
        """Test that circuit opens after reaching failure threshold."""
        breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=1.0)
        call_count = 0

        @breaker
        def failing_function():
            nonlocal call_count
            call_count += 1
            raise Exception("Fail")

        # First 3 failures should reach threshold
        for i in range(3):
            with pytest.raises(Exception, match="Fail"):
                failing_function()

        assert breaker.state == CircuitState.OPEN
        assert call_count == 3

        # Next call should fail immediately with CircuitBreakerError
        with pytest.raises(CircuitBreakerError, match="OPEN"):
            failing_function()

        # Function not called again
        assert call_count == 3

    def test_circuit_transitions_to_half_open_after_timeout(self):
        """Test that circuit transitions to HALF_OPEN after recovery timeout."""
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=0.2)

        @breaker
        def failing_function():
            raise Exception("Fail")

        # Open the circuit
        for _ in range(2):
            with pytest.raises(Exception):
                failing_function()

        assert breaker.state == CircuitState.OPEN

        # Wait for recovery timeout
        time.sleep(0.3)

        # Next call should transition to HALF_OPEN
        with pytest.raises(Exception):
            failing_function()

        # Circuit should be back to OPEN (failed in HALF_OPEN)
        assert breaker.state == CircuitState.OPEN

    def test_circuit_closes_on_success_in_half_open(self):
        """Test that circuit closes when call succeeds in HALF_OPEN state."""
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=0.2)
        should_fail = True

        @breaker
        def sometimes_fails():
            if should_fail:
                raise Exception("Fail")
            return "success"

        # Open the circuit
        for _ in range(2):
            with pytest.raises(Exception):
                sometimes_fails()

        assert breaker.state == CircuitState.OPEN

        # Wait for recovery timeout
        time.sleep(0.3)

        # Now succeed
        should_fail = False
        result = sometimes_fails()

        assert result == "success"
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0

    def test_circuit_resets_failure_count_on_success(self):
        """Test that failure count resets on successful call."""
        breaker = CircuitBreaker(failure_threshold=3)
        fail_count = 0

        @breaker
        def intermittent_failure():
            nonlocal fail_count
            fail_count += 1
            if fail_count <= 2:
                raise Exception("Fail")
            return "success"

        # First two calls fail
        for _ in range(2):
            with pytest.raises(Exception):
                intermittent_failure()

        assert breaker.failure_count == 2

        # Third call succeeds - should reset counter
        result = intermittent_failure()

        assert result == "success"
        assert breaker.failure_count == 0
        assert breaker.state == CircuitState.CLOSED

    def test_circuit_with_specific_exception(self):
        """Test circuit breaker with specific exception type."""
        breaker = CircuitBreaker(
            failure_threshold=2, expected_exception=ValueError
        )

        @breaker
        def raises_value_error():
            raise ValueError("Value error")

        @breaker
        def raises_type_error():
            raise TypeError("Type error")

        # ValueError should count as failure
        for _ in range(2):
            with pytest.raises(ValueError):
                raises_value_error()

        assert breaker.state == CircuitState.OPEN

        # But TypeError should pass through without affecting circuit
        breaker.reset()  # Reset for clean test

        with pytest.raises(TypeError):
            raises_type_error()

        # Circuit should still be closed
        assert breaker.state == CircuitState.CLOSED

    def test_circuit_manual_reset(self):
        """Test manual circuit breaker reset."""
        breaker = CircuitBreaker(failure_threshold=2)

        @breaker
        def failing_function():
            raise Exception("Fail")

        # Open the circuit
        for _ in range(2):
            with pytest.raises(Exception):
                failing_function()

        assert breaker.state == CircuitState.OPEN

        # Manual reset
        breaker.reset()

        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0

    def test_pre_configured_breakers(self):
        """Test that pre-configured breakers exist and work."""
        from artomate.utils.circuit_breaker import (
            openai_breaker,
            printify_breaker,
            etsy_breaker,
        )

        # All breakers should be in CLOSED state initially
        assert openai_breaker.state == CircuitState.CLOSED
        assert printify_breaker.state == CircuitState.CLOSED
        assert etsy_breaker.state == CircuitState.CLOSED

        # Names should be set
        assert openai_breaker.name == "OpenAI"
        assert printify_breaker.name == "Printify"
        assert etsy_breaker.name == "Etsy"

    def test_circuit_breaker_isolation(self):
        """Test that different circuit breakers are isolated."""
        breaker1 = CircuitBreaker(failure_threshold=2, name="Service1")
        breaker2 = CircuitBreaker(failure_threshold=2, name="Service2")

        @breaker1
        def service1_call():
            raise Exception("Service 1 fail")

        @breaker2
        def service2_call():
            return "success"

        # Fail service1
        for _ in range(2):
            with pytest.raises(Exception):
                service1_call()

        # Service1 circuit should be open
        assert breaker1.state == CircuitState.OPEN

        # But service2 should still work
        result = service2_call()
        assert result == "success"
        assert breaker2.state == CircuitState.CLOSED

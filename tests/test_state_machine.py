"""Tests for state machine."""

import pytest

from artomate.core.state_machine import StateMachine, JobState


class TestStateMachine:
    """Test state machine transitions."""

    def test_can_transition_valid(self):
        """Test valid state transitions."""
        sm = StateMachine()

        # Valid transitions
        assert sm.can_transition(JobState.CREATED, JobState.PROCESSING_INPUT)
        assert sm.can_transition(JobState.CREATED, JobState.GENERATING)
        assert sm.can_transition(JobState.GENERATING, JobState.RENDERING)
        assert sm.can_transition(JobState.RENDERING, JobState.PRINTIFY_UPLOAD)
        assert sm.can_transition(JobState.PRINTIFY_UPLOAD, JobState.PRINTIFY_PRODUCT)
        assert sm.can_transition(JobState.PRINTIFY_PRODUCT, JobState.ETSY_LISTING)
        assert sm.can_transition(JobState.ETSY_LISTING, JobState.SOCIAL_PUBLISHING)
        assert sm.can_transition(JobState.SOCIAL_PUBLISHING, JobState.STOCK_SUBMITTING)
        assert sm.can_transition(JobState.STOCK_SUBMITTING, JobState.DONE)

    def test_can_transition_invalid(self):
        """Test invalid state transitions."""
        sm = StateMachine()

        # Can't go backwards
        assert not sm.can_transition(JobState.DONE, JobState.CREATED)
        assert not sm.can_transition(JobState.GENERATING, JobState.CREATED)
        assert not sm.can_transition(JobState.RENDERING, JobState.GENERATING)

        # Can't skip states
        assert not sm.can_transition(JobState.CREATED, JobState.RENDERING)
        assert not sm.can_transition(JobState.CREATED, JobState.DONE)

    def test_can_transition_to_failed(self):
        """Test that any state can transition to FAILED."""
        sm = StateMachine()

        # Any state should be able to transition to FAILED
        for state in JobState:
            if state != JobState.FAILED:
                assert sm.can_transition(state, JobState.FAILED)

    def test_transition_with_callback(self):
        """Test transition with success callback."""
        sm = StateMachine()
        callback_called = []

        def on_success(old_state, new_state):
            callback_called.append((old_state, new_state))

        sm.transition(
            JobState.CREATED,
            JobState.GENERATING,
            on_success=on_success,
        )

        assert len(callback_called) == 1
        assert callback_called[0] == (JobState.CREATED, JobState.GENERATING)

    def test_transition_invalid_raises_error(self):
        """Test that invalid transition raises ValueError."""
        sm = StateMachine()

        with pytest.raises(ValueError, match="Invalid state transition"):
            sm.transition(JobState.DONE, JobState.CREATED)

    def test_get_next_states(self):
        """Test getting possible next states."""
        sm = StateMachine()

        # CREATED can go to PROCESSING_INPUT or GENERATING
        next_states = sm.get_next_states(JobState.CREATED)
        assert JobState.PROCESSING_INPUT in next_states
        assert JobState.GENERATING in next_states

        # DONE has no next states
        next_states = sm.get_next_states(JobState.DONE)
        assert len(next_states) == 0

    def test_is_terminal_state(self):
        """Test terminal state detection."""
        sm = StateMachine()

        # DONE and FAILED are terminal
        assert sm.is_terminal_state(JobState.DONE)
        assert sm.is_terminal_state(JobState.FAILED)

        # Others are not terminal
        assert not sm.is_terminal_state(JobState.CREATED)
        assert not sm.is_terminal_state(JobState.GENERATING)

    def test_get_all_states(self):
        """Test getting all possible states."""
        sm = StateMachine()
        all_states = sm.get_all_states()

        # Should include all JobState enum values
        assert len(all_states) == len(JobState)
        assert JobState.CREATED in all_states
        assert JobState.DONE in all_states

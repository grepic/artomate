"""Job state machine implementation."""

from datetime import datetime
from typing import Optional

from loguru import logger

from artomate.db.models import Job, JobState


class StateMachine:
    """Job state machine for managing job lifecycle.

    State transitions:
        CREATED → PROCESSING_INPUT → GENERATING → RENDERING
        → PRINTIFY_UPLOAD → PRINTIFY_PRODUCT → ETSY_LISTING
        → SOCIAL_PUBLISHING → STOCK_SUBMITTING → DONE

    Any state can transition to FAILED or CANCELLED.
    """

    # Valid state transitions
    TRANSITIONS = {
        JobState.CREATED: [JobState.PROCESSING_INPUT, JobState.GENERATING],
        JobState.PROCESSING_INPUT: [JobState.GENERATING],
        JobState.GENERATING: [JobState.RENDERING, JobState.PRINTIFY_UPLOAD],
        JobState.RENDERING: [JobState.PRINTIFY_UPLOAD],
        JobState.PRINTIFY_UPLOAD: [JobState.PRINTIFY_PRODUCT],
        JobState.PRINTIFY_PRODUCT: [JobState.ETSY_LISTING, JobState.SOCIAL_PUBLISHING, JobState.DONE],
        JobState.ETSY_LISTING: [JobState.SOCIAL_PUBLISHING, JobState.STOCK_SUBMITTING, JobState.DONE],
        JobState.SOCIAL_PUBLISHING: [JobState.STOCK_SUBMITTING, JobState.DONE],
        JobState.STOCK_SUBMITTING: [JobState.DONE],
        JobState.DONE: [],
        JobState.FAILED: [],
        JobState.CANCELLED: [],
    }

    @classmethod
    def can_transition(cls, from_state: JobState, to_state: JobState) -> bool:
        """Check if state transition is valid.

        Args:
            from_state: Current state
            to_state: Desired state

        Returns:
            True if transition is allowed
        """
        # Can always transition to FAILED or CANCELLED
        if to_state in (JobState.FAILED, JobState.CANCELLED):
            return True

        # Check valid transitions
        allowed_states = cls.TRANSITIONS.get(from_state, [])
        return to_state in allowed_states

    @classmethod
    def transition(
        cls,
        job: Job,
        to_state: JobState,
        step: Optional[str] = None,
        error: Optional[str] = None,
    ) -> bool:
        """Transition job to new state.

        Args:
            job: Job instance
            to_state: Target state
            step: Current processing step description
            error: Error message if transitioning to FAILED

        Returns:
            True if transition was successful

        Raises:
            ValueError: If transition is not allowed
        """
        from_state = job.state

        # Check if transition is valid
        if not cls.can_transition(from_state, to_state):
            raise ValueError(
                f"Invalid state transition: {from_state.value} → {to_state.value}"
            )

        # Record state history
        if job.state_history is None:
            job.state_history = {}

        if "transitions" not in job.state_history:
            job.state_history["transitions"] = []

        transition_record = {
            "from": from_state.value,
            "to": to_state.value,
            "timestamp": datetime.utcnow().isoformat(),
            "step": step,
        }

        if error:
            transition_record["error"] = error

        job.state_history["transitions"].append(transition_record)

        # Update job state
        job.state = to_state
        job.updated_at = datetime.utcnow()
        job.current_step = step

        # Mark completion time if done or failed
        if to_state in (JobState.DONE, JobState.FAILED, JobState.CANCELLED):
            job.completed_at = datetime.utcnow()

        # Log error if failed
        if to_state == JobState.FAILED and error:
            if job.error_log is None:
                job.error_log = {}

            if "errors" not in job.error_log:
                job.error_log["errors"] = []

            job.error_log["errors"].append(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "state": from_state.value,
                    "step": step,
                    "error": error,
                }
            )
            job.retry_count += 1

        logger.info(
            f"Job {job.id} transitioned: {from_state.value} → {to_state.value}"
            + (f" ({step})" if step else "")
        )

        return True

    @classmethod
    def get_next_states(cls, current_state: JobState) -> list[JobState]:
        """Get list of valid next states from current state.

        Args:
            current_state: Current job state

        Returns:
            List of valid next states
        """
        states = cls.TRANSITIONS.get(current_state, []).copy()
        # Can always fail or cancel
        if current_state not in (JobState.DONE, JobState.FAILED, JobState.CANCELLED):
            states.extend([JobState.FAILED, JobState.CANCELLED])
        return states

    @classmethod
    def is_terminal_state(cls, state: JobState) -> bool:
        """Check if state is terminal (no further transitions).

        Args:
            state: Job state to check

        Returns:
            True if state is terminal
        """
        return state in (JobState.DONE, JobState.FAILED, JobState.CANCELLED)

    @classmethod
    def is_processing_state(cls, state: JobState) -> bool:
        """Check if state represents active processing.

        Args:
            state: Job state to check

        Returns:
            True if job is actively processing
        """
        return state not in (
            JobState.CREATED,
            JobState.DONE,
            JobState.FAILED,
            JobState.CANCELLED,
        )

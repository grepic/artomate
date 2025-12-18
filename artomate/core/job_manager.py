"""Job lifecycle management."""

from datetime import datetime
from typing import Optional

from loguru import logger
from sqlalchemy.orm import Session

from artomate.core.config import Config, get_config
from artomate.core.state_machine import StateMachine
from artomate.db.database import get_db
from artomate.db.models import Job, JobState


class JobManager:
    """Manages job lifecycle and state transitions."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize job manager.

        Args:
            config: Application configuration. If None, uses global config.
        """
        self.config = config or get_config()
        self.db = get_db()

    def create_job(
        self,
        theme: str,
        niche: Optional[str] = None,
        style: Optional[str] = None,
        input_source: str = "manual",
        input_data: Optional[dict] = None,
        config: Optional[dict] = None,
        keywords: Optional[list[str]] = None,
        priority: int = 5,
        scheduled_for: Optional[datetime] = None,
    ) -> Job:
        """Create a new job.

        Args:
            theme: Main theme/subject (e.g., "cat", "japanese garden")
            niche: Niche category (e.g., "wall-art", "apparel")
            style: Design style (e.g., "japandi", "minimalist")
            input_source: Source of input ("manual", "csv", "trend")
            input_data: Additional input metadata
            config: Job-specific configuration
            keywords: List of keywords
            priority: Job priority (1-10, higher = more important)
            scheduled_for: When to process the job

        Returns:
            Created job instance
        """
        with self.db.session_scope() as session:
            job = Job(
                theme=theme,
                niche=niche,
                style=style,
                input_source=input_source,
                input_data=input_data or {},
                config=config or {},
                keywords=keywords or [],
                priority=priority,
                scheduled_for=scheduled_for,
                state=JobState.CREATED,
                state_history={"transitions": []},
                error_log={"errors": []},
            )

            session.add(job)
            session.flush()  # Get the job ID
            session.refresh(job)  # Refresh to get all defaults

            job_id = job.id

            logger.info(f"Created job {job_id}: theme='{theme}', style='{style}', niche='{niche}'")

        # Get job outside of session scope to avoid detached instance issues
        return self.get_job(job_id)

    def get_job(self, job_id: int, session: Optional[Session] = None) -> Optional[Job]:
        """Get job by ID.

        Args:
            job_id: Job ID
            session: Optional existing session

        Returns:
            Job instance or None if not found
        """
        if session:
            return session.query(Job).filter(Job.id == job_id).first()
        else:
            with self.db.session_scope() as session:
                job = session.query(Job).filter(Job.id == job_id).first()
                if job:
                    # Make instance detached but accessible
                    session.expunge(job)
                return job

    def get_jobs(
        self,
        state: Optional[JobState] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Job]:
        """Get list of jobs with optional filtering.

        Args:
            state: Filter by job state
            limit: Maximum number of jobs to return
            offset: Offset for pagination

        Returns:
            List of jobs
        """
        with self.db.session_scope() as session:
            query = session.query(Job)

            if state:
                query = query.filter(Job.state == state)

            query = query.order_by(Job.priority.desc(), Job.created_at.desc())
            query = query.limit(limit).offset(offset)

            return list(query.all())

    def update_job_state(
        self,
        job: Job,
        to_state: JobState,
        step: Optional[str] = None,
        error: Optional[str] = None,
        session: Optional[Session] = None,
    ) -> bool:
        """Update job state using state machine.

        Args:
            job: Job instance
            to_state: Target state
            step: Current processing step
            error: Error message if transitioning to FAILED
            session: Optional existing session

        Returns:
            True if state transition was successful

        Raises:
            ValueError: If state transition is invalid
        """
        try:
            StateMachine.transition(job, to_state, step=step, error=error)

            # If session provided, caller is responsible for commit
            if not session:
                with self.db.session_scope() as db_session:
                    db_session.add(job)

            return True

        except ValueError as e:
            logger.error(f"Failed to transition job {job.id}: {e}")
            raise

    def can_process_job(self, job: Job) -> tuple[bool, str]:
        """Check if job can be processed.

        Args:
            job: Job instance

        Returns:
            Tuple of (can_process, reason)
        """
        # Check if already completed or failed
        if StateMachine.is_terminal_state(job.state):
            return False, f"Job is in terminal state: {job.state.value}"

        # Check if scheduled for future
        if job.scheduled_for and job.scheduled_for > datetime.utcnow():
            return False, f"Job scheduled for {job.scheduled_for}"

        # Check retry limit
        if job.retry_count >= self.config.max_retries:
            return False, f"Exceeded max retries ({self.config.max_retries})"

        return True, "OK"

    def retry_job(self, job_id: int) -> Optional[Job]:
        """Retry a failed job by resetting to CREATED state.

        Args:
            job_id: Job ID to retry

        Returns:
            Updated job instance or None if job not found
        """
        with self.db.session_scope() as session:
            job = self.get_job(job_id, session=session)

            if not job:
                logger.error(f"Job {job_id} not found")
                return None

            if job.state != JobState.FAILED:
                logger.warning(f"Job {job_id} is not in FAILED state, current: {job.state.value}")
                return job

            # Reset to CREATED
            job.state = JobState.CREATED
            job.current_step = None
            job.completed_at = None

            logger.info(f"Retry job {job_id} (attempt {job.retry_count + 1})")

            session.add(job)

            return job

    def cancel_job(self, job_id: int) -> Optional[Job]:
        """Cancel a job.

        Args:
            job_id: Job ID to cancel

        Returns:
            Updated job instance or None if job not found
        """
        with self.db.session_scope() as session:
            job = self.get_job(job_id, session=session)

            if not job:
                logger.error(f"Job {job_id} not found")
                return None

            if StateMachine.is_terminal_state(job.state):
                logger.warning(f"Job {job_id} already in terminal state: {job.state.value}")
                return job

            # Transition to CANCELLED
            StateMachine.transition(job, JobState.CANCELLED, step="User cancelled")

            logger.info(f"Cancelled job {job_id}")

            session.add(job)

            return job

    def get_job_stats(self) -> dict:
        """Get overall job statistics.

        Returns:
            Dictionary with job counts by state
        """
        with self.db.session_scope() as session:
            stats = {
                "total": session.query(Job).count(),
            }

            for state in JobState:
                count = session.query(Job).filter(Job.state == state).count()
                stats[state.value] = count

            return stats

    def cleanup_old_jobs(self, days: int = 90) -> int:
        """Delete completed jobs older than specified days.

        Args:
            days: Age threshold in days

        Returns:
            Number of jobs deleted
        """
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        with self.db.session_scope() as session:
            deleted = (
                session.query(Job)
                .filter(
                    Job.state.in_([JobState.DONE, JobState.CANCELLED]),
                    Job.completed_at < cutoff_date,
                )
                .delete()
            )

            logger.info(f"Deleted {deleted} old jobs (older than {days} days)")

            return deleted

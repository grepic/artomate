"""Job queue system using Redis Queue (RQ) for background processing."""

import os
from typing import Optional, Callable, Any
from datetime import timedelta

from redis import Redis, ConnectionError as RedisConnectionError
from rq import Queue, Worker, Retry
from rq.job import Job
from loguru import logger

from artomate.core.config import get_config


class JobQueue:
    """Redis Queue wrapper for background job processing.

    Features:
    - Background job processing
    - Job scheduling
    - Job monitoring and status tracking
    - Automatic retries with exponential backoff
    - Failed job tracking

    Usage:
        # Enqueue a job
        queue = JobQueue()
        job = queue.enqueue(my_function, arg1, arg2, kwarg1=value)

        # Check job status
        status = queue.get_job_status(job.id)

        # Get result
        result = queue.get_job_result(job.id)
    """

    def __init__(
        self,
        redis_url: Optional[str] = None,
        queue_name: str = "artomate",
    ):
        """Initialize job queue.

        Args:
            redis_url: Redis connection URL (default: redis://localhost:6379)
            queue_name: Queue name (default: artomate)
        """
        config = get_config()

        # Get Redis URL from config or use default
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")

        try:
            self.redis_conn = Redis.from_url(self.redis_url)
            # Test connection
            self.redis_conn.ping()
            logger.info(f"✓ Connected to Redis at {self.redis_url}")
        except RedisConnectionError as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            logger.warning("Job queue will not be available. Start Redis with: redis-server")
            self.redis_conn = None

        self.queue_name = queue_name
        self.queue = Queue(queue_name, connection=self.redis_conn) if self.redis_conn else None

    def is_available(self) -> bool:
        """Check if queue is available (Redis connected)."""
        return self.redis_conn is not None and self.queue is not None

    def enqueue(
        self,
        func: Callable,
        *args,
        job_timeout: int = 600,  # 10 minutes
        result_ttl: int = 3600,  # 1 hour
        failure_ttl: int = 86400,  # 24 hours
        retry: Optional[Retry] = None,
        **kwargs,
    ) -> Optional[Job]:
        """Enqueue a job for background processing.

        Args:
            func: Function to execute
            *args: Positional arguments for the function
            job_timeout: Job execution timeout in seconds (default: 600)
            result_ttl: How long to keep successful results (default: 3600s)
            failure_ttl: How long to keep failed jobs (default: 86400s)
            retry: Retry configuration (default: None)
            **kwargs: Keyword arguments for the function

        Returns:
            Job object or None if queue not available
        """
        if not self.is_available():
            logger.warning("Queue not available, executing function synchronously")
            return None

        # Default retry: 3 attempts with exponential backoff
        if retry is None:
            retry = Retry(max=3, interval=[10, 30, 60])

        job = self.queue.enqueue(
            func,
            *args,
            job_timeout=job_timeout,
            result_ttl=result_ttl,
            failure_ttl=failure_ttl,
            retry=retry,
            **kwargs,
        )

        logger.info(f"✓ Enqueued job {job.id}: {func.__name__}")
        return job

    def enqueue_in(
        self,
        time_delta: timedelta,
        func: Callable,
        *args,
        **kwargs,
    ) -> Optional[Job]:
        """Schedule a job to run after a delay.

        Args:
            time_delta: Delay before execution
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Job object or None
        """
        if not self.is_available():
            logger.warning("Queue not available, cannot schedule job")
            return None

        job = self.queue.enqueue_in(time_delta, func, *args, **kwargs)
        logger.info(f"✓ Scheduled job {job.id} in {time_delta}")
        return job

    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID.

        Args:
            job_id: Job ID

        Returns:
            Job object or None
        """
        if not self.is_available():
            return None

        return Job.fetch(job_id, connection=self.redis_conn)

    def get_job_status(self, job_id: str) -> Optional[str]:
        """Get job status.

        Args:
            job_id: Job ID

        Returns:
            Job status: queued, started, finished, failed, or None
        """
        job = self.get_job(job_id)
        return job.get_status() if job else None

    def get_job_result(self, job_id: str) -> Optional[Any]:
        """Get job result.

        Args:
            job_id: Job ID

        Returns:
            Job result or None if not finished
        """
        job = self.get_job(job_id)
        if not job:
            return None

        if job.is_finished:
            return job.result
        elif job.is_failed:
            logger.error(f"Job {job_id} failed: {job.exc_info}")
            return None
        else:
            logger.info(f"Job {job_id} not finished yet (status: {job.get_status()})")
            return None

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a job.

        Args:
            job_id: Job ID

        Returns:
            True if cancelled, False otherwise
        """
        job = self.get_job(job_id)
        if job:
            job.cancel()
            logger.info(f"✓ Cancelled job {job_id}")
            return True
        return False

    def get_queue_length(self) -> int:
        """Get number of jobs in queue."""
        if not self.is_available():
            return 0
        return len(self.queue)

    def get_failed_jobs(self) -> list[Job]:
        """Get list of failed jobs."""
        if not self.is_available():
            return []

        from rq.registry import FailedJobRegistry
        registry = FailedJobRegistry(queue=self.queue)
        return [Job.fetch(job_id, connection=self.redis_conn) for job_id in registry.get_job_ids()]

    def get_workers(self) -> list[Worker]:
        """Get list of active workers."""
        if not self.is_available():
            return []
        return Worker.all(connection=self.redis_conn)

    def get_stats(self) -> dict:
        """Get queue statistics.

        Returns:
            Dict with queue stats
        """
        if not self.is_available():
            return {
                "available": False,
                "message": "Redis not connected",
            }

        from rq.registry import StartedJobRegistry, FinishedJobRegistry, FailedJobRegistry

        started_registry = StartedJobRegistry(queue=self.queue)
        finished_registry = FinishedJobRegistry(queue=self.queue)
        failed_registry = FailedJobRegistry(queue=self.queue)

        return {
            "available": True,
            "queue_name": self.queue_name,
            "queued": len(self.queue),
            "started": len(started_registry),
            "finished": len(finished_registry),
            "failed": len(failed_registry),
            "workers": len(self.get_workers()),
        }


# Global queue instance
_queue: Optional[JobQueue] = None


def get_queue() -> JobQueue:
    """Get or create global queue instance."""
    global _queue
    if _queue is None:
        _queue = JobQueue()
    return _queue


# Example usage:
# from artomate.workers.queue import get_queue
#
# # Enqueue a job
# queue = get_queue()
# job = queue.enqueue(my_function, arg1, arg2)
#
# # Check status
# status = queue.get_job_status(job.id)
#
# # Get result
# result = queue.get_job_result(job.id)

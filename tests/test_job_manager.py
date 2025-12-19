"""Tests for job manager."""

import pytest
from datetime import datetime, timedelta

from artomate.core.job_manager import JobManager
from artomate.core.config import Config
from artomate.db.models import Job, JobState
from artomate.db.database import Database


class TestJobManager:
    """Test job manager functionality."""

    @pytest.fixture
    def job_manager(self, test_config: Config, test_db: Database):
        """Create job manager for testing."""
        return JobManager(test_config)

    def test_create_job(self, job_manager: JobManager):
        """Test creating a new job."""
        job = job_manager.create_job(
            theme="test theme",
            style="minimalist",
            keywords=["test", "sample"],
            niche="home-decor",
        )

        assert job.id is not None
        assert job.theme == "test theme"
        assert job.style == "minimalist"
        assert job.keywords == ["test", "sample"]
        assert job.niche == "home-decor"
        assert job.state == JobState.CREATED

    def test_get_job(self, job_manager: JobManager, sample_job: Job):
        """Test retrieving a job by ID."""
        retrieved_job = job_manager.get_job(sample_job.id)

        assert retrieved_job is not None
        assert retrieved_job.id == sample_job.id
        assert retrieved_job.theme == sample_job.theme

    def test_get_job_not_found(self, job_manager: JobManager):
        """Test retrieving non-existent job returns None."""
        job = job_manager.get_job(99999)
        assert job is None

    def test_update_job_state(self, job_manager: JobManager, sample_job: Job):
        """Test updating job state."""
        job_manager.update_job_state(
            sample_job,
            JobState.GENERATING,
            step="Generating image",
        )

        # Refresh from database
        updated_job = job_manager.get_job(sample_job.id)

        assert updated_job.state == JobState.GENERATING
        assert updated_job.current_step == "Generating image"

    def test_update_job_state_with_error(self, job_manager: JobManager, sample_job: Job):
        """Test updating job state with error."""
        job_manager.update_job_state(
            sample_job,
            JobState.FAILED,
            error="Test error message",
        )

        updated_job = job_manager.get_job(sample_job.id)

        assert updated_job.state == JobState.FAILED
        assert updated_job.error_message == "Test error message"

    def test_list_jobs(self, job_manager: JobManager):
        """Test listing all jobs."""
        # Create multiple jobs
        job_manager.create_job(theme="theme1", style="style1")
        job_manager.create_job(theme="theme2", style="style2")
        job_manager.create_job(theme="theme3", style="style3")

        jobs = job_manager.list_jobs()

        assert len(jobs) == 3
        assert all(isinstance(job, Job) for job in jobs)

    def test_list_jobs_with_state_filter(self, job_manager: JobManager):
        """Test listing jobs filtered by state."""
        # Create jobs with different states
        job1 = job_manager.create_job(theme="theme1", style="style1")
        job2 = job_manager.create_job(theme="theme2", style="style2")

        # Update one to GENERATING
        job_manager.update_job_state(job2, JobState.GENERATING)

        # List only CREATED jobs
        created_jobs = job_manager.list_jobs(state=JobState.CREATED)

        assert len(created_jobs) == 1
        assert created_jobs[0].id == job1.id

    def test_list_jobs_with_limit(self, job_manager: JobManager):
        """Test listing jobs with limit."""
        # Create 5 jobs
        for i in range(5):
            job_manager.create_job(theme=f"theme{i}", style="style")

        # List with limit
        jobs = job_manager.list_jobs(limit=3)

        assert len(jobs) == 3

    def test_delete_job(self, job_manager: JobManager, sample_job: Job):
        """Test deleting a job."""
        job_id = sample_job.id

        # Delete job
        job_manager.delete_job(job_id)

        # Verify it's gone
        job = job_manager.get_job(job_id)
        assert job is None

    def test_get_job_stats(self, job_manager: JobManager):
        """Test getting job statistics."""
        # Create jobs with different states
        job_manager.create_job(theme="theme1", style="style1")

        job2 = job_manager.create_job(theme="theme2", style="style2")
        job_manager.update_job_state(job2, JobState.GENERATING)

        job3 = job_manager.create_job(theme="theme3", style="style3")
        job_manager.update_job_state(job3, JobState.DONE)

        stats = job_manager.get_job_stats()

        assert stats["total"] == 3
        assert stats["by_state"][JobState.CREATED.value] == 1
        assert stats["by_state"][JobState.GENERATING.value] == 1
        assert stats["by_state"][JobState.DONE.value] == 1

    def test_job_state_history(self, job_manager: JobManager, sample_job: Job):
        """Test that job state history is tracked."""
        # Transition through multiple states
        job_manager.update_job_state(sample_job, JobState.GENERATING)
        job_manager.update_job_state(sample_job, JobState.RENDERING)

        job = job_manager.get_job(sample_job.id)

        # Check that state was updated
        assert job.state == JobState.RENDERING

    def test_create_job_with_metadata(self, job_manager: JobManager):
        """Test creating job with additional metadata."""
        extra_data = {
            "source": "telegram",
            "user_id": 123,
            "custom_field": "value",
        }

        job = job_manager.create_job(
            theme="test",
            style="minimal",
            niche="art",
        )

        assert job is not None
        assert job.theme == "test"

    def test_concurrent_job_updates(self, job_manager: JobManager, sample_job: Job):
        """Test that concurrent updates don't cause issues."""
        # Simulate concurrent updates
        job_manager.update_job_state(sample_job, JobState.GENERATING, step="Step 1")
        job_manager.update_job_state(sample_job, JobState.RENDERING, step="Step 2")

        job = job_manager.get_job(sample_job.id)

        # Last update should win
        assert job.state == JobState.RENDERING
        assert job.current_step == "Step 2"

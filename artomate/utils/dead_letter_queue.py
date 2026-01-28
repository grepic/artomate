"""Dead Letter Queue for failed jobs."""

from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path
import json

from loguru import logger
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.orm import Session

from artomate.db.base import Base


class DeadLetterJob(Base):
    """Model for jobs that permanently failed."""
    
    __tablename__ = "dead_letter_queue"
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, nullable=False, index=True)
    error_type = Column(String(255), nullable=False)
    error_message = Column(Text, nullable=False)
    error_context = Column(JSON, nullable=True)
    retry_count = Column(Integer, default=0)
    failed_at = Column(DateTime, default=datetime.utcnow)
    job_data = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<DeadLetterJob(id={self.id}, job_id={self.job_id}, error={self.error_type})>"


class DeadLetterQueue:
    """Manager for dead letter queue."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def add_failed_job(
        self,
        job_id: int,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        job_data: Optional[Dict[str, Any]] = None
    ):
        """
        Add a failed job to the dead letter queue.
        
        Args:
            job_id: ID of the failed job
            error: Exception that caused the failure
            context: Additional context about the failure
            job_data: Job data for potential recovery
        """
        dlq_job = DeadLetterJob(
            job_id=job_id,
            error_type=type(error).__name__,
            error_message=str(error),
            error_context=context or {},
            job_data=job_data or {},
            failed_at=datetime.utcnow()
        )
        
        self.db.add(dlq_job)
        self.db.commit()
        
        logger.error(
            f"Job {job_id} added to dead letter queue",
            error_type=type(error).__name__,
            error_message=str(error),
            context=context
        )
    
    def get_failed_jobs(self, limit: int = 100):
        """Get failed jobs from the queue."""
        return self.db.query(DeadLetterJob).order_by(
            DeadLetterJob.failed_at.desc()
        ).limit(limit).all()
    
    def get_by_job_id(self, job_id: int):
        """Get all failures for a specific job."""
        return self.db.query(DeadLetterJob).filter(
            DeadLetterJob.job_id == job_id
        ).all()
    
    def retry_failed_job(self, dlq_id: int):
        """Mark a failed job for retry."""
        dlq_job = self.db.query(DeadLetterJob).filter(
            DeadLetterJob.id == dlq_id
        ).first()
        
        if dlq_job:
            dlq_job.retry_count += 1
            self.db.commit()
            logger.info(f"Dead letter job {dlq_id} marked for retry")
            return dlq_job.job_data
        
        return None
    
    def remove_from_queue(self, dlq_id: int):
        """Remove a job from the dead letter queue."""
        dlq_job = self.db.query(DeadLetterJob).filter(
            DeadLetterJob.id == dlq_id
        ).first()
        
        if dlq_job:
            self.db.delete(dlq_job)
            self.db.commit()
            logger.info(f"Removed dead letter job {dlq_id}")
    
    def export_to_file(self, output_path: Path):
        """Export dead letter queue to JSON for analysis."""
        failed_jobs = self.get_failed_jobs(limit=1000)
        
        data = [
            {
                "id": job.id,
                "job_id": job.job_id,
                "error_type": job.error_type,
                "error_message": job.error_message,
                "error_context": job.error_context,
                "retry_count": job.retry_count,
                "failed_at": job.failed_at.isoformat(),
                "job_data": job.job_data
            }
            for job in failed_jobs
        ]
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Exported {len(data)} failed jobs to {output_path}")


class ErrorCategory:
    """Error categorization for better handling."""
    
    TRANSIENT = "transient"  # Temporary errors (network, rate limit)
    PERMANENT = "permanent"  # Permanent errors (auth, validation)
    CONFIGURATION = "configuration"  # Config/setup errors
    UNKNOWN = "unknown"
    
    @staticmethod
    def categorize(error: Exception) -> str:
        """Categorize error type."""
        error_msg = str(error).lower()
        error_type = type(error).__name__.lower()
        
        # Configuration errors
        config_keywords = ["api key", "token", "authentication", "unauthorized", "401", "403"]
        if any(kw in error_msg for kw in config_keywords):
            return ErrorCategory.CONFIGURATION
        
        # Transient errors
        transient_keywords = ["timeout", "rate limit", "503", "502", "429", "connection", "network"]
        if any(kw in error_msg for kw in transient_keywords):
            return ErrorCategory.TRANSIENT
        
        # Permanent errors
        permanent_keywords = ["not found", "404", "invalid", "bad request", "400"]
        if any(kw in error_msg for kw in permanent_keywords):
            return ErrorCategory.PERMANENT
        
        return ErrorCategory.UNKNOWN
    
    @staticmethod
    def should_retry(error: Exception) -> bool:
        """Determine if error should be retried."""
        category = ErrorCategory.categorize(error)
        # Retry transient and unknown errors, but not permanent or config errors
        return category in (ErrorCategory.TRANSIENT, ErrorCategory.UNKNOWN)
    
    @staticmethod
    def get_retry_delay(error: Exception, attempt: int) -> float:
        """Get recommended retry delay based on error category."""
        category = ErrorCategory.categorize(error)
        
        if category == ErrorCategory.TRANSIENT:
            # Exponential backoff: 2s, 4s, 8s, 16s
            return min(2.0 * (2 ** attempt), 60.0)
        elif category == ErrorCategory.CONFIGURATION:
            # No point retrying quickly for config errors
            return 300.0  # 5 minutes
        else:
            # Standard backoff
            return min(5.0 * (1.5 ** attempt), 60.0)

"""Scheduler for automated publication of content."""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from artomate.db.database import get_db
from artomate.db.extended_models import ScheduledPublication, PublicationStatus, StockSubmission
from artomate.integrations.stock_platforms import get_platform_client
from artomate.db.models import Job, Asset

logger = logging.getLogger(__name__)


class PublicationScheduler:
    """Schedule and execute automated publications."""

    def __init__(self, db: Session):
        """Initialize scheduler."""
        self.db = db

    def schedule_publication(
        self,
        job_id: int,
        publication_type: str,
        target_platforms: List[str],
        scheduled_for: datetime,
        config: Optional[Dict] = None,
    ) -> ScheduledPublication:
        """Schedule a new publication."""
        publication = ScheduledPublication(
            job_id=job_id,
            publication_type=publication_type,
            target_platforms=target_platforms,
            scheduled_for=scheduled_for,
            status=PublicationStatus.SCHEDULED,
            publication_config=config or {},
        )

        self.db.add(publication)
        self.db.commit()
        self.db.refresh(publication)

        logger.info(f"Scheduled publication {publication.id} for {scheduled_for}")
        return publication

    def schedule_bulk_publication(
        self,
        job_id: int,
        platforms: List[str],
        schedule_times: Optional[List[datetime]] = None,
        interval_hours: int = 24,
    ) -> List[ScheduledPublication]:
        """Schedule publications to multiple platforms with staggered timing."""
        publications = []

        if not schedule_times:
            # Generate staggered schedule
            base_time = datetime.now() + timedelta(hours=1)
            schedule_times = [base_time + timedelta(hours=i * interval_hours) for i in range(len(platforms))]

        for platform, scheduled_time in zip(platforms, schedule_times):
            pub = self.schedule_publication(
                job_id=job_id,
                publication_type="stock",
                target_platforms=[platform],
                scheduled_for=scheduled_time,
            )
            publications.append(pub)

        logger.info(f"Scheduled {len(publications)} bulk publications for job {job_id}")
        return publications

    def process_due_publications(self) -> int:
        """Process all publications that are due."""
        due_publications = (
            self.db.query(ScheduledPublication)
            .filter(
                ScheduledPublication.status == PublicationStatus.SCHEDULED,
                ScheduledPublication.scheduled_for <= datetime.now(),
            )
            .all()
        )

        processed = 0
        for pub in due_publications:
            try:
                self._execute_publication(pub)
                processed += 1
            except Exception as e:
                logger.error(f"Failed to execute publication {pub.id}: {e}")
                pub.status = PublicationStatus.FAILED
                pub.errors = pub.errors or []
                pub.errors.append({"error": str(e), "timestamp": datetime.now().isoformat()})

                # Retry logic
                if pub.retry_count < pub.max_retries:
                    pub.retry_count += 1
                    pub.scheduled_for = datetime.now() + timedelta(hours=1)
                    pub.status = PublicationStatus.SCHEDULED
                    logger.info(f"Rescheduling publication {pub.id}, retry {pub.retry_count}/{pub.max_retries}")

                self.db.commit()

        logger.info(f"Processed {processed} due publications")
        return processed

    def _execute_publication(self, publication: ScheduledPublication):
        """Execute a scheduled publication."""
        logger.info(f"Executing publication {publication.id}")

        publication.status = PublicationStatus.PUBLISHING
        self.db.commit()

        # Get job and assets
        job = self.db.query(Job).filter(Job.id == publication.job_id).first()
        if not job:
            raise ValueError(f"Job {publication.job_id} not found")

        assets = self.db.query(Asset).filter(Asset.job_id == job.id).all()
        if not assets:
            raise ValueError(f"No assets found for job {job.id}")

        results = []
        errors = []

        # Execute based on type
        if publication.publication_type == "stock":
            for platform in publication.target_platforms:
                try:
                    result = self._publish_to_stock_platform(job, assets, platform, publication.publication_config)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Failed to publish to {platform}: {e}")
                    errors.append({"platform": platform, "error": str(e)})

        elif publication.publication_type == "social":
            for platform in publication.target_platforms:
                try:
                    result = self._publish_to_social_platform(job, assets, platform, publication.publication_config)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Failed to publish to {platform}: {e}")
                    errors.append({"platform": platform, "error": str(e)})

        # Update publication status
        publication.results = results
        publication.errors = errors
        publication.published_at = datetime.now()

        if errors:
            publication.status = PublicationStatus.FAILED
        else:
            publication.status = PublicationStatus.PUBLISHED

        self.db.commit()
        logger.info(f"Publication {publication.id} completed with status {publication.status}")

    def _publish_to_stock_platform(
        self, job: Job, assets: List[Asset], platform: str, config: Dict
    ) -> Dict:
        """Publish to a stock platform."""
        # Get main asset
        main_asset = next((a for a in assets if a.asset_type.value == "hero"), assets[0])

        # Get or create stock submission
        submission = StockSubmission(
            job_id=job.id,
            asset_id=main_asset.id,
            platform=platform,
            title=config.get("title", job.theme),
            description=config.get("description", ""),
            keywords=config.get("keywords", []),
            seo_tags=config.get("seo_tags", []),
        )

        self.db.add(submission)
        self.db.commit()

        # Get platform client
        # Note: In production, load credentials from PlatformCredentials table
        client = get_platform_client(platform)

        # Upload
        result = client.upload_image(
            image_path=Path(main_asset.storage_path),
            title=submission.title,
            description=submission.description or "",
            keywords=submission.keywords or [],
        )

        # Update submission
        if result.get("success"):
            submission.platform_submission_id = result.get("submission_id")
            submission.platform_url = result.get("platform_url")
            submission.status = result.get("status", "processing")
            submission.submitted_at = datetime.now()
        else:
            submission.status = "failed"
            submission.status_message = result.get("error", "Unknown error")

        self.db.commit()

        return {
            "platform": platform,
            "submission_id": submission.id,
            "success": result.get("success", False),
            "platform_submission_id": result.get("submission_id"),
        }

    def _publish_to_social_platform(
        self, job: Job, assets: List[Asset], platform: str, config: Dict
    ) -> Dict:
        """Publish to a social media platform."""
        # Placeholder for social media publishing
        # Would integrate with Instagram, TikTok, etc. APIs
        logger.info(f"Publishing to {platform} (placeholder)")

        return {
            "platform": platform,
            "success": True,
            "post_id": f"mock_{platform}_{job.id}",
        }

    def get_upcoming_publications(self, hours: int = 24) -> List[ScheduledPublication]:
        """Get publications scheduled in the next X hours."""
        cutoff = datetime.now() + timedelta(hours=hours)

        return (
            self.db.query(ScheduledPublication)
            .filter(
                ScheduledPublication.status == PublicationStatus.SCHEDULED,
                ScheduledPublication.scheduled_for <= cutoff,
            )
            .order_by(ScheduledPublication.scheduled_for)
            .all()
        )

    def cancel_publication(self, publication_id: int) -> bool:
        """Cancel a scheduled publication."""
        publication = self.db.query(ScheduledPublication).filter(ScheduledPublication.id == publication_id).first()

        if not publication:
            return False

        if publication.status == PublicationStatus.SCHEDULED:
            publication.status = PublicationStatus.CANCELLED
            self.db.commit()
            logger.info(f"Cancelled publication {publication_id}")
            return True

        return False

    def reschedule_publication(self, publication_id: int, new_time: datetime) -> bool:
        """Reschedule a publication."""
        publication = self.db.query(ScheduledPublication).filter(ScheduledPublication.id == publication_id).first()

        if not publication:
            return False

        if publication.status == PublicationStatus.SCHEDULED:
            publication.scheduled_for = new_time
            self.db.commit()
            logger.info(f"Rescheduled publication {publication_id} to {new_time}")
            return True

        return False


def run_scheduler_loop():
    """Main scheduler loop - run this in a background process."""
    logger.info("Starting publication scheduler...")

    while True:
        try:
            db = next(get_db())
            scheduler = PublicationScheduler(db)

            processed = scheduler.process_due_publications()

            if processed > 0:
                logger.info(f"Scheduler processed {processed} publications")

            # Wait before next check
            import time

            time.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            logger.info("Scheduler stopped")
            break
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            import time

            time.sleep(60)  # Wait before retrying


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_scheduler_loop()

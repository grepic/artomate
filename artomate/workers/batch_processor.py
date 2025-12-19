"""Batch processing for multiple jobs from CSV."""

import csv
from pathlib import Path
from typing import List, Dict, Any
from io import StringIO

from loguru import logger

from artomate.core.config import Config, get_config
from artomate.core.job_manager import JobManager
from artomate.workers.queue import get_queue


class BatchProcessor:
    """Process batch of jobs from CSV file."""

    def __init__(self, config: Config = None):
        """Initialize batch processor.

        Args:
            config: Application configuration
        """
        self.config = config or get_config()
        self.job_manager = JobManager(self.config)
        self.queue = get_queue()

    def parse_csv(self, csv_content: str | Path) -> List[Dict[str, Any]]:
        """Parse CSV content into job specifications.

        Args:
            csv_content: CSV string or path to CSV file

        Returns:
            List of job specification dicts

        CSV Format:
            theme,style,keywords,niche,variants
            cat,minimalist,zen calm,home-decor,12
            dog,boho,earthy natural,lifestyle,6

        Required columns: theme
        Optional columns: style, keywords, niche, variants
        """
        if isinstance(csv_content, Path):
            csv_content = csv_content.read_text()

        jobs_data = []
        reader = csv.DictReader(StringIO(csv_content))

        for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is 1)
            # Validate required fields
            if not row.get("theme"):
                logger.warning(f"Row {row_num}: Missing required 'theme' field, skipping")
                continue

            # Parse keywords
            keywords_str = row.get("keywords", "")
            keywords = [k.strip() for k in keywords_str.split(",") if k.strip()]

            # Parse variants count
            try:
                variants = int(row.get("variants", "12"))
            except ValueError:
                logger.warning(f"Row {row_num}: Invalid variants count, using default 12")
                variants = 12

            job_spec = {
                "theme": row["theme"].strip(),
                "style": row.get("style", "").strip() or None,
                "keywords": keywords,
                "niche": row.get("niche", "").strip() or None,
                "variants": variants,
                "source": "csv_batch",
            }

            jobs_data.append(job_spec)

        logger.info(f"Parsed {len(jobs_data)} jobs from CSV")

        return jobs_data

    def create_jobs_from_csv(
        self,
        csv_content: str | Path,
        enqueue: bool = True,
    ) -> List[int]:
        """Create jobs from CSV file.

        Args:
            csv_content: CSV string or path to CSV file
            enqueue: Whether to enqueue jobs for processing

        Returns:
            List of created job IDs

        Raises:
            ValueError: If CSV parsing fails
        """
        try:
            jobs_data = self.parse_csv(csv_content)

            if not jobs_data:
                raise ValueError("No valid jobs found in CSV")

            job_ids = []

            for job_spec in jobs_data:
                try:
                    # Create job
                    job = self.job_manager.create_job(
                        theme=job_spec["theme"],
                        style=job_spec.get("style"),
                        keywords=job_spec.get("keywords"),
                        niche=job_spec.get("niche"),
                        source=job_spec.get("source"),
                    )

                    job_ids.append(job.id)

                    # Enqueue for processing
                    if enqueue and self.queue.is_available():
                        from artomate.core.workflow_orchestrator import (
                            WorkflowOrchestrator,
                        )

                        self.queue.enqueue(
                            WorkflowOrchestrator().run_complete_workflow,
                            job.id,
                            {
                                "variant_count": job_spec.get("variants", 12),
                                "product_types": ["tshirt", "poster_18x24"],
                            },
                            job_timeout=3600,  # 1 hour timeout
                        )

                        logger.info(f"✓ Created and enqueued job {job.id}")
                    else:
                        logger.info(f"✓ Created job {job.id} (not enqueued)")

                except Exception as e:
                    logger.error(f"Failed to create job from spec {job_spec}: {e}")
                    continue

            logger.info(f"✓ Created {len(job_ids)} jobs from CSV")

            return job_ids

        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            raise ValueError(f"CSV processing failed: {e}")

    def get_batch_status(self, job_ids: List[int]) -> Dict[str, Any]:
        """Get status of batch jobs.

        Args:
            job_ids: List of job IDs

        Returns:
            Dict with batch statistics
        """
        stats = {
            "total": len(job_ids),
            "created": 0,
            "processing": 0,
            "done": 0,
            "failed": 0,
            "jobs": [],
        }

        for job_id in job_ids:
            job = self.job_manager.get_job(job_id)

            if not job:
                continue

            status = {
                "id": job.id,
                "theme": job.theme,
                "style": job.style,
                "state": job.state.value,
            }

            stats["jobs"].append(status)

            # Count by state
            if job.state.value == "CREATED":
                stats["created"] += 1
            elif job.state.value in ["PROCESSING_INPUT", "GENERATING", "RENDERING"]:
                stats["processing"] += 1
            elif job.state.value == "DONE":
                stats["done"] += 1
            elif job.state.value == "FAILED":
                stats["failed"] += 1

        return stats


# Example CSV template
CSV_TEMPLATE = """theme,style,keywords,niche,variants
minimalist cat,japandi,zen calm simple,home-decor,12
boho flowers,bohemian,earthy natural colorful,lifestyle,12
geometric pattern,modern,abstract clean lines,wall-art,6
vintage car,retro,nostalgic classic,apparel,12
mountain landscape,minimalist,nature peaceful,home-decor,12
"""


def get_csv_template() -> str:
    """Get CSV template for batch import.

    Returns:
        CSV template string
    """
    return CSV_TEMPLATE.strip()

"""CLI command for running RQ workers."""

import sys
import click
from loguru import logger
from redis import Redis
from rq import Worker

from artomate.workers.queue import get_queue
from artomate.utils.logger import setup_logging
from artomate.core.config import get_config


@click.command()
@click.option(
    "--queues",
    "-q",
    default="artomate",
    help="Comma-separated list of queues to listen to (default: artomate)",
)
@click.option(
    "--burst",
    is_flag=True,
    help="Run in burst mode (exit when all jobs are processed)",
)
@click.option(
    "--name",
    "-n",
    default=None,
    help="Worker name (default: auto-generated)",
)
def worker(queues: str, burst: bool, name: str):
    """Run RQ worker to process background jobs.

    The worker will continuously process jobs from the specified queue(s).
    Press Ctrl+C to gracefully shutdown the worker.

    Examples:
        # Start worker for default queue
        python -m artomate.cli.worker

        # Start worker for multiple queues
        python -m artomate.cli.worker --queues artomate,high-priority

        # Run in burst mode (for testing)
        python -m artomate.cli.worker --burst

        # Start with custom name
        python -m artomate.cli.worker --name worker-1
    """
    # Setup logging
    config = get_config()
    setup_logging(config)

    logger.info("🚀 Starting Artomate RQ Worker")
    logger.info(f"Queues: {queues}")

    # Get queue
    queue_manager = get_queue()

    if not queue_manager.is_available():
        logger.error("❌ Redis not available. Cannot start worker.")
        logger.error("Start Redis with: redis-server")
        sys.exit(1)

    # Parse queue names
    queue_names = [q.strip() for q in queues.split(",")]

    # Create worker
    try:
        worker = Worker(
            queue_names,
            connection=queue_manager.redis_conn,
            name=name,
        )

        logger.info(f"✓ Worker {worker.name} listening on {queue_names}")

        # Run worker
        worker.work(burst=burst, with_scheduler=True)

    except KeyboardInterrupt:
        logger.info("\n👋 Worker shutting down gracefully...")
    except Exception as e:
        logger.error(f"❌ Worker error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    worker()

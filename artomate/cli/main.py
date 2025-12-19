"""Main CLI interface using Click."""

import sys
from datetime import datetime
from typing import Optional

import click
from loguru import logger
from rich.console import Console
from rich.table import Table

from artomate.core.config import get_config
from artomate.core.job_manager import JobManager
from artomate.core.state_machine import StateMachine
from artomate.db.database import init_db, reset_db
from artomate.db.models import JobState
from artomate.workers.image_generator import ImageGenerator
from artomate.workers.render_engine import RenderEngine
from artomate.cli.validate import validate_config
from artomate.cli.worker import worker as worker_command

# Rich console for beautiful output
console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Artomate - Content-to-Commerce Automation System

    Automated design generation, product creation, and marketplace publishing.
    """
    pass


# ============================================================================
# Database Commands
# ============================================================================


@cli.command()
def init_db_cmd():
    """Initialize database (create tables)."""
    try:
        init_db()
        console.print("✓ Database initialized", style="green")
    except Exception as e:
        console.print(f"✗ Failed to initialize database: {e}", style="red")
        sys.exit(1)


@cli.command()
@click.confirmation_option(prompt="Are you sure you want to reset the database?")
def reset_db_cmd():
    """Reset database (drop and recreate tables)."""
    try:
        reset_db()
        console.print("✓ Database reset", style="green")
    except Exception as e:
        console.print(f"✗ Failed to reset database: {e}", style="red")
        sys.exit(1)


# ============================================================================
# Job Management Commands
# ============================================================================


@cli.command()
@click.option("--theme", required=True, help="Theme/subject (e.g., 'cat', 'japanese garden')")
@click.option("--style", help="Design style (e.g., 'japandi', 'minimalist')")
@click.option("--niche", help="Niche category (e.g., 'wall-art', 'apparel')")
@click.option("--keywords", help="Comma-separated keywords")
@click.option("--priority", default=5, type=int, help="Priority 1-10 (default: 5)")
def create(
    theme: str,
    style: Optional[str],
    niche: Optional[str],
    keywords: Optional[str],
    priority: int,
):
    """Create a new job."""
    try:
        manager = JobManager()

        keywords_list = [k.strip() for k in keywords.split(",")] if keywords else None

        job = manager.create_job(
            theme=theme,
            style=style,
            niche=niche,
            keywords=keywords_list,
            priority=priority,
        )

        console.print(f"✓ Created job {job.id}", style="green bold")
        console.print(f"  Theme: {theme}")
        console.print(f"  Style: {style or 'N/A'}")
        console.print(f"  Niche: {niche or 'N/A'}")

    except Exception as e:
        console.print(f"✗ Failed to create job: {e}", style="red")
        sys.exit(1)


@cli.command()
@click.argument("job_id", type=int)
def run(job_id: int):
    """Run a job (generate images, create products)."""
    try:
        config = get_config()
        manager = JobManager()
        generator = ImageGenerator()
        renderer = RenderEngine()

        # Get job
        job = manager.get_job(job_id)

        if not job:
            console.print(f"✗ Job {job_id} not found", style="red")
            sys.exit(1)

        # Check if can process
        can_process, reason = manager.can_process_job(job)
        if not can_process:
            console.print(f"✗ Cannot process job: {reason}", style="red")
            sys.exit(1)

        console.print(f"▶ Running job {job_id}: {job.theme}", style="blue bold")

        # Update state to GENERATING
        manager.update_job_state(job, JobState.GENERATING, step="Starting image generation")

        # Generate images
        console.print("  Generating images...", style="yellow")
        assets = generator.generate_for_job(job, count=1)

        if not assets:
            manager.update_job_state(
                job, JobState.FAILED, error="No assets generated"
            )
            console.print("✗ No images generated", style="red")
            sys.exit(1)

        console.print(f"  ✓ Generated {len(assets)} image(s)", style="green")

        # Update state to RENDERING
        manager.update_job_state(job, JobState.RENDERING, step="Rendering print files")

        # Render print files (example: common sizes)
        console.print("  Rendering print files...", style="yellow")

        common_sizes = [
            {"width": 4500, "height": 5400, "blueprint_id": 3},  # T-shirt
            {"width": 3000, "height": 4000, "blueprint_id": 6},  # Poster
        ]

        for asset in assets:
            for size_spec in common_sizes:
                renderer.create_print_file(
                    asset=asset,
                    target_width=size_spec["width"],
                    target_height=size_spec["height"],
                    crop_mode="cover",
                    printify_blueprint_id=size_spec.get("blueprint_id"),
                )

        console.print(f"  ✓ Rendered print files", style="green")

        # Update state to DONE (for MVP, skip Printify/Etsy)
        manager.update_job_state(job, JobState.DONE, step="Job completed")

        console.print(f"✓ Job {job_id} completed", style="green bold")

    except Exception as e:
        logger.exception("Job execution failed")
        console.print(f"✗ Job failed: {e}", style="red")

        # Mark job as failed
        try:
            manager.update_job_state(job, JobState.FAILED, error=str(e))
        except:
            pass

        sys.exit(1)


@cli.command()
@click.argument("job_id", type=int, required=False)
@click.option("--state", type=click.Choice([s.value for s in JobState]), help="Filter by state")
@click.option("--limit", default=20, help="Number of jobs to show")
def status(job_id: Optional[int], state: Optional[str], limit: int):
    """Show job status."""
    try:
        manager = JobManager()

        if job_id:
            # Show single job details
            job = manager.get_job(job_id)

            if not job:
                console.print(f"✗ Job {job_id} not found", style="red")
                sys.exit(1)

            console.print(f"\n[bold]Job {job.id}[/bold]")
            console.print(f"  Theme: {job.theme}")
            console.print(f"  Style: {job.style or 'N/A'}")
            console.print(f"  Niche: {job.niche or 'N/A'}")
            console.print(f"  State: [{_get_state_color(job.state)}]{job.state.value}[/]")
            console.print(f"  Created: {job.created_at}")
            console.print(f"  Updated: {job.updated_at}")

            if job.current_step:
                console.print(f"  Current step: {job.current_step}")

            if job.retry_count > 0:
                console.print(f"  Retries: {job.retry_count}")

            # Show state history
            if job.state_history and "transitions" in job.state_history:
                console.print("\n  [bold]State History:[/bold]")
                for t in job.state_history["transitions"][-5:]:  # Last 5 transitions
                    console.print(f"    {t['from']} → {t['to']} ({t['timestamp']})")

        else:
            # Show list of jobs
            state_filter = JobState(state) if state else None
            jobs = manager.get_jobs(state=state_filter, limit=limit)

            if not jobs:
                console.print("No jobs found", style="yellow")
                return

            table = Table(title=f"Jobs ({len(jobs)})")
            table.add_column("ID", style="cyan")
            table.add_column("Theme", style="white")
            table.add_column("Style", style="white")
            table.add_column("State", style="bold")
            table.add_column("Created", style="dim")

            for job in jobs:
                state_color = _get_state_color(job.state)
                table.add_row(
                    str(job.id),
                    job.theme[:30],
                    job.style or "-",
                    f"[{state_color}]{job.state.value}[/]",
                    job.created_at.strftime("%Y-%m-%d %H:%M"),
                )

            console.print(table)

    except Exception as e:
        console.print(f"✗ Error: {e}", style="red")
        sys.exit(1)


@cli.command()
@click.argument("job_id", type=int)
def retry(job_id: int):
    """Retry a failed job."""
    try:
        manager = JobManager()

        job = manager.retry_job(job_id)

        if not job:
            console.print(f"✗ Job {job_id} not found", style="red")
            sys.exit(1)

        console.print(f"✓ Job {job_id} reset to CREATED", style="green")
        console.print(f"  Run with: artomate run {job_id}", style="dim")

    except Exception as e:
        console.print(f"✗ Error: {e}", style="red")
        sys.exit(1)


@cli.command()
@click.argument("job_id", type=int)
@click.confirmation_option(prompt="Are you sure you want to cancel this job?")
def cancel(job_id: int):
    """Cancel a job."""
    try:
        manager = JobManager()

        job = manager.cancel_job(job_id)

        if not job:
            console.print(f"✗ Job {job_id} not found", style="red")
            sys.exit(1)

        console.print(f"✓ Job {job_id} cancelled", style="green")

    except Exception as e:
        console.print(f"✗ Error: {e}", style="red")
        sys.exit(1)


@cli.command()
def stats():
    """Show overall statistics."""
    try:
        manager = JobManager()

        stats = manager.get_job_stats()

        console.print("\n[bold]Job Statistics[/bold]\n")

        for key, value in stats.items():
            if key == "total":
                console.print(f"  Total jobs: [bold]{value}[/bold]")
            else:
                console.print(f"  {key}: {value}")

    except Exception as e:
        console.print(f"✗ Error: {e}", style="red")
        sys.exit(1)


# ============================================================================
# Export Commands
# ============================================================================


@cli.command()
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["json", "csv", "xml"]),
    default="json",
    help="Export format",
)
@click.option("--output", "-o", help="Output file path")
def export(fmt: str, output: Optional[str]):
    """Export products feed."""
    console.print(f"Export to {fmt} - Not yet implemented", style="yellow")
    # TODO: Implement feed export


# ============================================================================
# Helper Functions
# ============================================================================


def _get_state_color(state: JobState) -> str:
    """Get color for job state."""
    colors = {
        JobState.CREATED: "blue",
        JobState.PROCESSING_INPUT: "cyan",
        JobState.GENERATING: "yellow",
        JobState.RENDERING: "yellow",
        JobState.PRINTIFY_UPLOAD: "magenta",
        JobState.PRINTIFY_PRODUCT: "magenta",
        JobState.ETSY_LISTING: "magenta",
        JobState.DONE: "green",
        JobState.FAILED: "red",
        JobState.CANCELLED: "dim",
    }
    return colors.get(state, "white")


# ============================================================================
# Configuration Commands
# ============================================================================

# Add validate command
cli.add_command(validate_config, name="validate")

# ============================================================================
# Worker Commands
# ============================================================================

# Add worker command
cli.add_command(worker_command, name="worker")


# ============================================================================
# Main Entry Point
# ============================================================================


if __name__ == "__main__":
    # Configure logger
    logger.remove()
    logger.add(
        sys.stderr,
        format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> | <level>{message}</level>",
        level="INFO",
    )

    cli()

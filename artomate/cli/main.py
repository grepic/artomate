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
# Interactive Commands
# ============================================================================


@cli.command()
@click.argument("images_dir", type=click.Path(exists=True))
def crop_products(images_dir: str):
    """Interactive product cropping - step by step verification.
    
    Crop images for each product type with manual verification at each step.
    Perfect for testing and ensuring quality before uploading to Printify.
    
    Example:
        artomate crop-products data/assets/images
    """
    from artomate.cli.crop_interactive import run_crop_workflow
    
    run_crop_workflow(images_dir)


@cli.command()
@click.option("--use-ai/--no-ai", default=True, help="Use AI (GPT) to generate month-specific prompts")
def calendar(use_ai: bool):
    """Create calendar with interactive prompts (step-by-step conversation)."""
    from artomate.core.conversation_engine import ConversationEngine

    console.print("\n🎨 [ARTOMATE CALENDAR GENERATOR]", style="bold cyan")
    console.print("Interactive step-by-step conversation\n", style="cyan")

    if use_ai:
        console.print("✨ AI Mode: GPT will generate unique prompts for each month\n", style="green")
    else:
        console.print("📝 Simple Mode: Basic prompt generation\n", style="yellow")

    engine = ConversationEngine()
    reply, state = engine.start()

    # First message
    console.print(reply + "\n", style="yellow")

    try:
        while True:
            user_input = input("📝 You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "done"]:
                console.print("\n👋 Goodbye!", style="green")
                break

            reply, state = engine.process_input(user_input)

            if state.stage.value == "generate":
                console.print(f"\n✨ {reply}\n", style="green bold")

                # Generate prompts (with or without AI)
                prompts = engine.get_prompts(use_ai=use_ai)

                console.print("\n📋 Generated Prompts:\n", style="cyan bold")

                for prompt_data in prompts:
                    console.print(
                        f"\n[{prompt_data['month']}]",
                        style="bold cyan"
                    )
                    if "animals" in prompt_data:
                        console.print(f"  Animals: {prompt_data['animals']}")
                    if "habitat" in prompt_data:
                        console.print(f"  Habitat: {prompt_data['habitat']}", style="dim")
                    if "season" in prompt_data:
                        console.print(f"  Season: {prompt_data['season']}", style="dim")
                    if "style" in prompt_data:
                        console.print(f"  Style: {prompt_data['style']}")
                    if "theme" in prompt_data:
                        console.print(f"  Theme: {prompt_data['theme']}")
                    console.print(f"  Prompt:\n    {prompt_data['prompt']}\n")

                # Save to JSON
                import json
                from datetime import datetime

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"calendar_prompts_{timestamp}.json"

                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(prompts, f, indent=2, ensure_ascii=False)

                console.print(f"✓ Saved prompts to: {filename}\n", style="green")

                # Ask if wants to generate images
                console.print(
                    "\n💡 Next steps:",
                    style="cyan bold"
                )
                console.print("  1. Review the prompts above")
                console.print("  2. Use these prompts in Midjourney to generate images")
                console.print(f"  3. Or set OPENAI_API_KEY in .env for DALL-E generation")
                console.print(f"  4. Or manually create jobs with: artomate create --theme 'X' --style 'Y'\n")

                break
            else:
                console.print(f"\n🤖 Assistant: {reply}\n", style="cyan")

    except KeyboardInterrupt:
        console.print("\n\n⏸️  Interrupted by user", style="yellow")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n❌ Error: {e}", style="red")
        logger.exception("Error in calendar interactive mode")
        sys.exit(1)


@cli.command()
def list_starter_products():
    """List available starter products (Wall Art - easiest to start with)."""
    from artomate.workers.starter_products import list_products
    
    console.print("\n🖼️  [STARTER PRODUCTS - WALL ART]", style="bold cyan")
    console.print("These are the easiest products to start with (full coverage, no transparency)\n", style="dim")
    
    products = list_products()
    
    table = Table()
    table.add_column("Product ID", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Sizes", style="yellow")
    
    for product_id, name, size_count in products:
        table.add_row(product_id, name, str(size_count))
    
    console.print(table)
    
    console.print("\n💡 Next step:", style="green bold")
    console.print("  artomate crop-for-product <image_file> --product <product_id>\n")


@cli.command()
@click.argument("image_path", type=click.Path(exists=True))
@click.option("--product", "-p", required=True, help="Product ID (use 'list-starter-products' to see options)")
@click.option("--output-dir", "-o", default="crops_test", help="Output directory")
@click.option("--open-preview", is_flag=True, help="Open preview images after generation")
def crop_for_product(image_path: str, product: str, output_dir: str, open_preview: bool):
    """Crop a single image for all sizes of a product (interactive preview).
    
    This command will:
    1. Load the image
    2. Crop it for ALL sizes of the selected product
    3. Save crops to output directory
    4. Show preview of what was generated
    5. Wait for your confirmation
    
    Example:
        artomate crop-for-product january.png --product poster_matte_vertical
    """
    from artomate.workers.starter_products import get_product
    from artomate.workers.render_engine import RenderEngine
    from pathlib import Path
    from PIL import Image
    
    console.print(f"\n📐 [CROP FOR PRODUCT]\n", style="bold cyan")
    
    try:
        product_spec = get_product(product)
    except KeyError:
        console.print(f"❌ Unknown product: {product}", style="red")
        console.print("Use 'artomate list-starter-products' to see available products\n", style="yellow")
        sys.exit(1)
    
    console.print(f"Product: {product_spec['name']}", style="cyan")
    console.print(f"Category: {product_spec['category']}", style="dim")
    console.print(f"Sizes: {len(product_spec['print_areas'])}", style="dim")
    console.print(f"Coverage: {product_spec['coverage_type']}\n", style="dim")
    
    image_path = Path(image_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create product subfolder
    product_dir = output_dir / product
    product_dir.mkdir(parents=True, exist_ok=True)
    
    console.print(f"Processing: {image_path.name}\n", style="yellow")
    
    renderer = RenderEngine()
    generated_files = []
    
    # Generate crops for each size
    for idx, print_area in enumerate(product_spec['print_areas'], 1):
        size_name = print_area['name']
        width = print_area['width']
        height = print_area['height']
        
        console.print(f"[{idx}/{len(product_spec['print_areas'])}] Cropping {size_name} ({width}x{height})...", end="")
        
        try:
            rendered = renderer.render_image(
                source_path=image_path,
                target_width=width,
                target_height=height,
                mode="cover",
                dpi=product_spec['dpi'],
                transparent_background=(product_spec['coverage_type'] == "transparent"),
            )
            
            # Save
            safe_name = size_name.replace("/", "-").replace(" ", "_")
            output_file = product_dir / f"{safe_name}.png"
            rendered.save(output_file, format="PNG", dpi=(product_spec['dpi'], product_spec['dpi']))
            
            generated_files.append(output_file)
            console.print(f" ✓", style="green")
            
        except Exception as e:
            console.print(f" ✗ {e}", style="red")
    
    console.print(f"\n✅ Generated {len(generated_files)} crops", style="green bold")
    console.print(f"   Output directory: {product_dir}\n", style="dim")
    
    # Show file list
    console.print("📁 Generated files:", style="cyan")
    for f in generated_files:
        file_size = f.stat().st_size / 1024
        console.print(f"   • {f.name} ({file_size:.1f} KB)", style="dim")
    
    console.print("\n💡 Next steps:", style="green bold")
    console.print(f"   1. Review the crops in: {product_dir}")
    console.print(f"   2. If OK, upload to Printify with blueprint_id={product_spec['blueprint_id']}")
    console.print(f"   3. Or process more images: artomate crop-for-product <next_image> --product {product}\n")


@cli.command()
@click.argument("image_dir", type=click.Path(exists=True))
@click.option("--output-dir", "-o", default="crops_output", help="Output directory for crops")
@click.option("--families", "-f", multiple=True, help="Specific product families to process (e.g., poster, tshirt)")
@click.option("--preview", is_flag=True, help="Show what would be processed without actually processing")
def crop_images(image_dir: str, output_dir: str, families: tuple, preview: bool):
    """Crop multiple images for all product variants.
    
    Takes a directory of images (e.g., 12 calendar images) and creates crops
    for all product families and their variants.
    
    Example:
        artomate crop-images ./calendar_images --output-dir ./crops
        artomate crop-images ./calendar_images -f poster -f canvas
        artomate crop-images ./calendar_images --preview
    """
    from artomate.workers.batch_crop_processor import BatchCropProcessor
    from pathlib import Path
    import glob

    processor = BatchCropProcessor()
    
    # Get all images from directory
    image_dir_path = Path(image_dir)
    image_patterns = ["*.png", "*.jpg", "*.jpeg", "*.webp"]
    image_paths = []
    
    for pattern in image_patterns:
        image_paths.extend(image_dir_path.glob(pattern))
    
    image_paths = sorted(image_paths)
    
    if not image_paths:
        console.print(f"❌ No images found in {image_dir}", style="red")
        sys.exit(1)
    
    console.print(f"\n📁 Found {len(image_paths)} image(s) in {image_dir}", style="cyan")
    for img in image_paths:
        console.print(f"   • {img.name}", style="dim")
    
    # Convert families tuple to list
    families_list = list(families) if families else None
    
    # Preview mode
    if preview:
        console.print("\n🔍 PREVIEW MODE\n", style="yellow bold")
        summary = processor.get_processing_summary(product_families=families_list)
        
        console.print(f"📦 Product families: {summary['total_families']}", style="cyan")
        console.print(f"📐 Total variants per image: {summary['total_variants']}", style="cyan")
        console.print(f"🖼️  Total crops (all images): {len(image_paths) * summary['total_variants']}", style="green bold")
        
        console.print("\n📋 Families to process:\n", style="cyan")
        
        table = Table()
        table.add_column("Family", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Category", style="yellow")
        table.add_column("Coverage", style="magenta")
        table.add_column("Variants", style="green")
        
        for fam in summary['families']:
            table.add_row(
                fam['family_id'],
                fam['name'],
                fam['category'],
                fam['coverage_type'],
                str(fam['variants'])
            )
        
        console.print(table)
        console.print("\n💡 Run without --preview to actually process the images\n")
        return
    
    # Actual processing
    console.print(f"\n✨ Processing images...\n", style="green bold")
    
    try:
        results = processor.process_calendar_images(
            image_paths=image_paths,
            output_dir=Path(output_dir),
            product_families=families_list,
        )
        
        console.print(f"\n✅ SUCCESS!", style="green bold")
        console.print(f"   Images processed: {results['images_processed']}/{len(image_paths)}")
        console.print(f"   Total crops generated: {results['total_crops']}")
        console.print(f"   Output directory: {output_dir}")
        
        if results['errors']:
            console.print(f"\n⚠️  Errors: {len(results['errors'])}", style="yellow")
            for error in results['errors']:
                console.print(f"   • {error}", style="dim")
        
    except Exception as e:
        console.print(f"\n❌ Error: {e}", style="red")
        logger.exception("Error in batch crop processing")
        sys.exit(1)


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

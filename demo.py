#!/usr/bin/env python3
"""Artomate Demo - Interactive showcase of all features."""

import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

console = Console()


def print_header(title: str):
    """Print section header."""
    console.print(f"\n[bold blue]{'='*60}[/]")
    console.print(f"[bold blue]{title.center(60)}[/]")
    console.print(f"[bold blue]{'='*60}[/]\n")


def demo_cli():
    """Demo CLI commands."""
    print_header("1. CLI Commands (No API keys needed)")

    console.print("Testing basic CLI commands...\n")

    import subprocess

    # Version
    console.print("[yellow]→ artomate --version[/]")
    result = subprocess.run(["artomate", "--version"], capture_output=True, text=True)
    console.print(f"  {result.stdout.strip()}\n")

    # Stats
    console.print("[yellow]→ artomate stats[/]")
    result = subprocess.run(["artomate", "stats"], capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    for line in lines[:10]:  # First 10 lines
        console.print(f"  {line}")

    console.print("\n[green]✓ CLI commands working![/]")


def demo_trends():
    """Demo trend analyzer."""
    print_header("2. Trend Analyzer")

    from artomate.workers.trend_analyzer import TrendAnalyzer

    console.print("Analyzing current trends...\n")

    analyzer = TrendAnalyzer()
    trends = analyzer.get_trending_themes(limit=5)

    console.print("[bold]🔥 Top 5 Trending Themes:[/]\n")

    for i, trend in enumerate(trends, 1):
        score = trend.get('trend_score', 0)
        color = "green" if score > 70 else "yellow" if score > 50 else "white"

        console.print(f"  [{color}]{i}. {trend['theme'].title()}[/]")
        console.print(f"     Style: {trend.get('style', 'N/A')}")
        console.print(f"     Score: {score:.0f}/100")
        console.print(f"     Keywords: {', '.join(trend.get('keywords', [])[:3])}")
        console.print()

    console.print("[green]✓ Trend analysis complete![/]")


def demo_render():
    """Demo render engine."""
    print_header("3. Render Engine")

    from artomate.workers.render_engine import RenderEngine
    from PIL import Image
    import tempfile
    from pathlib import Path

    console.print("Testing image rendering...\n")

    # Create test image
    temp_dir = Path(tempfile.mkdtemp())
    test_image = temp_dir / "test.png"

    img = Image.new('RGB', (1024, 1024), color=(100, 149, 237))  # Cornflower blue
    img.save(test_image)

    console.print(f"[yellow]Created test image:[/] {test_image}")

    # Test rendering
    renderer = RenderEngine()

    console.print("\n[yellow]Testing crop modes:[/]\n")

    modes = ["contain", "cover"]
    for mode in modes:
        rendered = renderer.render_image(
            source_path=test_image,
            target_width=4500,
            target_height=5400,
            mode=mode,
            dpi=300
        )
        console.print(f"  ✓ {mode.capitalize()}: {rendered.size} @ 300 DPI")

    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)

    console.print("\n[green]✓ Render engine working perfectly![/]")


def demo_job_creation():
    """Demo job creation."""
    print_header("4. Job Management")

    from artomate.core.job_manager import JobManager

    console.print("Creating a sample job...\n")

    manager = JobManager()

    job = manager.create_job(
        theme="minimalist mountain",
        style="scandinavian",
        niche="wall-art",
        keywords=["nature", "minimal", "peaceful"],
        priority=8
    )

    console.print(Panel.fit(
        f"[bold]Job Created![/]\n\n"
        f"ID: {job.id}\n"
        f"Theme: {job.theme}\n"
        f"Style: {job.style}\n"
        f"Niche: {job.niche}\n"
        f"State: {job.state.value}\n"
        f"Priority: {job.priority}",
        border_style="green"
    ))

    console.print("\n[green]✓ Job management working![/]")

    return job


def demo_export():
    """Demo feed export."""
    print_header("5. Feed Export")

    from artomate.workers.feed_exporter import FeedExporter

    console.print("Exporting feeds in multiple formats...\n")

    exporter = FeedExporter()

    formats = ["json", "xml", "csv"]
    paths = []

    for fmt in formats:
        path = exporter.export_products(format=fmt)
        paths.append(path)
        console.print(f"  ✓ {fmt.upper()}: {path}")

    console.print("\n[green]✓ Feed export complete![/]")
    console.print(f"\n[dim]Files saved in: exports/[/]")


def demo_image_generation():
    """Demo image generation (requires API key)."""
    print_header("6. Image Generation (Requires OpenAI API)")

    import os

    if not os.getenv("OPENAI_API_KEY"):
        console.print("[yellow]⚠️  OPENAI_API_KEY not set[/]")
        console.print("\nTo test image generation:")
        console.print("1. Add to .env: OPENAI_API_KEY=sk-...")
        console.print("2. Run this demo again\n")
        console.print("[dim]Skipping image generation demo...[/]")
        return

    from artomate.workers.image_generator import ImageGenerator
    from artomate.core.job_manager import JobManager

    console.print("[green]✓ API key found[/]\n")

    if not Confirm.ask("Generate a real image? (costs ~$0.08)", default=False):
        console.print("[dim]Skipped by user[/]")
        return

    # Create job
    manager = JobManager()
    job = manager.create_job(
        theme="zen garden",
        style="minimalist",
        niche="wall-art"
    )

    console.print(f"\n[yellow]Generating image with DALL-E 3...[/]")
    console.print("[dim]This takes 30-60 seconds...[/]\n")

    generator = ImageGenerator()

    try:
        assets = generator.generate_for_job(job, count=1)

        console.print(Panel.fit(
            f"[bold green]Image Generated![/]\n\n"
            f"Asset ID: {assets[0].id}\n"
            f"Path: {assets[0].storage_path}\n"
            f"Size: {assets[0].width}x{assets[0].height}\n"
            f"File: {assets[0].file_size_bytes / 1024:.1f} KB",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"[red]✗ Generation failed: {e}[/]")


def main():
    """Run demo."""
    console.print(Panel.fit(
        "[bold cyan]Artomate Demo[/]\n\n"
        "Interactive showcase of all features\n"
        "Press Ctrl+C to skip any section",
        border_style="cyan"
    ))

    demos = [
        ("CLI Commands", demo_cli),
        ("Trend Analyzer", demo_trends),
        ("Render Engine", demo_render),
        ("Job Management", demo_job_creation),
        ("Feed Export", demo_export),
        ("Image Generation", demo_image_generation),
    ]

    for name, func in demos:
        try:
            if Confirm.ask(f"\nRun {name} demo?", default=True):
                func()
            else:
                console.print(f"[dim]Skipped {name}[/]")
        except KeyboardInterrupt:
            console.print(f"\n[yellow]Skipped {name}[/]")
        except Exception as e:
            console.print(f"\n[red]Error in {name}: {e}[/]")
            import traceback
            traceback.print_exc()

    console.print("\n" + "="*60)
    console.print("[bold green]Demo Complete![/]".center(60))
    console.print("="*60 + "\n")

    console.print("Next steps:")
    console.print("1. Read TESTING_GUIDE.md for detailed tests")
    console.print("2. Check README.md for full documentation")
    console.print("3. Run: uvicorn artomate.api.main:app --reload")
    console.print("\nHappy automating! 🚀\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Demo interrupted[/]")
        sys.exit(0)

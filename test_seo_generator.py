#!/usr/bin/env python3
"""Test script for SEO text generator with ChatGPT API."""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from artomate.core.config import get_config
from artomate.db.models import Job
from artomate.workers.seo_text_generator import SEOTextGenerator

console = Console()


def print_header(text: str):
    """Print section header."""
    console.print(f"\n[bold cyan]{'=' * 60}[/]")
    console.print(f"[bold cyan]{text.center(60)}[/]")
    console.print(f"[bold cyan]{'=' * 60}[/]\n")


def test_seo_generator():
    """Test SEO text generator."""
    print_header("SEO TEXT GENERATOR TEST")

    # Check API key
    config = get_config()
    if not config.openai_api_key:
        console.print("[red]❌ OPENAI_API_KEY not set in .env[/]")
        console.print("\n[yellow]Please add your OpenAI API key to .env:[/]")
        console.print("OPENAI_API_KEY=sk-...")
        return False

    console.print(f"[green]✓ OpenAI API key found (length: {len(config.openai_api_key)})[/]\n")

    # Create test job
    test_job = Job(
        theme="Cat Lover",
        style="Minimalist",
        niche="home-decor",
        keywords=["cat art", "animal print", "modern decor", "gift"],
        input_source="manual",
        input_data={"description": "Beautiful minimalist cat illustration for modern homes"},
    )

    console.print("[bold]Test Job Details:[/]")
    console.print(f"  Theme: {test_job.theme}")
    console.print(f"  Style: {test_job.style}")
    console.print(f"  Niche: {test_job.niche}")
    console.print(f"  Keywords: {', '.join(test_job.keywords)}")
    console.print(f"  Input Data: {test_job.input_data}\n")

    # Initialize generator
    try:
        generator = SEOTextGenerator(config)
        console.print("[green]✓ SEO Generator initialized[/]\n")
    except Exception as e:
        console.print(f"[red]❌ Failed to initialize generator: {e}[/]")
        return False

    # Test 1: Generate title for Printify
    print_header("TEST 1: Product Title for Printify")
    try:
        title = generator.generate_product_title(
            job=test_job,
            product_name="Poster",
            platform="printify",
        )
        console.print(Panel(title, title="[green]Generated Title (Printify)[/]"))
        console.print(f"Length: {len(title)} chars\n")
    except Exception as e:
        console.print(f"[red]❌ Failed: {e}[/]\n")
        return False

    # Test 2: Generate title for Etsy
    print_header("TEST 2: Product Title for Etsy")
    try:
        title_etsy = generator.generate_product_title(
            job=test_job,
            product_name="Wall Art Print",
            platform="etsy",
            max_length=140,
        )
        console.print(Panel(title_etsy, title="[green]Generated Title (Etsy)[/]"))
        console.print(f"Length: {len(title_etsy)} chars\n")
    except Exception as e:
        console.print(f"[red]❌ Failed: {e}[/]\n")
        return False

    # Test 3: Generate description
    print_header("TEST 3: Product Description")
    try:
        description = generator.generate_product_description(
            job=test_job,
            product_name="Poster",
            platform="printify",
        )
        console.print(Panel(description, title="[green]Generated Description[/]"))
        console.print(f"Length: {len(description)} chars\n")
    except Exception as e:
        console.print(f"[red]❌ Failed: {e}[/]\n")
        return False

    # Test 4: Generate tags
    print_header("TEST 4: Product Tags")
    try:
        tags_printify = generator.generate_product_tags(
            job=test_job,
            product_name="Poster",
            platform="printify",
            max_tags=10,
        )
        console.print("[green]Generated Tags (Printify):[/]")
        console.print(f"  {', '.join(tags_printify)}")
        console.print(f"  Count: {len(tags_printify)}\n")

        tags_etsy = generator.generate_product_tags(
            job=test_job,
            product_name="Wall Art",
            platform="etsy",
            max_tags=13,
        )
        console.print("[green]Generated Tags (Etsy):[/]")
        console.print(f"  {', '.join(tags_etsy)}")
        console.print(f"  Count: {len(tags_etsy)}\n")
    except Exception as e:
        console.print(f"[red]❌ Failed: {e}[/]\n")
        return False

    # Test 5: Complete SEO package
    print_header("TEST 5: Complete SEO Package")
    try:
        seo_package = generator.generate_complete_seo_package(
            job=test_job,
            product_name="Canvas Print",
            platform="etsy",
        )
        
        console.print("[bold]Complete SEO Package:[/]\n")
        console.print(Panel(seo_package["title"], title="[cyan]Title[/]"))
        console.print(Panel(seo_package["description"][:300] + "...", title="[cyan]Description (preview)[/]"))
        console.print(f"\n[cyan]Tags:[/] {', '.join(seo_package['tags'])}\n")
        
    except Exception as e:
        console.print(f"[red]❌ Failed: {e}[/]\n")
        return False

    # Summary
    print_header("TEST SUMMARY")
    console.print("[bold green]✅ All SEO text generation tests passed![/]\n")
    
    console.print("[bold]Key Features:[/]")
    console.print("  ✓ AI-powered title generation (platform-specific)")
    console.print("  ✓ AI-powered description generation")
    console.print("  ✓ AI-powered tag generation")
    console.print("  ✓ Complete SEO package generation")
    console.print("  ✓ Fallback to rule-based generation if AI fails")
    console.print("  ✓ Platform-specific optimization (Printify, Etsy, Amazon)")

    console.print("\n[bold]Usage in Workers:[/]")
    console.print("  • PrintifyWorker: Automatic AI SEO (if OPENAI_API_KEY set)")
    console.print("  • EtsyWorker: Automatic AI SEO (if OPENAI_API_KEY set)")
    console.print("  • Disable with: worker = PrintifyWorker(use_ai_seo=False)")

    return True


def main():
    """Main test function."""
    try:
        success = test_seo_generator()
        if success:
            console.print("\n[bold green]🎉 SEO Text Generator is working perfectly![/]\n")
            sys.exit(0)
        else:
            console.print("\n[bold red]❌ Some tests failed[/]\n")
            sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Test interrupted by user[/]\n")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]❌ Unexpected error: {e}[/]\n")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()

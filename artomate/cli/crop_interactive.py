"""Interactive product cropping workflow - step by step."""

import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm, Prompt

from artomate.workers.render_engine import RenderEngine
from artomate.integrations.printify_client import PrintifyClient
from artomate.core.config import get_config

console = Console()


class ProductCropWorkflow:
    """Interactive workflow for cropping images for products."""

    def __init__(self):
        """Initialize workflow."""
        self.config = get_config()
        self.render_engine = RenderEngine()
        self.printify = None
        
        # Common print sizes (inches) at 300 DPI
        self.print_sizes = {
            "tshirt": [(4500, 5400)],  # 15x18 inches
            "poster_12x18": [(3600, 5400)],
            "poster_18x24": [(5400, 7200)],
            "canvas_16x20": [(4800, 6000)],
            "mug": [(2700, 1050)],  # Wrap around
            "phone_case": [(1125, 2436)],  # iPhone X/11/12 Pro
            "tote_bag": [(4500, 5400)],
            "pillow_18x18": [(5400, 5400)],
        }

    def list_available_products(self) -> List[Dict]:
        """Get list of available product types.

        Returns:
            List of product type dicts
        """
        products = []
        for product_type, sizes in self.print_sizes.items():
            for width, height in sizes:
                products.append({
                    "type": product_type,
                    "width": width,
                    "height": height,
                    "width_inches": width / 300,
                    "height_inches": height / 300,
                })
        return products

    def crop_images_for_product(
        self,
        image_paths: List[Path],
        product_type: str,
        output_dir: Path,
    ) -> List[Path]:
        """Crop all images for a specific product type.

        Args:
            image_paths: List of source image paths
            product_type: Product type name
            output_dir: Output directory for cropped images

        Returns:
            List of output file paths
        """
        if product_type not in self.print_sizes:
            raise ValueError(f"Unknown product type: {product_type}")

        sizes = self.print_sizes[product_type]
        output_paths = []

        # Create output directory
        product_dir = output_dir / product_type
        product_dir.mkdir(parents=True, exist_ok=True)

        console.print(f"\n🔧 Cropping {len(image_paths)} images for [cyan]{product_type}[/cyan]...")

        for img_path in image_paths:
            for width, height in sizes:
                try:
                    # Generate output filename
                    stem = img_path.stem
                    output_path = product_dir / f"{stem}_{product_type}_{width}x{height}.png"

                    # Crop image
                    result = self.render_engine.render_image(
                        source_path=img_path,
                        target_width=width,
                        target_height=height,
                        mode="cover",
                        dpi=300,
                    )

                    # Save
                    result.save(output_path, "PNG", dpi=(300, 300))
                    output_paths.append(output_path)

                    console.print(
                        f"  ✓ {img_path.name} → {output_path.name}",
                        style="green"
                    )

                except Exception as e:
                    console.print(
                        f"  ✗ Failed to crop {img_path.name}: {e}",
                        style="red"
                    )
                    logger.exception(f"Failed to crop {img_path}")

        console.print(f"\n✓ Created {len(output_paths)} cropped images\n", style="green bold")
        return output_paths

    def show_cropped_files(self, output_paths: List[Path]):
        """Display table of cropped files.

        Args:
            output_paths: List of output file paths
        """
        table = Table(title="Cropped Files")
        table.add_column("Filename", style="cyan")
        table.add_column("Size", style="magenta")
        table.add_column("Path", style="dim")

        for path in output_paths:
            from PIL import Image
            try:
                with Image.open(path) as img:
                    size = f"{img.width}x{img.height}px"
            except:
                size = "?"

            table.add_row(
                path.name,
                size,
                str(path.relative_to(Path.cwd()) if path.is_relative_to(Path.cwd()) else path)
            )

        console.print(table)

    def run_interactive(self, images_dir: Path):
        """Run interactive workflow.

        Args:
            images_dir: Directory containing source images
        """
        console.print("\n🎨 [INTERACTIVE PRODUCT CROPPING]", style="bold cyan")
        console.print("Crop images product-by-product with manual verification\n")

        # Find images
        image_paths = []
        for ext in ["*.png", "*.jpg", "*.jpeg"]:
            image_paths.extend(images_dir.glob(ext))

        if not image_paths:
            console.print(f"❌ No images found in {images_dir}", style="red")
            return

        console.print(f"📸 Found [cyan]{len(image_paths)}[/cyan] images:", style="green")
        for img in image_paths[:5]:  # Show first 5
            console.print(f"  • {img.name}")
        if len(image_paths) > 5:
            console.print(f"  ... and {len(image_paths) - 5} more")

        # Output directory
        output_base = Path("data/assets/cropped_products")
        console.print(f"\n📁 Output directory: [cyan]{output_base}[/cyan]\n")

        # Get available products
        products = self.list_available_products()

        # Group by product type
        product_types = list(set(p["type"] for p in products))
        product_types.sort()

        console.print(f"📦 Available products: [cyan]{len(product_types)}[/cyan]", style="green")
        for i, ptype in enumerate(product_types, 1):
            console.print(f"  {i}. {ptype}")

        console.print()

        # Process each product interactively
        for product_type in product_types:
            console.print(f"\n{'='*60}")
            console.print(f"📦 PRODUCT: [cyan bold]{product_type.upper()}[/cyan bold]")
            console.print(f"{'='*60}\n")

            # Show product info
            product_info = [p for p in products if p["type"] == product_type][0]
            console.print(f"  Size: [yellow]{product_info['width']}x{product_info['height']}px[/yellow]")
            console.print(f"  Size: [yellow]{product_info['width_inches']:.1f}x{product_info['height_inches']:.1f} inches[/yellow]")
            console.print()

            # Ask to proceed
            proceed = Confirm.ask(
                f"🔧 Crop {len(image_paths)} images for {product_type}?",
                default=True
            )

            if not proceed:
                console.print(f"⏭️  Skipped {product_type}\n", style="yellow")
                continue

            # Crop images
            try:
                output_paths = self.crop_images_for_product(
                    image_paths=image_paths,
                    product_type=product_type,
                    output_dir=output_base,
                )

                # Show results
                self.show_cropped_files(output_paths)

                # Ask for verification
                console.print()
                verified = Confirm.ask(
                    "✅ Are the cropped images OK?",
                    default=True
                )

                if verified:
                    console.print(f"✓ {product_type} verified!\n", style="green")
                else:
                    console.print(f"⚠️  {product_type} needs review\n", style="yellow")

                # Ask to continue to next product
                if product_type != product_types[-1]:  # Not last product
                    continue_next = Confirm.ask(
                        "➡️  Continue to next product?",
                        default=True
                    )
                    if not continue_next:
                        console.print("\n⏸️  Workflow paused", style="yellow")
                        break

            except Exception as e:
                console.print(f"\n❌ Error processing {product_type}: {e}", style="red")
                logger.exception(f"Error processing {product_type}")

                retry = Confirm.ask("🔄 Retry this product?", default=False)
                if not retry:
                    continue

        console.print("\n" + "="*60)
        console.print("✨ [WORKFLOW COMPLETE]", style="bold green")
        console.print("="*60)
        console.print(f"\n📁 All cropped images saved to: [cyan]{output_base}[/cyan]")
        console.print("\n💡 Next steps:")
        console.print("  1. Review cropped images manually")
        console.print("  2. Upload to Printify (or use for other purposes)")
        console.print("  3. Create products on Printify")
        console.print()


def run_crop_workflow(images_dir: str):
    """Run interactive crop workflow.

    Args:
        images_dir: Directory containing source images
    """
    workflow = ProductCropWorkflow()
    workflow.run_interactive(Path(images_dir))

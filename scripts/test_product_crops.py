"""Test script for verifying product crops across all variants.

This script takes a single test image and generates crops for ALL product families
and ALL their size variants, allowing visual verification before enabling AI generation.

Usage:
    python scripts/test_product_crops.py <path_to_test_image>

Example:
    python scripts/test_product_crops.py test_images/cat.jpg
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PIL import Image
from loguru import logger

from artomate.core.config import get_config
from artomate.workers.render_engine import RenderEngine
from artomate.workers.printify_product_families import (
    PRODUCT_FAMILIES,
    get_all_family_ids,
    get_all_variants_summary,
)


class ProductCropTester:
    """Test product crops for all families and variants."""

    def __init__(self, test_image_path: Path):
        """Initialize tester.

        Args:
            test_image_path: Path to test image
        """
        self.test_image_path = Path(test_image_path)
        if not self.test_image_path.exists():
            raise FileNotFoundError(f"Test image not found: {test_image_path}")

        self.config = get_config()
        self.renderer = RenderEngine()

        # Create output directory
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.output_dir = Path("test_output") / f"crop_test_{timestamp}"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Test output directory: {self.output_dir}")

    def test_all_families(self) -> Dict[str, Any]:
        """Test all product families and their variants.

        Returns:
            Dict with test results
        """
        logger.info("=" * 80)
        logger.info("STARTING PRODUCT CROP TEST")
        logger.info("=" * 80)

        logger.info(f"Test image: {self.test_image_path}")
        logger.info(f"Output directory: {self.output_dir}")

        # Get summary
        summary = get_all_variants_summary()
        logger.info(f"\nTotal families: {summary['total_families']}")
        logger.info(f"Total variants: {summary['total_variants']}")

        results = {
            "test_image": str(self.test_image_path),
            "output_dir": str(self.output_dir),
            "timestamp": datetime.utcnow().isoformat(),
            "families_tested": [],
            "total_crops_generated": 0,
            "errors": [],
        }

        # Test each family
        all_family_ids = get_all_family_ids()

        for i, family_id in enumerate(all_family_ids, 1):
            logger.info(f"\n[{i}/{len(all_family_ids)}] Testing family: {family_id}")

            try:
                family_result = self.test_family(family_id)
                results["families_tested"].append(family_result)
                results["total_crops_generated"] += family_result["crops_generated"]

                logger.info(
                    f"  ✓ {family_result['name']}: "
                    f"{family_result['crops_generated']} crops generated"
                )

            except Exception as e:
                error_msg = f"Failed to test {family_id}: {e}"
                logger.error(f"  ✗ {error_msg}")
                results["errors"].append(error_msg)

        # Create summary
        logger.info("\n" + "=" * 80)
        logger.info("TEST COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Families tested: {len(results['families_tested'])}")
        logger.info(f"Total crops generated: {results['total_crops_generated']}")
        logger.info(f"Errors: {len(results['errors'])}")
        logger.info(f"\nOutput directory: {self.output_dir}")

        return results

    def test_family(self, family_id: str) -> Dict[str, Any]:
        """Test a single product family.

        Args:
            family_id: Product family ID

        Returns:
            Dict with family test results
        """
        family = PRODUCT_FAMILIES[family_id]

        result = {
            "family_id": family_id,
            "name": family["name"],
            "category": family["category"],
            "coverage_type": family["coverage_type"],
            "variant_count": len(family["variants"]),
            "crops_generated": 0,
            "variants_tested": [],
        }

        # Create family directory
        family_dir = self.output_dir / family["category"] / family_id
        family_dir.mkdir(parents=True, exist_ok=True)

        # Determine rendering settings
        needs_transparent = family["coverage_type"] == "transparent"

        if family["coverage_type"] == "full":
            crop_mode = "cover"
        elif family["coverage_type"] == "centered":
            crop_mode = "contain"
        else:  # transparent
            crop_mode = "contain"

        # Test each variant
        for variant in family["variants"]:
            variant_result = self.test_variant(
                variant=variant,
                family_dir=family_dir,
                crop_mode=crop_mode,
                dpi=family["dpi"],
                needs_transparent=needs_transparent,
            )

            result["variants_tested"].append(variant_result)
            result["crops_generated"] += 1

        return result

    def test_variant(
        self,
        variant: dict,
        family_dir: Path,
        crop_mode: str,
        dpi: int,
        needs_transparent: bool,
    ) -> Dict[str, Any]:
        """Test a single variant.

        Args:
            variant: Variant specification
            family_dir: Family output directory
            crop_mode: Crop mode to use
            dpi: DPI for rendering
            needs_transparent: Whether to use transparent background

        Returns:
            Dict with variant test results
        """
        # Render image
        rendered = self.renderer.render_image(
            source_path=self.test_image_path,
            target_width=variant["width"],
            target_height=variant["height"],
            mode=crop_mode,
            dpi=dpi,
            transparent_background=needs_transparent,
            remove_white_bg=needs_transparent,
        )

        # Save
        safe_name = variant["name"].replace("/", "_").replace(" ", "_")
        filename = f"{safe_name}_{variant['width']}x{variant['height']}.png"
        output_path = family_dir / filename

        rendered.save(output_path, format="PNG", dpi=(dpi, dpi), optimize=True)

        return {
            "variant_id": variant["variant_id"],
            "name": variant["name"],
            "width": variant["width"],
            "height": variant["height"],
            "file": str(output_path.relative_to(self.output_dir)),
            "file_size_kb": round(output_path.stat().st_size / 1024, 2),
        }

    def generate_html_report(self, results: Dict[str, Any]) -> Path:
        """Generate HTML report with image previews.

        Args:
            results: Test results dict

        Returns:
            Path to HTML report
        """
        html_path = self.output_dir / "index.html"

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Product Crop Test Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #333; margin-bottom: 10px; }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .stat {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #007bff;
        }}
        .stat-label {{ font-size: 14px; color: #666; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #333; margin-top: 5px; }}
        .family {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .family-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e9ecef;
        }}
        .family-name {{ font-size: 24px; font-weight: bold; color: #333; }}
        .family-meta {{
            display: flex;
            gap: 15px;
            font-size: 14px;
        }}
        .badge {{
            padding: 5px 10px;
            border-radius: 5px;
            font-weight: 500;
        }}
        .badge-transparent {{ background: #cfe2ff; color: #084298; }}
        .badge-full {{ background: #d1e7dd; color: #0f5132; }}
        .badge-centered {{ background: #f8d7da; color: #842029; }}
        .variants {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
        }}
        .variant {{
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 15px;
            transition: all 0.3s ease;
        }}
        .variant:hover {{
            border-color: #007bff;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .variant-image {{
            width: 100%;
            height: 200px;
            object-fit: contain;
            background: #f8f9fa;
            border-radius: 5px;
            margin-bottom: 10px;
        }}
        .variant-name {{
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }}
        .variant-details {{
            font-size: 13px;
            color: #666;
        }}
        .variant-details div {{ margin: 3px 0; }}
        .category-badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: 500;
            margin-bottom: 5px;
        }}
        .cat-apparel {{ background: #ffc107; color: #000; }}
        .cat-home_living {{ background: #28a745; color: white; }}
        .cat-wall_art {{ background: #dc3545; color: white; }}
        .cat-drinkware {{ background: #17a2b8; color: white; }}
        .cat-accessories {{ background: #6f42c1; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 Product Crop Test Report</h1>
            <p>Generated: {results['timestamp']}</p>
            <p>Test image: <code>{results['test_image']}</code></p>

            <div class="summary">
                <div class="stat">
                    <div class="stat-label">Families Tested</div>
                    <div class="stat-value">{len(results['families_tested'])}</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Total Crops</div>
                    <div class="stat-value">{results['total_crops_generated']}</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Errors</div>
                    <div class="stat-value">{len(results['errors'])}</div>
                </div>
            </div>
        </div>
"""

        # Add each family
        for family_result in results["families_tested"]:
            coverage_class = f"badge-{family_result['coverage_type']}"
            cat_class = f"cat-{family_result['category']}"

            html += f"""
        <div class="family">
            <div class="family-header">
                <div>
                    <div class="family-name">{family_result['name']}</div>
                    <span class="category-badge {cat_class}">{family_result['category']}</span>
                </div>
                <div class="family-meta">
                    <span class="badge {coverage_class}">{family_result['coverage_type']}</span>
                    <span class="badge">{family_result['variant_count']} variants</span>
                </div>
            </div>
            <div class="variants">
"""

            for variant in family_result["variants_tested"]:
                html += f"""
                <div class="variant">
                    <img src="{variant['file']}" alt="{variant['name']}" class="variant-image">
                    <div class="variant-name">{variant['name']}</div>
                    <div class="variant-details">
                        <div>📐 {variant['width']} × {variant['height']} px</div>
                        <div>💾 {variant['file_size_kb']} KB</div>
                        <div>📄 {variant['file']}</div>
                    </div>
                </div>
"""

            html += """
            </div>
        </div>
"""

        html += """
    </div>
</body>
</html>
"""

        html_path.write_text(html)
        logger.info(f"✓ Generated HTML report: {html_path}")

        return html_path


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_product_crops.py <path_to_test_image>")
        print("\nExample:")
        print("  python scripts/test_product_crops.py test_images/cat.jpg")
        sys.exit(1)

    test_image_path = Path(sys.argv[1])

    # Create tester
    tester = ProductCropTester(test_image_path)

    # Run tests
    print("\n🎨 Starting product crop test...")
    print(f"📸 Test image: {test_image_path}")
    print(f"📁 Output: {tester.output_dir}\n")

    results = tester.test_all_families()

    # Generate HTML report
    print("\n📊 Generating HTML report...")
    html_path = tester.generate_html_report(results)

    print("\n" + "=" * 80)
    print("✅ TEST COMPLETE!")
    print("=" * 80)
    print(f"📁 Output directory: {tester.output_dir}")
    print(f"📄 HTML report: {html_path}")
    print("\nOpen the HTML report in your browser to review all crops!")
    print(f"\n  file://{html_path.absolute()}")
    print("\n")


if __name__ == "__main__":
    main()

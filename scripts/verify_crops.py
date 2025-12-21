"""Verify crop quality and coverage types.

Checks that:
- Transparent backgrounds have alpha channel
- Full coverage crops are RGB
- Dimensions match specifications
"""

import sys
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent))

from PIL import Image
from loguru import logger

from artomate.workers.printify_product_families import (
    PRODUCT_FAMILIES,
    get_all_family_ids,
)


class CropVerifier:
    """Verify generated crops."""

    def __init__(self, test_output_dir: Path):
        """Initialize verifier.

        Args:
            test_output_dir: Path to test output directory
        """
        self.test_output_dir = Path(test_output_dir)
        if not self.test_output_dir.exists():
            raise FileNotFoundError(f"Test output not found: {test_output_dir}")

    def verify_all(self) -> Dict[str, any]:
        """Verify all crops.

        Returns:
            Dict with verification results
        """
        logger.info("=" * 80)
        logger.info("VERIFYING CROP QUALITY")
        logger.info("=" * 80)

        results = {
            "families_verified": 0,
            "crops_verified": 0,
            "errors": [],
            "warnings": [],
        }

        all_family_ids = get_all_family_ids()

        for family_id in all_family_ids:
            family = PRODUCT_FAMILIES[family_id]
            family_dir = (
                self.test_output_dir / family["category"] / family_id
            )

            if not family_dir.exists():
                results["errors"].append(
                    f"Missing family directory: {family_id}"
                )
                continue

            logger.info(f"\nVerifying: {family['name']} ({family_id})")

            # Check each variant
            for variant in family["variants"]:
                try:
                    self.verify_variant(family, variant, family_dir, results)
                    results["crops_verified"] += 1
                except Exception as e:
                    error_msg = f"{family_id}/{variant['name']}: {e}"
                    results["errors"].append(error_msg)
                    logger.error(f"  ✗ {error_msg}")

            results["families_verified"] += 1

        # Print summary
        logger.info("\n" + "=" * 80)
        logger.info("VERIFICATION COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Families verified: {results['families_verified']}")
        logger.info(f"Crops verified: {results['crops_verified']}")
        logger.info(f"Errors: {len(results['errors'])}")
        logger.info(f"Warnings: {len(results['warnings'])}")

        if results["errors"]:
            logger.error("\nErrors found:")
            for error in results["errors"]:
                logger.error(f"  - {error}")

        if results["warnings"]:
            logger.warning("\nWarnings:")
            for warning in results["warnings"]:
                logger.warning(f"  - {warning}")

        return results

    def verify_variant(
        self,
        family: dict,
        variant: dict,
        family_dir: Path,
        results: dict,
    ) -> None:
        """Verify a single variant.

        Args:
            family: Product family
            variant: Variant specification
            family_dir: Family directory
            results: Results dict to update
        """
        # Find crop file
        safe_name = variant["name"].replace("/", "_").replace(" ", "_")
        filename = f"{safe_name}_{variant['width']}x{variant['height']}.png"
        crop_path = family_dir / filename

        if not crop_path.exists():
            raise FileNotFoundError(f"Crop file not found: {filename}")

        # Load image
        img = Image.open(crop_path)

        # Verify dimensions
        if img.width != variant["width"] or img.height != variant["height"]:
            raise ValueError(
                f"Dimension mismatch: expected {variant['width']}x{variant['height']}, "
                f"got {img.width}x{img.height}"
            )

        # Verify mode based on coverage type
        needs_transparent = family["coverage_type"] == "transparent"

        if needs_transparent:
            if img.mode != "RGBA":
                raise ValueError(
                    f"Expected RGBA for transparent coverage, got {img.mode}"
                )

            # Check if alpha channel is used
            alpha = img.split()[-1]
            alpha_min = alpha.getextrema()[0]
            if alpha_min == 255:
                results["warnings"].append(
                    f"{family['family_id']}/{variant['name']}: "
                    f"Alpha channel present but not used (all opaque)"
                )

            logger.debug(
                f"  ✓ {variant['name']}: {img.width}x{img.height} RGBA"
            )
        else:
            if img.mode not in ["RGB", "RGBA"]:
                raise ValueError(
                    f"Expected RGB for full coverage, got {img.mode}"
                )

            logger.debug(
                f"  ✓ {variant['name']}: {img.width}x{img.height} {img.mode}"
            )

        img.close()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/verify_crops.py <test_output_dir>")
        print("\nExample:")
        print(
            "  python scripts/verify_crops.py test_output/crop_test_20251221_044749"
        )
        sys.exit(1)

    test_output_dir = Path(sys.argv[1])

    # Create verifier
    verifier = CropVerifier(test_output_dir)

    # Run verification
    results = verifier.verify_all()

    # Exit with error if issues found
    if results["errors"]:
        print("\n❌ VERIFICATION FAILED")
        sys.exit(1)
    else:
        print("\n✅ VERIFICATION PASSED")
        if results["warnings"]:
            print(f"   ({len(results['warnings'])} warnings)")
        sys.exit(0)


if __name__ == "__main__":
    main()

"""Batch processor for cropping multiple images for all product variants."""

from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from loguru import logger
from PIL import Image

from artomate.core.config import Config, get_config
from artomate.workers.render_engine import RenderEngine
from artomate.workers.printify_product_families import (
    PRODUCT_FAMILIES,
    ProductFamily,
    get_all_family_ids,
)


class BatchCropProcessor:
    """Process multiple images and crop for all product variants."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize batch crop processor.

        Args:
            config: Application configuration
        """
        self.config = config or get_config()
        self.renderer = RenderEngine(config=config)

    def process_calendar_images(
        self,
        image_paths: List[Path],
        output_dir: Path,
        product_families: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Process calendar images and create crops for all products.

        Args:
            image_paths: List of image paths (12 for calendar)
            output_dir: Output directory for crops
            product_families: List of family IDs to process (None = all)

        Returns:
            Dict with processing results
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("=" * 80)
        logger.info("BATCH CROP PROCESSING")
        logger.info("=" * 80)
        logger.info(f"Images to process: {len(image_paths)}")
        logger.info(f"Output directory: {output_dir}")

        # Determine which families to process
        if product_families is None:
            family_ids = get_all_family_ids()
        else:
            family_ids = product_families

        logger.info(f"Product families: {len(family_ids)}")

        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "images_processed": 0,
            "total_crops": 0,
            "families_used": len(family_ids),
            "images": [],
            "errors": [],
        }

        # Process each image
        for idx, image_path in enumerate(image_paths, 1):
            image_path = Path(image_path)

            if not image_path.exists():
                error_msg = f"Image not found: {image_path}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
                continue

            logger.info(f"\n[{idx}/{len(image_paths)}] Processing: {image_path.name}")

            try:
                image_result = self.process_single_image(
                    image_path=image_path,
                    output_dir=output_dir,
                    family_ids=family_ids,
                )

                results["images"].append(image_result)
                results["images_processed"] += 1
                results["total_crops"] += image_result["crops_generated"]

                logger.info(
                    f"  ✓ Generated {image_result['crops_generated']} crops "
                    f"across {image_result['families_processed']} families"
                )

            except Exception as e:
                error_msg = f"Failed to process {image_path.name}: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)

        # Save results
        results_file = output_dir / "batch_results.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        logger.info("\n" + "=" * 80)
        logger.info("BATCH PROCESSING COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Images processed: {results['images_processed']}/{len(image_paths)}")
        logger.info(f"Total crops generated: {results['total_crops']}")
        logger.info(f"Errors: {len(results['errors'])}")
        logger.info(f"Results saved to: {results_file}")

        return results

    def process_single_image(
        self,
        image_path: Path,
        output_dir: Path,
        family_ids: List[str],
    ) -> Dict[str, Any]:
        """Process a single image for all product families.

        Args:
            image_path: Path to source image
            output_dir: Output directory
            family_ids: List of family IDs to process

        Returns:
            Dict with processing results for this image
        """
        image_path = Path(image_path)
        image_name = image_path.stem

        # Create subdirectory for this image
        image_output_dir = output_dir / image_name
        image_output_dir.mkdir(parents=True, exist_ok=True)

        result = {
            "image_name": image_name,
            "source_path": str(image_path),
            "output_dir": str(image_output_dir),
            "families_processed": 0,
            "crops_generated": 0,
            "families": [],
        }

        # Process each family
        for family_id in family_ids:
            if family_id not in PRODUCT_FAMILIES:
                logger.warning(f"  Unknown family: {family_id}")
                continue

            family = PRODUCT_FAMILIES[family_id]

            try:
                family_result = self.crop_for_family(
                    image_path=image_path,
                    output_dir=image_output_dir,
                    family=family,
                )

                result["families"].append(family_result)
                result["families_processed"] += 1
                result["crops_generated"] += family_result["variants_processed"]

            except Exception as e:
                logger.error(f"  Failed to process family {family_id}: {e}")

        return result

    def crop_for_family(
        self,
        image_path: Path,
        output_dir: Path,
        family: ProductFamily,
    ) -> Dict[str, Any]:
        """Create crops for all variants in a product family.

        Args:
            image_path: Source image path
            output_dir: Output directory
            family: Product family specification

        Returns:
            Dict with results for this family
        """
        family_id = family["family_id"]
        coverage_type = family["coverage_type"]

        # Create family subdirectory
        family_dir = output_dir / family_id
        family_dir.mkdir(parents=True, exist_ok=True)

        result = {
            "family_id": family_id,
            "family_name": family["name"],
            "coverage_type": coverage_type,
            "variants_processed": 0,
            "variants": [],
        }

        # Process each variant
        for variant in family["variants"]:
            variant_id = variant["variant_id"]
            width = variant["width"]
            height = variant["height"]

            # Determine rendering parameters
            transparent = coverage_type == "transparent"
            mode = "cover"  # Fill entire area

            try:
                # Render the crop
                rendered_img = self.renderer.render_image(
                    source_path=image_path,
                    target_width=width,
                    target_height=height,
                    mode=mode,
                    dpi=family["dpi"],
                    transparent_background=transparent,
                )

                # Save the crop
                filename = f"{variant_id}_{width}x{height}.png"
                output_path = family_dir / filename
                rendered_img.save(output_path, format="PNG", dpi=(family["dpi"], family["dpi"]))

                result["variants"].append({
                    "variant_id": variant_id,
                    "width": width,
                    "height": height,
                    "filename": filename,
                    "path": str(output_path),
                })

                result["variants_processed"] += 1

            except Exception as e:
                logger.error(f"    Failed to crop {variant_id}: {e}")

        return result

    def get_processing_summary(
        self,
        product_families: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get summary of what would be processed.

        Args:
            product_families: List of family IDs (None = all)

        Returns:
            Dict with summary information
        """
        if product_families is None:
            family_ids = get_all_family_ids()
        else:
            family_ids = product_families

        total_variants = 0
        families_info = []

        for family_id in family_ids:
            if family_id not in PRODUCT_FAMILIES:
                continue

            family = PRODUCT_FAMILIES[family_id]
            variant_count = len(family["variants"])
            total_variants += variant_count

            families_info.append({
                "family_id": family_id,
                "name": family["name"],
                "category": family["category"],
                "coverage_type": family["coverage_type"],
                "variants": variant_count,
            })

        return {
            "total_families": len(family_ids),
            "total_variants": total_variants,
            "families": families_info,
        }

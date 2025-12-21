"""Batch generate products from a list of prompts.

Usage:
    python scripts/batch_generate_products.py prompts.csv --delay 60
"""

import argparse
import csv
import sys
import time
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from generate_product_from_ai import ProductGenerator


def load_prompts_from_csv(csv_path: Path) -> List[Dict[str, str]]:
    """Load prompts from CSV file.

    CSV format:
        prompt,animal,families
        "cute red panda astronaut","red panda","tshirt,poster,mug"
        "majestic lion king","lion",""

    Args:
        csv_path: Path to CSV file

    Returns:
        List of prompt dicts
    """
    prompts = []

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            prompt_data = {
                "prompt": row["prompt"],
                "animal": row["animal"],
                "families": (
                    row.get("families", "").split(",")
                    if row.get("families")
                    else None
                ),
            }
            prompts.append(prompt_data)

    return prompts


def batch_generate(
    prompts: List[Dict[str, str]],
    delay: int = 60,
    dry_run: bool = False,
    upload_to_printify: bool = True,
    publish_to_etsy: bool = True,
    create_social_content: bool = True,
) -> Dict[str, any]:
    """Batch generate products.

    Args:
        prompts: List of prompt dicts
        delay: Delay between generations (seconds)
        dry_run: Don't actually upload/publish
        upload_to_printify: Upload to Printify
        publish_to_etsy: Publish to Etsy
        create_social_content: Create social media content

    Returns:
        Dict with batch results
    """
    logger.info("=" * 80)
    logger.info("BATCH PRODUCT GENERATION")
    logger.info("=" * 80)
    logger.info(f"Total prompts: {len(prompts)}")
    logger.info(f"Delay between generations: {delay}s")
    logger.info(f"Dry run: {dry_run}")

    results = {
        "total": len(prompts),
        "completed": 0,
        "failed": 0,
        "generations": [],
    }

    generator = ProductGenerator(dry_run=dry_run)

    for i, prompt_data in enumerate(prompts, 1):
        logger.info("\n" + "=" * 80)
        logger.info(f"GENERATION {i}/{len(prompts)}")
        logger.info("=" * 80)

        try:
            # Generate product line
            generation_result = generator.generate_full_product_line(
                prompt=prompt_data["prompt"],
                animal_name=prompt_data["animal"],
                family_ids=prompt_data.get("families"),
                upload_to_printify=upload_to_printify,
                publish_to_etsy=publish_to_etsy,
                create_social_content=create_social_content,
            )

            results["completed"] += 1
            results["generations"].append({
                "index": i,
                "prompt": prompt_data["prompt"],
                "animal": prompt_data["animal"],
                "status": "completed",
                "products": len(generation_result["products_created"]),
                "errors": generation_result["errors"],
            })

            logger.info(f"✅ Generation {i} completed")

        except Exception as e:
            logger.error(f"❌ Generation {i} failed: {e}")
            results["failed"] += 1
            results["generations"].append({
                "index": i,
                "prompt": prompt_data["prompt"],
                "animal": prompt_data["animal"],
                "status": "failed",
                "error": str(e),
            })

        # Delay before next generation (except for last one)
        if i < len(prompts):
            logger.info(f"Waiting {delay}s before next generation...")
            time.sleep(delay)

    # Print summary
    logger.info("\n" + "=" * 80)
    logger.info("BATCH GENERATION COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Total: {results['total']}")
    logger.info(f"Completed: {results['completed']}")
    logger.info(f"Failed: {results['failed']}")

    return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Batch generate products from CSV"
    )
    parser.add_argument(
        "csv_file",
        type=Path,
        help="CSV file with prompts (columns: prompt, animal, families)",
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=60,
        help="Delay between generations in seconds (default: 60)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't actually upload/publish",
    )
    parser.add_argument(
        "--no-printify",
        action="store_true",
        help="Skip Printify upload",
    )
    parser.add_argument(
        "--no-etsy",
        action="store_true",
        help="Skip Etsy publishing",
    )
    parser.add_argument(
        "--no-social",
        action="store_true",
        help="Skip social media content",
    )

    args = parser.parse_args()

    # Check CSV exists
    if not args.csv_file.exists():
        print(f"❌ CSV file not found: {args.csv_file}")
        sys.exit(1)

    # Load prompts
    try:
        prompts = load_prompts_from_csv(args.csv_file)
        logger.info(f"Loaded {len(prompts)} prompts from {args.csv_file}")
    except Exception as e:
        print(f"❌ Failed to load prompts: {e}")
        sys.exit(1)

    # Run batch generation
    try:
        results = batch_generate(
            prompts=prompts,
            delay=args.delay,
            dry_run=args.dry_run,
            upload_to_printify=not args.no_printify,
            publish_to_etsy=not args.no_etsy,
            create_social_content=not args.no_social,
        )

        # Print summary
        print("\n" + "=" * 80)
        print("📊 BATCH SUMMARY")
        print("=" * 80)
        print(f"Total: {results['total']}")
        print(f"Completed: {results['completed']}")
        print(f"Failed: {results['failed']}")

        if results["failed"] > 0:
            print("\n❌ Some generations failed:")
            for gen in results["generations"]:
                if gen["status"] == "failed":
                    print(f"  - {gen['prompt']}: {gen['error']}")
            sys.exit(1)
        else:
            print("\n✅ ALL GENERATIONS SUCCESSFUL!")
            sys.exit(0)

    except Exception as e:
        print(f"\n❌ BATCH GENERATION FAILED: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

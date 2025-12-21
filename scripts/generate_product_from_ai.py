"""Generate complete product line from AI-generated image.

This script:
1. Generates AI image with DALL-E
2. Creates crops for ALL product families and variants
3. Uploads to Printify
4. Publishes to Etsy
5. Creates viral social media content

Usage:
    python scripts/generate_product_from_ai.py --prompt "cute red panda astronaut" --animal "red panda"
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

from artomate.core.config import get_config
from artomate.db.database import Database
from artomate.db.models import Job, Asset, Product, JobState, AssetType
from artomate.workers.image_generator import ImageGenerator
from artomate.workers.render_engine import RenderEngine
from artomate.workers.printify_worker import PrintifyWorker
from artomate.workers.printify_product_families import get_all_family_ids, PRODUCT_FAMILIES
from artomate.workers.ai_facts_generator import AIFactsGenerator
from artomate.workers.enhanced_video_renderer import EnhancedVideoRenderer


class ProductGenerator:
    """Generate complete product line from AI image."""

    def __init__(
        self,
        config: Optional[object] = None,
        dry_run: bool = False,
    ):
        """Initialize generator.

        Args:
            config: Configuration object
            dry_run: If True, don't actually upload/publish
        """
        self.config = config or get_config()
        self.dry_run = dry_run

        self.ai_generator = ImageGenerator(config)
        self.renderer = RenderEngine()
        self.printify = PrintifyWorker(config)
        self.facts_generator = AIFactsGenerator(config)
        self.video_renderer = EnhancedVideoRenderer(config)

        logger.info(f"Product Generator initialized (dry_run={dry_run})")

    def generate_full_product_line(
        self,
        prompt: str,
        animal_name: str,
        family_ids: Optional[List[str]] = None,
        upload_to_printify: bool = True,
        publish_to_etsy: bool = True,
        create_social_content: bool = True,
    ) -> dict:
        """Generate complete product line.

        Args:
            prompt: DALL-E prompt
            animal_name: Animal name for facts
            family_ids: Product families to create (default: all)
            upload_to_printify: Upload to Printify
            publish_to_etsy: Publish to Etsy
            create_social_content: Create social media content

        Returns:
            Dict with results
        """
        logger.info("=" * 80)
        logger.info("GENERATING FULL PRODUCT LINE")
        logger.info("=" * 80)
        logger.info(f"Prompt: {prompt}")
        logger.info(f"Animal: {animal_name}")
        logger.info(f"Dry run: {self.dry_run}")

        results = {
            "prompt": prompt,
            "animal": animal_name,
            "timestamp": datetime.utcnow().isoformat(),
            "ai_image": None,
            "products_created": [],
            "social_content": [],
            "errors": [],
        }

        # Create job in database
        db = Database()
        with db.session_scope() as session:
            job = Job(
                theme=animal_name,
                input_source="manual",
                input_data={"prompt": prompt, "animal": animal_name},
                state=JobState.GENERATING,
            )
            session.add(job)
            session.commit()
            job_id = job.id

            logger.info(f"Created job: {job_id}")

            try:
                # Step 1: Generate AI image
                logger.info("\n" + "=" * 80)
                logger.info("STEP 1: Generating AI Image")
                logger.info("=" * 80)

                # Generate with DALL-E
                image_data_list = self.ai_generator.generate_with_dalle(
                    prompt=prompt,
                    size="1024x1024",
                    quality="hd",
                )

                image_data = image_data_list[0]

                # Download image
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                filename = f"ai_{timestamp}.png"
                image_dir = Path("data/ai_images")
                image_dir.mkdir(parents=True, exist_ok=True)
                image_path = image_dir / filename

                download_result = self.ai_generator.download_image(
                    url=image_data["url"],
                    save_path=image_path,
                )

                # Create asset in database
                ai_image = Asset(
                    job_id=job.id,
                    asset_type=AssetType.HERO,
                    storage_path=str(image_path),
                    generator="dall-e-3",
                )
                session.add(ai_image)
                session.commit()

                logger.info(f"✓ AI image generated: {ai_image.storage_path}")
                results["ai_image"] = str(ai_image.storage_path)

                # Step 2: Create products for each family
                if family_ids is None:
                    family_ids = get_all_family_ids()

                logger.info("\n" + "=" * 80)
                logger.info(f"STEP 2: Creating Products ({len(family_ids)} families)")
                logger.info("=" * 80)

                for i, family_id in enumerate(family_ids, 1):
                    family = PRODUCT_FAMILIES[family_id]
                    logger.info(
                        f"\n[{i}/{len(family_ids)}] Creating: {family['name']} ({family_id})"
                    )

                    try:
                        if self.dry_run:
                            logger.info("  [DRY RUN] Skipping actual creation")
                            results["products_created"].append({
                                "family_id": family_id,
                                "name": family["name"],
                                "status": "dry_run",
                            })
                        elif upload_to_printify:
                            product = self.printify.create_product_family(
                                job=job,
                                asset=ai_image,
                                family_id=family_id,
                                create_all_variants=True,
                            )

                            logger.info(f"  ✓ Created product: {product.printify_id}")

                            results["products_created"].append({
                                "family_id": family_id,
                                "name": family["name"],
                                "printify_id": product.printify_id,
                                "variants": len(family["variants"]),
                            })

                            # Publish to Etsy if requested
                            if publish_to_etsy and not self.dry_run:
                                # TODO: Implement Etsy publishing
                                logger.info("  [TODO] Publish to Etsy")

                        else:
                            logger.info("  [SKIP] Upload disabled")

                    except Exception as e:
                        error_msg = f"Failed to create {family_id}: {e}"
                        logger.error(f"  ✗ {error_msg}")
                        results["errors"].append(error_msg)

                # Step 3: Generate AI facts
                if create_social_content:
                    logger.info("\n" + "=" * 80)
                    logger.info("STEP 3: Generating AI Facts & Social Content")
                    logger.info("=" * 80)

                    try:
                        facts = self.facts_generator.generate_animal_facts(
                            animal=animal_name,
                            count=5,
                            style="viral",
                        )

                        logger.info(f"✓ Generated {len(facts)} facts")

                        # Create viral videos
                        for platform in ["tiktok", "instagram_reel", "youtube_short"]:
                            if self.dry_run:
                                logger.info(f"  [DRY RUN] Skip {platform} video")
                                results["social_content"].append({
                                    "platform": platform,
                                    "status": "dry_run",
                                })
                            else:
                                try:
                                    video = self.video_renderer.create_viral_video(
                                        job=job,
                                        asset=ai_image,
                                        video_format=platform,
                                        style="ken_burns",
                                        add_facts=True,
                                        add_music=False,  # Skip music for now
                                        add_hook=True,
                                    )

                                    logger.info(f"  ✓ Created {platform} video: {video.file_path}")

                                    results["social_content"].append({
                                        "platform": platform,
                                        "file": str(video.file_path),
                                    })

                                except Exception as e:
                                    error_msg = f"Failed to create {platform} video: {e}"
                                    logger.error(f"  ✗ {error_msg}")
                                    results["errors"].append(error_msg)

                    except Exception as e:
                        error_msg = f"Failed to generate social content: {e}"
                        logger.error(f"✗ {error_msg}")
                        results["errors"].append(error_msg)

                # Update job state
                job.state = JobState.DONE
                session.commit()

                logger.info("\n" + "=" * 80)
                logger.info("✅ PRODUCT LINE GENERATION COMPLETE")
                logger.info("=" * 80)
                logger.info(f"Products created: {len(results['products_created'])}")
                logger.info(f"Social content: {len(results['social_content'])}")
                logger.info(f"Errors: {len(results['errors'])}")

            except Exception as e:
                logger.error(f"❌ Generation failed: {e}")
                job.state = JobState.FAILED
                session.commit()
                results["errors"].append(str(e))
                raise

        return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate complete product line from AI image"
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="DALL-E prompt (e.g., 'cute red panda astronaut')",
    )
    parser.add_argument(
        "--animal",
        required=True,
        help="Animal name for facts (e.g., 'red panda')",
    )
    parser.add_argument(
        "--families",
        nargs="+",
        help="Product families to create (default: all)",
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

    # Create generator
    generator = ProductGenerator(dry_run=args.dry_run)

    # Run generation
    try:
        results = generator.generate_full_product_line(
            prompt=args.prompt,
            animal_name=args.animal,
            family_ids=args.families,
            upload_to_printify=not args.no_printify,
            publish_to_etsy=not args.no_etsy,
            create_social_content=not args.no_social,
        )

        # Print summary
        print("\n" + "=" * 80)
        print("📊 GENERATION SUMMARY")
        print("=" * 80)
        print(f"AI Image: {results['ai_image']}")
        print(f"Products: {len(results['products_created'])}")
        for product in results["products_created"]:
            print(f"  - {product['name']}: {product.get('printify_id', 'N/A')}")
        print(f"Social Content: {len(results['social_content'])}")
        for content in results["social_content"]:
            print(f"  - {content['platform']}: {content.get('file', 'N/A')}")

        if results["errors"]:
            print(f"\n⚠️  Errors: {len(results['errors'])}")
            for error in results["errors"]:
                print(f"  - {error}")
            sys.exit(1)
        else:
            print("\n✅ SUCCESS!")
            sys.exit(0)

    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

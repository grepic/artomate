"""Simple test of the product generation workflow structure."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

from artomate.core.config import get_config
from artomate.db.database import Database
from artomate.db.models import Job, JobState
from artomate.workers.printify_product_families import (
    get_all_family_ids,
    PRODUCT_FAMILIES,
)


def test_workflow():
    """Test workflow structure."""
    logger.info("=" * 80)
    logger.info("TESTING WORKFLOW STRUCTURE")
    logger.info("=" * 80)

    # Test 1: Database connection
    logger.info("\n[1/5] Testing database connection...")
    try:
        db = Database()
        db.create_tables()
        logger.info("✓ Database connection OK")
    except Exception as e:
        logger.error(f"✗ Database error: {e}")
        return False

    # Test 2: Create job
    logger.info("\n[2/5] Testing job creation...")
    try:
        with db.session_scope() as session:
            job = Job(
                theme="test theme",
                input_source="manual",
                input_data={"prompt": "test prompt", "animal": "test animal"},
                state=JobState.GENERATING,
            )
            session.add(job)
            session.commit()
            job_id = job.id
            logger.info(f"✓ Created job: {job_id}")
    except Exception as e:
        logger.error(f"✗ Job creation error: {e}")
        return False

    # Test 3: Load product families
    logger.info("\n[3/5] Testing product families...")
    try:
        family_ids = get_all_family_ids()
        logger.info(f"✓ Loaded {len(family_ids)} product families")

        # Show first 5
        for family_id in family_ids[:5]:
            family = PRODUCT_FAMILIES[family_id]
            logger.info(
                f"  - {family['name']} ({family_id}): "
                f"{len(family['variants'])} variants, "
                f"{family['coverage_type']} coverage"
            )

    except Exception as e:
        logger.error(f"✗ Product family error: {e}")
        return False

    # Test 4: Configuration
    logger.info("\n[4/5] Testing configuration...")
    try:
        config = get_config()
        logger.info(f"✓ Config loaded")
        logger.info(f"  - Database: {config.database_url[:50]}...")
        logger.info(f"  - OpenAI key: {'SET' if config.openai_api_key else 'NOT SET'}")
        logger.info(f"  - Printify token: {'SET' if config.printify_api_token else 'NOT SET'}")
    except Exception as e:
        logger.error(f"✗ Configuration error: {e}")
        return False

    # Test 5: Test image path
    logger.info("\n[5/5] Testing test image...")
    try:
        test_image = Path("test_images/test_image.png")
        if test_image.exists():
            logger.info(f"✓ Test image exists: {test_image}")
            from PIL import Image
            img = Image.open(test_image)
            logger.info(f"  - Size: {img.width}x{img.height}")
            logger.info(f"  - Mode: {img.mode}")
        else:
            logger.warning(f"⚠ Test image not found: {test_image}")
    except Exception as e:
        logger.error(f"✗ Test image error: {e}")
        return False

    logger.info("\n" + "=" * 80)
    logger.info("✅ ALL TESTS PASSED")
    logger.info("=" * 80)
    logger.info("\nWorkflow structure is ready!")
    logger.info("Next steps:")
    logger.info("  1. Set up OpenAI API key in .env")
    logger.info("  2. Set up Printify API key in .env")
    logger.info("  3. Run: python scripts/generate_product_from_ai.py --dry-run ...")

    return True


if __name__ == "__main__":
    success = test_workflow()
    sys.exit(0 if success else 1)

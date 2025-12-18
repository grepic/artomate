"""Stock platform integration (Shutterstock, Adobe Stock)."""

from pathlib import Path
from typing import Literal, Optional

from loguru import logger

from artomate.core.config import Config, get_config
from artomate.db.database import get_db
from artomate.db.models import Asset, Job


StockPlatform = Literal["shutterstock", "adobe_stock"]


class StockPlatformWorker:
    """Submits assets to stock platforms."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize stock platform worker.

        Args:
            config: Application configuration
        """
        self.config = config or get_config()
        self.db = get_db()

    def prepare_submission(
        self,
        asset: Asset,
        job: Job,
        platform: StockPlatform,
    ) -> dict:
        """Prepare asset for stock submission.

        Args:
            asset: Asset to submit
            job: Job instance
            platform: Target platform

        Returns:
            Submission data dict

        Raises:
            ValueError: If asset not suitable for stock
        """
        # Validate asset
        if not self._is_suitable_for_stock(asset):
            raise ValueError(f"Asset {asset.id} not suitable for stock platforms")

        # Generate metadata
        title = self._generate_stock_title(job, asset)
        description = self._generate_stock_description(job, asset)
        keywords = self._generate_stock_keywords(job, asset, platform)
        categories = self._suggest_categories(job, platform)

        # AI disclosure
        ai_disclosure = self._generate_ai_disclosure(asset)

        submission = {
            "asset_id": asset.id,
            "platform": platform,
            "title": title,
            "description": description,
            "keywords": keywords,
            "categories": categories,
            "ai_disclosure": ai_disclosure,
            "file_path": asset.storage_path,
            "file_size": asset.file_size_bytes,
            "dimensions": f"{asset.width}x{asset.height}",
        }

        logger.info(f"✓ Prepared {platform} submission for asset {asset.id}")

        return submission

    def _is_suitable_for_stock(self, asset: Asset) -> bool:
        """Check if asset is suitable for stock platforms.

        Args:
            asset: Asset to check

        Returns:
            True if suitable
        """
        # Stock platforms requirements:
        # - No trademarked content
        # - High quality
        # - Proper dimensions
        # - No people (or with model release)
        # - No copyrighted elements

        # Check compliance
        if not asset.compliance_checked:
            logger.warning(f"Asset {asset.id} not yet compliance-checked")
            return False

        if asset.compliance_status == "rejected":
            return False

        # Check dimensions (min 4MP for most stock sites)
        if asset.width and asset.height:
            megapixels = (asset.width * asset.height) / 1_000_000
            if megapixels < 4:
                logger.warning(f"Asset {asset.id} too small for stock ({megapixels:.1f}MP)")
                return False

        return True

    def _generate_stock_title(self, job: Job, asset: Asset) -> str:
        """Generate stock platform title.

        Args:
            job: Job instance
            asset: Asset

        Returns:
            Title (max 200 chars)
        """
        parts = []

        if job.theme:
            parts.append(job.theme.title())

        if job.style:
            parts.append(f"{job.style} Style")

        parts.append("Digital Art")

        if job.niche:
            niche_names = {
                "wall-art": "Wall Art",
                "home-decor": "Home Decoration",
                "apparel": "T-Shirt Design",
            }
            parts.append(niche_names.get(job.niche, job.niche.title()))

        title = " - ".join(parts)

        return title[:200]

    def _generate_stock_description(self, job: Job, asset: Asset) -> str:
        """Generate stock platform description.

        Args:
            job: Job instance
            asset: Asset

        Returns:
            Description
        """
        parts = [
            f"High-quality {job.theme} digital artwork in {job.style or 'modern'} style.",
            "",
            "Perfect for:",
            f"• {job.niche or 'Various applications'}",
            "• Print on demand",
            "• Web design",
            "• Marketing materials",
            "• Social media",
            "",
            f"Image dimensions: {asset.width}x{asset.height} pixels",
            "High resolution, print-ready quality.",
        ]

        return "\n".join(parts)

    def _generate_stock_keywords(
        self,
        job: Job,
        asset: Asset,
        platform: StockPlatform,
    ) -> list[str]:
        """Generate keywords for stock platform.

        Args:
            job: Job instance
            asset: Asset
            platform: Platform

        Returns:
            List of keywords
        """
        keywords = []

        # Job-specific keywords
        if job.theme:
            keywords.append(job.theme.lower())
        if job.style:
            keywords.append(job.style.lower())
        if job.niche:
            keywords.append(job.niche.lower().replace("-", " "))

        # Add job keywords
        if job.keywords:
            keywords.extend([k.lower() for k in job.keywords if isinstance(k, str)])

        # Generic stock keywords
        generic = [
            "digital art",
            "illustration",
            "design",
            "artwork",
            "graphic",
            "creative",
            "modern",
            "unique",
            "print",
            "background",
            "pattern",
            "texture",
            "abstract",
            "decorative",
            "artistic",
        ]

        keywords.extend(generic)

        # Remove duplicates
        keywords = list(dict.fromkeys(keywords))

        # Platform limits
        limits = {
            "shutterstock": 50,
            "adobe_stock": 49,
        }

        limit = limits.get(platform, 50)

        return keywords[:limit]

    def _suggest_categories(self, job: Job, platform: StockPlatform) -> list[str]:
        """Suggest categories for platform.

        Args:
            job: Job instance
            platform: Platform

        Returns:
            Category suggestions
        """
        # Platform-specific category mapping
        categories = []

        if job.niche == "wall-art":
            categories.extend(["Arts", "Illustrations", "Backgrounds"])
        elif job.niche == "home-decor":
            categories.extend(["Home", "Interior", "Decorative"])
        elif job.niche == "apparel":
            categories.extend(["Fashion", "Apparel", "T-Shirt"])
        else:
            categories.extend(["Arts", "Design", "Creative"])

        return categories

    def _generate_ai_disclosure(self, asset: Asset) -> str:
        """Generate AI disclosure statement.

        Args:
            asset: Asset

        Returns:
            Disclosure text
        """
        return (
            "This artwork was created using AI technology (generative AI). "
            "The image has been reviewed and approved for stock platform submission."
        )

    def create_outbox_file(self, submission: dict, outbox_dir: Optional[Path] = None) -> Path:
        """Create submission file in outbox for manual processing.

        Args:
            submission: Submission data
            outbox_dir: Output directory

        Returns:
            Path to outbox file

        Note:
            For MVP, we create JSON files that can be manually processed.
            Future: Direct API integration.
        """
        import json

        if outbox_dir is None:
            outbox_dir = self.config.exports_dir / "stock_outbox"

        outbox_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{submission['platform']}_asset_{submission['asset_id']}.json"
        outbox_path = outbox_dir / filename

        with open(outbox_path, "w") as f:
            json.dump(submission, f, indent=2)

        logger.info(f"✓ Created outbox file: {outbox_path}")

        return outbox_path


# ============================================================================
# Helper Functions
# ============================================================================


def prepare_for_shutterstock(asset: Asset, job: Job) -> dict:
    """Prepare asset for Shutterstock submission.

    Args:
        asset: Asset to submit
        job: Job instance

    Returns:
        Submission data
    """
    worker = StockPlatformWorker()
    return worker.prepare_submission(asset, job, "shutterstock")


def prepare_for_adobe_stock(asset: Asset, job: Job) -> dict:
    """Prepare asset for Adobe Stock submission.

    Args:
        asset: Asset to submit
        job: Job instance

    Returns:
        Submission data
    """
    worker = StockPlatformWorker()
    return worker.prepare_submission(asset, job, "adobe_stock")

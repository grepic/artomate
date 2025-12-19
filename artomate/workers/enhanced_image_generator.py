"""Enhanced image generator with monthly variants."""

from typing import Optional
from datetime import datetime

from loguru import logger

from artomate.core.config import Config, get_config
from artomate.db.database import get_db
from artomate.db.models import Asset, Job
from artomate.workers.image_generator import ImageGenerator


class EnhancedImageGenerator(ImageGenerator):
    """Enhanced image generator with variant support."""

    # Monthly themes/moods
    MONTHLY_VARIATIONS = {
        0: {"season": "winter", "mood": "cozy", "colors": "cool tones, blues, whites"},
        1: {"season": "winter", "mood": "romantic", "colors": "reds, pinks, warm"},
        2: {"season": "spring", "mood": "fresh", "colors": "pastels, greens, yellows"},
        3: {"season": "spring", "mood": "vibrant", "colors": "bright colors, floral"},
        4: {"season": "spring", "mood": "cheerful", "colors": "yellows, greens"},
        5: {"season": "summer", "mood": "sunny", "colors": "warm yellows, oranges"},
        6: {"season": "summer", "mood": "tropical", "colors": "turquoise, coral"},
        7: {"season": "summer", "mood": "beachy", "colors": "blues, sand tones"},
        8: {"season": "fall", "mood": "cozy", "colors": "oranges, browns, warm"},
        9: {"season": "fall", "mood": "harvest", "colors": "rust, gold, amber"},
        10: {"season": "fall", "mood": "moody", "colors": "deep oranges, browns"},
        11: {"season": "winter", "mood": "festive", "colors": "reds, greens, gold"},
    }

    def generate_monthly_variant(
        self,
        job: Job,
        month_index: int,
        base_prompt: Optional[str] = None,
    ) -> list[Asset]:
        """Generate image variant for specific month.

        Args:
            job: Job instance
            month_index: Month index (0-11)
            base_prompt: Optional base prompt override

        Returns:
            List with single Asset instance

        Raises:
            RuntimeError: If generation fails
        """
        if month_index < 0 or month_index > 11:
            raise ValueError(f"Month index must be 0-11, got {month_index}")

        variation = self.MONTHLY_VARIATIONS[month_index]

        logger.info(
            f"Generating variant {month_index+1}/12 "
            f"({variation['season']}, {variation['mood']})"
        )

        # Build enhanced prompt
        if base_prompt is None:
            base_prompt = self.build_prompt(
                theme=job.theme,
                style=job.style,
                niche=job.niche,
                keywords=job.keywords,
            )

        # Add seasonal variation
        enhanced_prompt = (
            f"{base_prompt}, "
            f"{variation['season']} {variation['mood']} mood, "
            f"{variation['colors']}, "
            f"calendar month style"
        )

        logger.debug(f"Enhanced prompt: {enhanced_prompt}")

        # Generate
        results = self.generate_with_dalle(
            prompt=enhanced_prompt,
            size=self.config.default_image_size,
            quality=self.config.default_image_quality,
        )

        # Download and save
        assets = []
        for idx, result in enumerate(results):
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"job_{job.id}_month{month_index+1:02d}_{timestamp}_{idx}.png"
            save_path = self.config.assets_dir / "images" / filename

            image_data = self.download_image(result["url"], save_path)

            asset = Asset(
                job_id=job.id,
                asset_type="hero",
                subtype=f"month_{month_index+1:02d}",
                storage_path=str(save_path),
                file_size_bytes=image_data["size_bytes"],
                width=image_data["width"],
                height=image_data["height"],
                format=image_data["format"],
                generator=result["provider"],
                prompt=result.get("revised_prompt", enhanced_prompt),
                generation_params={
                    "model": result["model"],
                    "size": result["size"],
                    "quality": result.get("quality"),
                    "month_index": month_index,
                    "variation": variation,
                    "original_prompt": enhanced_prompt,
                },
                compliance_checked=False,
            )

            with self.db.session_scope() as session:
                session.add(asset)
                session.flush()
                session.expunge(asset)
                assets.append(asset)

            logger.info(f"✓ Created monthly variant asset {asset.id}")

        return assets

    def generate_all_monthly_variants(
        self,
        job: Job,
        start_month: int = 0,
        end_month: int = 11,
    ) -> list[Asset]:
        """Generate all 12 monthly variants.

        Args:
            job: Job instance
            start_month: Starting month index (0-11)
            end_month: Ending month index (0-11)

        Returns:
            List of all generated Assets

        Raises:
            RuntimeError: If generation fails
        """
        logger.info(f"Generating variants {start_month+1} to {end_month+1}")

        all_assets = []

        for month_index in range(start_month, end_month + 1):
            try:
                assets = self.generate_monthly_variant(job, month_index)
                all_assets.extend(assets)

                logger.info(
                    f"✓ Completed variant {month_index+1}/{end_month-start_month+1}"
                )

            except Exception as e:
                logger.error(f"Failed to generate variant {month_index+1}: {e}")
                # Continue with next month instead of failing completely
                continue

        logger.info(f"✓ Generated {len(all_assets)} total monthly variants")

        return all_assets

    def generate_seasonal_batch(
        self,
        job: Job,
        season: str,
    ) -> list[Asset]:
        """Generate batch for specific season.

        Args:
            job: Job instance
            season: Season name ("winter", "spring", "summer", "fall")

        Returns:
            List of Assets for that season

        Raises:
            ValueError: If invalid season
        """
        season_months = {
            "winter": [0, 1, 11],  # Jan, Feb, Dec
            "spring": [2, 3, 4],   # Mar, Apr, May
            "summer": [5, 6, 7],   # Jun, Jul, Aug
            "fall": [8, 9, 10],    # Sep, Oct, Nov
        }

        if season not in season_months:
            raise ValueError(f"Invalid season: {season}")

        months = season_months[season]

        logger.info(f"Generating {season} season variants (months: {months})")

        all_assets = []

        for month_index in months:
            assets = self.generate_monthly_variant(job, month_index)
            all_assets.extend(assets)

        logger.info(f"✓ Generated {len(all_assets)} {season} variants")

        return all_assets

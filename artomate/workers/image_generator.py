"""Image generation worker using AI providers."""

import os
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional

import requests
from loguru import logger
from openai import OpenAI

from artomate.core.config import Config, get_config
from artomate.db.database import get_db
from artomate.db.models import Asset, AssetType, Job


class ImageGenerator:
    """Generates images using AI providers (OpenAI, Stability AI)."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize image generator.

        Args:
            config: Application configuration
        """
        self.config = config or get_config()
        self.db = get_db()

        # Initialize clients
        self.openai_client = None
        if self.config.openai_api_key:
            self.openai_client = OpenAI(api_key=self.config.openai_api_key)

    def build_prompt(
        self,
        theme: str,
        style: Optional[str] = None,
        niche: Optional[str] = None,
        keywords: Optional[list[str]] = None,
        additional_params: Optional[dict] = None,
    ) -> str:
        """Build image generation prompt from job parameters.

        Args:
            theme: Main theme/subject
            style: Design style
            niche: Niche category
            keywords: Additional keywords
            additional_params: Extra parameters

        Returns:
            Formatted prompt string
        """
        prompt_parts = []

        # Main theme
        prompt_parts.append(theme)

        # Style
        if style:
            prompt_parts.append(f"{style} style")

        # Niche context
        niche_context = {
            "wall-art": "suitable for wall art print",
            "apparel": "centered design for clothing",
            "home-decor": "decorative pattern",
            "stationery": "clean design for stationery",
        }

        if niche and niche in niche_context:
            prompt_parts.append(niche_context[niche])

        # Keywords
        if keywords:
            prompt_parts.extend(keywords)

        # Quality modifiers
        quality_terms = [
            "high quality",
            "detailed",
            "professional",
        ]
        prompt_parts.extend(quality_terms)

        # Compliance filters (avoid trademarked content)
        prompt_parts.append("original design")
        prompt_parts.append("no text")
        prompt_parts.append("no logos")

        prompt = ", ".join(prompt_parts)

        logger.debug(f"Generated prompt: {prompt}")

        return prompt

    def generate_with_dalle(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: Literal["standard", "hd"] = "hd",
        n: int = 1,
    ) -> list[dict]:
        """Generate images using OpenAI DALL-E 3.

        Args:
            prompt: Image generation prompt
            size: Image size (1024x1024, 1792x1024, 1024x1792)
            quality: Image quality (standard, hd)
            n: Number of images to generate (DALL-E 3 only supports n=1)

        Returns:
            List of generated image data dicts

        Raises:
            RuntimeError: If generation fails
        """
        if not self.openai_client:
            raise RuntimeError("OpenAI API key not configured")

        logger.info(f"Generating image with DALL-E 3: {prompt[:100]}...")

        try:
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality=quality,
                n=1,  # DALL-E 3 only supports 1 image at a time
            )

            results = []
            for image in response.data:
                results.append(
                    {
                        "url": image.url,
                        "revised_prompt": image.revised_prompt,
                        "provider": "openai",
                        "model": "dall-e-3",
                        "size": size,
                        "quality": quality,
                    }
                )

            logger.info(f"✓ Generated {len(results)} image(s) with DALL-E 3")

            return results

        except Exception as e:
            logger.error(f"DALL-E 3 generation failed: {e}")
            raise RuntimeError(f"Image generation failed: {e}")

    def download_image(self, url: str, save_path: Path) -> dict:
        """Download image from URL and save locally.

        Args:
            url: Image URL
            save_path: Local save path

        Returns:
            Dict with image metadata

        Raises:
            RuntimeError: If download fails
        """
        try:
            save_path.parent.mkdir(parents=True, exist_ok=True)

            response = requests.get(url, timeout=60)
            response.raise_for_status()

            save_path.write_bytes(response.content)

            file_size = save_path.stat().st_size

            logger.info(f"✓ Downloaded image: {save_path} ({file_size:,} bytes)")

            # Get image dimensions using Pillow
            from PIL import Image

            with Image.open(save_path) as img:
                width, height = img.size
                format_ = img.format

            return {
                "path": str(save_path),
                "size_bytes": file_size,
                "width": width,
                "height": height,
                "format": format_,
            }

        except Exception as e:
            logger.error(f"Failed to download image from {url}: {e}")
            raise RuntimeError(f"Image download failed: {e}")

    def generate_for_job(
        self,
        job: Job,
        count: int = 1,
        provider: Optional[str] = None,
    ) -> list[Asset]:
        """Generate images for a job and save as assets.

        Args:
            job: Job instance
            count: Number of images to generate
            provider: AI provider ("openai", "stability"), defaults to config

        Returns:
            List of created Asset instances

        Raises:
            RuntimeError: If generation fails
        """
        provider = provider or self.config.default_image_provider

        # Build prompt
        prompt = self.build_prompt(
            theme=job.theme,
            style=job.style,
            niche=job.niche,
            keywords=job.keywords,
            additional_params=job.config,
        )

        assets = []

        for i in range(count):
            try:
                # Generate image
                if provider == "openai":
                    results = self.generate_with_dalle(
                        prompt=prompt,
                        size=self.config.default_image_size,
                        quality=self.config.default_image_quality,
                    )
                else:
                    raise ValueError(f"Unsupported provider: {provider}")

                # Download and save each generated image
                for idx, result in enumerate(results):
                    # Create filename
                    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                    filename = f"job_{job.id}_{timestamp}_{i}_{idx}.png"
                    save_path = self.config.assets_dir / "images" / filename

                    # Download
                    image_data = self.download_image(result["url"], save_path)

                    # Create asset record
                    asset = Asset(
                        job_id=job.id,
                        asset_type=AssetType.HERO,
                        storage_path=str(save_path),
                        file_size_bytes=image_data["size_bytes"],
                        width=image_data["width"],
                        height=image_data["height"],
                        format=image_data["format"],
                        generator=result["provider"],
                        prompt=result.get("revised_prompt", prompt),
                        generation_params={
                            "model": result["model"],
                            "size": result["size"],
                            "quality": result.get("quality"),
                            "original_prompt": prompt,
                        },
                        compliance_checked=False,
                    )

                    # Save to database
                    with self.db.session_scope() as session:
                        session.add(asset)
                        session.flush()
                        assets.append(asset)

                    logger.info(f"✓ Created asset {asset.id} for job {job.id}")

            except Exception as e:
                logger.error(f"Failed to generate image {i+1}/{count} for job {job.id}: {e}")
                # Continue with next image instead of failing completely
                continue

        if not assets:
            raise RuntimeError(f"Failed to generate any images for job {job.id}")

        logger.info(f"✓ Generated {len(assets)} asset(s) for job {job.id}")

        return assets

    def generate_variants(
        self,
        base_asset: Asset,
        variations: list[str],
    ) -> list[Asset]:
        """Generate variations of an existing image.

        Args:
            base_asset: Base asset to create variations from
            variations: List of variation descriptions (e.g., ["blue tones", "vintage"])

        Returns:
            List of variant Asset instances

        Note:
            For MVP, this creates new images with modified prompts.
            Could be enhanced with image-to-image transformation.
        """
        job_id = base_asset.job_id
        original_prompt = base_asset.prompt or ""

        variants = []

        for variation in variations:
            # Modify prompt
            variant_prompt = f"{original_prompt}, {variation}"

            try:
                # Generate variant
                results = self.generate_with_dalle(
                    prompt=variant_prompt,
                    size=self.config.default_image_size,
                    quality=self.config.default_image_quality,
                )

                # Save variant
                for result in results:
                    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                    filename = f"job_{job_id}_variant_{timestamp}.png"
                    save_path = self.config.assets_dir / "images" / filename

                    image_data = self.download_image(result["url"], save_path)

                    variant_asset = Asset(
                        job_id=job_id,
                        asset_type=AssetType.VARIANT,
                        subtype=variation,
                        storage_path=str(save_path),
                        file_size_bytes=image_data["size_bytes"],
                        width=image_data["width"],
                        height=image_data["height"],
                        format=image_data["format"],
                        generator=result["provider"],
                        prompt=result.get("revised_prompt", variant_prompt),
                        generation_params={
                            "model": result["model"],
                            "base_asset_id": base_asset.id,
                            "variation": variation,
                        },
                    )

                    with self.db.session_scope() as session:
                        session.add(variant_asset)
                        session.flush()
                        variants.append(variant_asset)

                    logger.info(f"✓ Created variant asset {variant_asset.id}")

            except Exception as e:
                logger.error(f"Failed to generate variant '{variation}': {e}")
                continue

        return variants

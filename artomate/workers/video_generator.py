"""Video generation for social media (Reels, Shorts, TikTok)."""

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional

from loguru import logger
from PIL import Image, ImageDraw, ImageFont

from artomate.core.config import Config, get_config
from artomate.db.database import get_db
from artomate.db.models import Asset, AssetType, Job


VideoStyle = Literal["slideshow", "zoom", "pan", "ken_burns"]


class VideoGenerator:
    """Generates short-form videos for social media."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize video generator.

        Args:
            config: Application configuration
        """
        self.config = config or get_config()
        self.db = get_db()

    def create_reel(
        self,
        job: Job,
        assets: list[Asset],
        duration: int = 5,
        style: VideoStyle = "ken_burns",
        add_text: bool = True,
    ) -> Asset:
        """Create Instagram Reel / TikTok / YouTube Short.

        Args:
            job: Job instance
            assets: List of image assets
            duration: Duration in seconds
            style: Video style
            add_text: Add text overlay

        Returns:
            Created video Asset

        Raises:
            RuntimeError: If video creation fails
        """
        logger.info(f"Creating {style} video for job {job.id}")

        # Generate output path
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        output_filename = f"reel_{job.id}_{timestamp}.mp4"
        output_path = self.config.assets_dir / "videos" / output_filename

        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            if style == "slideshow":
                video_path = self._create_slideshow(assets, output_path, duration)
            elif style == "zoom":
                video_path = self._create_zoom_effect(assets[0], output_path, duration)
            elif style == "pan":
                video_path = self._create_pan_effect(assets[0], output_path, duration)
            elif style == "ken_burns":
                video_path = self._create_ken_burns(assets[0], output_path, duration)
            else:
                raise ValueError(f"Unknown style: {style}")

            # Add text overlay if requested
            if add_text:
                text = self._generate_text_overlay(job)
                video_path = self._add_text_overlay(video_path, text)

            # Create asset record
            file_size = video_path.stat().st_size

            # Get video dimensions (assume 1080x1920 for 9:16)
            width, height = 1080, 1920

            asset = Asset(
                job_id=job.id,
                asset_type=AssetType.VIDEO,
                subtype=style,
                storage_path=str(video_path),
                file_size_bytes=file_size,
                width=width,
                height=height,
                format="MP4",
                generator="ffmpeg",
                generation_params={
                    "style": style,
                    "duration": duration,
                    "add_text": add_text,
                    "source_asset_ids": [a.id for a in assets],
                },
            )

            with self.db.session_scope() as session:
                session.add(asset)
                session.flush()
                session.expunge(asset)

            logger.info(f"✓ Created video asset {asset.id}")

            return asset

        except Exception as e:
            logger.error(f"Failed to create video: {e}")
            raise RuntimeError(f"Video creation failed: {e}")

    def _create_slideshow(
        self,
        assets: list[Asset],
        output_path: Path,
        duration: int,
    ) -> Path:
        """Create slideshow video.

        Args:
            assets: Image assets
            output_path: Output path
            duration: Total duration

        Returns:
            Path to created video
        """
        # Duration per image
        per_image_duration = duration / len(assets)

        # Create file list for ffmpeg
        filelist_path = output_path.parent / f"filelist_{output_path.stem}.txt"

        with open(filelist_path, "w") as f:
            for asset in assets:
                f.write(f"file '{asset.storage_path}'\n")
                f.write(f"duration {per_image_duration}\n")

        # FFmpeg command for slideshow
        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", str(filelist_path),
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-r", "30",
            "-y",
            str(output_path),
        ]

        subprocess.run(cmd, check=True, capture_output=True)

        # Cleanup
        filelist_path.unlink()

        return output_path

    def _create_zoom_effect(
        self,
        asset: Asset,
        output_path: Path,
        duration: int,
    ) -> Path:
        """Create zoom effect video (Ken Burns style).

        Args:
            asset: Image asset
            output_path: Output path
            duration: Duration

        Returns:
            Path to created video
        """
        # Zoom from 1.0 to 1.2 scale
        cmd = [
            "ffmpeg",
            "-loop", "1",
            "-i", asset.storage_path,
            "-vf",
            f"scale=1080:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,"
            f"zoompan=z='min(zoom+0.0015,1.5)':d={duration * 30}:s=1080x1920",
            "-c:v", "libx264",
            "-t", str(duration),
            "-pix_fmt", "yuv420p",
            "-r", "30",
            "-y",
            str(output_path),
        ]

        subprocess.run(cmd, check=True, capture_output=True)

        return output_path

    def _create_pan_effect(
        self,
        asset: Asset,
        output_path: Path,
        duration: int,
    ) -> Path:
        """Create pan effect video.

        Args:
            asset: Image asset
            output_path: Output path
            duration: Duration

        Returns:
            Path to created video
        """
        # Pan from left to right
        cmd = [
            "ffmpeg",
            "-loop", "1",
            "-i", asset.storage_path,
            "-vf",
            f"scale=2160:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920:x='(iw-1080)*t/{duration}':y=0",
            "-c:v", "libx264",
            "-t", str(duration),
            "-pix_fmt", "yuv420p",
            "-r", "30",
            "-y",
            str(output_path),
        ]

        subprocess.run(cmd, check=True, capture_output=True)

        return output_path

    def _create_ken_burns(
        self,
        asset: Asset,
        output_path: Path,
        duration: int,
    ) -> Path:
        """Create Ken Burns effect (zoom + pan).

        Args:
            asset: Image asset
            output_path: Output path
            duration: Duration

        Returns:
            Path to created video
        """
        # Combination of zoom and pan
        cmd = [
            "ffmpeg",
            "-loop", "1",
            "-i", asset.storage_path,
            "-vf",
            f"scale=1620:2880:force_original_aspect_ratio=increase,"
            f"zoompan=z='min(1.0+0.0015*on,1.3)':"
            f"x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)':"
            f"d={duration * 30}:s=1080x1920",
            "-c:v", "libx264",
            "-t", str(duration),
            "-pix_fmt", "yuv420p",
            "-r", "30",
            "-y",
            str(output_path),
        ]

        subprocess.run(cmd, check=True, capture_output=True)

        return output_path

    def _generate_text_overlay(self, job: Job) -> str:
        """Generate text for overlay.

        Args:
            job: Job instance

        Returns:
            Text to overlay
        """
        # Generate catchy text
        texts = [
            f"{job.theme.title()} Art",
            f"{job.style or 'Unique'} Design",
            "Available Now!",
            "Link in Bio 👆",
        ]

        return "\n".join(texts)

    def _add_text_overlay(self, video_path: Path, text: str) -> Path:
        """Add text overlay to video.

        Args:
            video_path: Video path
            text: Text to overlay

        Returns:
            Path to video with text (same file, modified in place)

        Note:
            This is a simplified implementation. For production, use
            drawtext filter in ffmpeg or create text images.
        """
        # For MVP, skip text overlay (requires more complex ffmpeg setup)
        # TODO: Implement with ffmpeg drawtext filter
        logger.debug(f"Text overlay not yet implemented: {text}")

        return video_path

    def create_mockup_video(
        self,
        asset: Asset,
        product_images: list[Path],
        duration: int = 10,
    ) -> Asset:
        """Create product mockup video.

        Args:
            asset: Design asset
            product_images: Mockup images (product photos)
            duration: Duration

        Returns:
            Video asset

        Note:
            For MVP, this creates a simple slideshow of mockups.
            Can be enhanced with 3D mockups, transitions, etc.
        """
        logger.info("Mockup video generation - simplified MVP")

        # Use slideshow approach
        # Convert paths to temporary Asset objects
        temp_assets = [asset]  # Just use the main asset for now

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        output_filename = f"mockup_{asset.job_id}_{timestamp}.mp4"
        output_path = self.config.assets_dir / "videos" / output_filename

        return self.create_reel(
            job=asset.job,  # type: ignore
            assets=temp_assets,
            duration=duration,
            style="zoom",
            add_text=False,
        )

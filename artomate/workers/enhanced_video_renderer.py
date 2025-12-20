"""Enhanced video renderer with AI facts, music, and viral optimization."""

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional

from loguru import logger

from artomate.core.config import Config, get_config
from artomate.db.database import get_db
from artomate.db.models import Asset, AssetType, Job
from artomate.workers.ai_facts_generator import AIFactsGenerator


VideoFormat = Literal["tiktok", "instagram_reel", "instagram_square", "youtube_short", "youtube"]
VideoStyle = Literal["slideshow", "zoom", "pan", "ken_burns"]


class EnhancedVideoRenderer:
    """Creates viral-optimized videos with AI facts and professional editing."""

    # Video format specifications
    FORMATS = {
        "tiktok": {"width": 1080, "height": 1920, "aspect": "9:16", "fps": 30, "duration": 15},
        "instagram_reel": {"width": 1080, "height": 1920, "aspect": "9:16", "fps": 30, "duration": 15},
        "instagram_square": {"width": 1080, "height": 1080, "aspect": "1:1", "fps": 30, "duration": 15},
        "youtube_short": {"width": 1080, "height": 1920, "aspect": "9:16", "fps": 30, "duration": 60},
        "youtube": {"width": 1920, "height": 1080, "aspect": "16:9", "fps": 30, "duration": 60},
    }

    def __init__(self, config: Optional[Config] = None):
        """Initialize enhanced video renderer.

        Args:
            config: Application configuration
        """
        self.config = config or get_config()
        self.db = get_db()
        self.facts_generator = AIFactsGenerator(config)

    def create_viral_video(
        self,
        job: Job,
        asset: Asset,
        video_format: VideoFormat = "tiktok",
        style: VideoStyle = "ken_burns",
        add_facts: bool = True,
        add_music: bool = True,
        add_hook: bool = True,
    ) -> Asset:
        """Create viral-optimized video with AI facts.

        Args:
            job: Job instance
            asset: Image asset to use
            video_format: Target platform format
            style: Animation style
            add_facts: Add AI-generated facts overlay
            add_music: Add background music
            add_hook: Add viral hook intro

        Returns:
            Created video Asset

        Example:
            >>> renderer = EnhancedVideoRenderer()
            >>> video = renderer.create_viral_video(
            ...     job=job,
            ...     asset=cat_image,
            ...     video_format="tiktok",
            ...     add_facts=True
            ... )
        """
        logger.info(f"Creating viral {video_format} video for job {job.id}")

        # Get format specs
        specs = self.FORMATS[video_format]

        # Generate output path
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        output_filename = f"viral_{video_format}_{job.id}_{timestamp}.mp4"
        output_path = self.config.assets_dir / "videos" / output_filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Step 1: Create base video with animation
            logger.info(f"Step 1/5: Creating base video with {style} animation")
            base_video = self._create_base_video(
                asset=asset,
                output_path=output_path.with_suffix(".base.mp4"),
                width=specs["width"],
                height=specs["height"],
                duration=specs["duration"],
                style=style,
            )

            # Step 2: Generate AI facts (if enabled)
            facts = []
            hook = None
            if add_facts:
                logger.info("Step 2/5: Generating AI facts")
                theme = self._extract_theme_from_job(job)
                facts = self.facts_generator.generate_animal_facts(
                    animal=theme,
                    count=3,
                    style="viral",
                )
                logger.info(f"Generated {len(facts)} facts: {facts}")

            if add_hook:
                logger.info("Step 2b/5: Generating viral hook")
                theme = self._extract_theme_from_job(job)
                hook = self.facts_generator.generate_viral_hook(theme, duration="short")
                logger.info(f"Generated hook: {hook}")

            # Step 3: Add text overlays
            logger.info("Step 3/5: Adding text overlays")
            video_with_text = self._add_text_overlays(
                video_path=base_video,
                output_path=output_path.with_suffix(".text.mp4"),
                facts=facts,
                hook=hook,
                duration=specs["duration"],
                width=specs["width"],
                height=specs["height"],
            )

            # Step 4: Add background music (if enabled)
            final_video = video_with_text
            if add_music:
                logger.info("Step 4/5: Adding background music")
                final_video = self._add_background_music(
                    video_path=video_with_text,
                    output_path=output_path,
                    duration=specs["duration"],
                )
            else:
                # Just rename
                video_with_text.rename(output_path)

            # Step 5: Create asset record
            logger.info("Step 5/5: Creating asset record")
            file_size = output_path.stat().st_size

            video_asset = Asset(
                job_id=job.id,
                asset_type=AssetType.VIDEO,
                subtype=video_format,
                storage_path=str(output_path),
                file_size_bytes=file_size,
                width=specs["width"],
                height=specs["height"],
                format="MP4",
                generator="enhanced_renderer",
                generation_params={
                    "format": video_format,
                    "style": style,
                    "duration": specs["duration"],
                    "add_facts": add_facts,
                    "add_music": add_music,
                    "add_hook": add_hook,
                    "facts": facts,
                    "hook": hook,
                    "source_asset_id": asset.id,
                },
            )

            with self.db.session_scope() as session:
                session.add(video_asset)
                session.flush()
                session.expunge(video_asset)

            # Cleanup temp files
            if base_video.exists():
                base_video.unlink()
            if video_with_text.exists() and video_with_text != output_path:
                video_with_text.unlink()

            logger.info(f"✓ Created viral video asset {video_asset.id} at {output_path}")

            return video_asset

        except Exception as e:
            logger.error(f"Failed to create viral video: {e}")
            raise RuntimeError(f"Viral video creation failed: {e}")

    def _extract_theme_from_job(self, job: Job) -> str:
        """Extract main animal/theme from job.

        Args:
            job: Job instance

        Returns:
            Theme keyword (e.g., "cat", "elephant")
        """
        # Try to extract animal name from theme
        theme = job.theme.lower()

        # Common animals
        animals = [
            "cat", "dog", "elephant", "lion", "tiger", "bear", "wolf",
            "fox", "rabbit", "deer", "owl", "eagle", "parrot", "penguin",
            "dolphin", "whale", "shark", "octopus", "turtle", "frog",
            "butterfly", "bee", "horse", "cow", "pig", "chicken",
        ]

        for animal in animals:
            if animal in theme:
                return animal

        # Fallback to first word of theme
        return theme.split()[0]

    def _create_base_video(
        self,
        asset: Asset,
        output_path: Path,
        width: int,
        height: int,
        duration: int,
        style: VideoStyle,
    ) -> Path:
        """Create base animated video.

        Args:
            asset: Image asset
            output_path: Output path
            width: Video width
            height: Video height
            duration: Duration in seconds
            style: Animation style

        Returns:
            Path to created video
        """
        if style == "ken_burns":
            # Zoom + pan effect
            cmd = [
                "ffmpeg",
                "-loop", "1",
                "-i", asset.storage_path,
                "-vf",
                f"scale={int(width * 1.5)}:{int(height * 1.5)}:force_original_aspect_ratio=increase,"
                f"zoompan=z='min(1.0+0.0015*on,1.3)':"
                f"x='iw/2-(iw/zoom/2)':"
                f"y='ih/2-(ih/zoom/2)':"
                f"d={duration * 30}:s={width}x{height}",
                "-c:v", "libx264",
                "-t", str(duration),
                "-pix_fmt", "yuv420p",
                "-r", "30",
                "-y",
                str(output_path),
            ]
        elif style == "zoom":
            # Simple zoom
            cmd = [
                "ffmpeg",
                "-loop", "1",
                "-i", asset.storage_path,
                "-vf",
                f"scale={width}:{height}:force_original_aspect_ratio=increase,"
                f"crop={width}:{height},"
                f"zoompan=z='min(zoom+0.0015,1.5)':d={duration * 30}:s={width}x{height}",
                "-c:v", "libx264",
                "-t", str(duration),
                "-pix_fmt", "yuv420p",
                "-r", "30",
                "-y",
                str(output_path),
            ]
        else:
            # Static (fallback)
            cmd = [
                "ffmpeg",
                "-loop", "1",
                "-i", asset.storage_path,
                "-vf",
                f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}",
                "-c:v", "libx264",
                "-t", str(duration),
                "-pix_fmt", "yuv420p",
                "-r", "30",
                "-y",
                str(output_path),
            ]

        subprocess.run(cmd, check=True, capture_output=True)

        return output_path

    def _add_text_overlays(
        self,
        video_path: Path,
        output_path: Path,
        facts: list[str],
        hook: Optional[str],
        duration: int,
        width: int,
        height: int,
    ) -> Path:
        """Add text overlays with facts.

        Args:
            video_path: Input video path
            output_path: Output path
            facts: List of facts to overlay
            hook: Viral hook for intro
            duration: Video duration
            width: Video width
            height: Video height

        Returns:
            Path to video with text
        """
        # Calculate timing for each fact
        segments = len(facts) + (1 if hook else 0)
        segment_duration = duration / max(segments, 1)

        # Build drawtext filters
        filters = []

        current_time = 0

        # Add hook (first 3-5 seconds)
        if hook:
            hook_duration = min(5, segment_duration)
            filters.append(
                f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
                f"text='{self._escape_text(hook)}':"
                f"fontcolor=white:fontsize={int(width * 0.06)}:"
                f"box=1:boxcolor=black@0.7:boxborderw=10:"
                f"x=(w-text_w)/2:y=(h-text_h)/2:"
                f"enable='between(t,{current_time},{current_time + hook_duration})'"
            )
            current_time += hook_duration

        # Add facts
        for i, fact in enumerate(facts):
            fact_start = current_time
            fact_end = current_time + segment_duration

            # Clean fact text (remove emojis for ffmpeg - they cause issues)
            clean_fact = self._clean_text_for_ffmpeg(fact)

            # Fact number
            filters.append(
                f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
                f"text='FACT {i + 1}':"
                f"fontcolor=yellow:fontsize={int(width * 0.05)}:"
                f"x=(w-text_w)/2:y={int(height * 0.2)}:"
                f"enable='between(t,{fact_start},{fact_end})'"
            )

            # Fact text (split into multiple lines if long)
            filters.append(
                f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
                f"text='{self._escape_text(clean_fact)}':"
                f"fontcolor=white:fontsize={int(width * 0.04)}:"
                f"box=1:boxcolor=black@0.6:boxborderw=8:"
                f"x=(w-text_w)/2:y=(h-text_h)/2:"
                f"enable='between(t,{fact_start},{fact_end})'"
            )

            current_time = fact_end

        # Add CTA at the end (last 2 seconds)
        cta_start = duration - 2
        filters.append(
            f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
            f"text='FOLLOW FOR MORE!':"
            f"fontcolor=yellow:fontsize={int(width * 0.06)}:"
            f"box=1:boxcolor=black@0.8:boxborderw=10:"
            f"x=(w-text_w)/2:y={(height * 0.75)}:"
            f"enable='between(t,{cta_start},{duration})'"
        )

        # Combine all filters
        filter_chain = ",".join(filters) if filters else "null"

        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-vf", filter_chain,
            "-c:v", "libx264",
            "-c:a", "copy",
            "-pix_fmt", "yuv420p",
            "-y",
            str(output_path),
        ]

        subprocess.run(cmd, check=True, capture_output=True)

        return output_path

    def _escape_text(self, text: str) -> str:
        """Escape text for ffmpeg drawtext filter.

        Args:
            text: Text to escape

        Returns:
            Escaped text
        """
        # FFmpeg drawtext needs special escaping
        text = text.replace("\\", "\\\\")
        text = text.replace("'", "\\'")
        text = text.replace(":", "\\:")
        text = text.replace("[", "\\[")
        text = text.replace("]", "\\]")
        return text

    def _clean_text_for_ffmpeg(self, text: str) -> str:
        """Remove emojis and special chars that ffmpeg can't render.

        Args:
            text: Original text

        Returns:
            Cleaned text
        """
        import re

        # Remove emojis (simple approach - remove non-ASCII)
        text = re.sub(r"[^\x00-\x7F]+", "", text)

        # Remove extra whitespace
        text = " ".join(text.split())

        return text

    def _add_background_music(
        self,
        video_path: Path,
        output_path: Path,
        duration: int,
    ) -> Path:
        """Add background music to video.

        Args:
            video_path: Input video path
            output_path: Output path
            duration: Video duration

        Returns:
            Path to video with music

        Note:
            For MVP, this is a placeholder. In production:
            - Use royalty-free music library (e.g., Pixabay, Uppbeat)
            - Or generate music with AI (e.g., Mubert API)
            - Store music files in assets/music/
        """
        # Check if music directory exists
        music_dir = self.config.assets_dir / "music"

        if not music_dir.exists() or not list(music_dir.glob("*.mp3")):
            logger.warning("No background music found. Skipping music overlay.")
            # Just copy the video
            video_path.rename(output_path)
            return output_path

        # Get first available music file
        music_files = list(music_dir.glob("*.mp3"))
        music_file = music_files[0]

        logger.info(f"Using background music: {music_file.name}")

        # Add music with lower volume (so facts are audible)
        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-i", str(music_file),
            "-filter_complex",
            f"[1:a]volume=0.3,afade=t=in:st=0:d=1,afade=t=out:st={duration - 1}:d=1[music];"
            f"[music]atrim=0:{duration}[musiccut]",
            "-map", "0:v",
            "-map", "[musiccut]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            "-y",
            str(output_path),
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to add music: {e}. Using video without music.")
            video_path.rename(output_path)

        return output_path

    def create_multi_format_videos(
        self,
        job: Job,
        asset: Asset,
        formats: Optional[list[VideoFormat]] = None,
    ) -> list[Asset]:
        """Create videos for multiple platforms at once.

        Args:
            job: Job instance
            asset: Image asset
            formats: List of formats (default: all major platforms)

        Returns:
            List of created video assets

        Example:
            >>> renderer = EnhancedVideoRenderer()
            >>> videos = renderer.create_multi_format_videos(
            ...     job=job,
            ...     asset=cat_image,
            ...     formats=["tiktok", "instagram_reel", "youtube_short"]
            ... )
            >>> print(f"Created {len(videos)} videos")
        """
        if formats is None:
            formats = ["tiktok", "instagram_reel", "youtube_short"]

        logger.info(f"Creating {len(formats)} format videos for job {job.id}")

        videos = []

        for video_format in formats:
            try:
                video = self.create_viral_video(
                    job=job,
                    asset=asset,
                    video_format=video_format,
                    style="ken_burns",
                    add_facts=True,
                    add_music=True,
                    add_hook=True,
                )
                videos.append(video)
                logger.info(f"✓ Created {video_format} video")
            except Exception as e:
                logger.error(f"Failed to create {video_format} video: {e}")

        logger.info(f"✓ Created {len(videos)}/{len(formats)} videos successfully")

        return videos

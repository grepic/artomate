"""Viral content optimizer - complete workflow for viral videos."""

from datetime import datetime
from pathlib import Path
from typing import Optional

from loguru import logger

from artomate.core.config import Config, get_config
from artomate.db.database import get_db
from artomate.db.models import Asset, Job, SocialPlatform, SocialPost
from artomate.workers.ai_facts_generator import AIFactsGenerator
from artomate.workers.enhanced_video_renderer import EnhancedVideoRenderer, VideoFormat


class ViralContentOptimizer:
    """Complete viral content creation workflow."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize viral content optimizer.

        Args:
            config: Application configuration
        """
        self.config = config or get_config()
        self.db = get_db()
        self.facts_generator = AIFactsGenerator(config)
        self.video_renderer = EnhancedVideoRenderer(config)

    def create_complete_viral_package(
        self,
        job: Job,
        image_asset: Asset,
        platforms: Optional[list[str]] = None,
    ) -> dict:
        """Create complete viral content package for multiple platforms.

        This creates:
        - Viral videos for each platform (TikTok, Instagram, YouTube)
        - AI-generated facts about the subject
        - Optimized captions and hashtags
        - Ready-to-post social media content

        Args:
            job: Job instance
            image_asset: Source image asset
            platforms: List of platforms (default: ["tiktok", "instagram", "youtube"])

        Returns:
            Dictionary with all created content:
            {
                "videos": [Asset, ...],
                "posts": [SocialPost, ...],
                "facts": [str, ...],
                "captions": {"platform": "caption", ...},
                "hashtags": {"platform": [tags], ...},
            }

        Example:
            >>> optimizer = ViralContentOptimizer()
            >>> package = optimizer.create_complete_viral_package(
            ...     job=cat_job,
            ...     image_asset=cat_image,
            ...     platforms=["tiktok", "instagram", "youtube"]
            ... )
            >>> print(f"Created {len(package['videos'])} videos")
            >>> print(f"Generated {len(package['facts'])} facts")
        """
        logger.info(f"Creating complete viral package for job {job.id}")

        if platforms is None:
            platforms = ["tiktok", "instagram", "youtube"]

        # Map platform names to video formats
        platform_formats = {
            "tiktok": "tiktok",
            "instagram": "instagram_reel",
            "youtube": "youtube_short",
        }

        # Step 1: Generate AI facts
        logger.info("Step 1/4: Generating AI facts")
        theme = self._extract_theme(job)
        facts = self.facts_generator.generate_animal_facts(
            animal=theme,
            count=5,
            style="viral",
        )
        logger.info(f"Generated {len(facts)} facts")

        # Step 2: Create videos for each platform
        logger.info("Step 2/4: Creating platform-specific videos")
        videos = []
        for platform in platforms:
            video_format = platform_formats.get(platform)
            if not video_format:
                logger.warning(f"Unknown platform: {platform}")
                continue

            try:
                video = self.video_renderer.create_viral_video(
                    job=job,
                    asset=image_asset,
                    video_format=video_format,
                    style="ken_burns",
                    add_facts=True,
                    add_music=True,
                    add_hook=True,
                )
                videos.append(video)
                logger.info(f"✓ Created {platform} video")
            except Exception as e:
                logger.error(f"Failed to create {platform} video: {e}")

        # Step 3: Generate captions and hashtags
        logger.info("Step 3/4: Generating captions and hashtags")
        captions = {}
        hashtags = {}

        for platform in platforms:
            captions[platform] = self.facts_generator.generate_caption(
                theme=theme,
                facts=facts,
                platform=platform,
            )

            hashtags[platform] = self.facts_generator.generate_hashtags(
                theme=theme,
                niche=job.niche or "viral",
                platform=platform,
            )

        # Step 4: Create social post records
        logger.info("Step 4/4: Creating social post records")
        posts = []

        platform_enum_map = {
            "tiktok": SocialPlatform.TIKTOK,
            "instagram": SocialPlatform.INSTAGRAM,
            "youtube": SocialPlatform.YOUTUBE_SHORTS,
        }

        for i, platform in enumerate(platforms):
            if i >= len(videos):
                break

            platform_enum = platform_enum_map.get(platform)
            if not platform_enum:
                continue

            video = videos[i]

            post = SocialPost(
                job_id=job.id,
                platform=platform_enum,
                caption=captions[platform],
                hashtags=hashtags[platform],
                video_asset_id=video.id,
                status="draft",
                post_data={
                    "theme": theme,
                    "facts": facts,
                    "video_format": video.subtype,
                    "optimized_for_viral": True,
                },
            )

            with self.db.session_scope() as session:
                session.add(post)
                session.flush()
                session.expunge(post)

            posts.append(post)
            logger.info(f"✓ Created {platform} post record")

        # Create package
        package = {
            "videos": videos,
            "posts": posts,
            "facts": facts,
            "captions": captions,
            "hashtags": hashtags,
            "theme": theme,
            "platforms": platforms,
        }

        logger.info(
            f"✓ Viral package complete: {len(videos)} videos, "
            f"{len(posts)} posts, {len(facts)} facts"
        )

        return package

    def export_ready_to_post_package(
        self,
        package: dict,
        export_dir: Optional[Path] = None,
    ) -> Path:
        """Export viral package as ready-to-post files.

        Creates a directory structure:
        ```
        export/job_123_20250120/
        ├── tiktok/
        │   ├── video.mp4
        │   ├── caption.txt
        │   └── hashtags.txt
        ├── instagram/
        │   ├── video.mp4
        │   ├── caption.txt
        │   └── hashtags.txt
        ├── youtube/
        │   ├── video.mp4
        │   ├── caption.txt
        │   └── hashtags.txt
        └── README.md
        ```

        Args:
            package: Viral package from create_complete_viral_package()
            export_dir: Export directory (default: data/exports/)

        Returns:
            Path to export directory
        """
        if export_dir is None:
            export_dir = self.config.assets_dir / "exports"

        # Create timestamped export folder
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        job_id = package["videos"][0].job_id if package["videos"] else "unknown"
        folder_name = f"job_{job_id}_{timestamp}"
        export_path = export_dir / folder_name

        export_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Exporting viral package to {export_path}")

        # Export each platform
        for platform in package["platforms"]:
            platform_dir = export_path / platform
            platform_dir.mkdir(exist_ok=True)

            # Find video for this platform
            video = None
            for v in package["videos"]:
                if platform in v.subtype:
                    video = v
                    break

            if not video:
                logger.warning(f"No video found for {platform}")
                continue

            # Copy video
            import shutil
            video_dest = platform_dir / "video.mp4"
            shutil.copy2(video.storage_path, video_dest)

            # Write caption
            caption_file = platform_dir / "caption.txt"
            caption_file.write_text(package["captions"][platform])

            # Write hashtags
            hashtags_file = platform_dir / "hashtags.txt"
            hashtags_text = " ".join(package["hashtags"][platform])
            hashtags_file.write_text(hashtags_text)

            logger.info(f"✓ Exported {platform} content")

        # Create README
        readme_content = f"""# Viral Content Package

**Generated:** {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}
**Theme:** {package['theme']}
**Platforms:** {', '.join(package['platforms'])}

## AI-Generated Facts

{chr(10).join(f"{i+1}. {fact}" for i, fact in enumerate(package['facts']))}

## How to Post

### TikTok
1. Open TikTok app
2. Upload `tiktok/video.mp4`
3. Copy caption from `tiktok/caption.txt`
4. Copy hashtags from `tiktok/hashtags.txt`
5. Post!

### Instagram Reels
1. Open Instagram app
2. Create new Reel
3. Upload `instagram/video.mp4`
4. Copy caption from `instagram/caption.txt`
5. Copy hashtags from `instagram/hashtags.txt`
6. Post!

### YouTube Shorts
1. Open YouTube Studio app
2. Create Short
3. Upload `youtube/video.mp4`
4. Copy caption from `youtube/caption.txt`
5. Copy hashtags from `youtube/hashtags.txt`
6. Post!

## Tips for Maximum Virality

- Post during peak hours (7-9 PM local time)
- Respond to comments quickly (first 30 mins critical)
- Cross-post to all platforms within 1 hour
- Pin top comment asking engagement question
- Share to Stories/Feed after posting

## Analytics

Track performance in the Artomate dashboard or manually:
- Views
- Likes
- Comments
- Shares
- Watch time %

Good luck! 🚀
"""

        readme_file = export_path / "README.md"
        readme_file.write_text(readme_content)

        logger.info(f"✓ Export complete: {export_path}")

        return export_path

    def _extract_theme(self, job: Job) -> str:
        """Extract main theme/animal from job.

        Args:
            job: Job instance

        Returns:
            Theme string
        """
        theme = job.theme.lower()

        # Common animals
        animals = [
            "cat", "dog", "elephant", "lion", "tiger", "bear", "wolf",
            "fox", "rabbit", "deer", "owl", "eagle", "parrot", "penguin",
            "dolphin", "whale", "shark", "octopus", "turtle", "frog",
        ]

        for animal in animals:
            if animal in theme:
                return animal

        # Fallback
        return theme.split()[0]

    def get_posting_schedule_recommendations(
        self,
        platforms: list[str],
    ) -> dict:
        """Get recommended posting times for each platform.

        Args:
            platforms: List of platforms

        Returns:
            Dictionary with posting recommendations

        Example:
            >>> optimizer = ViralContentOptimizer()
            >>> schedule = optimizer.get_posting_schedule_recommendations(
            ...     platforms=["tiktok", "instagram", "youtube"]
            ... )
            >>> print(schedule["tiktok"]["best_times"])
        """
        recommendations = {
            "tiktok": {
                "best_times": ["7-9 PM", "12-1 PM"],
                "best_days": ["Tuesday", "Thursday", "Friday"],
                "frequency": "1-3 posts/day",
                "optimal_length": "15-30 seconds",
                "tips": [
                    "Use trending sounds",
                    "Hook in first 3 seconds",
                    "Engage with comments immediately",
                    "Post consistently same time daily",
                ],
            },
            "instagram": {
                "best_times": ["6-9 AM", "12-2 PM", "5-7 PM"],
                "best_days": ["Monday", "Wednesday", "Thursday"],
                "frequency": "1-2 reels/day",
                "optimal_length": "7-15 seconds",
                "tips": [
                    "Use 5-7 relevant hashtags",
                    "Share to stories after posting",
                    "Cross-post to feed",
                    "Collaborate with similar accounts",
                ],
            },
            "youtube": {
                "best_times": ["2-4 PM", "8-11 PM"],
                "best_days": ["Friday", "Saturday", "Sunday"],
                "frequency": "3-5 shorts/week",
                "optimal_length": "15-60 seconds",
                "tips": [
                    "Use strong title hooks",
                    "Add to relevant playlists",
                    "Pin engaging comment",
                    "Create series for binge-watching",
                ],
            },
        }

        return {p: recommendations.get(p, {}) for p in platforms if p in recommendations}

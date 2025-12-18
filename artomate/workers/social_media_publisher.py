"""Social media publishing worker."""

from datetime import datetime
from typing import Optional

from loguru import logger

from artomate.core.config import Config, get_config
from artomate.db.database import get_db
from artomate.db.models import Asset, Job, SocialPlatform, SocialPost


class SocialMediaPublisher:
    """Publishes content to social media platforms."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize social media publisher.

        Args:
            config: Application configuration
        """
        self.config = config or get_config()
        self.db = get_db()

    def create_post(
        self,
        job: Job,
        platform: SocialPlatform,
        video_asset: Optional[Asset] = None,
        image_assets: Optional[list[Asset]] = None,
        scheduled_for: Optional[datetime] = None,
    ) -> SocialPost:
        """Create social media post.

        Args:
            job: Job instance
            platform: Social platform
            video_asset: Video asset (for Reels/Shorts/TikTok)
            image_assets: Image assets (for carousel)
            scheduled_for: Schedule for future posting

        Returns:
            Created SocialPost instance
        """
        # Generate caption and hashtags
        caption = self._generate_caption(job, platform)
        hashtags = self._generate_hashtags(job, platform)

        # Create post record
        post = SocialPost(
            job_id=job.id,
            platform=platform,
            caption=caption,
            hashtags=hashtags,
            video_asset_id=video_asset.id if video_asset else None,
            image_asset_ids=[a.id for a in image_assets] if image_assets else [],
            status="scheduled" if scheduled_for else "draft",
            scheduled_for=scheduled_for,
            post_data={
                "theme": job.theme,
                "style": job.style,
                "niche": job.niche,
            },
        )

        with self.db.session_scope() as session:
            session.add(post)
            session.flush()
            session.expunge(post)

        logger.info(f"✓ Created {platform.value} post {post.id}")

        return post

    def _generate_caption(self, job: Job, platform: SocialPlatform) -> str:
        """Generate engaging caption.

        Args:
            job: Job instance
            platform: Platform

        Returns:
            Caption text
        """
        # Platform-specific caption lengths
        max_lengths = {
            SocialPlatform.INSTAGRAM: 2200,
            SocialPlatform.TIKTOK: 300,
            SocialPlatform.YOUTUBE_SHORTS: 5000,
        }

        max_length = max_lengths.get(platform, 2200)

        # Generate caption
        parts = [
            f"✨ {job.theme.title()} {job.style or 'Art'} ✨",
            "",
            f"New {job.niche or 'design'} drop! 🎨",
            "",
            "Available now - link in bio! 👆",
            "",
            "Double tap if you love it! ❤️",
        ]

        caption = "\n".join(parts)

        # Trim if needed
        if len(caption) > max_length:
            caption = caption[:max_length - 3] + "..."

        return caption

    def _generate_hashtags(self, job: Job, platform: SocialPlatform) -> list[str]:
        """Generate hashtags for platform.

        Args:
            job: Job instance
            platform: Platform

        Returns:
            List of hashtags
        """
        hashtags = []

        # Job-specific tags
        if job.theme:
            hashtags.append(f"#{job.theme.lower().replace(' ', '')}")
        if job.style:
            hashtags.append(f"#{job.style.lower().replace(' ', '')}")
        if job.niche:
            hashtags.append(f"#{job.niche.lower().replace('-', '')}")

        # Generic high-performing hashtags
        generic = [
            "#art",
            "#design",
            "#artist",
            "#artwork",
            "#creative",
            "#handmade",
            "#unique",
            "#gift",
            "#homedecor",
            "#walldecor",
            "#printsondemand",
            "#etsy",
            "#etsyshop",
            "#smallbusiness",
            "#shopsmall",
        ]

        hashtags.extend(generic)

        # Platform limits
        limits = {
            SocialPlatform.INSTAGRAM: 30,
            SocialPlatform.TIKTOK: 10,
            SocialPlatform.YOUTUBE_SHORTS: 15,
        }

        limit = limits.get(platform, 30)

        return hashtags[:limit]

    def publish_post(self, post: SocialPost) -> bool:
        """Publish post to platform.

        Args:
            post: SocialPost instance

        Returns:
            True if published

        Note:
            This is a placeholder. Actual implementation requires:
            - Instagram Graph API (business account + Facebook Page)
            - TikTok API (app approval required)
            - YouTube Data API
        """
        logger.warning(
            f"Social media publishing not yet implemented for {post.platform.value}. "
            "Post created as draft."
        )

        # For MVP: mark as "outbox" - manual posting
        post.status = "pending_manual"

        with self.db.session_scope() as session:
            session.add(post)

        return False

    def get_post_analytics(self, post: SocialPost) -> dict:
        """Get post analytics.

        Args:
            post: SocialPost instance

        Returns:
            Analytics data
        """
        # Placeholder for analytics retrieval
        return {
            "views": post.views_count,
            "likes": post.likes_count,
            "comments": post.comments_count,
            "shares": post.shares_count,
        }

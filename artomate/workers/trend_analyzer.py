"""Trend analysis for automatic theme generation."""

from datetime import datetime, timedelta
from typing import Optional

from loguru import logger

from artomate.core.config import Config, get_config


class TrendAnalyzer:
    """Analyzes trends to suggest themes."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize trend analyzer.

        Args:
            config: Application configuration
        """
        self.config = config or get_config()

    def get_trending_themes(
        self,
        niche: Optional[str] = None,
        limit: int = 10,
    ) -> list[dict]:
        """Get trending themes.

        Args:
            niche: Optional niche filter
            limit: Number of themes to return

        Returns:
            List of trending theme dicts

        Note:
            For MVP, uses predefined trends. Can be enhanced with:
            - Google Trends API (pytrends)
            - Etsy trending searches
            - Pinterest trends
            - Social media hashtag analysis
        """
        # Seasonal trends
        season = self._get_current_season()
        seasonal_themes = self._get_seasonal_themes(season)

        # Evergreen themes
        evergreen_themes = self._get_evergreen_themes()

        # Combine
        all_themes = seasonal_themes + evergreen_themes

        # Filter by niche if provided
        if niche:
            all_themes = [t for t in all_themes if niche in t.get("niches", [])]

        # Score and sort
        scored_themes = []
        for theme in all_themes:
            score = self._calculate_trend_score(theme, season)
            scored_themes.append({**theme, "trend_score": score})

        scored_themes.sort(key=lambda x: x["trend_score"], reverse=True)

        return scored_themes[:limit]

    def _get_current_season(self) -> str:
        """Get current season.

        Returns:
            Season name
        """
        month = datetime.now().month

        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "fall"

    def _get_seasonal_themes(self, season: str) -> list[dict]:
        """Get seasonal themes.

        Args:
            season: Current season

        Returns:
            List of themes
        """
        seasonal_map = {
            "winter": [
                {
                    "theme": "cozy cabin",
                    "style": "rustic",
                    "niches": ["wall-art", "home-decor"],
                    "keywords": ["winter", "cozy", "cabin", "snow"],
                },
                {
                    "theme": "winter forest",
                    "style": "minimalist",
                    "niches": ["wall-art"],
                    "keywords": ["winter", "forest", "trees", "nature"],
                },
                {
                    "theme": "holiday ornaments",
                    "style": "festive",
                    "niches": ["home-decor", "stationery"],
                    "keywords": ["holiday", "christmas", "ornament"],
                },
            ],
            "spring": [
                {
                    "theme": "cherry blossoms",
                    "style": "japandi",
                    "niches": ["wall-art", "home-decor"],
                    "keywords": ["spring", "blossom", "sakura", "japan"],
                },
                {
                    "theme": "garden flowers",
                    "style": "watercolor",
                    "niches": ["wall-art", "stationery"],
                    "keywords": ["spring", "flowers", "garden", "botanical"],
                },
            ],
            "summer": [
                {
                    "theme": "tropical paradise",
                    "style": "vibrant",
                    "niches": ["wall-art", "apparel"],
                    "keywords": ["summer", "tropical", "beach", "palm"],
                },
                {
                    "theme": "ocean waves",
                    "style": "minimalist",
                    "niches": ["wall-art"],
                    "keywords": ["ocean", "waves", "sea", "coastal"],
                },
            ],
            "fall": [
                {
                    "theme": "autumn leaves",
                    "style": "vintage",
                    "niches": ["wall-art", "home-decor"],
                    "keywords": ["fall", "autumn", "leaves", "foliage"],
                },
                {
                    "theme": "pumpkin spice",
                    "style": "boho",
                    "niches": ["apparel", "stationery"],
                    "keywords": ["fall", "pumpkin", "autumn", "cozy"],
                },
            ],
        }

        return seasonal_map.get(season, [])

    def _get_evergreen_themes(self) -> list[dict]:
        """Get evergreen (always popular) themes.

        Returns:
            List of themes
        """
        return [
            {
                "theme": "minimalist cat",
                "style": "minimalist",
                "niches": ["wall-art", "apparel"],
                "keywords": ["cat", "minimalist", "simple", "pet"],
            },
            {
                "theme": "geometric patterns",
                "style": "modern",
                "niches": ["wall-art", "home-decor"],
                "keywords": ["geometric", "pattern", "abstract", "modern"],
            },
            {
                "theme": "mountain landscape",
                "style": "minimalist",
                "niches": ["wall-art"],
                "keywords": ["mountain", "landscape", "nature", "minimal"],
            },
            {
                "theme": "botanical prints",
                "style": "vintage",
                "niches": ["wall-art", "home-decor"],
                "keywords": ["botanical", "plant", "vintage", "nature"],
            },
            {
                "theme": "abstract shapes",
                "style": "modern",
                "niches": ["wall-art", "apparel"],
                "keywords": ["abstract", "shapes", "modern", "art"],
            },
        ]

    def _calculate_trend_score(self, theme: dict, current_season: str) -> float:
        """Calculate trend score for theme.

        Args:
            theme: Theme dict
            current_season: Current season

        Returns:
            Score (0-100)
        """
        score = 50.0  # Base score

        # Seasonal bonus
        if "season" in theme:
            if theme["season"] == current_season:
                score += 30

        # Time-sensitive bonuses
        month = datetime.now().month

        # November-December: Holiday boost
        if month in [11, 12]:
            if any(kw in ["holiday", "christmas", "winter"] for kw in theme.get("keywords", [])):
                score += 20

        # January-February: New Year / Valentine's
        if month in [1, 2]:
            if any(kw in ["love", "heart", "valentine"] for kw in theme.get("keywords", [])):
                score += 15

        return min(score, 100)

    def suggest_jobs_from_trends(
        self,
        count: int = 10,
        niche: Optional[str] = None,
    ) -> list[dict]:
        """Suggest job configurations from trends.

        Args:
            count: Number of jobs to suggest
            niche: Optional niche filter

        Returns:
            List of job config dicts
        """
        trends = self.get_trending_themes(niche=niche, limit=count)

        jobs = []
        for trend in trends:
            job_config = {
                "theme": trend["theme"],
                "style": trend.get("style"),
                "niche": trend.get("niches", ["wall-art"])[0],
                "keywords": trend.get("keywords", []),
                "priority": 8 if trend.get("trend_score", 0) > 70 else 5,
                "input_source": "trend",
                "input_data": {
                    "trend_score": trend.get("trend_score"),
                    "season": self._get_current_season(),
                },
            }
            jobs.append(job_config)

        logger.info(f"✓ Suggested {len(jobs)} jobs from trends")

        return jobs

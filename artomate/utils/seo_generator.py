"""SEO and metadata optimization using AI."""

import logging
from typing import Dict, List, Optional

from openai import OpenAI

logger = logging.getLogger(__name__)


class SEOGenerator:
    """Generate SEO-optimized metadata for different platforms."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """Initialize SEO generator."""
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.model = model

    def generate_stock_metadata(
        self,
        theme: str,
        niche: Optional[str] = None,
        style: Optional[str] = None,
        platform: str = "shutterstock",
        image_description: Optional[str] = None,
    ) -> Dict:
        """Generate SEO metadata for stock platforms."""
        if not self.client:
            return self._generate_fallback_metadata(theme, niche, platform)

        try:
            prompt = self._build_stock_prompt(theme, niche, style, platform, image_description)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in stock photography SEO and metadata optimization. Generate titles, descriptions, and keywords that maximize discoverability and sales.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )

            # Parse response
            content = response.choices[0].message.content
            return self._parse_seo_response(content, platform)

        except Exception as e:
            logger.error(f"SEO generation failed: {e}")
            return self._generate_fallback_metadata(theme, niche, platform)

    def _build_stock_prompt(
        self,
        theme: str,
        niche: Optional[str],
        style: Optional[str],
        platform: str,
        image_description: Optional[str],
    ) -> str:
        """Build prompt for stock metadata generation."""
        prompt = f"""Generate SEO-optimized metadata for a stock image with these characteristics:

Theme: {theme}
"""
        if niche:
            prompt += f"Niche: {niche}\n"
        if style:
            prompt += f"Style: {style}\n"
        if image_description:
            prompt += f"Image Description: {image_description}\n"

        prompt += f"\nTarget Platform: {platform}\n"

        platform_guidelines = {
            "shutterstock": "Max 200 char title, 1000 char description, 50 keywords",
            "adobe_stock": "Max 70 char title, 500 char description, 49 keywords",
            "getty_images": "Max 100 char title, detailed description, 50 keywords",
            "istock": "Max 100 char title, detailed description, 50 keywords",
            "unsplash": "Natural description, focus on mood and usage",
            "pexels": "Clear descriptive title and tags",
        }

        prompt += f"\nPlatform Guidelines: {platform_guidelines.get(platform, 'Standard SEO best practices')}\n"

        prompt += """
Generate:
1. TITLE: SEO-optimized, descriptive, includes main keywords
2. DESCRIPTION: Detailed, natural language, searchable terms, commercial usage suggestions
3. KEYWORDS: 30-50 relevant keywords, mix of specific and broad terms
4. SEO_TAGS: Top 10 most important search terms
5. CATEGORIES: 2-3 relevant categories

Format as:
TITLE: [your title]
DESCRIPTION: [your description]
KEYWORDS: keyword1, keyword2, keyword3, ...
SEO_TAGS: tag1, tag2, tag3, ...
CATEGORIES: category1, category2, category3
"""
        return prompt

    def _parse_seo_response(self, content: str, platform: str) -> Dict:
        """Parse AI response into structured metadata."""
        result = {
            "title": "",
            "description": "",
            "keywords": [],
            "seo_tags": [],
            "categories": [],
        }

        lines = content.split("\n")
        current_field = None

        for line in lines:
            line = line.strip()
            if line.startswith("TITLE:"):
                result["title"] = line[6:].strip()
            elif line.startswith("DESCRIPTION:"):
                result["description"] = line[12:].strip()
            elif line.startswith("KEYWORDS:"):
                keywords_str = line[9:].strip()
                result["keywords"] = [k.strip() for k in keywords_str.split(",") if k.strip()]
            elif line.startswith("SEO_TAGS:"):
                tags_str = line[9:].strip()
                result["seo_tags"] = [t.strip() for t in tags_str.split(",") if t.strip()]
            elif line.startswith("CATEGORIES:"):
                cats_str = line[11:].strip()
                result["categories"] = [c.strip() for c in cats_str.split(",") if c.strip()]

        return result

    def _generate_fallback_metadata(self, theme: str, niche: Optional[str], platform: str) -> Dict:
        """Generate basic fallback metadata without AI."""
        title = theme.title()
        if niche:
            title = f"{niche.title()} {title}"

        description = f"High-quality {theme.lower()}"
        if niche:
            description += f" for {niche.lower()}"
        description += f". Perfect for commercial use, marketing, and creative projects."

        keywords = [
            theme.lower(),
            f"{theme.lower()} design",
            f"{theme.lower()} art",
            "creative",
            "professional",
        ]

        if niche:
            keywords.extend([niche.lower(), f"{niche.lower()} {theme.lower()}"])

        return {
            "title": title[:100],
            "description": description,
            "keywords": keywords[:30],
            "seo_tags": keywords[:10],
            "categories": [theme.lower(), niche.lower() if niche else "general"],
        }

    def generate_social_caption(
        self,
        theme: str,
        platform: str = "instagram",
        tone: str = "engaging",
        include_hashtags: bool = True,
        max_hashtags: int = 30,
    ) -> Dict:
        """Generate social media caption with hashtags."""
        if not self.client:
            return self._generate_fallback_caption(theme, platform, include_hashtags)

        try:
            prompt = f"""Generate an engaging social media caption for {platform}:

Theme/Content: {theme}
Tone: {tone}
Platform: {platform}

Requirements:
- {platform}-appropriate length and style
- Engaging and authentic
- Call-to-action if relevant
- {'Include relevant hashtags (max ' + str(max_hashtags) + ')' if include_hashtags else 'No hashtags'}

Format as:
CAPTION: [your caption text]
{f'HASHTAGS: #hashtag1 #hashtag2 #hashtag3 ...' if include_hashtags else ''}
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an expert social media content creator for {platform}. Create engaging, platform-appropriate captions.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.8,
            )

            content = response.choices[0].message.content
            return self._parse_caption_response(content)

        except Exception as e:
            logger.error(f"Caption generation failed: {e}")
            return self._generate_fallback_caption(theme, platform, include_hashtags)

    def _parse_caption_response(self, content: str) -> Dict:
        """Parse caption response."""
        result = {"caption": "", "hashtags": []}

        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("CAPTION:"):
                result["caption"] = line[8:].strip()
            elif line.startswith("HASHTAGS:"):
                hashtags_str = line[9:].strip()
                result["hashtags"] = [h.strip() for h in hashtags_str.split() if h.startswith("#")]

        return result

    def _generate_fallback_caption(self, theme: str, platform: str, include_hashtags: bool) -> Dict:
        """Generate simple fallback caption."""
        caption = f"Check out this amazing {theme}! 🎨✨"

        hashtags = []
        if include_hashtags:
            hashtags = [
                f"#{theme.replace(' ', '').lower()}",
                "#art",
                "#design",
                "#creative",
                "#digital art",
            ]

        return {"caption": caption, "hashtags": hashtags}

    def optimize_for_platform(self, metadata: Dict, source_platform: str, target_platform: str) -> Dict:
        """Adapt metadata from one platform format to another."""
        optimized = metadata.copy()

        # Platform-specific limits
        limits = {
            "shutterstock": {"title": 200, "description": 1000, "keywords": 50},
            "adobe_stock": {"title": 70, "description": 500, "keywords": 49},
            "getty_images": {"title": 100, "description": 2000, "keywords": 50},
            "unsplash": {"title": 100, "description": 500, "keywords": 20},
            "etsy": {"title": 140, "description": 5000, "keywords": 13},
        }

        target_limits = limits.get(target_platform, {"title": 100, "description": 1000, "keywords": 30})

        # Truncate/adapt
        if "title" in optimized and len(optimized["title"]) > target_limits["title"]:
            optimized["title"] = optimized["title"][: target_limits["title"] - 3] + "..."

        if "description" in optimized and len(optimized["description"]) > target_limits["description"]:
            optimized["description"] = optimized["description"][: target_limits["description"] - 3] + "..."

        if "keywords" in optimized and len(optimized["keywords"]) > target_limits["keywords"]:
            optimized["keywords"] = optimized["keywords"][: target_limits["keywords"]]

        return optimized

    def generate_bulk_variants(self, theme: str, count: int = 5) -> List[Dict]:
        """Generate multiple title/description variants for A/B testing."""
        variants = []

        base_metadata = self.generate_stock_metadata(theme)
        variants.append({**base_metadata, "variant_id": 1, "variant_type": "original"})

        # Generate additional variants
        for i in range(2, count + 1):
            variant = self.generate_stock_metadata(
                theme,
                platform="shutterstock",  # Use as default
            )
            variant["variant_id"] = i
            variant["variant_type"] = f"variant_{i}"
            variants.append(variant)

        return variants

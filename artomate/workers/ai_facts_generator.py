"""AI-powered facts generator for viral content."""

import json
from typing import Optional

from loguru import logger
from openai import OpenAI

from artomate.core.config import Config, get_config


class AIFactsGenerator:
    """Generates interesting facts and trivia using AI."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize facts generator.

        Args:
            config: Application configuration
        """
        self.config = config or get_config()
        self.client = OpenAI(api_key=self.config.openai_api_key)

    def generate_animal_facts(
        self,
        animal: str,
        count: int = 5,
        style: str = "fun",
    ) -> list[str]:
        """Generate interesting facts about an animal.

        Args:
            animal: Animal name (e.g., "cat", "elephant", "octopus")
            count: Number of facts to generate
            style: Style of facts ("fun", "educational", "shocking", "cute")

        Returns:
            List of facts

        Example:
            >>> generator = AIFactsGenerator()
            >>> facts = generator.generate_animal_facts("cat", count=3, style="fun")
            >>> print(facts)
            [
                "Cats spend 70% of their lives sleeping - that's 13-16 hours a day! 😴",
                "A cat's purr vibrates at 25-150 Hz, the same frequency used for healing bones! 🦴",
                "Cats can rotate their ears 180 degrees to hear prey from any direction! 👂"
            ]
        """
        logger.info(f"Generating {count} {style} facts about {animal}")

        # Style-specific prompts
        style_prompts = {
            "fun": "Generate fun and entertaining facts that make people smile",
            "educational": "Generate educational and scientific facts",
            "shocking": "Generate surprising and mind-blowing facts",
            "cute": "Generate adorable and heartwarming facts",
            "viral": "Generate viral-worthy facts that make people want to share",
        }

        style_instruction = style_prompts.get(style, style_prompts["fun"])

        prompt = f"""Generate {count} interesting facts about {animal}.

Style: {style_instruction}

Requirements:
- Each fact should be 1-2 sentences max
- Add relevant emoji at the end of each fact
- Make them shareable and memorable
- Perfect for social media (TikTok, Instagram, YouTube Shorts)
- Include surprising or little-known information
- Keep language simple and engaging

Return ONLY a JSON array of facts, nothing else.

Example format:
["Fact 1 with emoji 🐱", "Fact 2 with emoji 😺", "Fact 3 with emoji 🐾"]
"""

        try:
            response = self.client.chat.completions.create(
                model=self.config.openai_model or "gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a viral content creator who specializes in creating shareable animal facts for social media.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.8,  # More creative
                max_tokens=500,
            )

            content = response.choices[0].message.content.strip()

            # Parse JSON response
            facts = json.loads(content)

            if not isinstance(facts, list):
                raise ValueError("Response is not a list")

            logger.info(f"✓ Generated {len(facts)} facts about {animal}")

            return facts[:count]

        except Exception as e:
            logger.error(f"Failed to generate facts: {e}")

            # Fallback to generic facts
            return self._get_fallback_facts(animal, count)

    def _get_fallback_facts(self, animal: str, count: int) -> list[str]:
        """Get fallback facts if AI generation fails.

        Args:
            animal: Animal name
            count: Number of facts

        Returns:
            List of generic facts
        """
        generic_facts = {
            "cat": [
                "Cats spend 70% of their lives sleeping! 😴",
                "A group of cats is called a 'clowder'! 🐱",
                "Cats have over 20 different vocalizations! 🗣️",
                "A cat's purr can help heal bones! 🦴",
                "Cats can jump up to 6 times their length! 🏃",
            ],
            "dog": [
                "Dogs can smell 100,000 times better than humans! 👃",
                "A dog's sense of time is surprisingly accurate! ⏰",
                "Dogs can learn over 100 words and gestures! 🧠",
                "Puppies are born deaf and blind! 🐶",
                "Dogs have three eyelids! 👁️",
            ],
            "elephant": [
                "Elephants can't jump! 🐘",
                "An elephant's trunk has over 40,000 muscles! 💪",
                "Elephants mourn their dead like humans! 😢",
                "Elephants can hear each other from 5 miles away! 👂",
                "Elephants are pregnant for 22 months! 🤰",
            ],
            "octopus": [
                "Octopuses have three hearts! ❤️❤️❤️",
                "Octopuses can change color in 0.3 seconds! 🎨",
                "Octopuses have blue blood! 💙",
                "Each octopus arm has a mind of its own! 🧠",
                "Octopuses can squeeze through tiny holes! 🕳️",
            ],
        }

        # Try to find specific facts, otherwise use generic
        facts = generic_facts.get(animal.lower(), [
            f"Amazing {animal} fact! 🌟",
            f"Did you know {animal}s are incredible? 🤯",
            f"{animal.title()}s are fascinating creatures! ✨",
        ])

        return facts[:count]

    def generate_viral_hook(
        self,
        theme: str,
        duration: str = "short",
    ) -> str:
        """Generate viral hook for video intro.

        Args:
            theme: Theme/topic of video
            duration: "short" (3-5s) or "long" (7-10s)

        Returns:
            Hook text

        Example:
            >>> generator.generate_viral_hook("cats")
            "Did you know cats have a SECRET superpower? 🤯"
        """
        logger.info(f"Generating viral hook for: {theme}")

        duration_instruction = (
            "Keep it under 10 words, punchy and immediate"
            if duration == "short"
            else "Can be 15-20 words with buildup"
        )

        prompt = f"""Generate a VIRAL hook for a video about {theme}.

Duration: {duration_instruction}

Requirements:
- Start with attention-grabbing pattern: "Did you know...", "This will blow your mind...", "Nobody talks about...", etc.
- Create curiosity gap (make people NEED to watch)
- Use power words: secret, shocking, hidden, amazing, unbelievable
- Add relevant emoji
- Perfect for TikTok/Instagram Reels/YouTube Shorts

Return ONLY the hook text, nothing else.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.config.openai_model or "gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a viral video creator specializing in attention-grabbing hooks.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.9,  # Very creative
                max_tokens=100,
            )

            hook = response.choices[0].message.content.strip()

            logger.info(f"✓ Generated viral hook: {hook[:50]}...")

            return hook

        except Exception as e:
            logger.error(f"Failed to generate hook: {e}")

            # Fallback hooks
            fallbacks = [
                f"Did you know about {theme}? This will blow your mind! 🤯",
                f"Nobody talks about this {theme} secret... 🤫",
                f"This {theme} fact is SHOCKING! 😱",
                f"Wait for it... this {theme} fact is INSANE! 🔥",
            ]

            import random
            return random.choice(fallbacks)

    def generate_caption(
        self,
        theme: str,
        facts: list[str],
        platform: str = "instagram",
    ) -> str:
        """Generate engaging caption for social media.

        Args:
            theme: Video theme
            facts: List of facts shown in video
            platform: Platform (instagram, tiktok, youtube)

        Returns:
            Caption text with emojis and hashtags

        Example:
            >>> generator.generate_caption(
            ...     "cats",
            ...     ["Cats sleep 16 hours a day! 😴"],
            ...     platform="instagram"
            ... )
            "🐱 Mind-Blowing Cat Facts! 🤯\\n\\nDid you know...\\n✓ Cats sleep 16 hours a day!\\n..."
        """
        logger.info(f"Generating caption for {platform}")

        # Platform-specific max lengths
        max_lengths = {
            "instagram": 2200,
            "tiktok": 300,
            "youtube": 5000,
        }

        max_length = max_lengths.get(platform, 2200)

        # Build caption
        lines = [
            f"🌟 Amazing {theme.title()} Facts! 🤯",
            "",
            "Did you know...",
            "",
        ]

        # Add facts with checkmarks
        for i, fact in enumerate(facts[:5], 1):
            lines.append(f"{i}. {fact}")
            if i < len(facts):
                lines.append("")

        lines.extend([
            "",
            "Which fact surprised you most? Comment below! 👇",
            "",
            "Follow for more amazing facts! ❤️",
            "",
            "—",
        ])

        caption = "\n".join(lines)

        # Trim if needed
        if len(caption) > max_length:
            caption = caption[:max_length - 3] + "..."

        return caption

    def generate_hashtags(
        self,
        theme: str,
        niche: str,
        platform: str = "instagram",
    ) -> list[str]:
        """Generate optimized hashtags.

        Args:
            theme: Content theme
            niche: Content niche
            platform: Platform

        Returns:
            List of hashtags

        Example:
            >>> generator.generate_hashtags("cat", "pets", "instagram")
            ["#catfacts", "#cats", "#catsofinstagram", ...]
        """
        hashtags = []

        # Theme-specific
        theme_tag = theme.lower().replace(" ", "")
        hashtags.extend([
            f"#{theme_tag}facts",
            f"#{theme_tag}",
            f"#{theme_tag}lover",
            f"#{theme_tag}sofinstagram",
        ])

        # Niche-specific
        niche_tags = {
            "pets": ["#pets", "#petlover", "#petsofinstagram", "#petstagram"],
            "wildlife": ["#wildlife", "#nature", "#animals", "#wildlifeplanet"],
            "ocean": ["#ocean", "#marine", "#sealife", "#oceanlife"],
            "education": ["#didyouknow", "#facts", "#learning", "#education"],
        }

        if niche in niche_tags:
            hashtags.extend(niche_tags[niche])

        # Viral/engagement tags
        viral_tags = [
            "#viral",
            "#amazing",
            "#mindblown",
            "#interesting",
            "#cool",
            "#wow",
            "#reels",
            "#reelsinstagram",
            "#explore",
            "#explorepage",
            "#fyp",
            "#foryou",
            "#trending",
        ]

        hashtags.extend(viral_tags)

        # Platform limits
        limits = {
            "instagram": 30,
            "tiktok": 10,
            "youtube": 15,
        }

        limit = limits.get(platform, 30)

        return hashtags[:limit]

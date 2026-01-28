"""AI-powered SEO text generator using ChatGPT API."""

from typing import Dict, List, Optional

from loguru import logger
from openai import OpenAI

from artomate.core.config import Config, get_config
from artomate.db.models import Job


class SEOTextGenerator:
    """Generates SEO-optimized titles, descriptions, and tags using ChatGPT."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize SEO text generator.

        Args:
            config: Application configuration
        """
        self.config = config or get_config()
        self.client = OpenAI(api_key=self.config.openai_api_key)

    def generate_product_title(
        self,
        job: Job,
        product_name: str,
        platform: str = "printify",
        max_length: int = 80,
    ) -> str:
        """Generate SEO-optimized product title.

        Args:
            job: Job instance with prompt details
            product_name: Type of product (e.g., "Poster", "T-Shirt", "Mug")
            platform: Target platform ("printify", "etsy", "amazon")
            max_length: Maximum title length

        Returns:
            SEO-optimized title

        Example:
            >>> generator = SEOTextGenerator()
            >>> title = generator.generate_product_title(job, "Poster")
            >>> print(title)
            "Cat Lover Gift | Minimalist Cat Art Poster | Modern Home Decor"
        """
        logger.info(f"Generating SEO title for {product_name} on {platform}")

        system_prompt = f"""You are an expert at creating SEO-optimized product titles for e-commerce.

Platform: {platform.upper()}
Guidelines:
- Maximum length: {max_length} characters
- Include relevant keywords naturally
- Make it compelling and click-worthy
- Use separators (| or -) for readability
- Front-load the most important keywords
- Include the product type
- Be specific and descriptive

For Etsy: Focus on what the customer is searching for
For Printify/Shopify: Balance SEO and brand appeal
For Amazon: Use all characters, be very descriptive"""

        user_message = f"""Create an SEO-optimized product title for this product:

Product Type: {product_name}
Theme: {job.theme or 'modern'}
Style: {job.style or 'contemporary'}
Niche: {job.niche or 'home decor'}
Keywords: {', '.join(job.keywords or [])}

Generate ONLY the title text, no explanations."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=100,
            )

            title = response.choices[0].message.content.strip()
            
            # Remove quotes if present
            title = title.strip('"').strip("'")
            
            # Ensure max length
            if len(title) > max_length:
                title = title[:max_length-3] + "..."
                
            logger.info(f"✓ Generated title: {title}")
            return title

        except Exception as e:
            logger.error(f"Failed to generate title: {e}")
            # Fallback to simple title
            return f"{job.theme} {product_name} | {job.style or 'Modern'} {job.niche or 'Design'}"

    def generate_product_description(
        self,
        job: Job,
        product_name: str,
        platform: str = "printify",
        min_length: int = 200,
        max_length: int = 1000,
    ) -> str:
        """Generate SEO-optimized product description.

        Args:
            job: Job instance with prompt details
            product_name: Type of product
            platform: Target platform
            min_length: Minimum description length
            max_length: Maximum description length

        Returns:
            SEO-optimized description

        Example:
            >>> generator = SEOTextGenerator()
            >>> desc = generator.generate_product_description(job, "Poster")
        """
        logger.info(f"Generating SEO description for {product_name} on {platform}")

        system_prompt = f"""You are an expert at writing SEO-optimized product descriptions for e-commerce.

Platform: {platform.upper()}
Length: {min_length}-{max_length} characters

Guidelines:
- Start with a compelling hook
- Include relevant keywords naturally (don't stuff)
- Highlight benefits, not just features
- Use bullet points for readability
- Include product specifications
- Address customer pain points
- End with a call to action
- Use emotional language
- Be specific and descriptive

Format:
- Opening paragraph (2-3 sentences)
- Blank line
- "Perfect for:" section with use cases
- Blank line  
- "Features:" bullet points
- Blank line
- "Specifications:" bullet points
- Blank line
- Closing paragraph with CTA"""

        user_message = f"""Create an SEO-optimized product description for:

Product Type: {product_name}
Theme: {job.theme or 'modern'}
Style: {job.style or 'contemporary'}
Niche: {job.niche or 'home decor'}
Keywords: {', '.join(job.keywords or [])}

Target customer: Someone looking for {job.niche or 'home decor'} with {job.theme or 'modern'} aesthetic

Generate the full description, no meta-commentary."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=800,
            )

            description = response.choices[0].message.content.strip()
            
            # Ensure min/max length
            if len(description) < min_length:
                logger.warning(f"Description too short ({len(description)} chars), using fallback")
                return self._fallback_description(job, product_name)
            
            if len(description) > max_length:
                description = description[:max_length-3] + "..."
                
            logger.info(f"✓ Generated description ({len(description)} chars)")
            return description

        except Exception as e:
            logger.error(f"Failed to generate description: {e}")
            return self._fallback_description(job, product_name)

    def generate_product_tags(
        self,
        job: Job,
        product_name: str,
        platform: str = "printify",
        max_tags: int = 13,
    ) -> List[str]:
        """Generate SEO-optimized product tags.

        Args:
            job: Job instance with prompt details
            product_name: Type of product
            platform: Target platform
            max_tags: Maximum number of tags

        Returns:
            List of SEO-optimized tags

        Example:
            >>> generator = SEOTextGenerator()
            >>> tags = generator.generate_product_tags(job, "Poster", max_tags=10)
            >>> print(tags)
            ['cat art', 'minimalist poster', 'home decor', 'cat lover gift', ...]
        """
        logger.info(f"Generating {max_tags} SEO tags for {product_name} on {platform}")

        system_prompt = f"""You are an expert at generating SEO-optimized tags for e-commerce.

Platform: {platform.upper()}
Max tags: {max_tags}

Guidelines for {platform}:
"""

        if platform == "etsy":
            system_prompt += """
- Maximum 13 tags
- Each tag: 20 characters max
- Use multi-word phrases (2-3 words)
- Include long-tail keywords
- Mix broad and specific terms
- Think like the customer searches
- Include product type, style, occasion
"""
        else:
            system_prompt += """
- Focus on searchable keywords
- Mix single words and phrases
- Include product category
- Include style/theme descriptors
- Include target audience/occasion
- Be specific and relevant
"""

        system_prompt += """
Return ONLY a JSON array of strings, like:
["tag 1", "tag 2", "tag 3"]"""

        user_message = f"""Generate SEO tags for:

Product Type: {product_name}
Theme: {job.theme or 'modern'}
Style: {job.style or 'contemporary'}
Niche: {job.niche or 'home decor'}
Existing Keywords: {', '.join(job.keywords or [])}

Generate {max_tags} tags optimized for {platform}."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=300,
            )

            content = response.choices[0].message.content.strip()
            
            # Parse JSON array
            import json
            
            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            tags = json.loads(content)
            
            # Ensure it's a list
            if not isinstance(tags, list):
                raise ValueError("Response is not a list")
            
            # Convert to strings and limit
            tags = [str(tag).strip().lower() for tag in tags][:max_tags]
            
            # Remove duplicates while preserving order
            seen = set()
            unique_tags = []
            for tag in tags:
                if tag not in seen:
                    seen.add(tag)
                    unique_tags.append(tag)
            
            logger.info(f"✓ Generated {len(unique_tags)} tags: {unique_tags}")
            return unique_tags

        except Exception as e:
            logger.error(f"Failed to generate tags: {e}")
            return self._fallback_tags(job, product_name, max_tags)

    def generate_complete_seo_package(
        self,
        job: Job,
        product_name: str,
        platform: str = "printify",
    ) -> Dict[str, any]:
        """Generate complete SEO package: title, description, tags.

        Args:
            job: Job instance
            product_name: Type of product
            platform: Target platform

        Returns:
            Dictionary with 'title', 'description', 'tags'

        Example:
            >>> generator = SEOTextGenerator()
            >>> seo = generator.generate_complete_seo_package(job, "Poster", "etsy")
            >>> print(seo['title'])
            >>> print(seo['description'])
            >>> print(seo['tags'])
        """
        logger.info(f"Generating complete SEO package for {product_name} on {platform}")

        # Adjust parameters based on platform
        if platform == "etsy":
            max_title_length = 140
            max_tags = 13
        elif platform == "amazon":
            max_title_length = 200
            max_tags = 50
        else:  # printify, shopify
            max_title_length = 80
            max_tags = 15

        title = self.generate_product_title(
            job=job,
            product_name=product_name,
            platform=platform,
            max_length=max_title_length,
        )

        description = self.generate_product_description(
            job=job,
            product_name=product_name,
            platform=platform,
        )

        tags = self.generate_product_tags(
            job=job,
            product_name=product_name,
            platform=platform,
            max_tags=max_tags,
        )

        return {
            "title": title,
            "description": description,
            "tags": tags,
        }

    def _fallback_description(self, job: Job, product_name: str) -> str:
        """Generate fallback description if AI fails."""
        parts = [
            f"Beautiful {job.theme or 'modern'} design in {job.style or 'contemporary'} style.",
            "",
            f"Perfect for {job.niche or 'any space'}!",
            "",
            "Features:",
            f"• High-quality {product_name}",
            "• Premium materials",
            "• Unique design",
            "• Fast shipping",
            "",
            "Specifications:",
            "• Professional printing",
            "• Vibrant colors",
            "• Durable quality",
            "",
            "Care instructions: Follow product care label.",
        ]
        return "\n".join(parts)

    def _fallback_tags(self, job: Job, product_name: str, max_tags: int) -> List[str]:
        """Generate fallback tags if AI fails."""
        tags = []

        # Add theme
        if job.theme:
            tags.append(job.theme.lower())

        # Add style
        if job.style:
            tags.append(job.style.lower())

        # Add niche
        if job.niche:
            tags.append(job.niche.lower())

        # Add keywords
        if job.keywords:
            tags.extend([k.lower() for k in job.keywords if isinstance(k, str)])

        # Add product name
        tags.append(product_name.lower())

        # Add generic tags
        tags.extend(["unique", "gift", "art", "design", "home decor"])

        # Remove duplicates and limit
        tags = list(dict.fromkeys(tags))[:max_tags]

        return tags

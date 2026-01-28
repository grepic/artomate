"""Etsy marketplace worker."""

from pathlib import Path
from typing import Optional

from loguru import logger

from artomate.core.config import Config, get_config
from artomate.db.database import get_db
from artomate.db.models import Asset, Job, MarketplaceListing, MarketplaceType, Product
from artomate.integrations.etsy_client import EtsyClient
from artomate.workers.seo_text_generator import SEOTextGenerator


class EtsyWorker:
    """Creates and manages Etsy listings."""

    def __init__(self, config: Optional[Config] = None, use_ai_seo: bool = True):
        """Initialize Etsy worker.

        Args:
            config: Application configuration
            use_ai_seo: If True, use AI-powered SEO text generation (requires OpenAI API key)
        """
        self.config = config or get_config()
        self.db = get_db()
        self.etsy = EtsyClient()
        self.use_ai_seo = use_ai_seo and self.config.openai_api_key
        
        if self.use_ai_seo:
            self.seo_generator = SEOTextGenerator(config)
            logger.info("✓ AI-powered SEO text generation enabled for Etsy")
        else:
            self.seo_generator = None
            if use_ai_seo:
                logger.warning("Etsy AI SEO disabled: OPENAI_API_KEY not set")

    def create_listing_for_product(
        self,
        product: Product,
        job: Job,
        images: Optional[list[Asset]] = None,
    ) -> MarketplaceListing:
        """Create Etsy listing for a Printify product.

        Args:
            product: Product instance
            job: Job instance
            images: Optional list of image assets for gallery

        Returns:
            Created MarketplaceListing instance

        Raises:
            RuntimeError: If listing creation fails
        """
        logger.info(f"Creating Etsy listing for product {product.id}")

        # Generate optimized title and description
        title = self.optimize_title(product.title, job)
        description = self.optimize_description(product.description, job)
        tags = self.optimize_tags(product.tags or [], job)

        # Find taxonomy
        taxonomy_id = self.etsy.find_taxonomy_for_niche(job.niche or "wall-art")

        try:
            # Create listing
            listing_data = self.etsy.create_listing(
                title=title,
                description=description,
                price=product.selling_price or 19.99,
                quantity=999,  # Made to order
                taxonomy_id=taxonomy_id,
                who_made="i_did",
                when_made="made_to_order",
                tags=tags,
            )

            listing_id = listing_data["listing_id"]

            # Upload images if provided
            image_urls = []
            if images:
                for idx, image_asset in enumerate(images[:10], start=1):  # Etsy allows max 10
                    try:
                        self.etsy.upload_listing_image(
                            listing_id=listing_id,
                            image_path=image_asset.storage_path,
                            rank=idx,
                        )
                        if image_asset.storage_url:
                            image_urls.append(image_asset.storage_url)
                    except Exception as e:
                        logger.warning(f"Failed to upload image {idx}: {e}")

            # Create marketplace listing record
            listing = MarketplaceListing(
                product_id=product.id,
                job_id=job.id,
                marketplace=MarketplaceType.ETSY,
                marketplace_listing_id=str(listing_id),
                title=title,
                description=description,
                tags=tags,
                category=f"taxonomy_{taxonomy_id}",
                seo_title=title,
                seo_keywords=tags,
                status="active",
                listing_url=f"https://www.etsy.com/listing/{listing_id}",
                image_urls=image_urls,
                price=product.selling_price,
                currency="USD",
                listing_data={
                    "taxonomy_id": taxonomy_id,
                    "who_made": "i_did",
                    "when_made": "made_to_order",
                    "etsy_response": listing_data,
                },
            )

            with self.db.session_scope() as session:
                session.add(listing)
                session.flush()
                session.expunge(listing)

            logger.info(f"✓ Created Etsy listing: {listing_id}")

            return listing

        except Exception as e:
            logger.error(f"Failed to create Etsy listing: {e}")
            raise RuntimeError(f"Etsy listing creation failed: {e}")

    def optimize_title(self, base_title: str, job: Job) -> str:
        """Optimize title for Etsy SEO.

        Args:
            base_title: Base title
            job: Job instance

        Returns:
            Optimized title (max 140 chars)
        """
        # Use AI-powered SEO if available
        if self.use_ai_seo and self.seo_generator:
            try:
                # Extract product name from base title
                product_name = base_title.split("|")[-1].strip() if "|" in base_title else "Product"
                return self.seo_generator.generate_product_title(
                    job=job,
                    product_name=product_name,
                    platform="etsy",
                    max_length=140,
                )
            except Exception as e:
                logger.warning(f"AI title optimization failed: {e}, using fallback")
        
        # Fallback to rule-based optimization
        # Etsy SEO best practices:
        # - Front-load keywords
        # - Include key terms: theme, style, product type
        # - Use vertical bars |

        parts = []

        # Start with theme (most specific)
        if job.theme:
            parts.append(job.theme.title())

        # Add style
        if job.style:
            parts.append(job.style.title())

        # Add niche
        if job.niche:
            niche_names = {
                "wall-art": "Wall Art",
                "apparel": "Clothing",
                "home-decor": "Home Decor",
            }
            parts.append(niche_names.get(job.niche, job.niche.title()))

        # Add product type from base title
        if "|" in base_title:
            product_type = base_title.split("|")[-1].strip()
            parts.append(product_type)

        title = " | ".join(parts)

        # Add generic keywords at end if space
        if len(title) < 120:
            title += " | Unique Gift"

        # Limit to 140
        return title[:140]

    def optimize_description(self, base_description: str, job: Job) -> str:
        """Optimize description for Etsy.

        Args:
            base_description: Base description
            job: Job instance

        Returns:
            Optimized description
        """
        # Use AI-powered SEO if available
        if self.use_ai_seo and self.seo_generator:
            try:
                return self.seo_generator.generate_product_description(
                    job=job,
                    product_name="product",
                    platform="etsy",
                )
            except Exception as e:
                logger.warning(f"AI description optimization failed: {e}, using fallback")
        
        # Fallback to template-based description
        parts = [
            "✨ ABOUT THIS ITEM",
            "",
            base_description,
            "",
            "🎨 DESIGN",
            f"This unique {job.theme} design features a {job.style or 'modern'} aesthetic.",
            "Created with care and attention to detail.",
            "",
            "📦 SHIPPING & PRODUCTION",
            "• Made to order",
            "• High-quality printing",
            "• Fast processing",
            "• Secure packaging",
            "",
            "💝 PERFECT FOR",
            f"• {job.niche or 'Home decor'} enthusiasts",
            "• Unique gift giving",
            "• Personal collections",
            "• Interior design",
            "",
            "❓ QUESTIONS?",
            "Feel free to message us with any questions!",
            "",
            "⭐ Thank you for visiting our shop!",
        ]

        return "\n".join(parts)

    def optimize_tags(self, base_tags: list[str], job: Job) -> list[str]:
        """Optimize tags for Etsy SEO.

        Args:
            base_tags: Base tags
            job: Job instance

        Returns:
            Optimized tags (max 13)
        """
        # Use AI-powered SEO if available
        if self.use_ai_seo and self.seo_generator:
            try:
                return self.seo_generator.generate_product_tags(
                    job=job,
                    product_name="product",
                    platform="etsy",
                    max_tags=13,
                )
            except Exception as e:
                logger.warning(f"AI tags optimization failed: {e}, using fallback")
        
        # Fallback to rule-based tags
        tags = set()

        # Priority tags
        if job.theme:
            tags.add(job.theme.lower())
            # Add plural if singular
            if not job.theme.endswith("s"):
                tags.add(f"{job.theme.lower()}s")

        if job.style:
            tags.add(job.style.lower())

        if job.niche:
            tags.add(job.niche.lower().replace("-", " "))

        # Add base tags
        tags.update(t.lower() for t in base_tags if t)

        # Add high-performing Etsy tags
        generic_tags = [
            "unique gift",
            "handmade",
            "custom",
            "art print",
            "wall decor",
            "home decor",
            "gift idea",
        ]

        for tag in generic_tags:
            if len(tags) >= 13:
                break
            tags.add(tag)

        # Convert to list and limit
        return list(tags)[:13]

    def update_listing_stats(self, listing: MarketplaceListing) -> MarketplaceListing:
        """Update listing statistics from Etsy.

        Args:
            listing: Listing instance

        Returns:
            Updated listing

        Note:
            Etsy API has limited stats access. This is a placeholder
            for future implementation when using OAuth.
        """
        if not listing.marketplace_listing_id:
            return listing

        try:
            listing_data = self.etsy.get_listing(int(listing.marketplace_listing_id))

            # Update views, favorites if available
            # Note: Requires OAuth and shop ownership
            if "views" in listing_data:
                listing.views_count = listing_data["views"]

            if "num_favorers" in listing_data:
                listing.favorites_count = listing_data["num_favorers"]

            with self.db.session_scope() as session:
                session.add(listing)

            logger.info(f"✓ Updated stats for listing {listing.id}")

        except Exception as e:
            logger.warning(f"Failed to update stats for listing {listing.id}: {e}")

        return listing

    def deactivate_listing(self, listing: MarketplaceListing) -> bool:
        """Deactivate (delete) listing on Etsy.

        Args:
            listing: Listing to deactivate

        Returns:
            True if deactivated
        """
        if not listing.marketplace_listing_id:
            return False

        try:
            self.etsy.delete_listing(int(listing.marketplace_listing_id))

            listing.status = "inactive"

            with self.db.session_scope() as session:
                session.add(listing)

            logger.info(f"✓ Deactivated listing {listing.id}")

            return True

        except Exception as e:
            logger.error(f"Failed to deactivate listing {listing.id}: {e}")
            return False

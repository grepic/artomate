"""Printify product creation worker."""

from typing import Optional

from loguru import logger

from artomate.core.config import Config, get_config
from artomate.db.database import get_db
from artomate.db.models import Asset, Job, PrintFile, Product
from artomate.integrations.printify_client import PrintifyClient
from artomate.workers.render_engine import RenderEngine
from artomate.workers.printify_product_catalog import PRINTIFY_PRODUCTS, get_all_product_ids


class PrintifyWorker:
    """Creates and manages Printify products."""

    # Use comprehensive product catalog
    BLUEPRINT_SPECS = PRINTIFY_PRODUCTS

    def __init__(self, config: Optional[Config] = None):
        """Initialize Printify worker.

        Args:
            config: Application configuration
        """
        self.config = config or get_config()
        self.db = get_db()
        self.printify = PrintifyClient()
        self.renderer = RenderEngine(config)

    def calculate_price(self, base_cost: float) -> float:
        """Calculate selling price with markup.

        Args:
            base_cost: Base cost from Printify

        Returns:
            Selling price rounded to .99
        """
        markup = base_cost * (self.config.markup_percentage / 100)
        total = base_cost + markup

        # Ensure minimum profit
        if markup < self.config.minimum_profit:
            total = base_cost + self.config.minimum_profit

        # Round to .99
        whole = int(total)
        return whole + self.config.round_prices_to

    def create_product_for_job(
        self,
        job: Job,
        asset: Asset,
        product_types: Optional[list[str]] = None,
    ) -> list[Product]:
        """Create Printify products for a job.

        Args:
            job: Job instance
            asset: Primary asset to use
            product_types: List of product types to create (e.g., ["tshirt", "poster_12x18"])
                          If None, uses config defaults

        Returns:
            List of created Product instances

        Raises:
            RuntimeError: If product creation fails
        """
        if product_types is None:
            # Default to common products
            product_types = ["tshirt", "poster_18x24", "mug"]

        products = []

        for product_type in product_types:
            try:
                product = self.create_product(
                    job=job,
                    asset=asset,
                    product_type=product_type,
                )
                products.append(product)
                logger.info(f"✓ Created {product_type} product {product.id}")

            except Exception as e:
                logger.error(f"Failed to create {product_type} for job {job.id}: {e}")
                continue

        if not products:
            raise RuntimeError(f"Failed to create any products for job {job.id}")

        return products

    def create_product(
        self,
        job: Job,
        asset: Asset,
        product_type: str,
    ) -> Product:
        """Create a single Printify product.

        Args:
            job: Job instance
            asset: Asset to use
            product_type: Product type key (e.g., "tshirt", "poster_12x18")

        Returns:
            Created Product instance

        Raises:
            ValueError: If product type not found
            RuntimeError: If creation fails
        """
        if product_type not in self.BLUEPRINT_SPECS:
            raise ValueError(f"Unknown product type: {product_type}")

        spec = self.BLUEPRINT_SPECS[product_type]

        logger.info(f"Creating {product_type} for job {job.id}")

        # Determine if transparent background needed
        needs_transparent = spec["coverage_type"] == "transparent"

        # Determine crop mode based on coverage type
        if spec["coverage_type"] == "full":
            crop_mode = "cover"  # Fill entire area
        elif spec["coverage_type"] == "centered":
            crop_mode = "contain"  # Center design with borders
        else:  # transparent
            crop_mode = "contain"  # Center design on transparent

        logger.info(
            f"Product specs: {spec['name']} - "
            f"{spec['print_area']['width']}x{spec['print_area']['height']}px, "
            f"{spec['coverage_type']}, transparent={needs_transparent}"
        )

        # Step 1: Render print file for this product
        print_file = self.renderer.create_print_file(
            asset=asset,
            target_width=spec["print_area"]["width"],
            target_height=spec["print_area"]["height"],
            crop_mode=crop_mode,
            dpi=spec["dpi"],
            printify_blueprint_id=spec["blueprint_id"],
            printify_provider_id=spec["provider_id"],
            transparent_background=needs_transparent,
            remove_white_bg=needs_transparent,  # Auto-remove white BG for transparent products
        )

        # Step 2: Upload image to Printify
        upload_response = self.printify.upload_image(print_file.storage_path)
        image_id = upload_response["id"]

        # Step 3: Get blueprint variants
        variants_data = self.printify.get_blueprint_variants(
            blueprint_id=spec["blueprint_id"],
            print_provider_id=spec["provider_id"],
        )

        # Step 4: Configure variants with pricing
        variants = []
        for variant in variants_data.get("variants", []):
            # Get base cost (in cents, convert to dollars)
            base_cost = variant.get("cost", 0) / 100
            selling_price_dollars = self.calculate_price(base_cost)
            selling_price_cents = int(selling_price_dollars * 100)

            variants.append({
                "id": variant["id"],
                "price": selling_price_cents,
                "is_enabled": True,
            })

        # Step 5: Configure print areas
        print_areas = [
            {
                "variant_ids": [v["id"] for v in variants],
                "placeholders": [
                    {
                        "position": "front",
                        "images": [
                            {
                                "id": image_id,
                                "x": 0.5,  # Center
                                "y": 0.5,
                                "scale": 1.0,
                                "angle": 0,
                            }
                        ],
                    }
                ],
            }
        ]

        # Step 6: Generate title and description
        title = self.generate_title(job, spec["name"])
        description = self.generate_description(job, spec["name"])
        tags = self.generate_tags(job)

        # Step 7: Create product in Printify
        printify_product = self.printify.create_product(
            title=title,
            description=description,
            blueprint_id=spec["blueprint_id"],
            print_provider_id=spec["provider_id"],
            variants=variants,
            print_areas=print_areas,
            tags=tags,
        )

        # Step 8: Save product to database
        avg_base_cost = sum(v.get("price", 0) / 100 for v in variants) / len(variants)
        avg_selling_price = self.calculate_price(avg_base_cost)
        profit_margin = ((avg_selling_price - avg_base_cost) / avg_base_cost) * 100

        product = Product(
            job_id=job.id,
            title=title,
            description=description,
            tags=tags,
            printify_product_id=printify_product["id"],
            printify_blueprint_id=spec["blueprint_id"],
            printify_shop_id=self.config.printify_shop_id,
            printify_status="unpublished",
            base_cost=avg_base_cost,
            selling_price=avg_selling_price,
            profit_margin=profit_margin,
            primary_asset_id=asset.id,
            print_file_ids=[print_file.id],
            product_data={
                "product_type": product_type,
                "printify_image_id": image_id,
                "variant_count": len(variants),
            },
        )

        with self.db.session_scope() as session:
            session.add(product)
            session.flush()
            session.expunge(product)

        logger.info(f"✓ Created Printify product: {printify_product['id']}")

        return product

    def publish_product(self, product: Product) -> bool:
        """Publish product to connected sales channel.

        Args:
            product: Product to publish

        Returns:
            True if published successfully

        Raises:
            RuntimeError: If publishing fails
        """
        if not product.printify_product_id:
            raise RuntimeError("Product has no Printify ID")

        logger.info(f"Publishing product {product.id} to sales channel")

        try:
            self.printify.publish_product(
                product_id=product.printify_product_id,
                title=product.title,
                description=product.description,
                tags=product.tags,
            )

            # Update status
            with self.db.session_scope() as session:
                db_product = session.query(Product).filter(Product.id == product.id).first()
                if db_product:
                    db_product.printify_status = "published"
                    session.add(db_product)

            logger.info(f"✓ Published product {product.id}")

            return True

        except Exception as e:
            logger.error(f"Failed to publish product {product.id}: {e}")
            raise RuntimeError(f"Publishing failed: {e}")

    def generate_title(self, job: Job, product_name: str) -> str:
        """Generate SEO-optimized product title.

        Args:
            job: Job instance
            product_name: Product type name

        Returns:
            SEO title
        """
        # Use template from config
        template = self.config.seo_title_template

        title = template.format(
            theme=job.theme.title(),
            style=(job.style or "Modern").title(),
            niche=(job.niche or "Art").title(),
        )

        # Add product type
        title = f"{title} - {product_name}"

        # Limit length
        if len(title) > 140:
            title = title[:137] + "..."

        return title

    def generate_description(self, job: Job, product_name: str) -> str:
        """Generate product description.

        Args:
            job: Job instance
            product_name: Product type name

        Returns:
            Product description
        """
        parts = [
            f"Beautiful {job.theme} design in {job.style or 'modern'} style.",
            "",
            f"Perfect for {job.niche or 'any space'}!",
            "",
            "Features:",
            f"• High-quality {product_name}",
            "• Premium materials",
            "• Unique design",
            "• Fast shipping",
            "",
            "Care instructions: Follow product care label.",
        ]

        return "\n".join(parts)

    def generate_tags(self, job: Job) -> list[str]:
        """Generate product tags.

        Args:
            job: Job instance

        Returns:
            List of tags (limited by config)
        """
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

        # Add generic tags
        tags.extend(["unique", "gift", "art", "design"])

        # Remove duplicates and limit
        tags = list(dict.fromkeys(tags))  # Remove duplicates, preserve order
        tags = tags[: self.config.seo_max_tags]

        return tags

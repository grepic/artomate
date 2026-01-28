"""Printify product creation worker."""

from typing import Optional

from loguru import logger

from artomate.core.config import Config, get_config
from artomate.db.database import get_db
from artomate.db.models import Asset, Job, PrintFile, Product
from artomate.integrations.printify_client import PrintifyClient
from artomate.workers.render_engine import RenderEngine
from artomate.workers.printify_product_catalog import PRINTIFY_PRODUCTS, get_all_product_ids
from artomate.workers.printify_product_families import PRODUCT_FAMILIES, get_all_family_ids
from artomate.workers.seo_text_generator import SEOTextGenerator


class PrintifyWorker:
    """Creates and manages Printify products."""

    # Use comprehensive product catalog
    BLUEPRINT_SPECS = PRINTIFY_PRODUCTS

    def __init__(self, config: Optional[Config] = None, use_ai_seo: bool = True):
        """Initialize Printify worker.

        Args:
            config: Application configuration
            use_ai_seo: If True, use AI-powered SEO text generation (requires OpenAI API key)
        """
        self.config = config or get_config()
        self.db = get_db()
        self.printify = PrintifyClient()
        self.renderer = RenderEngine(config)
        self.use_ai_seo = use_ai_seo and self.config.openai_api_key
        
        if self.use_ai_seo:
            self.seo_generator = SEOTextGenerator(config)
            logger.info("✓ AI-powered SEO text generation enabled")
        else:
            self.seo_generator = None
            if use_ai_seo:
                logger.warning("AI SEO disabled: OPENAI_API_KEY not set")
        self.use_ai_seo = use_ai_seo and self.config.openai_api_key
        
        if self.use_ai_seo:
            self.seo_generator = SEOTextGenerator(config)
            logger.info("✓ AI-powered SEO text generation enabled")
        else:
            self.seo_generator = None
            if use_ai_seo:
                logger.warning("AI SEO disabled: OPENAI_API_KEY not set")

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
        """Create Printify products for a job (legacy method).

        NOTE: This creates single-variant products. For ALL variants, use
        create_product_families_for_job() instead.

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

    def create_product_families_for_job(
        self,
        job: Job,
        asset: Asset,
        family_ids: Optional[list[str]] = None,
        create_all_variants: bool = True,
    ) -> list[Product]:
        """Create Printify product families with ALL variants for a job.

        This is the RECOMMENDED method - creates products with all size/color options.

        Args:
            job: Job instance
            asset: Primary asset to use
            family_ids: List of family IDs (e.g., ["poster", "canvas", "tshirt"])
                       If None, uses common defaults
            create_all_variants: If True, creates optimized print file for each size.
                                If False, uses one file for all (Printify scales).

        Returns:
            List of created Product instances (each with multiple variants)

        Raises:
            RuntimeError: If product creation fails

        Example:
            >>> worker = PrintifyWorker()
            >>> products = worker.create_product_families_for_job(
            ...     job=job,
            ...     asset=cat_image,
            ...     family_ids=["poster", "canvas", "tshirt"]
            ... )
            >>> # Creates 3 products:
            >>> # - Poster (6 size variants)
            >>> # - Canvas (9 size variants)
            >>> # - T-shirt (all colors/sizes)
        """
        if family_ids is None:
            # Default to common product families
            family_ids = ["tshirt", "poster", "mug"]

        products = []

        for family_id in family_ids:
            try:
                product = self.create_product_family(
                    job=job,
                    asset=asset,
                    family_id=family_id,
                    create_all_variants=create_all_variants,
                )
                products.append(product)
                logger.info(f"✓ Created {family_id} family product {product.id}")

            except Exception as e:
                logger.error(f"Failed to create {family_id} family for job {job.id}: {e}")
                continue

        if not products:
            raise RuntimeError(f"Failed to create any product families for job {job.id}")

        logger.info(
            f"✓ Created {len(products)} product families for job {job.id} "
            f"(total variants across all products)"
        )

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

    def create_product_family(
        self,
        job: Job,
        asset: Asset,
        family_id: str,
        create_all_variants: bool = True,
    ) -> Product:
        """Create Printify product with ALL size/color variants.

        This creates ONE Printify product with MULTIPLE variants (all sizes).
        For example, "poster" family creates 1 product with 6 size options:
        8x10, 12x16, 12x18, 16x20, 18x24, 24x36.

        Args:
            job: Job instance
            asset: Asset to use
            family_id: Product family ID (e.g., "poster", "canvas", "tshirt")
            create_all_variants: If True, creates optimized print file for EACH variant.
                                If False, uses largest variant for all (Printify scales).

        Returns:
            Created Product instance with all variants

        Raises:
            ValueError: If family not found
            RuntimeError: If creation fails

        Example:
            >>> worker = PrintifyWorker()
            >>> product = worker.create_product_family(job, asset, "poster")
            >>> # Creates 1 product with 6 size options (8x10 to 24x36)
        """
        if family_id not in PRODUCT_FAMILIES:
            raise ValueError(f"Unknown product family: {family_id}")

        family = PRODUCT_FAMILIES[family_id]

        logger.info(
            f"Creating product family '{family_id}' ({family['name']}) "
            f"with {len(family['variants'])} variants for job {job.id}"
        )

        # Determine if transparent background needed
        needs_transparent = family["coverage_type"] == "transparent"

        # Determine crop mode based on coverage type
        if family["coverage_type"] == "full":
            crop_mode = "cover"  # Fill entire area
        elif family["coverage_type"] == "centered":
            crop_mode = "contain"  # Center design with borders
        else:  # transparent
            crop_mode = "contain"  # Center design on transparent

        # Step 1: Create print files for variants
        print_files = []
        variant_print_file_map = {}  # Maps variant_id to print_file

        if create_all_variants and len(family["variants"]) > 1:
            # Create optimized print file for EACH variant (maximum quality)
            logger.info(f"Creating {len(family['variants'])} optimized print files...")

            for variant in family["variants"]:
                logger.info(
                    f"  Creating print file for {variant['name']} "
                    f"({variant['width']}x{variant['height']}px)"
                )

                print_file = self.renderer.create_print_file(
                    asset=asset,
                    target_width=variant["width"],
                    target_height=variant["height"],
                    crop_mode=crop_mode,
                    dpi=family["dpi"],
                    printify_blueprint_id=family["blueprint_id"],
                    printify_provider_id=family["provider_id"],
                    transparent_background=needs_transparent,
                    remove_white_bg=needs_transparent,
                )

                print_files.append(print_file)
                variant_print_file_map[variant["variant_id"]] = print_file

            logger.info(f"✓ Created {len(print_files)} print files")

        else:
            # Create 1 print file for largest variant, use for all (efficient)
            largest_variant = max(family["variants"], key=lambda v: v["width"] * v["height"])

            logger.info(
                f"Creating 1 print file for largest variant {largest_variant['name']} "
                f"({largest_variant['width']}x{largest_variant['height']}px)"
            )

            print_file = self.renderer.create_print_file(
                asset=asset,
                target_width=largest_variant["width"],
                target_height=largest_variant["height"],
                crop_mode=crop_mode,
                dpi=family["dpi"],
                printify_blueprint_id=family["blueprint_id"],
                printify_provider_id=family["provider_id"],
                transparent_background=needs_transparent,
                remove_white_bg=needs_transparent,
            )

            print_files.append(print_file)

            # Use same print file for all variants
            for variant in family["variants"]:
                variant_print_file_map[variant["variant_id"]] = print_file

            logger.info("✓ Created 1 print file (will be scaled for all variants)")

        # Step 2: Upload images to Printify
        uploaded_images = {}
        for variant_id, print_file in variant_print_file_map.items():
            if print_file.storage_path not in uploaded_images:
                logger.info(f"Uploading print file: {print_file.storage_path}")
                upload_response = self.printify.upload_image(print_file.storage_path)
                uploaded_images[print_file.storage_path] = upload_response["id"]

        # If multiple print files, use first one for now (can be enhanced)
        # TODO: Support different images per variant in Printify API
        primary_image_id = list(uploaded_images.values())[0]

        logger.info(f"✓ Uploaded {len(uploaded_images)} image(s) to Printify")

        # Step 3: Get blueprint variants from Printify
        variants_data = self.printify.get_blueprint_variants(
            blueprint_id=family["blueprint_id"],
            print_provider_id=family["provider_id"],
        )

        # Step 4: Configure ALL variants with pricing
        variants = []
        variant_count = 0

        for variant in variants_data.get("variants", []):
            # Get base cost (in cents, convert to dollars)
            base_cost = variant.get("cost", 0) / 100
            selling_price_dollars = self.calculate_price(base_cost)
            selling_price_cents = int(selling_price_dollars * 100)

            variants.append({
                "id": variant["id"],
                "price": selling_price_cents,
                "is_enabled": True,  # Enable ALL variants!
            })

            variant_count += 1

        logger.info(f"✓ Configured {variant_count} Printify variants with pricing")

        # Step 5: Configure print areas
        print_areas = [
            {
                "variant_ids": [v["id"] for v in variants],
                "placeholders": [
                    {
                        "position": "front",
                        "images": [
                            {
                                "id": primary_image_id,
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
        title = self.generate_title(job, family["name"])
        description = self.generate_description(job, family["name"])
        tags = self.generate_tags(job)

        # Step 7: Create product in Printify
        logger.info(f"Creating Printify product with {variant_count} variants...")

        printify_product = self.printify.create_product(
            title=title,
            description=description,
            blueprint_id=family["blueprint_id"],
            print_provider_id=family["provider_id"],
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
            printify_blueprint_id=family["blueprint_id"],
            printify_shop_id=self.config.printify_shop_id,
            printify_status="unpublished",
            base_cost=avg_base_cost,
            selling_price=avg_selling_price,
            profit_margin=profit_margin,
            primary_asset_id=asset.id,
            print_file_ids=[pf.id for pf in print_files],
            product_data={
                "product_family": family_id,
                "family_name": family["name"],
                "variant_count": variant_count,
                "size_variants": [v["name"] for v in family["variants"]],
                "printify_image_ids": list(uploaded_images.values()),
                "created_all_print_files": create_all_variants,
            },
        )

        with self.db.session_scope() as session:
            session.add(product)
            session.flush()
            session.expunge(product)

        logger.info(
            f"✓ Created product family '{family_id}': {printify_product['id']} "
            f"with {variant_count} variants ({len(print_files)} print files)"
        )

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
        # Use AI-powered SEO if available
        if self.use_ai_seo and self.seo_generator:
            try:
                return self.seo_generator.generate_product_title(
                    job=job,
                    product_name=product_name,
                    platform="printify",
                )
            except Exception as e:
                logger.warning(f"AI title generation failed: {e}, using fallback")
        
        # Fallback to template-based title
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
        # Use AI-powered SEO if available
        if self.use_ai_seo and self.seo_generator:
            try:
                return self.seo_generator.generate_product_description(
                    job=job,
                    product_name=product_name,
                    platform="printify",
                )
            except Exception as e:
                logger.warning(f"AI description generation failed: {e}, using fallback")
        
        # Fallback to simple description
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
        # Use AI-powered SEO if available
        if self.use_ai_seo and self.seo_generator:
            try:
                return self.seo_generator.generate_product_tags(
                    job=job,
                    product_name="product",
                    platform="printify",
                    max_tags=self.config.seo_max_tags,
                )
            except Exception as e:
                logger.warning(f"AI tags generation failed: {e}, using fallback")
        
        # Fallback to simple tags
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

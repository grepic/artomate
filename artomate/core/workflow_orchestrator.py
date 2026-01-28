"""Complete workflow orchestrator for end-to-end automation."""

from typing import Optional, Callable
from datetime import datetime

from loguru import logger

from artomate.core.config import Config, get_config
from artomate.core.job_manager import JobManager
from artomate.core.state_machine import StateMachine
from artomate.db.models import Job, JobState, SocialPlatform
from artomate.workers.enhanced_image_generator import EnhancedImageGenerator
from artomate.workers.render_engine import RenderEngine
from artomate.workers.printify_worker import PrintifyWorker
from artomate.workers.etsy_worker import EtsyWorker
from artomate.workers.video_generator import VideoGenerator
from artomate.workers.social_media_publisher import SocialMediaPublisher
from artomate.workers.stock_platforms import StockPlatformWorker
from artomate.integrations.telegram_notifier import get_telegram_notifier
from artomate.utils.logger import get_logger_with_context, set_correlation_id, clear_correlation_id
from artomate.utils.circuit_breaker import CircuitBreakerError


class WorkflowOrchestrator:
    """Orchestrates complete content-to-commerce workflow."""

    def __init__(
        self,
        config: Optional[Config] = None,
        progress_callback: Optional[Callable[[str, float], None]] = None,
    ):
        """Initialize workflow orchestrator.

        Args:
            config: Application configuration
            progress_callback: Optional callback for progress updates
                              (message: str, progress: float 0-1)
        """
        self.config = config or get_config()
        self.progress_callback = progress_callback

        # Initialize workers
        self.job_manager = JobManager(config)
        self.image_generator = EnhancedImageGenerator(config)
        self.render_engine = RenderEngine(config)
        self.printify_worker = PrintifyWorker(config)
        self.etsy_worker = EtsyWorker(config)
        self.video_generator = VideoGenerator(config)
        self.social_publisher = SocialMediaPublisher(config)
        self.stock_worker = StockPlatformWorker(config)
        self.telegram_notifier = get_telegram_notifier()

    def _update_progress(self, message: str, progress: float):
        """Update progress."""
        logger.info(f"Progress {progress*100:.0f}%: {message}")
        if self.progress_callback:
            self.progress_callback(message, progress)

    def run_complete_workflow(
        self,
        job_id: int,
        options: Optional[dict] = None,
    ) -> dict:
        """Run complete workflow from start to finish.

        Args:
            job_id: Job ID to process
            options: Optional workflow options:
                - variant_count: Number of image variants (default: 12)
                - product_types: List of product types (default: ["tshirt", "poster"])
                - create_printify: Create Printify products (default: True)
                - list_etsy: Create Etsy listings (default: False)
                - create_social: Create social media posts (default: True)
                - submit_stock: Submit to stock platforms (default: True)

        Returns:
            dict with workflow results

        Raises:
            RuntimeError: If workflow fails
        """
        options = options or {}
        variant_count = options.get("variant_count", 12)
        product_types = options.get("product_types", ["tshirt", "poster_18x24"])
        create_printify = options.get("create_printify", True)
        list_etsy = options.get("list_etsy", False)
        create_social = options.get("create_social", True)
        submit_stock = options.get("submit_stock", True)

        results = {
            "job_id": job_id,
            "started_at": datetime.utcnow().isoformat(),
            "assets": [],
            "print_files": [],
            "products": [],
            "listings": [],
            "social_posts": [],
            "stock_submissions": [],
            "errors": [],
        }

        # Set correlation ID for tracking this workflow across all logs
        correlation_id = set_correlation_id()
        log = get_logger_with_context(job_id=job_id, correlation_id=correlation_id)
        
        log.info(f"Starting complete workflow for job {job_id}", extra={
            "workflow_options": options,
            "correlation_id": correlation_id,
        })

        try:
            # Get job
            job = self.job_manager.get_job(job_id)
            if not job:
                raise RuntimeError(f"Job {job_id} not found")

            # STEP 1: Generate image variants (12 monthly)
            self._update_progress(f"Generating {variant_count} image variants...", 0.0)

            self.job_manager.update_job_state(
                job, JobState.GENERATING, step="Generating monthly variants"
            )

            assets = self.image_generator.generate_all_monthly_variants(
                job,
                start_month=0,
                end_month=min(variant_count - 1, 11),
            )

            results["assets"] = [a.id for a in assets]
            self._update_progress(f"✓ Generated {len(assets)} variants", 0.2)

            # STEP 2: Render print files for all products
            self._update_progress("Rendering print files for all products...", 0.25)

            self.job_manager.update_job_state(
                job, JobState.RENDERING, step="Rendering print files"
            )

            # Printify blueprint specs
            from artomate.workers.printify_worker import PrintifyWorker

            blueprint_specs_map = {
                "tshirt": PrintifyWorker.BLUEPRINT_SPECS["tshirt"],
                "poster_12x18": PrintifyWorker.BLUEPRINT_SPECS["poster_12x18"],
                "poster_18x24": PrintifyWorker.BLUEPRINT_SPECS["poster_18x24"],
                "mug": PrintifyWorker.BLUEPRINT_SPECS["mug"],
                "hoodie": PrintifyWorker.BLUEPRINT_SPECS["hoodie"],
                "canvas_16x20": PrintifyWorker.BLUEPRINT_SPECS["canvas_16x20"],
            }

            all_print_files = []

            for asset in assets:
                for product_type in product_types:
                    if product_type not in blueprint_specs_map:
                        continue

                    spec = blueprint_specs_map[product_type]

                    print_file = self.render_engine.create_print_file(
                        asset=asset,
                        target_width=spec["print_area"]["width"],
                        target_height=spec["print_area"]["height"],
                        crop_mode="cover",
                        printify_blueprint_id=spec["blueprint_id"],
                        printify_provider_id=spec["provider_id"],
                    )

                    all_print_files.append(print_file)

            results["print_files"] = [pf.id for pf in all_print_files]
            self._update_progress(
                f"✓ Rendered {len(all_print_files)} print files", 0.4
            )

            # STEP 3: Create Printify products
            if create_printify:
                self._update_progress("Creating Printify products...", 0.45)

                self.job_manager.update_job_state(
                    job, JobState.PRINTIFY_PRODUCT, step="Creating products"
                )

                products = []

                for asset in assets:
                    asset_products = self.printify_worker.create_product_for_job(
                        job, asset, product_types
                    )
                    products.extend(asset_products)

                results["products"] = [p.id for p in products]
                self._update_progress(f"✓ Created {len(products)} products", 0.6)

            # STEP 4: Create Etsy listings (optional)
            if list_etsy and results["products"]:
                self._update_progress("Creating Etsy listings...", 0.65)

                self.job_manager.update_job_state(
                    job, JobState.ETSY_LISTING, step="Creating Etsy listings"
                )

                listings = []

                for product_id in results["products"][:12]:  # Max 12 for demo
                    try:
                        from artomate.db.database import get_db

                        with get_db().session_scope() as session:
                            from artomate.db.models import Product

                            product = session.query(Product).filter(
                                Product.id == product_id
                            ).first()

                            if product:
                                listing = self.etsy_worker.create_listing_for_product(
                                    product, job, assets
                                )
                                listings.append(listing)

                    except Exception as e:
                        logger.warning(f"Etsy listing failed for product {product_id}: {e}")
                        results["errors"].append(str(e))

                results["listings"] = [l.id for l in listings]
                self._update_progress(f"✓ Created {len(listings)} Etsy listings", 0.7)

            # STEP 5: Create social media posts
            if create_social:
                self._update_progress("Creating social media content...", 0.75)

                self.job_manager.update_job_state(
                    job, JobState.SOCIAL_PUBLISHING, step="Creating social posts"
                )

                social_posts = []

                # Instagram carousel with all 12 images
                carousel_post = self.social_publisher.create_post(
                    job=job,
                    platform=SocialPlatform.INSTAGRAM,
                    image_assets=assets[:10],  # IG max 10
                )
                social_posts.append(carousel_post)

                # Create Reels/Shorts for each variant
                for idx, asset in enumerate(assets[:3]):  # First 3 for demo
                    video = self.video_generator.create_reel(
                        job=job,
                        assets=[asset],
                        duration=5,
                        style="ken_burns",
                    )

                    # Instagram Reel
                    reel_post = self.social_publisher.create_post(
                        job=job,
                        platform=SocialPlatform.INSTAGRAM,
                        video_asset=video,
                    )
                    social_posts.append(reel_post)

                    # TikTok
                    tiktok_post = self.social_publisher.create_post(
                        job=job,
                        platform=SocialPlatform.TIKTOK,
                        video_asset=video,
                    )
                    social_posts.append(tiktok_post)

                    # YouTube Shorts
                    shorts_post = self.social_publisher.create_post(
                        job=job,
                        platform=SocialPlatform.YOUTUBE_SHORTS,
                        video_asset=video,
                    )
                    social_posts.append(shorts_post)

                results["social_posts"] = [sp.id for sp in social_posts]
                self._update_progress(f"✓ Created {len(social_posts)} social posts", 0.85)

            # STEP 6: Submit to stock platforms
            if submit_stock:
                self._update_progress("Submitting to stock platforms...", 0.90)

                self.job_manager.update_job_state(
                    job, JobState.STOCK_SUBMITTING, step="Submitting to stock"
                )

                stock_submissions = []

                for asset in assets:
                    # Shutterstock
                    shutterstock_sub = self.stock_worker.prepare_submission(
                        asset, job, "shutterstock"
                    )
                    shutterstock_path = self.stock_worker.create_outbox_file(
                        shutterstock_sub
                    )
                    stock_submissions.append(str(shutterstock_path))

                    # Adobe Stock
                    adobe_sub = self.stock_worker.prepare_submission(
                        asset, job, "adobe_stock"
                    )
                    adobe_path = self.stock_worker.create_outbox_file(adobe_sub)
                    stock_submissions.append(str(adobe_path))

                results["stock_submissions"] = stock_submissions
                self._update_progress(
                    f"✓ Created {len(stock_submissions)} stock submissions", 0.95
                )

            # STEP 7: Mark as done
            self.job_manager.update_job_state(job, JobState.DONE, step="Workflow complete")

            results["completed_at"] = datetime.utcnow().isoformat()
            results["status"] = "success"

            self._update_progress("✓ Workflow complete!", 1.0)

            logger.info(f"✓ Workflow complete for job {job_id}")

            # Send Telegram notification
            if self.telegram_notifier.is_available():
                try:
                    self.telegram_notifier.notify_job_complete_sync(job, results)
                except Exception as notif_error:
                    logger.warning(f"Failed to send Telegram notification: {notif_error}")

            return results

        except CircuitBreakerError as e:
            log.error(f"Circuit breaker OPEN - service unavailable: {e}", exc_info=True)
            
            results["status"] = "failed"
            results["error"] = f"Service unavailable (circuit breaker open): {str(e)}"
            results["failed_at"] = datetime.utcnow().isoformat()
            
            try:
                self.job_manager.update_job_state(
                    job, JobState.FAILED, error=str(e)
                )
            except:
                pass
            
            raise

        except Exception as e:
            log.error(f"Workflow failed for job {job_id}: {e}", exc_info=True)

            results["status"] = "failed"
            results["error"] = str(e)
            results["failed_at"] = datetime.utcnow().isoformat()

            # Mark job as failed
            try:
                self.job_manager.update_job_state(
                    job, JobState.FAILED, error=str(e)
                )
            except:
                pass

            raise
        
        finally:
            # Clear correlation ID after workflow completes
            clear_correlation_id()
            if self.telegram_notifier.is_available():
                try:
                    self.telegram_notifier.notify_job_failed_sync(job, str(e))
                except Exception as notif_error:
                    logger.warning(f"Failed to send Telegram notification: {notif_error}")

            raise RuntimeError(f"Workflow failed: {e}")

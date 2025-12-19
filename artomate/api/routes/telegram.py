"""Telegram webhook handler for job creation."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from loguru import logger

from artomate.core.job_manager import JobManager
from artomate.core.workflow_orchestrator import WorkflowOrchestrator

router = APIRouter()


class TelegramMessage(BaseModel):
    """Telegram message structure."""
    text: str
    chat_id: int


class TelegramWebhook(BaseModel):
    """Telegram webhook payload."""
    message: TelegramMessage


class JobCreationRequest(BaseModel):
    """Job creation from Telegram."""
    theme: str
    style: str | None = None
    niche: str | None = None
    keywords: list[str] | None = None
    variant_count: int = 12
    product_types: list[str] | None = None
    auto_run: bool = True


def parse_telegram_message(text: str) -> JobCreationRequest:
    """Parse Telegram message into job request.

    Format:
        /create theme: cat, style: japandi, niche: wall-art, keywords: minimal zen cute

    Args:
        text: Message text

    Returns:
        JobCreationRequest

    Raises:
        ValueError: If parsing fails
    """
    if not text.startswith("/create"):
        raise ValueError("Message must start with /create")

    # Remove /create prefix
    text = text.replace("/create", "").strip()

    # Parse key:value pairs
    params = {}
    parts = [p.strip() for p in text.split(",")]

    for part in parts:
        if ":" not in part:
            continue

        key, value = part.split(":", 1)
        key = key.strip().lower()
        value = value.strip()

        if key == "keywords":
            params[key] = [k.strip() for k in value.split()]
        else:
            params[key] = value

    if "theme" not in params:
        raise ValueError("Theme is required")

    return JobCreationRequest(
        theme=params["theme"],
        style=params.get("style"),
        niche=params.get("niche", "wall-art"),
        keywords=params.get("keywords", []),
        variant_count=int(params.get("variants", 12)),
        product_types=params.get("products", "tshirt,poster_18x24").split(","),
    )


async def run_workflow_background(job_id: int, options: dict):
    """Run workflow in background.

    Args:
        job_id: Job ID
        options: Workflow options
    """
    try:
        logger.info(f"Starting background workflow for job {job_id}")

        orchestrator = WorkflowOrchestrator()
        results = orchestrator.run_complete_workflow(job_id, options)

        logger.info(f"✓ Workflow complete for job {job_id}: {results['status']}")

    except Exception as e:
        logger.error(f"Background workflow failed for job {job_id}: {e}")


@router.post("/webhook")
async def telegram_webhook(
    payload: TelegramWebhook,
    background_tasks: BackgroundTasks,
):
    """Receive Telegram webhook and create job.

    Args:
        payload: Telegram webhook data
        background_tasks: FastAPI background tasks

    Returns:
        Response with job ID
    """
    try:
        message_text = payload.message.text
        chat_id = payload.message.chat_id

        logger.info(f"Received Telegram message from {chat_id}: {message_text}")

        # Parse message
        try:
            job_request = parse_telegram_message(message_text)
        except ValueError as e:
            logger.warning(f"Failed to parse message: {e}")
            return {
                "status": "error",
                "message": f"Invalid format: {e}",
                "help": (
                    "Format: /create theme: cat, style: japandi, "
                    "niche: wall-art, keywords: minimal zen"
                ),
            }

        # Create job
        manager = JobManager()

        job = manager.create_job(
            theme=job_request.theme,
            style=job_request.style,
            niche=job_request.niche,
            keywords=job_request.keywords,
            priority=8,
            input_source="telegram",
            input_data={"chat_id": chat_id, "message": message_text},
        )

        logger.info(f"✓ Created job {job.id} from Telegram")

        # Prepare workflow options
        workflow_options = {
            "variant_count": job_request.variant_count,
            "product_types": job_request.product_types or ["tshirt", "poster_18x24"],
            "create_printify": True,
            "list_etsy": False,  # Requires OAuth
            "create_social": True,
            "submit_stock": True,
        }

        # Run workflow in background if auto_run
        if job_request.auto_run:
            background_tasks.add_task(run_workflow_background, job.id, workflow_options)

            return {
                "status": "processing",
                "job_id": job.id,
                "message": (
                    f"✓ Job {job.id} created and processing started!\n\n"
                    f"Theme: {job.theme}\n"
                    f"Style: {job.style or 'N/A'}\n"
                    f"Variants: {job_request.variant_count}\n"
                    f"Products: {', '.join(job_request.product_types)}\n\n"
                    "Workflow includes:\n"
                    f"• {job_request.variant_count} image variants\n"
                    f"• {len(job_request.product_types) * job_request.variant_count} products\n"
                    "• Instagram carousel + Reels\n"
                    "• TikTok + YouTube Shorts\n"
                    "• Shutterstock + Adobe Stock\n\n"
                    "Check status with: /status {job.id}"
                ),
            }
        else:
            return {
                "status": "created",
                "job_id": job.id,
                "message": (
                    f"✓ Job {job.id} created!\n\n"
                    f"Run with: /run {job.id}\n"
                    f"Or check UI: http://your-domain/ui"
                ),
            }

    except Exception as e:
        logger.error(f"Telegram webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/status/{job_id}")
async def get_job_status(job_id: int):
    """Get job status.

    Args:
        job_id: Job ID

    Returns:
        Job status
    """
    try:
        manager = JobManager()
        job = manager.get_job(job_id)

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Get counts
        from artomate.db.database import get_db
        from artomate.db.models import Asset, Product, SocialPost

        with get_db().session_scope() as session:
            asset_count = session.query(Asset).filter(Asset.job_id == job_id).count()
            product_count = session.query(Product).filter(Product.job_id == job_id).count()
            social_count = session.query(SocialPost).filter(SocialPost.job_id == job_id).count()

        return {
            "job_id": job.id,
            "theme": job.theme,
            "state": job.state.value,
            "created_at": job.created_at.isoformat(),
            "current_step": job.current_step,
            "assets_generated": asset_count,
            "products_created": product_count,
            "social_posts_created": social_count,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

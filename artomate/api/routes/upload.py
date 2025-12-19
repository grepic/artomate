"""File upload endpoints for user images and CSV batch import."""

import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse, PlainTextResponse
from PIL import Image
from loguru import logger

from artomate.core.config import get_config
from artomate.db.database import get_db
from artomate.db.models import Asset, AssetType
from artomate.core.job_manager import JobManager
from artomate.workers.batch_processor import BatchProcessor, get_csv_template

router = APIRouter()

# Allowed file extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    job_id: Optional[int] = Form(None),
    create_job: bool = Form(False),
    theme: Optional[str] = Form(None),
    style: Optional[str] = Form(None),
) -> JSONResponse:
    """Upload user image for processing.

    Args:
        file: Image file to upload
        job_id: Optional existing job ID to attach to
        create_job: Whether to create a new job
        theme: Theme for new job (required if create_job=True)
        style: Style for new job

    Returns:
        JSON with asset details

    Raises:
        HTTPException: If upload fails
    """
    config = get_config()

    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Read file
    contents = await file.read()

    # Validate file size
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB",
        )

    try:
        # Validate it's a real image
        from io import BytesIO
        img = Image.open(BytesIO(contents))
        width, height = img.size
        format_ = img.format

        logger.info(
            f"Received image upload: {file.filename} ({width}x{height}, {format_})"
        )

        # Create job if requested
        if create_job:
            if not theme:
                raise HTTPException(
                    status_code=400, detail="theme required when create_job=True"
                )

            job_manager = JobManager(config)
            job = job_manager.create_job(
                theme=theme or "uploaded image",
                style=style or "user-uploaded",
                source="upload",
            )
            job_id = job.id
            logger.info(f"Created new job {job_id} for uploaded image")

        elif not job_id:
            raise HTTPException(
                status_code=400,
                detail="Either job_id or create_job=True must be provided",
            )

        # Generate unique filename
        unique_id = uuid.uuid4().hex[:8]
        filename = f"upload_{job_id}_{unique_id}{file_ext}"
        save_path = config.assets_dir / "images" / filename

        # Ensure directory exists
        save_path.parent.mkdir(parents=True, exist_ok=True)

        # Save file
        save_path.write_bytes(contents)

        file_size = save_path.stat().st_size

        logger.info(f"✓ Saved uploaded image: {save_path} ({file_size:,} bytes)")

        # Create Asset record
        asset = Asset(
            job_id=job_id,
            asset_type=AssetType.IMAGE,
            storage_path=str(save_path),
            url=None,  # User upload, no external URL
            width=width,
            height=height,
            file_size=file_size,
            format=format_,
            provider="user_upload",
            prompt=f"User uploaded: {file.filename}",
        )

        # Save to database
        with get_db().session_scope() as session:
            session.add(asset)
            session.flush()

            logger.info(f"✓ Created asset record {asset.id}")

        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "asset_id": asset.id,
                "job_id": job_id,
                "filename": filename,
                "width": width,
                "height": height,
                "file_size": file_size,
                "message": "Image uploaded successfully",
            },
        )

    except Image.UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="Invalid image file")
    except Exception as e:
        logger.error(f"Image upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/limits")
async def get_upload_limits():
    """Get upload limits and allowed formats.

    Returns:
        JSON with upload configuration
    """
    return {
        "max_file_size_mb": MAX_FILE_SIZE / 1024 / 1024,
        "max_file_size_bytes": MAX_FILE_SIZE,
        "allowed_extensions": list(ALLOWED_EXTENSIONS),
        "allowed_mime_types": [
            "image/jpeg",
            "image/png",
            "image/webp",
            "image/heic",
        ],
    }


@router.post("/csv")
async def upload_csv_batch(
    file: UploadFile = File(...),
    enqueue: bool = Form(True),
) -> JSONResponse:
    """Upload CSV file for batch job creation.

    CSV Format:
        theme,style,keywords,niche,variants
        cat,minimalist,zen calm,home-decor,12
        dog,boho,earthy natural,lifestyle,6

    Args:
        file: CSV file
        enqueue: Whether to enqueue jobs for immediate processing

    Returns:
        JSON with created job IDs and status

    Raises:
        HTTPException: If upload fails
    """
    # Validate file type
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be CSV format")

    try:
        # Read CSV content
        contents = await file.read()
        csv_content = contents.decode("utf-8")

        logger.info(f"Received CSV batch upload: {file.filename}")

        # Process CSV
        batch_processor = BatchProcessor()
        job_ids = batch_processor.create_jobs_from_csv(
            csv_content=csv_content, enqueue=enqueue
        )

        # Get batch status
        status = batch_processor.get_batch_status(job_ids)

        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "jobs_created": len(job_ids),
                "job_ids": job_ids,
                "enqueued": enqueue,
                "status": status,
                "message": f"Created {len(job_ids)} jobs from CSV",
            },
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"CSV batch upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch upload failed: {str(e)}")


@router.get("/csv-template")
async def get_csv_template_endpoint() -> PlainTextResponse:
    """Get CSV template for batch import.

    Returns:
        CSV template as plain text
    """
    template = get_csv_template()
    return PlainTextResponse(content=template, media_type="text/csv")


@router.get("/batch-status/{job_ids}")
async def get_batch_status_endpoint(job_ids: str) -> JSONResponse:
    """Get status of batch jobs.

    Args:
        job_ids: Comma-separated list of job IDs (e.g., "1,2,3,4")

    Returns:
        JSON with batch status
    """
    try:
        # Parse job IDs
        ids = [int(id.strip()) for id in job_ids.split(",")]

        # Get status
        batch_processor = BatchProcessor()
        status = batch_processor.get_batch_status(ids)

        return JSONResponse(content=status)

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job IDs format")
    except Exception as e:
        logger.error(f"Failed to get batch status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def list_templates(category: Optional[str] = None) -> JSONResponse:
    """List all available design templates.

    Args:
        category: Optional category filter (home-decor, apparel, lifestyle, etc.)

    Returns:
        JSON with template list
    """
    from artomate.templates.templates import list_templates as get_templates

    templates = get_templates(category=category)

    return JSONResponse(content={"templates": templates, "count": len(templates)})


@router.get("/templates/{template_id}")
async def get_template(template_id: str) -> JSONResponse:
    """Get specific template details.

    Args:
        template_id: Template identifier

    Returns:
        JSON with template details

    Raises:
        HTTPException: If template not found
    """
    from artomate.templates.templates import get_template as fetch_template

    try:
        template = fetch_template(template_id)
        return JSONResponse(content=template)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Template not found: {template_id}")


@router.post("/templates/{template_id}/create-job")
async def create_job_from_template(
    template_id: str,
    enqueue: bool = Form(True),
) -> JSONResponse:
    """Create job from template.

    Args:
        template_id: Template identifier
        enqueue: Whether to enqueue for immediate processing

    Returns:
        JSON with created job ID

    Raises:
        HTTPException: If template not found or job creation fails
    """
    from artomate.templates.templates import get_template as fetch_template

    try:
        template = fetch_template(template_id)

        # Create job from template
        job_manager = JobManager()
        job = job_manager.create_job(
            theme=template["theme"],
            style=template["style"],
            keywords=template.get("keywords"),
            niche=template.get("niche"),
            source=f"template:{template_id}",
        )

        # Enqueue if requested
        if enqueue and get_queue().is_available():
            from artomate.core.workflow_orchestrator import WorkflowOrchestrator

            get_queue().enqueue(
                WorkflowOrchestrator().run_complete_workflow,
                job.id,
                {"product_types": template.get("recommended_products", ["tshirt"])},
                job_timeout=3600,
            )

            logger.info(f"✓ Created and enqueued job {job.id} from template {template_id}")

        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "job_id": job.id,
                "template_id": template_id,
                "enqueued": enqueue,
                "message": f"Job created from template: {template['name']}",
            },
        )

    except KeyError:
        raise HTTPException(status_code=404, detail=f"Template not found: {template_id}")
    except Exception as e:
        logger.error(f"Failed to create job from template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

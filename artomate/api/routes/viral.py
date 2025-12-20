"""API routes for viral video content creation."""

from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from artomate.db.database import get_db
from artomate.db.models import Asset, Job
from artomate.utils.logger import get_logger_with_context
from artomate.workers.ai_facts_generator import AIFactsGenerator
from artomate.workers.viral_content_optimizer import ViralContentOptimizer

logger = get_logger_with_context()
router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================


class FactsRequest(BaseModel):
    """Request for generating animal facts."""

    animal: str = Field(..., description="Animal name (e.g., 'cat', 'elephant')")
    count: int = Field(5, ge=1, le=10, description="Number of facts to generate")
    style: str = Field("viral", description="Style: fun, educational, shocking, cute, viral")


class FactsResponse(BaseModel):
    """Response with generated facts."""

    animal: str
    facts: List[str]
    count: int


class ViralHookRequest(BaseModel):
    """Request for generating viral hook."""

    theme: str = Field(..., description="Video theme/topic")
    duration: str = Field("short", description="Duration: short (3-5s) or long (7-10s)")


class ViralHookResponse(BaseModel):
    """Response with viral hook."""

    theme: str
    hook: str
    duration: str


class ViralPackageRequest(BaseModel):
    """Request for creating viral content package."""

    job_id: int = Field(..., description="Job ID")
    asset_id: int = Field(..., description="Image asset ID")
    platforms: Optional[List[str]] = Field(
        ["tiktok", "instagram", "youtube"],
        description="Platforms to create content for"
    )
    export: bool = Field(True, description="Export ready-to-post package")


class ViralPackageResponse(BaseModel):
    """Response with viral package details."""

    job_id: int
    video_count: int
    post_count: int
    fact_count: int
    platforms: List[str]
    theme: str
    export_path: Optional[str] = None
    videos: List[dict]
    captions: dict
    hashtags: dict


class PostingScheduleResponse(BaseModel):
    """Response with posting schedule recommendations."""

    platforms: dict


# ============================================================================
# Routes
# ============================================================================


@router.post("/facts", response_model=FactsResponse)
async def generate_facts(request: FactsRequest):
    """Generate AI facts about an animal.

    Example:
        ```bash
        curl -X POST http://localhost:8000/api/viral/facts \\
          -H "Content-Type: application/json" \\
          -d '{
            "animal": "cat",
            "count": 5,
            "style": "viral"
          }'
        ```

    Returns:
        ```json
        {
          "animal": "cat",
          "facts": [
            "Cats spend 70% of their lives sleeping! 😴",
            "A cat's purr can help heal bones! 🦴",
            ...
          ],
          "count": 5
        }
        ```
    """
    logger.info(f"Generating {request.count} {request.style} facts about {request.animal}")

    try:
        generator = AIFactsGenerator()
        facts = generator.generate_animal_facts(
            animal=request.animal,
            count=request.count,
            style=request.style,
        )

        return FactsResponse(
            animal=request.animal,
            facts=facts,
            count=len(facts),
        )

    except Exception as e:
        logger.error(f"Failed to generate facts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate facts: {str(e)}")


@router.post("/hook", response_model=ViralHookResponse)
async def generate_hook(request: ViralHookRequest):
    """Generate viral hook for video intro.

    Example:
        ```bash
        curl -X POST http://localhost:8000/api/viral/hook \\
          -H "Content-Type: application/json" \\
          -d '{
            "theme": "cats",
            "duration": "short"
          }'
        ```

    Returns:
        ```json
        {
          "theme": "cats",
          "hook": "Did you know cats have a SECRET superpower? 🤯",
          "duration": "short"
        }
        ```
    """
    logger.info(f"Generating viral hook for: {request.theme}")

    try:
        generator = AIFactsGenerator()
        hook = generator.generate_viral_hook(
            theme=request.theme,
            duration=request.duration,
        )

        return ViralHookResponse(
            theme=request.theme,
            hook=hook,
            duration=request.duration,
        )

    except Exception as e:
        logger.error(f"Failed to generate hook: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate hook: {str(e)}")


@router.post("/package", response_model=ViralPackageResponse)
async def create_viral_package(request: ViralPackageRequest):
    """Create complete viral content package for multiple platforms.

    This endpoint:
    1. Generates AI facts about the subject
    2. Creates viral videos for TikTok, Instagram, YouTube
    3. Generates optimized captions and hashtags
    4. Creates social post records
    5. Optionally exports ready-to-post package

    Example:
        ```bash
        curl -X POST http://localhost:8000/api/viral/package \\
          -H "Content-Type: application/json" \\
          -d '{
            "job_id": 123,
            "asset_id": 456,
            "platforms": ["tiktok", "instagram", "youtube"],
            "export": true
          }'
        ```

    Returns:
        ```json
        {
          "job_id": 123,
          "video_count": 3,
          "post_count": 3,
          "fact_count": 5,
          "platforms": ["tiktok", "instagram", "youtube"],
          "theme": "cat",
          "export_path": "/data/exports/job_123_20250120/",
          "videos": [...],
          "captions": {...},
          "hashtags": {...}
        }
        ```
    """
    logger.info(f"Creating viral package for job {request.job_id}, asset {request.asset_id}")

    db = get_db()

    # Get job and asset
    with db.session_scope() as session:
        job = session.query(Job).filter(Job.id == request.job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {request.job_id} not found")

        asset = session.query(Asset).filter(Asset.id == request.asset_id).first()
        if not asset:
            raise HTTPException(status_code=404, detail=f"Asset {request.asset_id} not found")

        # Expunge to use outside session
        session.expunge(job)
        session.expunge(asset)

    try:
        # Create viral package
        optimizer = ViralContentOptimizer()
        package = optimizer.create_complete_viral_package(
            job=job,
            image_asset=asset,
            platforms=request.platforms,
        )

        # Export if requested
        export_path = None
        if request.export:
            export_dir = optimizer.export_ready_to_post_package(package)
            export_path = str(export_dir)
            logger.info(f"Exported package to: {export_path}")

        # Build response
        videos_data = [
            {
                "id": v.id,
                "format": v.subtype,
                "path": v.storage_path,
                "size_mb": round(v.file_size_bytes / 1024 / 1024, 2),
                "width": v.width,
                "height": v.height,
            }
            for v in package["videos"]
        ]

        return ViralPackageResponse(
            job_id=job.id,
            video_count=len(package["videos"]),
            post_count=len(package["posts"]),
            fact_count=len(package["facts"]),
            platforms=package["platforms"],
            theme=package["theme"],
            export_path=export_path,
            videos=videos_data,
            captions=package["captions"],
            hashtags={k: v for k, v in package["hashtags"].items()},
        )

    except Exception as e:
        logger.error(f"Failed to create viral package: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create viral package: {str(e)}"
        )


@router.get("/schedule", response_model=PostingScheduleResponse)
async def get_posting_schedule(
    platforms: List[str] = Query(["tiktok", "instagram", "youtube"])
):
    """Get recommended posting schedule for platforms.

    Example:
        ```bash
        curl http://localhost:8000/api/viral/schedule?platforms=tiktok&platforms=instagram
        ```

    Returns:
        ```json
        {
          "platforms": {
            "tiktok": {
              "best_times": ["7-9 PM", "12-1 PM"],
              "best_days": ["Tuesday", "Thursday", "Friday"],
              "frequency": "1-3 posts/day",
              "tips": [...]
            },
            ...
          }
        }
        ```
    """
    logger.info(f"Getting posting schedule for: {platforms}")

    try:
        optimizer = ViralContentOptimizer()
        schedule = optimizer.get_posting_schedule_recommendations(platforms)

        return PostingScheduleResponse(platforms=schedule)

    except Exception as e:
        logger.error(f"Failed to get schedule: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get schedule: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check for viral content service.

    Returns:
        ```json
        {
          "status": "healthy",
          "services": {
            "ai_facts": true,
            "video_renderer": true,
            "optimizer": true
          }
        }
        ```
    """
    try:
        # Test services
        generator = AIFactsGenerator()
        optimizer = ViralContentOptimizer()

        return {
            "status": "healthy",
            "services": {
                "ai_facts": generator is not None,
                "video_renderer": optimizer.video_renderer is not None,
                "optimizer": optimizer is not None,
            },
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }

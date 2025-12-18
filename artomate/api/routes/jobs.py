"""Job management endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from artomate.core.job_manager import JobManager

router = APIRouter()

class JobCreate(BaseModel):
    theme: str
    style: str | None = None
    niche: str | None = None
    keywords: list[str] | None = None

@router.post("")
async def create_job(job: JobCreate):
    """Create new job."""
    manager = JobManager()
    created = manager.create_job(
        theme=job.theme,
        style=job.style,
        niche=job.niche,
        keywords=job.keywords,
    )
    return {"id": created.id, "theme": created.theme, "state": created.state.value}

@router.get("/{job_id}")
async def get_job(job_id: int):
    """Get job by ID."""
    manager = JobManager()
    job = manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"id": job.id, "theme": job.theme, "state": job.state.value}

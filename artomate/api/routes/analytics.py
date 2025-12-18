"""Analytics endpoints."""
from fastapi import APIRouter
from artomate.core.job_manager import JobManager

router = APIRouter()

@router.get("/stats")
async def get_stats():
    """Get overall statistics."""
    manager = JobManager()
    return manager.get_job_stats()

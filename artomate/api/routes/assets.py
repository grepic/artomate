"""Asset endpoints."""
from fastapi import APIRouter

router = APIRouter()

@router.get("")
async def list_assets():
    """List all assets."""
    return {"assets": []}

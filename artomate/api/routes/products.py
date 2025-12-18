"""Product endpoints."""
from fastapi import APIRouter

router = APIRouter()

@router.get("")
async def list_products():
    """List all products."""
    return {"products": []}

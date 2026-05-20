from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(tags=["config"])


@router.get("/config")
async def get_public_config() -> dict:
    """Return public (non-secret) frontend configuration — pixel IDs only, never tokens."""
    return {
        "meta_pixel_id": settings.META_PIXEL_ID or None,
        "tiktok_pixel_id": settings.TIKTOK_PIXEL_ID or None,
        "snap_pixel_id": settings.SNAP_PIXEL_ID or None,
    }

import httpx
import logging
import time
from typing import Optional, Any
from app.core.config import settings
from app.services.capi.hashing import hash_phone_snap

logger = logging.getLogger("najd")

SNAP_CAPI_URL = "https://tr.snapchat.com/v2/conversion"


async def send_snap_purchase(
    *,
    event_id: str,
    phone_e164: str,
    total_sar: float,
    order_number: str,
    content_ids: list[str],
    client_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    event_source_url: Optional[str] = None,
) -> dict[str, Any]:
    if not settings.SNAP_PIXEL_ID or not settings.SNAP_ACCESS_TOKEN:
        return {"skipped": True, "reason": "Snapchat credentials not configured"}

    user_data: dict[str, Any] = {
        "ph": [hash_phone_snap(phone_e164)],
    }
    if client_ip:
        user_data["client_ip_address"] = client_ip
    if user_agent:
        user_data["client_user_agent"] = user_agent

    payload: dict[str, Any] = {
        "pixel_id": settings.SNAP_PIXEL_ID,
        "test_mode": bool(settings.SNAP_TEST_EVENT_CODE),
        "data": [
            {
                "event_name": "PURCHASE",
                "event_time": int(time.time()),
                "event_id": event_id,
                "event_source_url": event_source_url
                or f"{settings.FRONTEND_BASE_URL}/thank-you/{order_number}",
                "user_data": user_data,
                "custom_data": {
                    "currency": "SAR",
                    "value": total_sar,
                    "content_ids": content_ids,
                    "order_id": order_number,
                },
            }
        ],
    }

    headers = {
        "Authorization": f"Bearer {settings.SNAP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(SNAP_CAPI_URL, json=payload, headers=headers)
            return {"status_code": response.status_code, "body": response.text}
    except Exception as exc:
        logger.error(f"Snapchat CAPI error: {exc}")
        return {"error": str(exc)}

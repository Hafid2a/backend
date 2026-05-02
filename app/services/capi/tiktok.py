import httpx
import logging
import time
from typing import Optional, Any
from app.core.config import settings
from app.services.capi.hashing import hash_phone_tiktok

logger = logging.getLogger("najd")

TIKTOK_CAPI_URL = "https://business-api.tiktok.com/open_api/v1.3/event/track/"


async def send_tiktok_purchase(
    *,
    event_id: str,
    phone_e164: str,
    total_sar: float,
    order_number: str,
    items: list[dict],
    client_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    ttclid: Optional[str] = None,
    ttp: Optional[str] = None,
    landing_page: Optional[str] = None,
    referrer: Optional[str] = None,
) -> dict[str, Any]:
    if not settings.TIKTOK_PIXEL_ID or not settings.TIKTOK_ACCESS_TOKEN:
        return {"skipped": True, "reason": "TikTok credentials not configured"}

    user: dict[str, Any] = {
        "phone": hash_phone_tiktok(phone_e164),
    }
    if client_ip:
        user["ip"] = client_ip
    if user_agent:
        user["user_agent"] = user_agent
    if ttclid:
        user["ttclid"] = ttclid
    if ttp:
        user["ttp"] = ttp

    event: dict[str, Any] = {
        "event": "CompletePayment",
        "event_time": int(time.time()),
        "event_id": event_id,
        "user": user,
        "properties": {
            "currency": "SAR",
            "value": total_sar,
            "contents": items,
        },
        "page": {
            "url": landing_page or f"{settings.FRONTEND_BASE_URL}/thank-you/{order_number}",
            "referrer": referrer or "",
        },
    }

    payload: dict[str, Any] = {
        "event_source": "web",
        "event_source_id": settings.TIKTOK_PIXEL_ID,
        "data": [event],
    }

    if settings.TIKTOK_TEST_EVENT_CODE:
        payload["test_event_code"] = settings.TIKTOK_TEST_EVENT_CODE

    headers = {
        "Access-Token": settings.TIKTOK_ACCESS_TOKEN,
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(TIKTOK_CAPI_URL, json=payload, headers=headers)
            return {"status_code": response.status_code, "body": response.json()}
    except Exception as exc:
        logger.error(f"TikTok CAPI error: {exc}")
        return {"error": str(exc)}

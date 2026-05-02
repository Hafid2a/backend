import httpx
import logging
import time
from typing import Optional, Any
from app.core.config import settings
from app.services.capi.hashing import hash_phone_meta

logger = logging.getLogger("najd")

META_CAPI_URL = "https://graph.facebook.com/{version}/{pixel_id}/events"


async def send_meta_purchase(
    *,
    event_id: str,
    phone_e164: str,
    total_sar: float,
    order_number: str,
    items: list[dict],
    client_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    fbp: Optional[str] = None,
    fbc: Optional[str] = None,
    event_source_url: Optional[str] = None,
) -> dict[str, Any]:
    if not settings.META_PIXEL_ID or not settings.META_ACCESS_TOKEN:
        return {"skipped": True, "reason": "Meta credentials not configured"}

    url = META_CAPI_URL.format(
        version=settings.META_CAPI_VERSION,
        pixel_id=settings.META_PIXEL_ID,
    )

    user_data: dict[str, Any] = {
        "ph": [hash_phone_meta(phone_e164)],
    }
    if client_ip:
        user_data["client_ip_address"] = client_ip
    if user_agent:
        user_data["client_user_agent"] = user_agent
    if fbp:
        user_data["fbp"] = fbp
    if fbc:
        user_data["fbc"] = fbc

    payload: dict[str, Any] = {
        "data": [
            {
                "event_name": "Purchase",
                "event_time": int(time.time()),
                "event_id": event_id,
                "action_source": "website",
                "event_source_url": event_source_url
                or f"{settings.FRONTEND_BASE_URL}/thank-you/{order_number}",
                "user_data": user_data,
                "custom_data": {
                    "currency": "SAR",
                    "value": total_sar,
                    "content_type": "product",
                    "contents": items,
                    "order_id": order_number,
                },
            }
        ]
    }

    if settings.META_TEST_EVENT_CODE:
        payload["test_event_code"] = settings.META_TEST_EVENT_CODE

    params = {"access_token": settings.META_ACCESS_TOKEN}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload, params=params)
            return {"status_code": response.status_code, "body": response.json()}
    except Exception as exc:
        logger.error(f"Meta CAPI error: {exc}")
        return {"error": str(exc)}

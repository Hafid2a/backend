import uuid
import asyncio
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Order, OrderItem, TrackingEvent, utcnow
from app.services.capi.meta import send_meta_purchase
from app.services.capi.tiktok import send_tiktok_purchase
from app.services.capi.snapchat import send_snap_purchase

logger = logging.getLogger("najd")


def _build_meta_items(items: list[OrderItem]) -> list[dict]:
    return [
        {
            "id": item.product_slug,
            "quantity": item.quantity,
            "item_price": round(item.unit_price_sar, 2),
        }
        for item in items
    ]


def _build_tiktok_items(items: list[OrderItem]) -> list[dict]:
    return [
        {
            "content_id": item.product_slug,
            "content_type": "product",
            "content_name": item.product_name_ar,
            "quantity": item.quantity,
            "price": round(item.unit_price_sar, 2),
        }
        for item in items
    ]


async def _log_tracking_event(
    db: AsyncSession,
    *,
    order_id: object,
    platform: str,
    event_name: str,
    event_id: str,
    status: str,
    request_payload: Optional[dict] = None,
    response_payload: Optional[dict] = None,
    error_message: Optional[str] = None,
) -> None:
    event = TrackingEvent(
        id=uuid.uuid4(),
        order_id=order_id,
        platform=platform,
        event_name=event_name,
        event_id=event_id,
        status=status,
        request_payload=request_payload,
        response_payload=response_payload,
        error_message=error_message,
        created_at=utcnow(),
    )
    db.add(event)


async def dispatch_purchase_capi(
    db: AsyncSession,
    order: Order,
    purchase_event_id: str,
) -> None:
    """Dispatch Purchase event to all configured CAPI platforms. Never raises."""
    items: list[OrderItem] = order.items

    meta_items = _build_meta_items(items)
    tiktok_items = _build_tiktok_items(items)
    content_ids = list({item.product_slug for item in items})

    async def run_meta() -> None:
        try:
            result = await send_meta_purchase(
                event_id=purchase_event_id,
                phone_e164=order.phone_e164,
                total_sar=float(order.total_sar),
                order_number=order.order_number,
                items=meta_items,
                client_ip=order.client_ip,
                user_agent=order.user_agent,
                fbp=order.fbp,
                fbc=order.fbc,
                event_source_url=order.landing_page or None,
            )
            status = (
                "sent"
                if result.get("status_code") in (200, 201) or result.get("skipped")
                else "failed"
            )
            await _log_tracking_event(
                db,
                order_id=order.id,
                platform="meta",
                event_name="Purchase",
                event_id=purchase_event_id,
                status=status,
                response_payload=result,
            )
        except Exception as exc:
            logger.error(f"Meta CAPI dispatch error: {exc}")
            await _log_tracking_event(
                db,
                order_id=order.id,
                platform="meta",
                event_name="Purchase",
                event_id=purchase_event_id,
                status="failed",
                error_message=str(exc),
            )

    async def run_tiktok() -> None:
        try:
            result = await send_tiktok_purchase(
                event_id=purchase_event_id,
                phone_e164=order.phone_e164,
                total_sar=float(order.total_sar),
                order_number=order.order_number,
                items=tiktok_items,
                client_ip=order.client_ip,
                user_agent=order.user_agent,
                ttclid=order.ttclid,
                ttp=order.ttp,
                landing_page=order.landing_page,
                referrer=order.referrer,
            )
            status = (
                "sent"
                if result.get("status_code") in (200, 201) or result.get("skipped")
                else "failed"
            )
            await _log_tracking_event(
                db,
                order_id=order.id,
                platform="tiktok",
                event_name="CompletePayment",
                event_id=purchase_event_id,
                status=status,
                response_payload=result,
            )
        except Exception as exc:
            logger.error(f"TikTok CAPI dispatch error: {exc}")
            await _log_tracking_event(
                db,
                order_id=order.id,
                platform="tiktok",
                event_name="CompletePayment",
                event_id=purchase_event_id,
                status="failed",
                error_message=str(exc),
            )

    async def run_snap() -> None:
        try:
            result = await send_snap_purchase(
                event_id=purchase_event_id,
                phone_e164=order.phone_e164,
                total_sar=float(order.total_sar),
                order_number=order.order_number,
                content_ids=content_ids,
                client_ip=order.client_ip,
                user_agent=order.user_agent,
            )
            status = (
                "sent"
                if result.get("status_code") in (200, 201) or result.get("skipped")
                else "failed"
            )
            await _log_tracking_event(
                db,
                order_id=order.id,
                platform="snapchat",
                event_name="PURCHASE",
                event_id=purchase_event_id,
                status=status,
                response_payload=result,
            )
        except Exception as exc:
            logger.error(f"Snapchat CAPI dispatch error: {exc}")
            await _log_tracking_event(
                db,
                order_id=order.id,
                platform="snapchat",
                event_name="PURCHASE",
                event_id=purchase_event_id,
                status="failed",
                error_message=str(exc),
            )

    await asyncio.gather(run_meta(), run_tiktok(), run_snap())
    await db.commit()

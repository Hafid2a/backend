import httpx
import logging
from datetime import timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db.models import Order, OrderItem, utcnow

logger = logging.getLogger("najd")


def _build_items_summary(items: list[OrderItem], upsell_only: bool = False) -> str:
    parts = []
    for item in items:
        if upsell_only and not item.is_upsell:
            continue
        if not upsell_only and item.is_upsell:
            continue
        parts.append(f"{item.product_name_ar} x{item.quantity} - {item.line_total_sar} SAR")
    return " | ".join(parts)


async def send_order_to_sheet(db: AsyncSession, order: Order) -> bool:
    """Send order to Google Sheets webhook. Returns True on success, False on failure."""
    if not settings.SHEET_WEBHOOK_URL:
        logger.info("Sheet webhook URL not configured, skipping")
        return True

    created_at_str = (
        order.created_at.astimezone(timezone.utc).isoformat()
        if order.created_at
        else ""
    )

    payload = {
        "secret": settings.SHEET_WEBHOOK_SECRET,
        "order_number": order.order_number,
        "created_at": created_at_str,
        "customer_name": order.customer_name,
        "phone_e164": order.phone_e164,
        "status": order.status,
        "confirmation_status": order.confirmation_status,
        "total_sar": order.total_sar,
        "currency": order.currency,
        "items_summary": _build_items_summary(order.items, upsell_only=False),
        "upsell_items_summary": _build_items_summary(order.items, upsell_only=True),
        "utm_source": order.utm_source or "",
        "utm_medium": order.utm_medium or "",
        "utm_campaign": order.utm_campaign or "",
        "landing_page": order.landing_page or "",
        "referrer": order.referrer or "",
        "client_ip": order.client_ip or "",
        "user_agent": order.user_agent or "",
        "notes": order.notes or "",
    }

    headers: dict = {}
    if settings.SHEET_WEBHOOK_SECRET:
        headers["X-NAJD-SECRET"] = settings.SHEET_WEBHOOK_SECRET

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                settings.SHEET_WEBHOOK_URL,
                json=payload,
                headers=headers,
            )
            if response.status_code == 200:
                order.sheet_sync_status = "synced"
                order.sheet_synced_at = utcnow()
                await db.commit()
                return True
            else:
                logger.error(f"Sheet webhook returned {response.status_code}: {response.text}")
                order.sheet_sync_status = "failed"
                await db.commit()
                return False
    except Exception as exc:
        logger.error(f"Sheet webhook error: {exc}")
        order.sheet_sync_status = "failed"
        try:
            await db.commit()
        except Exception:
            pass
        return False

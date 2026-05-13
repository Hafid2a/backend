import httpx
import logging
from datetime import timezone
from urllib.parse import urljoin
from zoneinfo import ZoneInfo
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db.models import Order, OrderItem, utcnow

logger = logging.getLogger("najd")

# Google Apps Script Web Apps respond with redirects; POST must arrive at the final URL with a JSON body.
# httpx defaults to follow_redirects=False (non-200), and following 302 can downgrade POST→GET.


async def _post_json_sheet_webhook(
    client: httpx.AsyncClient,
    url: str,
    payload: dict,
    headers: dict,
    *,
    max_hops: int = 8,
) -> httpx.Response:
    current = url
    last_response: httpx.Response | None = None
    for hop in range(max_hops):
        response = await client.post(
            current,
            json=payload,
            headers=headers,
            follow_redirects=False,
        )
        last_response = response
        if response.status_code == 200:
            return response
        loc = response.headers.get("location")
        if (
            loc
            and response.status_code in (301, 302, 303, 307, 308)
        ):
            current = urljoin(str(response.request.url), loc)
            logger.debug(
                "Sheet webhook redirect hop %s -> %s (status %s)",
                hop + 1,
                current[:120],
                response.status_code,
            )
            continue
        return response
    assert last_response is not None
    return last_response

# Matches `backend/app/db/seed.py` product slugs → SKU for Google Sheet column "sku".
_SLUG_TO_SKU: dict[str, str] = {
    "najd-thabat-al-khat": "NAJD-STAY-PRIMER",
    "najd-darag-al-nahar": "NAJD-DAY-SPF-50",
    "najd-safa-al-jabha": "NAJD-HAIRLINE-SERUM",
}


def _sheet_date_riyadh(order: Order) -> str:
    if not order.created_at:
        return ""
    return order.created_at.astimezone(ZoneInfo("Asia/Riyadh")).strftime("%Y-%m-%d %H:%M")


def _product_names_line(items: list[OrderItem]) -> str:
    return " | ".join(f"{i.product_name_ar} x{i.quantity}" for i in items)


def _sku_qty_line(items: list[OrderItem]) -> str:
    parts: list[str] = []
    for i in items:
        sku = _SLUG_TO_SKU.get(i.product_slug, i.product_slug.upper())
        parts.append(f"{sku}×{i.quantity}")
    return ", ".join(parts)


def _total_quantity(items: list[OrderItem]) -> int:
    return sum(i.quantity for i in items)


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
    sheet_items = sorted(order.items, key=lambda i: (i.is_upsell, i.created_at))

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
        # Google Sheet «NAJD STORER» columns (Apps Script maps these):
        "sheet_date": _sheet_date_riyadh(order),
        "sheet_country": "Saudi Arabia",
        "sheet_product": _product_names_line(sheet_items),
        "sheet_sku": _sku_qty_line(sheet_items),
        "sheet_quantity": _total_quantity(sheet_items),
    }

    headers: dict = {}
    if settings.SHEET_WEBHOOK_SECRET:
        headers["X-NAJD-SECRET"] = settings.SHEET_WEBHOOK_SECRET

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await _post_json_sheet_webhook(
                client,
                settings.SHEET_WEBHOOK_URL.strip(),
                payload,
                headers,
            )
            if response.status_code == 200:
                order.sheet_sync_status = "synced"
                order.sheet_synced_at = utcnow()
                await db.commit()
                return True
            else:
                logger.error(
                    "Sheet webhook returned %s: %s",
                    response.status_code,
                    (response.text or "")[:500],
                )
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

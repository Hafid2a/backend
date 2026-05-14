import uuid
import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.models import Order, OrderItem, utcnow
from app.schemas.order import (
    CreateOrderRequest,
    UpsellItemOut,
    OrderDetailResponse,
    OrderItemOut,
)
from app.services.phone import normalize_saudi_mobile, mask_phone
from app.services.maxmind_geo import assert_ip_allowed_for_order, phone_bypasses_geo_check
from fastapi import HTTPException

logger = logging.getLogger("najd")

OFFER_PRICE_TABLE: dict[int, int] = {1: 199, 2: 279, 3: 349}

UPSELL_MAP: dict[str, str] = {
    "face-primer": "forehead-serum",
    "face-sunscreen-spf50": "face-primer",
    "forehead-serum": "face-sunscreen-spf50",
}

UPSELL_PRICE = 99

PRODUCT_NAMES: dict[str, str] = {
    "face-primer": "ثبات الخط",
    "face-sunscreen-spf50": "درع النهار",
    "forehead-serum": "صفاء الجبهة",
}


async def _generate_order_number(db: AsyncSession) -> str:
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    result = await db.execute(
        select(func.count()).select_from(Order).where(
            Order.order_number.like(f"NAJD-{today}-%")
        )
    )
    count = result.scalar() or 0
    return f"NAJD-{today}-{str(count + 1).zfill(6)}"


def _recalculate_total(items: list[dict]) -> int:
    """Recalculate order total server-side. Never trust frontend prices."""
    total = 0
    for item in items:
        qty = item["offer_qty"]
        canonical_price = OFFER_PRICE_TABLE.get(qty)
        if canonical_price is None:
            raise ValueError(f"Invalid offer_qty: {qty}")
        if item.get("is_upsell"):
            total += UPSELL_PRICE
        else:
            total += canonical_price
    return total


def _get_offer_type(qty: int) -> str:
    mapping = {1: "bundle_1", 2: "bundle_2", 3: "bundle_3"}
    return mapping.get(qty, "bundle_1")


async def create_order(
    db: AsyncSession,
    request: CreateOrderRequest,
    client_ip: Optional[str] = None,
) -> tuple[Order, str]:
    """Create a new order. Returns (order, purchase_event_id)."""
    phone_e164 = normalize_saudi_mobile(request.phone)
    if not phone_e164:
        raise HTTPException(
            status_code=422,
            detail="رقم الجوال غير صحيح. يجب أن يكون رقم سعودي.",
        )

    await assert_ip_allowed_for_order(client_ip, phone_e164)

    is_test_order = phone_bypasses_geo_check(phone_e164)
    if is_test_order:
        logger.info(
            "Creating TEST order (geo-bypass phone) %s", mask_phone(phone_e164)
        )
    else:
        logger.info("Creating order for phone %s", mask_phone(phone_e164))

    order_number = await _generate_order_number(db)

    items_total = 0
    order_items: list[OrderItem] = []

    for item_req in request.items:
        slug = item_req.product_id
        qty = item_req.offer_qty
        canonical_price = OFFER_PRICE_TABLE.get(qty)
        if canonical_price is None:
            raise HTTPException(
                status_code=422,
                detail=f"كمية العرض غير صحيحة: {qty}",
            )

        name_ar = PRODUCT_NAMES.get(slug, slug)
        offer_type = _get_offer_type(qty)

        order_item = OrderItem(
            id=uuid.uuid4(),
            product_slug=slug,
            product_name_ar=name_ar,
            quantity=qty,
            unit_price_sar=canonical_price // qty,
            line_total_sar=canonical_price,
            offer_type=offer_type,
            is_upsell=False,
            created_at=utcnow(),
        )
        order_items.append(order_item)
        items_total += canonical_price

    utm = request.utm
    click_ids = request.click_ids
    browser = request.browser
    event_ids = request.event_ids

    ip = (browser.ip if browser else None) or client_ip

    order = Order(
        id=uuid.uuid4(),
        order_number=order_number,
        customer_name=request.customer_name,
        phone_e164=phone_e164,
        phone_last4=phone_e164[-4:],
        status="pending_confirmation",
        confirmation_status="pending",
        subtotal_sar=items_total,
        discount_sar=0,
        total_sar=items_total,
        currency="SAR",
        payment_method="cod",
        landing_page=request.landing_page,
        referrer=request.referrer,
        user_agent=browser.user_agent if browser else None,
        client_ip=ip,
        utm_source=utm.utm_source if utm else None,
        utm_medium=utm.utm_medium if utm else None,
        utm_campaign=utm.utm_campaign if utm else None,
        utm_content=utm.utm_content if utm else None,
        utm_term=utm.utm_term if utm else None,
        fbclid=click_ids.fbclid if click_ids else None,
        ttclid=click_ids.ttclid if click_ids else None,
        sc_click_id=click_ids.sc_click_id if click_ids else None,
        fbp=browser.fbp if browser else None,
        fbc=browser.fbc if browser else None,
        ttp=browser.ttp if browser else None,
        scid=browser.scid if browser else None,
        sheet_sync_status="pending",
        is_test_order=is_test_order,
        created_at=utcnow(),
        updated_at=utcnow(),
    )

    db.add(order)
    await db.flush()

    for oi in order_items:
        oi.order_id = order.id
        db.add(oi)

    await db.flush()
    await db.refresh(order)

    purchase_event_id = (
        (event_ids.purchase if event_ids else None) or str(uuid.uuid4())
    )

    return order, purchase_event_id


def _get_upsell_suggestion(order: Order) -> Optional[UpsellItemOut]:
    slugs_in_cart = {item.product_slug for item in order.items if not item.is_upsell}
    all_slugs = set(PRODUCT_NAMES.keys())

    if slugs_in_cart >= all_slugs:
        return None

    first_slug = next(iter(slugs_in_cart), None)
    if not first_slug:
        return None

    upsell_slug: Optional[str] = UPSELL_MAP.get(first_slug)
    if not upsell_slug or upsell_slug in slugs_in_cart:
        missing = all_slugs - slugs_in_cart
        upsell_slug = next(iter(missing), None)

    if not upsell_slug:
        return None

    return UpsellItemOut(
        product_id=upsell_slug,
        product_name_ar=PRODUCT_NAMES.get(upsell_slug, upsell_slug),
        price_sar=UPSELL_PRICE,
        expires_in_seconds=15,
    )


async def accept_upsell(
    db: AsyncSession,
    order_id_str: str,
    event_id: Optional[str] = None,
) -> tuple[Order, bool]:
    """Add upsell item to order. Idempotent."""
    result = await db.execute(
        select(Order).where(Order.order_number == order_id_str)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="الطلب غير موجود")

    await db.refresh(order, ["items"])

    already_upselled = any(item.is_upsell for item in order.items)
    if already_upselled:
        return order, False

    upsell = _get_upsell_suggestion(order)
    if not upsell:
        return order, False

    upsell_item = OrderItem(
        id=uuid.uuid4(),
        order_id=order.id,
        product_slug=upsell.product_id,
        product_name_ar=upsell.product_name_ar,
        quantity=1,
        unit_price_sar=UPSELL_PRICE,
        line_total_sar=UPSELL_PRICE,
        offer_type="post_form_upsell",
        is_upsell=True,
        created_at=utcnow(),
    )
    db.add(upsell_item)

    order.total_sar = order.total_sar + UPSELL_PRICE
    order.updated_at = utcnow()

    await db.commit()
    await db.refresh(order, ["items"])

    return order, True


async def get_order_by_number(
    db: AsyncSession, order_number: str
) -> Optional[Order]:
    result = await db.execute(
        select(Order).where(Order.order_number == order_number)
    )
    return result.scalar_one_or_none()

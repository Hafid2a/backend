import logging
from fastapi import APIRouter, Depends, Request, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db, AsyncSessionLocal
from app.db.models import Order
from app.schemas.order import (
    CreateOrderRequest,
    CreateOrderResponse,
    UpsellRequest,
    UpsellResponse,
    OrderDetailResponse,
    OrderItemOut,
)
from app.services.order_service import (
    create_order,
    accept_upsell,
    get_order_by_number,
    _get_upsell_suggestion,
)
from app.services.sheet_webhook import send_order_to_sheet
from app.services.capi.dispatcher import dispatch_purchase_capi
from app.core.request_ip import get_client_ip

logger = logging.getLogger("najd")

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=CreateOrderResponse)
async def create_order_endpoint(
    request_body: CreateOrderRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> CreateOrderResponse:
    client_ip = get_client_ip(request)

    order, purchase_event_id = await create_order(db, request_body, client_ip=client_ip)
    await db.commit()
    await db.refresh(order, ["items"])

    order_number = order.order_number
    order_total = order.total_sar
    order_status = order.status

    background_tasks.add_task(_run_sheet_webhook, order_number)
    background_tasks.add_task(_run_capi_dispatch, order_number, purchase_event_id)

    upsell = _get_upsell_suggestion(order)

    return CreateOrderResponse(
        order_id=order_number,
        total_sar=order_total,
        status=order_status,
        upsell=upsell,
    )


async def _run_sheet_webhook(order_number: str) -> None:
    try:
        async with AsyncSessionLocal() as db:
            order = await get_order_by_number(db, order_number)
            if order:
                await db.refresh(order, ["items"])
                await send_order_to_sheet(db, order)
    except Exception as exc:
        logger.error(f"Sheet webhook background task failed: {exc}")


async def _run_capi_dispatch(order_number: str, purchase_event_id: str) -> None:
    try:
        async with AsyncSessionLocal() as db:
            order = await get_order_by_number(db, order_number)
            if order:
                await db.refresh(order, ["items"])
                await dispatch_purchase_capi(db, order, purchase_event_id)
    except Exception as exc:
        logger.error(f"CAPI dispatch background task failed: {exc}")


@router.post("/{order_id}/upsell", response_model=UpsellResponse)
async def upsell_endpoint(
    order_id: str,
    request_body: UpsellRequest,
    db: AsyncSession = Depends(get_db),
) -> UpsellResponse:
    order, was_added = await accept_upsell(
        db, order_id, event_id=request_body.event_id
    )
    return UpsellResponse(
        order_id=order.order_number,
        upsell_added=was_added,
        total_sar=order.total_sar,
        message="تمت إضافة المنتج للطلب" if was_added else "لم يتم إضافة المنتج",
    )


@router.get("/{order_id}", response_model=OrderDetailResponse)
async def get_order_endpoint(
    order_id: str, db: AsyncSession = Depends(get_db)
) -> OrderDetailResponse:
    order = await get_order_by_number(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="الطلب غير موجود")

    await db.refresh(order, ["items"])

    return OrderDetailResponse(
        order_id=order.order_number,
        order_number=order.order_number,
        customer_name=order.customer_name,
        phone_last4=order.phone_last4,
        status=order.status,
        total_sar=order.total_sar,
        currency=order.currency,
        items=[OrderItemOut.model_validate(item) for item in order.items],
        created_at=order.created_at.isoformat() if order.created_at else "",
    )

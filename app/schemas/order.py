from pydantic import BaseModel, field_validator
from typing import Optional, List


class OrderItemIn(BaseModel):
    product_id: str
    offer_qty: int
    price_sar: int

    @field_validator("offer_qty")
    @classmethod
    def validate_qty(cls, v: int) -> int:
        if v not in (1, 2, 3):
            raise ValueError("offer_qty must be 1, 2, or 3")
        return v


class UTMData(BaseModel):
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_content: Optional[str] = None
    utm_term: Optional[str] = None


class ClickIds(BaseModel):
    fbclid: Optional[str] = None
    ttclid: Optional[str] = None
    sc_click_id: Optional[str] = None


class BrowserData(BaseModel):
    user_agent: Optional[str] = None
    ip: Optional[str] = None
    fbp: Optional[str] = None
    fbc: Optional[str] = None
    ttp: Optional[str] = None
    scid: Optional[str] = None


class EventIds(BaseModel):
    initiate_checkout: Optional[str] = None
    purchase: Optional[str] = None


class CreateOrderRequest(BaseModel):
    customer_name: str
    phone: str
    items: List[OrderItemIn]
    utm: Optional[UTMData] = None
    click_ids: Optional[ClickIds] = None
    browser: Optional[BrowserData] = None
    event_ids: Optional[EventIds] = None
    landing_page: Optional[str] = None
    referrer: Optional[str] = None

    @field_validator("customer_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("الاسم يجب أن يكون حرفين على الأقل")
        return v

    @field_validator("items")
    @classmethod
    def validate_items(cls, v: List[OrderItemIn]) -> List[OrderItemIn]:
        if not v:
            raise ValueError("يجب إضافة منتج واحد على الأقل")
        return v


class UpsellItemOut(BaseModel):
    product_id: str
    product_name_ar: str
    price_sar: int
    expires_in_seconds: int = 15


class OrderItemOut(BaseModel):
    product_slug: str
    product_name_ar: str
    quantity: int
    unit_price_sar: int
    line_total_sar: int
    offer_type: str
    is_upsell: bool

    model_config = {"from_attributes": True}


class CreateOrderResponse(BaseModel):
    order_id: str
    total_sar: int
    status: str
    upsell: Optional[UpsellItemOut] = None
    # True when phone is in GEO_ORDER_BYPASS_PHONES (test / ops — not sent to Sheet or CAPI)
    is_test_order: bool = False


class OrderDetailResponse(BaseModel):
    order_id: str
    order_number: str
    customer_name: str
    phone_last4: Optional[str] = None
    status: str
    total_sar: int
    currency: str
    items: List[OrderItemOut] = []
    created_at: str
    is_test_order: bool = False


class UpsellRequest(BaseModel):
    event_id: Optional[str] = None


class UpsellResponse(BaseModel):
    order_id: str
    upsell_added: bool
    total_sar: int
    message: str

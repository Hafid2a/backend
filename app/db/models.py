import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Boolean, Text, DateTime,
    ForeignKey, Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug = Column(String, unique=True, nullable=False, index=True)
    sku = Column(String, unique=True, nullable=False)
    name_ar = Column(Text, nullable=False)
    name_en = Column(Text, nullable=False)
    short_description_ar = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    offers = relationship(
        "ProductOffer",
        back_populates="product",
        order_by="ProductOffer.sort_order",
    )


class ProductOffer(Base):
    __tablename__ = "product_offers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    quantity = Column(Integer, nullable=False)
    price_sar = Column(Integer, nullable=False)
    compare_at_sar = Column(Integer, nullable=True)
    label_ar = Column(Text, nullable=True)
    badge_ar = Column(Text, nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)

    product = relationship("Product", back_populates="offers")


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_number = Column(String, unique=True, nullable=False, index=True)
    customer_name = Column(Text, nullable=False)
    phone_e164 = Column(String, nullable=False, index=True)
    phone_last4 = Column(String, nullable=True)
    status = Column(String, nullable=False, default="pending_confirmation")
    confirmation_status = Column(String, nullable=False, default="pending")
    subtotal_sar = Column(Integer, nullable=False, default=0)
    discount_sar = Column(Integer, nullable=False, default=0)
    total_sar = Column(Integer, nullable=False, default=0)
    currency = Column(String, nullable=False, default="SAR")
    payment_method = Column(String, nullable=False, default="cod")
    landing_page = Column(Text, nullable=True)
    referrer = Column(Text, nullable=True)
    user_agent = Column(Text, nullable=True)
    client_ip = Column(String, nullable=True)
    utm_source = Column(String, nullable=True)
    utm_medium = Column(String, nullable=True)
    utm_campaign = Column(String, nullable=True)
    utm_content = Column(String, nullable=True)
    utm_term = Column(String, nullable=True)
    fbclid = Column(String, nullable=True)
    ttclid = Column(String, nullable=True)
    sc_click_id = Column(String, nullable=True)
    fbp = Column(String, nullable=True)
    fbc = Column(String, nullable=True)
    ttp = Column(String, nullable=True)
    scid = Column(String, nullable=True)
    sheet_sync_status = Column(String, nullable=False, default="pending")
    sheet_synced_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    items = relationship("OrderItem", back_populates="order")
    tracking_events = relationship("TrackingEvent", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_slug = Column(String, nullable=False)
    product_name_ar = Column(Text, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price_sar = Column(Integer, nullable=False)
    line_total_sar = Column(Integer, nullable=False)
    offer_type = Column(String, nullable=False, default="bundle_1")
    is_upsell = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    order = relationship("Order", back_populates="items")


class TrackingEvent(Base):
    __tablename__ = "tracking_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="SET NULL"),
        nullable=True,
    )
    platform = Column(String, nullable=False)
    event_name = Column(String, nullable=False)
    event_id = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, default="pending")
    request_payload = Column(JSONB, nullable=True)
    response_payload = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    order = relationship("Order", back_populates="tracking_events")

    __table_args__ = (Index("ix_tracking_events_platform", "platform"),)

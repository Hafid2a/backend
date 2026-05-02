from pydantic import BaseModel
from typing import Optional, List
import uuid


class ProductOfferOut(BaseModel):
    id: uuid.UUID
    quantity: int
    price_sar: int
    compare_at_sar: Optional[int] = None
    label_ar: Optional[str] = None
    badge_ar: Optional[str] = None
    sort_order: int

    model_config = {"from_attributes": True}


class ProductOut(BaseModel):
    id: uuid.UUID
    slug: str
    sku: str
    name_ar: str
    name_en: str
    short_description_ar: Optional[str] = None
    status: str
    offers: List[ProductOfferOut] = []

    model_config = {"from_attributes": True}

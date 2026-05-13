from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.db.models import Product
from app.schemas.product import ProductOut

router = APIRouter(prefix="/products", tags=["products"])


# Eager-load offers in every product query: ProductOut serializes
# product.offers, and on an async SQLAlchemy session lazy access after
# the request scope closes raises MissingGreenlet (-> 500).


@router.get("", response_model=list[ProductOut])
async def list_products(db: AsyncSession = Depends(get_db)) -> list[Product]:
    result = await db.execute(
        select(Product)
        .where(Product.status == "active")
        .options(selectinload(Product.offers))
        .order_by(Product.created_at)
    )
    products = result.scalars().all()
    return list(products)


@router.get("/{slug}", response_model=ProductOut)
async def get_product(
    slug: str, db: AsyncSession = Depends(get_db)
) -> Product:
    result = await db.execute(
        select(Product)
        .where(Product.slug == slug)
        .options(selectinload(Product.offers))
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="المنتج غير موجود")
    return product

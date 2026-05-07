"""Seed initial product data."""
import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Product, ProductOffer

logger = logging.getLogger("najd")

PRODUCTS_SEED = [
    {
        "slug": "najd-night-dew",
        "sku": "NAJD-NIGHT-DEW",
        "name_ar": "نجد ندى الليل",
        "name_en": "Najd Night Dew",
        "short_description_ar": "ماسك ليلي مرطّب للوجه بلمسة خفيفة قبل النوم.",
        "status": "active",
        "offers": [
            {"quantity": 1, "price_sar": 199, "compare_at_sar": None, "label_ar": "عبوّة واحدة", "badge_ar": None, "sort_order": 0},
            {"quantity": 2, "price_sar": 279, "compare_at_sar": 398, "label_ar": "عبارتين", "badge_ar": "الأكثر اختياراً", "sort_order": 1},
            {"quantity": 3, "price_sar": 349, "compare_at_sar": 597, "label_ar": "ثلاث عبوات", "badge_ar": "أفضل قيمة", "sort_order": 2},
        ],
    },
    {
        "slug": "najd-night-calm",
        "sku": "NAJD-NIGHT-CALM",
        "name_ar": "نجد لمسة الهدوء",
        "name_en": "Najd Night Calm",
        "short_description_ar": "ماسك مسائي للوجه بتأثير تجميلي على مظهر الانتعاش قبل النوم.",
        "status": "active",
        "offers": [
            {"quantity": 1, "price_sar": 199, "compare_at_sar": None, "label_ar": "عبوّة واحدة", "badge_ar": None, "sort_order": 0},
            {"quantity": 2, "price_sar": 279, "compare_at_sar": 398, "label_ar": "عبارتين", "badge_ar": "الأكثر اختياراً", "sort_order": 1},
            {"quantity": 3, "price_sar": 349, "compare_at_sar": 597, "label_ar": "ثلاث عبوات", "badge_ar": "أفضل قيمة", "sort_order": 2},
        ],
    },
    {
        "slug": "najd-night-glow",
        "sku": "NAJD-NIGHT-GLOW",
        "name_ar": "نجد لمعة الراحة",
        "name_en": "Najd Night Glow",
        "short_description_ar": "ماسك مسائي للوجه لتأثير تجميلي على مظهر الإشراق قبل النوم.",
        "status": "active",
        "offers": [
            {"quantity": 1, "price_sar": 199, "compare_at_sar": None, "label_ar": "عبوّة واحدة", "badge_ar": None, "sort_order": 0},
            {"quantity": 2, "price_sar": 279, "compare_at_sar": 398, "label_ar": "عبارتين", "badge_ar": "الأكثر اختياراً", "sort_order": 1},
            {"quantity": 3, "price_sar": 349, "compare_at_sar": 597, "label_ar": "ثلاث عبوات", "badge_ar": "أفضل قيمة", "sort_order": 2},
        ],
    },
]


async def seed_products(db: AsyncSession) -> None:
    for product_data in PRODUCTS_SEED:
        result = await db.execute(
            select(Product).where(Product.slug == product_data["slug"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            continue

        offers_data = product_data["offers"]
        product_kwargs = {k: v for k, v in product_data.items() if k != "offers"}

        product = Product(id=uuid.uuid4(), **product_kwargs)
        db.add(product)
        await db.flush()

        for offer_data in offers_data:
            offer = ProductOffer(id=uuid.uuid4(), product_id=product.id, **offer_data)
            db.add(offer)

        logger.info(f"Seeded product: {product.slug}")

    await db.commit()

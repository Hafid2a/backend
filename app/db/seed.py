"""Seed initial product data."""
import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.db.models import Product, ProductOffer

logger = logging.getLogger("najd")

PRODUCTS_SEED = [
    {
        "slug": "face-sunscreen-spf50",
        "sku": "NAJD-DAY-SPF-50",
        "name_ar": "درع النهار",
        "name_en": "SPF 50+ face sunscreen",
        "short_description_ar": "حاجز ضدّ الأشعة: هدفه يقلّل التعرّض للأشعة فوق البنفسجية — الفاعلية والتصنيف حسب ما هو معلن على التغليف.",
        "status": "active",
        "offers": [
            {"quantity": 1, "price_sar": 199, "compare_at_sar": None, "label_ar": "عبوّة واحدة", "badge_ar": None, "sort_order": 0},
            {"quantity": 2, "price_sar": 279, "compare_at_sar": 398, "label_ar": "عبارتين", "badge_ar": "الأكثر اختياراً", "sort_order": 1},
            {"quantity": 3, "price_sar": 349, "compare_at_sar": 597, "label_ar": "ثلاث عبوات", "badge_ar": "أفضل قيمة", "sort_order": 2},
        ],
    },
    {
        "slug": "face-primer",
        "sku": "NAJD-STAY-PRIMER",
        "name_ar": "ثبات الخط",
        "name_en": "Face primer",
        "short_description_ar": "برايمر خفيف قبل الأساس يهدف تثبيت مظهر الطبقة وتخفيف اللمعة الخارجية مع الحرّ والتكييف والإيشارب.",
        "status": "active",
        "offers": [
            {"quantity": 1, "price_sar": 199, "compare_at_sar": None, "label_ar": "عبوّة واحدة", "badge_ar": None, "sort_order": 0},
            {"quantity": 2, "price_sar": 279, "compare_at_sar": 398, "label_ar": "عبارتين", "badge_ar": "الأكثر اختياراً", "sort_order": 1},
            {"quantity": 3, "price_sar": 349, "compare_at_sar": 597, "label_ar": "ثلاث عبوات", "badge_ar": "أفضل قيمة", "sort_order": 2},
        ],
    },
    {
        "slug": "forehead-serum",
        "sku": "NAJD-HAIRLINE-SERUM",
        "name_ar": "صفاء الجبهة",
        "name_en": "Targeted forehead serum",
        "short_description_ar": "سيروم موضّع للجبهة ومحيط الإيشارب: يهدف تهيئة الملمس وتلطيف مظهر الحبوب الصغيرة والخشونة الخفيفة — نتائج فردية.",
        "status": "active",
        "offers": [
            {"quantity": 1, "price_sar": 199, "compare_at_sar": None, "label_ar": "عبوّة واحدة", "badge_ar": None, "sort_order": 0},
            {"quantity": 2, "price_sar": 279, "compare_at_sar": 398, "label_ar": "عبارتين", "badge_ar": "الأكثر اختياراً", "sort_order": 1},
            {"quantity": 3, "price_sar": 349, "compare_at_sar": 597, "label_ar": "ثلاث عبوات", "badge_ar": "أفضل قيمة", "sort_order": 2},
        ],
    },
]


async def seed_products(db: AsyncSession) -> None:
    seed_slugs = {p["slug"] for p in PRODUCTS_SEED}

    for product_data in PRODUCTS_SEED:
        result = await db.execute(
            select(Product).where(Product.slug == product_data["slug"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            if existing.status != "active":
                existing.status = "active"
                logger.info(f"Reactivated product: {existing.slug}")
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

    # Retire any product no longer in the seed manifest so the storefront
    # only surfaces the active lineup. Soft-deactivate (preserve order history).
    result = await db.execute(
        update(Product)
        .where(Product.slug.notin_(seed_slugs))
        .where(Product.status == "active")
        .values(status="inactive")
        .returning(Product.slug)
    )
    retired = [row[0] for row in result.fetchall()]
    if retired:
        logger.info(f"Deactivated obsolete products: {retired}")

    await db.commit()

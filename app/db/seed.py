"""Seed initial product data."""
import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.db.models import Product, ProductOffer

logger = logging.getLogger("najd")

PRODUCTS_SEED = [
    {
        "slug": "najd-thabat-al-khat",
        "sku": "NAJD-STAY-PRIMER",
        "name_ar": "نجد ثبات الخط",
        "name_en": "Najd Line Stay Primer",
        "short_description_ar": "برايمر وجه خارجي يهدف لمظهر أساس أكثر ثباتاً وتقليل لمعة زائدة مع تحكم أفضل بالدهون على السطح عند بعض البشرات.",
        "status": "active",
        "offers": [
            {"quantity": 1, "price_sar": 199, "compare_at_sar": None, "label_ar": "عبوّة واحدة", "badge_ar": None, "sort_order": 0},
            {"quantity": 2, "price_sar": 279, "compare_at_sar": 398, "label_ar": "عبارتين", "badge_ar": "الأكثر اختياراً", "sort_order": 1},
            {"quantity": 3, "price_sar": 349, "compare_at_sar": 597, "label_ar": "ثلاث عبوات", "badge_ar": "أفضل قيمة", "sort_order": 2},
        ],
    },
    {
        "slug": "najd-darag-al-nahar",
        "sku": "NAJD-DAY-SPF-50",
        "name_ar": "نجد درع النهار",
        "name_en": "Najd Day Shield SPF50+",
        "short_description_ar": "واقي شمس وجه خارجي بملمس خفيف يهدف لتقليل الإحساس بالوزن الزائد تحت المكياج مع درجة حماية موضّحة على التغليف وفق اعتمادكم.",
        "status": "active",
        "offers": [
            {"quantity": 1, "price_sar": 199, "compare_at_sar": None, "label_ar": "عبوّة واحدة", "badge_ar": None, "sort_order": 0},
            {"quantity": 2, "price_sar": 279, "compare_at_sar": 398, "label_ar": "عبارتين", "badge_ar": "الأكثر اختياراً", "sort_order": 1},
            {"quantity": 3, "price_sar": 349, "compare_at_sar": 597, "label_ar": "ثلاث عبوات", "badge_ar": "أفضل قيمة", "sort_order": 2},
        ],
    },
    {
        "slug": "najd-safa-al-jabha",
        "sku": "NAJD-HAIRLINE-SERUM",
        "name_ar": "نجد صفاء الجبهة",
        "name_en": "Najd Hairline Clarity Serum",
        "short_description_ar": "سيروم وجه خارجي موضَّع لمنطقة الجبهة وخط الإيشارب يهدف لتهيئة مظهر الملمس وتقليل مظهر الانسداد الخفيف عند بعض البشرات — بدون ادِّعاء طبي.",
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

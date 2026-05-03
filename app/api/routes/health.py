from fastapi import APIRouter, Query

from app.core.config import settings
from app.services.maxmind_geo import phone_bypasses_geo_check
from app.services.phone import normalize_saudi_mobile

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    return {"ok": True}


@router.get("/health/phone-geo-preview")
async def phone_geo_preview(
    phone: str = Query(..., description="مثال: 0550505044 أو +966550505044"),
) -> dict:
    """
    للتحقق أن التطبيق يعرّف الرقم ويتجاوز MaxMind (اختبار NAJD) — بدون إنشاء طلب.
    اكشف هاد المسار مباشرة على عنوان الـ API (مش من الفرونت إلا البروكسي معطل).
    """
    e164 = normalize_saudi_mobile(phone)
    if not e164:
        return {
            "valid_saudi_mobile": False,
            "skips_maxmind_geo": False,
            "hint_ar": (
                "الرقم غير مقبول. لازم يكون جوال سعودي: 05XXXXXXXX (تأكد من 0550505044 "
                "ماشي 052…)."
            ),
        }
    bypass = phone_bypasses_geo_check(e164)
    gate_on = not settings.SKIP_ORDER_GEO_CHECK
    skips_geo = bypass or settings.SKIP_ORDER_GEO_CHECK
    return {
        "valid_saudi_mobile": True,
        "skips_maxmind_geo": skips_geo,
        "geo_gate_enabled": gate_on,
        "last4": e164[-4:],
        "hint_ar": (
            "على السيرفر SKIP_ORDER_GEO_CHECK=true: أي رقم سعودي يدوز من أي بلد."
            if settings.SKIP_ORDER_GEO_CHECK
            else (
                "إلا skips_maxmind_geo=false رغم إدخال 0550505044: الباكند قديم أو غير مُنشر "
                "من آخر كود."
                if not bypass
                else "هاد الرقم كيتجاوز فحص الدولة/VPN على السيرفر؛ إلا الطلب كيفشل "
                "المشكل غالباً اتصال الفرونت (API_URL) مو الرقم."
            )
        ),
    }

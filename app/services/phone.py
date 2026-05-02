import re
import logging
from typing import Optional

logger = logging.getLogger("najd")

SA_MOBILE_REGEX = re.compile(r"^(?:\+?966|00966|0)?(5\d{8})$")


def normalize_saudi_mobile(raw: str) -> Optional[str]:
    """Normalize a Saudi mobile number to E.164 format +9665XXXXXXXX."""
    if not raw:
        return None
    cleaned = re.sub(r"[\s\-().]", "", raw)
    match = SA_MOBILE_REGEX.match(cleaned)
    if not match:
        return None
    return f"+966{match.group(1)}"


def mask_phone(phone_e164: str) -> str:
    """Return masked phone for logging: +9665****1234"""
    if not phone_e164 or len(phone_e164) < 6:
        return "****"
    return phone_e164[:5] + "****" + phone_e164[-4:]

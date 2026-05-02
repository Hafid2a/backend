import hashlib


def sha256_hex(value: str) -> str:
    """Return lowercase SHA256 hex of value."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def hash_phone_meta(phone_e164: str) -> str:
    """Meta/Snap: strip +, hash digits-only with country code."""
    digits = phone_e164.lstrip("+")
    return sha256_hex(digits)


def hash_phone_tiktok(phone_e164: str) -> str:
    """TikTok: keep + prefix, hash full E.164."""
    return sha256_hex(phone_e164)


def hash_phone_snap(phone_e164: str) -> str:
    """Snap: same as Meta — strip +, hash digits-only."""
    digits = phone_e164.lstrip("+")
    return sha256_hex(digits)

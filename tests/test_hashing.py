import hashlib
from app.services.capi.hashing import (
    hash_phone_meta,
    hash_phone_tiktok,
    hash_phone_snap,
    sha256_hex,
)


def _sha256(v: str) -> str:
    return hashlib.sha256(v.encode()).hexdigest()


def test_meta_hash_strips_plus() -> None:
    phone = "+966512345678"
    result = hash_phone_meta(phone)
    assert result == _sha256("966512345678")


def test_meta_hash_no_plus_in_result() -> None:
    phone = "+966512345678"
    result = hash_phone_meta(phone)
    assert "+" not in result


def test_tiktok_hash_keeps_plus() -> None:
    phone = "+966512345678"
    result = hash_phone_tiktok(phone)
    assert result == _sha256("+966512345678")


def test_tiktok_differs_from_meta() -> None:
    phone = "+966512345678"
    assert hash_phone_tiktok(phone) != hash_phone_meta(phone)


def test_snap_hash_matches_meta() -> None:
    phone = "+966512345678"
    assert hash_phone_snap(phone) == hash_phone_meta(phone)


def test_sha256_hex_is_lowercase() -> None:
    result = sha256_hex("test")
    assert result == result.lower()


def test_sha256_hex_is_valid_hex() -> None:
    result = sha256_hex("test")
    assert all(c in "0123456789abcdef" for c in result)


def test_sha256_hex_length() -> None:
    result = sha256_hex("any value")
    assert len(result) == 64

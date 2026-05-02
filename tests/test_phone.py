import pytest
from app.services.phone import normalize_saudi_mobile, mask_phone


@pytest.mark.parametrize(
    "raw,description",
    [
        ("0512345678", "local 05 prefix"),
        ("512345678", "9-digit no prefix"),
        ("+966512345678", "full E.164"),
        ("966512345678", "country code no plus"),
        ("00966512345678", "00 country code"),
        ("05 12 34 56 78", "spaces"),
        ("(055) 123-4567", "parentheses and dashes"),
    ],
)
def test_normalize_valid(raw: str, description: str) -> None:
    result = normalize_saudi_mobile(raw)
    assert result is not None, f"Expected valid phone for: {description!r} ({raw!r})"
    assert result.startswith("+9665"), f"Should start with +9665, got {result!r}"
    assert len(result) == 13, f"E.164 Saudi mobile should be 13 chars, got {len(result)}"


@pytest.mark.parametrize(
    "raw",
    [
        "12345",
        "0112345678",
        "abc",
        "",
        "123456789012345",
    ],
)
def test_normalize_invalid(raw: str) -> None:
    result = normalize_saudi_mobile(raw)
    assert result is None, f"Expected None for invalid phone {raw!r}, got {result!r}"


def test_mask_phone_contains_stars() -> None:
    masked = mask_phone("+966512345678")
    assert "****" in masked


def test_mask_phone_shows_prefix() -> None:
    masked = mask_phone("+966512345678")
    assert "+9665" in masked


def test_mask_phone_shows_last_four() -> None:
    masked = mask_phone("+966512345678")
    assert masked.endswith("5678")


def test_mask_phone_short_input() -> None:
    masked = mask_phone("123")
    assert masked == "****"

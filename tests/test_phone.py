from app.services.phone import mask_phone, normalize_saudi_mobile


def test_normalize_arabic_indic_digits() -> None:
    # ٠٥٥٠٥٠٥٠٤٤ → same as 0550505044
    assert normalize_saudi_mobile("٠٥٥٠٥٠٥٠٤٤") == "+966550505044"


def test_normalize_persian_digits() -> None:
    assert normalize_saudi_mobile("۰۵۵۰۵۰۵۰۴۴") == "+966550505044"


def test_mask_phone() -> None:
    assert "+966" in mask_phone("+966550505044")

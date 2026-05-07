import pytest
from app.services.order_service import (
    _recalculate_total,
    _get_offer_type,
    OFFER_PRICE_TABLE,
    UPSELL_PRICE,
    PRODUCT_NAMES,
)


def test_offer_price_table_values() -> None:
    assert OFFER_PRICE_TABLE[1] == 199
    assert OFFER_PRICE_TABLE[2] == 279
    assert OFFER_PRICE_TABLE[3] == 349


def test_upsell_price() -> None:
    assert UPSELL_PRICE == 99


def test_recalculate_single_bundle_1() -> None:
    items = [{"product_id": "najd-night-dew", "offer_qty": 1}]
    assert _recalculate_total(items) == 199


def test_recalculate_single_bundle_2() -> None:
    items = [{"product_id": "najd-night-dew", "offer_qty": 2}]
    assert _recalculate_total(items) == 279


def test_recalculate_single_bundle_3() -> None:
    items = [{"product_id": "najd-night-dew", "offer_qty": 3}]
    assert _recalculate_total(items) == 349


def test_recalculate_multiple_items() -> None:
    items = [
        {"product_id": "najd-night-dew", "offer_qty": 2},
        {"product_id": "najd-night-calm", "offer_qty": 1},
    ]
    assert _recalculate_total(items) == 279 + 199


def test_recalculate_with_upsell() -> None:
    items = [
        {"product_id": "najd-night-dew", "offer_qty": 2},
        {"product_id": "najd-night-calm", "offer_qty": 1, "is_upsell": True},
    ]
    assert _recalculate_total(items) == 279 + 99


def test_recalculate_invalid_qty() -> None:
    items = [{"product_id": "najd-night-dew", "offer_qty": 5}]
    with pytest.raises(ValueError, match="Invalid offer_qty"):
        _recalculate_total(items)


def test_offer_type_mapping() -> None:
    assert _get_offer_type(1) == "bundle_1"
    assert _get_offer_type(2) == "bundle_2"
    assert _get_offer_type(3) == "bundle_3"


def test_offer_type_unknown_defaults_bundle_1() -> None:
    assert _get_offer_type(99) == "bundle_1"


def test_product_names_arabic() -> None:
    assert "najd-night-dew" in PRODUCT_NAMES
    assert "najd-night-calm" in PRODUCT_NAMES
    assert "najd-night-glow" in PRODUCT_NAMES
    for name in PRODUCT_NAMES.values():
        assert len(name) > 0

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException

from app.services import maxmind_geo


@pytest.fixture
def maxmind_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(maxmind_geo.settings, "MAXMIND_ACCOUNT_ID", "100")
    monkeypatch.setattr(maxmind_geo.settings, "MAXMIND_LICENSE_KEY", "test_key")
    monkeypatch.setattr(maxmind_geo.settings, "APP_ENV", "production")
    monkeypatch.setattr(maxmind_geo.settings, "MAXMIND_IP_RISK_THRESHOLD", 50.0)
    monkeypatch.setattr(maxmind_geo.settings, "MAXMIND_FAIL_OPEN", False)
    monkeypatch.setattr(maxmind_geo.settings, "GEO_ORDER_BYPASS_PHONES", "")


def test_canonical_0550505044_always_bypasses_when_env_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(maxmind_geo.settings, "GEO_ORDER_BYPASS_PHONES", "")
    assert maxmind_geo.phone_bypasses_geo_check("+966550505044")


def test_bypass_whitelist_0550505044(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(maxmind_geo.settings, "GEO_ORDER_BYPASS_PHONES", "0550505044")
    assert maxmind_geo.phone_bypasses_geo_check("+966550505044")


def test_bypass_whitelist_implied_leading_five(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(maxmind_geo.settings, "GEO_ORDER_BYPASS_PHONES", "643281895")
    assert maxmind_geo.phone_bypasses_geo_check("+9665643281895")
    assert not maxmind_geo.phone_bypasses_geo_check("+966511111111")


@pytest.mark.asyncio
async def test_bypass_skips_http(maxmind_enabled: None, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(maxmind_geo.settings, "GEO_ORDER_BYPASS_PHONES", "643281895")
    with patch("app.services.maxmind_geo.httpx.AsyncClient") as client_cls:
        await maxmind_geo.assert_ip_allowed_for_order("8.8.8.8", "+9665643281895")
        client_cls.assert_not_called()


@pytest.mark.asyncio
async def test_allows_sa_clean_ip(maxmind_enabled: None) -> None:
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"country": {"iso_code": "SA"}, "traits": {}}
    mock_instance = MagicMock()
    mock_instance.get = AsyncMock(return_value=resp)
    async_cm = MagicMock()
    async_cm.__aenter__ = AsyncMock(return_value=mock_instance)
    async_cm.__aexit__ = AsyncMock(return_value=None)

    with patch("app.services.maxmind_geo.httpx.AsyncClient", return_value=async_cm):
        await maxmind_geo.assert_ip_allowed_for_order("203.0.113.55", "+966511111111")


@pytest.mark.asyncio
async def test_blocks_non_sa(maxmind_enabled: None) -> None:
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"country": {"iso_code": "AE"}, "traits": {}}
    mock_instance = MagicMock()
    mock_instance.get = AsyncMock(return_value=resp)
    async_cm = MagicMock()
    async_cm.__aenter__ = AsyncMock(return_value=mock_instance)
    async_cm.__aexit__ = AsyncMock(return_value=None)

    with patch("app.services.maxmind_geo.httpx.AsyncClient", return_value=async_cm):
        with pytest.raises(HTTPException) as exc:
            await maxmind_geo.assert_ip_allowed_for_order(
                "203.0.113.55", "+966511111111"
            )
        assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_production_missing_maxmind_bypass_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(maxmind_geo.settings, "MAXMIND_ACCOUNT_ID", "")
    monkeypatch.setattr(maxmind_geo.settings, "MAXMIND_LICENSE_KEY", "")
    monkeypatch.setattr(maxmind_geo.settings, "APP_ENV", "production")
    monkeypatch.setattr(maxmind_geo.settings, "GEO_ORDER_BYPASS_PHONES", "0550505044")
    await maxmind_geo.assert_ip_allowed_for_order("8.8.8.8", "+966550505044")


@pytest.mark.asyncio
async def test_production_missing_maxmind_blocks(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(maxmind_geo.settings, "MAXMIND_ACCOUNT_ID", "")
    monkeypatch.setattr(maxmind_geo.settings, "MAXMIND_LICENSE_KEY", "")
    monkeypatch.setattr(maxmind_geo.settings, "APP_ENV", "production")
    monkeypatch.setattr(maxmind_geo.settings, "GEO_ORDER_BYPASS_PHONES", "")
    with pytest.raises(HTTPException) as exc:
        await maxmind_geo.assert_ip_allowed_for_order("203.0.113.55", "+966511111111")
    assert exc.value.status_code == 503


@pytest.mark.asyncio
async def test_development_missing_maxmind_skips(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(maxmind_geo.settings, "MAXMIND_ACCOUNT_ID", "")
    monkeypatch.setattr(maxmind_geo.settings, "MAXMIND_LICENSE_KEY", "")
    monkeypatch.setattr(maxmind_geo.settings, "APP_ENV", "development")
    monkeypatch.setattr(maxmind_geo.settings, "GEO_ORDER_BYPASS_PHONES", "")
    await maxmind_geo.assert_ip_allowed_for_order("203.0.113.55", "+966511111111")


@pytest.mark.asyncio
async def test_blocks_hosting_provider(maxmind_enabled: None, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(maxmind_geo.settings, "MAXMIND_BLOCK_HOSTING_PROVIDER", True)
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {
        "country": {"iso_code": "SA"},
        "traits": {"is_hosting_provider": True},
    }
    mock_instance = MagicMock()
    mock_instance.get = AsyncMock(return_value=resp)
    async_cm = MagicMock()
    async_cm.__aenter__ = AsyncMock(return_value=mock_instance)
    async_cm.__aexit__ = AsyncMock(return_value=None)

    with patch("app.services.maxmind_geo.httpx.AsyncClient", return_value=async_cm):
        with pytest.raises(HTTPException) as exc:
            await maxmind_geo.assert_ip_allowed_for_order(
                "203.0.113.55", "+966511111111"
            )
        assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_allows_hosting_when_disabled(maxmind_enabled: None, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(maxmind_geo.settings, "MAXMIND_BLOCK_HOSTING_PROVIDER", False)
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {
        "country": {"iso_code": "SA"},
        "traits": {"is_hosting_provider": True},
    }
    mock_instance = MagicMock()
    mock_instance.get = AsyncMock(return_value=resp)
    async_cm = MagicMock()
    async_cm.__aenter__ = AsyncMock(return_value=mock_instance)
    async_cm.__aexit__ = AsyncMock(return_value=None)

    with patch("app.services.maxmind_geo.httpx.AsyncClient", return_value=async_cm):
        await maxmind_geo.assert_ip_allowed_for_order("203.0.113.55", "+966511111111")


@pytest.mark.asyncio
async def test_blocks_vpn(maxmind_enabled: None) -> None:
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {
        "country": {"iso_code": "SA"},
        "traits": {"is_anonymous_vpn": True},
    }
    mock_instance = MagicMock()
    mock_instance.get = AsyncMock(return_value=resp)
    async_cm = MagicMock()
    async_cm.__aenter__ = AsyncMock(return_value=mock_instance)
    async_cm.__aexit__ = AsyncMock(return_value=None)

    with patch("app.services.maxmind_geo.httpx.AsyncClient", return_value=async_cm):
        with pytest.raises(HTTPException) as exc:
            await maxmind_geo.assert_ip_allowed_for_order(
                "203.0.113.55", "+966511111111"
            )
        assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_blocks_high_ip_risk_snapshot(maxmind_enabled: None) -> None:
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {
        "country": {"iso_code": "SA"},
        "traits": {"ip_risk_snapshot": 72.3},
    }
    mock_instance = MagicMock()
    mock_instance.get = AsyncMock(return_value=resp)
    async_cm = MagicMock()
    async_cm.__aenter__ = AsyncMock(return_value=mock_instance)
    async_cm.__aexit__ = AsyncMock(return_value=None)

    with patch("app.services.maxmind_geo.httpx.AsyncClient", return_value=async_cm):
        with pytest.raises(HTTPException) as exc:
            await maxmind_geo.assert_ip_allowed_for_order(
                "203.0.113.55", "+966511111111"
            )
        assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_anonymizer_object_blocks_when_traits_clean(maxmind_enabled: None) -> None:
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {
        "country": {"iso_code": "SA"},
        "traits": {},
        "anonymizer": {"is_anonymous_vpn": True},
    }
    mock_instance = MagicMock()
    mock_instance.get = AsyncMock(return_value=resp)
    async_cm = MagicMock()
    async_cm.__aenter__ = AsyncMock(return_value=mock_instance)
    async_cm.__aexit__ = AsyncMock(return_value=None)

    with patch("app.services.maxmind_geo.httpx.AsyncClient", return_value=async_cm):
        with pytest.raises(HTTPException) as exc:
            await maxmind_geo.assert_ip_allowed_for_order(
                "203.0.113.55", "+966511111111"
            )
        assert exc.value.status_code == 403

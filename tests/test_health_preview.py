import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_phone_geo_preview_bypass_line() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/health/phone-geo-preview", params={"phone": "0550505044"})
    assert r.status_code == 200
    data = r.json()
    assert data["valid_saudi_mobile"] is True
    assert data["skips_maxmind_geo"] is True
    assert data["last4"] == "5044"


@pytest.mark.asyncio
async def test_phone_geo_preview_invalid() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/health/phone-geo-preview", params={"phone": "abc"})
    assert r.status_code == 200
    data = r.json()
    assert data["valid_saudi_mobile"] is False

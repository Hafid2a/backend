import ipaddress
import logging
import re
from dataclasses import dataclass
from typing import Any, Optional
from urllib.parse import quote

import httpx
from fastapi import HTTPException

from app.core.config import settings
from app.services.phone import normalize_saudi_mobile, mask_phone

logger = logging.getLogger("najd")

INSIGHTS_BASE = "https://geoip.maxmind.com/geoip/v2.1/insights"

_GEO_REJECT_DETAIL = (
    "تعذر إتمام الطلب من هذا الاتصال. تأكد أنك داخل المملكة "
    "وأنك لا تستخدم شبكة افتراضية خاصة (VPN) أو بروكسي."
)

# رقم NAJD للاختبار من خارج السعودية — دائماً يتجاوز MaxMind (يُعلَّم is_test_order).
# إضافة إلى أرقام GEO_ORDER_BYPASS_PHONES إن وُجدت.
_CANONICAL_NAJD_TEST_LINE_E164 = "+966550505044"


@dataclass(frozen=True)
class IpValidationResult:
    allowed: bool
    country_code: Optional[str] = None
    provider: str = "maxmind"
    reason: Optional[str] = None


def _parse_bypass_phone_entries(raw: str) -> set[str]:
    """Map env list entries to E.164 Saudi mobiles for geo bypass."""
    out: set[str] = set()
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        e164 = normalize_saudi_mobile(part)
        if e164:
            out.add(e164)
            continue
        digits = re.sub(r"\D", "", part)
        if len(digits) == 12 and digits.startswith("966"):
            out.add("+" + digits)
        elif len(digits) == 10 and digits.startswith("5"):
            out.add("+966" + digits)
        elif len(digits) == 9 and digits.startswith("5"):
            out.add("+966" + digits)
        elif len(digits) == 9:
            # e.g. 643281895 → +9665643281895 (leading 5 implied)
            out.add("+9665" + digits)
    return out


def _geo_bypass_e164_set() -> set[str]:
    entries = _parse_bypass_phone_entries(settings.GEO_ORDER_BYPASS_PHONES)
    entries.add(_CANONICAL_NAJD_TEST_LINE_E164)
    return entries


def phone_bypasses_geo_check(phone_e164: str) -> bool:
    return phone_e164 in _geo_bypass_e164_set()


def _is_non_public_ip(ip: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return True
    return bool(
        addr.is_private
        or addr.is_loopback
        or addr.is_link_local
        or addr.is_reserved
        or addr.is_multicast
    )


def _traits_block_reason(traits: dict[str, Any]) -> Optional[str]:
    if traits.get("is_anonymous"):
        return "anonymous"
    if traits.get("is_anonymous_vpn"):
        return "anonymous_vpn"
    if traits.get("is_public_proxy"):
        return "public_proxy"
    if traits.get("is_residential_proxy"):
        return "residential_proxy"
    if traits.get("is_tor_exit_node"):
        return "tor_exit"
    if traits.get("is_hosting_provider") and settings.MAXMIND_BLOCK_HOSTING_PROVIDER:
        return "hosting_provider"
    risk = traits.get("ip_risk_snapshot")
    if risk is not None and float(risk) >= settings.MAXMIND_IP_RISK_THRESHOLD:
        return f"ip_risk_snapshot={risk}"
    return None


def _anonymizer_block_reason(anonymizer: dict[str, Any]) -> Optional[str]:
    if anonymizer.get("is_anonymous"):
        return "anonymizer_anonymous"
    if anonymizer.get("is_anonymous_vpn"):
        return "anonymizer_vpn"
    if anonymizer.get("is_public_proxy"):
        return "anonymizer_public_proxy"
    if anonymizer.get("is_residential_proxy"):
        return "anonymizer_residential_proxy"
    if anonymizer.get("is_tor_exit_node"):
        return "anonymizer_tor"
    if anonymizer.get("is_hosting_provider") and settings.MAXMIND_BLOCK_HOSTING_PROVIDER:
        return "anonymizer_hosting_provider"
    return None


def _secondary_block_reason(data: dict[str, Any]) -> Optional[str]:
    for key in (
        "vpn",
        "proxy",
        "tor",
        "active_vpn",
        "active_proxy",
        "is_vpn",
        "is_proxy",
        "is_tor",
        "is_anonymous",
        "is_hosting_provider",
    ):
        if data.get(key) is True:
            return f"secondary_{key}"

    for key in ("fraud_score", "risk_score", "ip_risk_score", "score"):
        value = data.get(key)
        if value is None:
            continue
        try:
            score = float(value)
        except (TypeError, ValueError):
            continue
        if score >= settings.SECONDARY_VPN_RISK_THRESHOLD:
            return f"secondary_{key}={value}"
    return None


async def _check_secondary_vpn_provider(client_ip: str) -> IpValidationResult:
    if not settings.SECONDARY_VPN_CHECK_URL:
        return IpValidationResult(allowed=True, provider="secondary_vpn")

    url = settings.SECONDARY_VPN_CHECK_URL.format(ip=quote(client_ip, safe=""))
    headers = {}
    if settings.SECONDARY_VPN_CHECK_API_KEY:
        headers["Authorization"] = f"Bearer {settings.SECONDARY_VPN_CHECK_API_KEY}"

    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            response = await client.get(url, headers=headers)
    except httpx.RequestError as exc:
        logger.error("Secondary VPN provider request failed: %s", exc)
        return IpValidationResult(
            allowed=settings.SECONDARY_VPN_FAIL_OPEN,
            provider="secondary_vpn",
            reason="secondary_request_failed",
        )

    if response.status_code != 200:
        logger.error(
            "Secondary VPN provider unexpected HTTP %s: %s",
            response.status_code,
            response.text[:200],
        )
        return IpValidationResult(
            allowed=settings.SECONDARY_VPN_FAIL_OPEN,
            provider="secondary_vpn",
            reason=f"secondary_http_{response.status_code}",
        )

    data = response.json()
    reason = _secondary_block_reason(data)
    if reason:
        return IpValidationResult(allowed=False, provider="secondary_vpn", reason=reason)
    return IpValidationResult(allowed=True, provider="secondary_vpn")


async def evaluate_ip_for_ksa_traffic(client_ip: Optional[str]) -> IpValidationResult:
    """Validate traffic for analytics/orders: public Saudi IP, no VPN/proxy/risk flags."""
    if settings.SKIP_ORDER_GEO_CHECK:
        logger.warning(
            "SKIP_ORDER_GEO_CHECK=true: geo/VPN gate disabled for analytics/orders"
        )
        return IpValidationResult(allowed=True, provider="skipped")

    if not settings.MAXMIND_ACCOUNT_ID or not settings.MAXMIND_LICENSE_KEY:
        if settings.APP_ENV.strip().lower() == "production":
            logger.error("MaxMind credentials missing in production; refusing traffic")
            return IpValidationResult(
                allowed=False,
                provider="maxmind",
                reason="maxmind_credentials_missing",
            )
        logger.warning(
            "MAXMIND_ACCOUNT_ID / MAXMIND_LICENSE_KEY not set; skipping IP geo check (non-production)"
        )
        return IpValidationResult(allowed=True, provider="development_skip")

    if not client_ip:
        logger.info("Traffic blocked: missing client IP")
        return IpValidationResult(allowed=False, provider="maxmind", reason="missing_ip")

    if _is_non_public_ip(client_ip):
        if settings.APP_ENV.strip().lower() == "development":
            logger.warning("Private/local client IP in development; skipping MaxMind (%s)", client_ip)
            return IpValidationResult(allowed=True, provider="development_skip")
        logger.info("Traffic blocked: non-public IP %s", client_ip)
        return IpValidationResult(allowed=False, provider="maxmind", reason="non_public_ip")

    path_ip = quote(client_ip, safe="")
    url = f"{INSIGHTS_BASE}/{path_ip}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                url,
                auth=(settings.MAXMIND_ACCOUNT_ID, settings.MAXMIND_LICENSE_KEY),
            )
    except httpx.RequestError as exc:
        logger.error("MaxMind request failed: %s", exc)
        return IpValidationResult(
            allowed=settings.MAXMIND_FAIL_OPEN,
            provider="maxmind",
            reason="maxmind_request_failed",
        )

    if response.status_code == 404:
        logger.info("MaxMind 404 for IP %s", client_ip)
        return IpValidationResult(allowed=False, provider="maxmind", reason="maxmind_404")
    if response.status_code == 401 or response.status_code == 403:
        logger.error("MaxMind auth rejected (HTTP %s)", response.status_code)
        return IpValidationResult(allowed=False, provider="maxmind", reason="maxmind_auth_rejected")
    if response.status_code != 200:
        logger.error("MaxMind unexpected HTTP %s: %s", response.status_code, response.text[:200])
        return IpValidationResult(
            allowed=settings.MAXMIND_FAIL_OPEN,
            provider="maxmind",
            reason=f"maxmind_http_{response.status_code}",
        )

    data = response.json()
    country = (data.get("country") or {}).get("iso_code")
    if country != "SA":
        logger.info("Traffic blocked: country %s for IP %s", country, client_ip)
        return IpValidationResult(
            allowed=False,
            country_code=country,
            provider="maxmind",
            reason="non_sa_country",
        )

    traits = data.get("traits") or {}
    reason = _traits_block_reason(traits)
    if not reason:
        reason = _anonymizer_block_reason(data.get("anonymizer") or {})

    if reason:
        logger.info("Traffic blocked: %s (IP %s)", reason, client_ip)
        return IpValidationResult(
            allowed=False,
            country_code=country,
            provider="maxmind",
            reason=reason,
        )

    secondary = await _check_secondary_vpn_provider(client_ip)
    if not secondary.allowed:
        return IpValidationResult(
            allowed=False,
            country_code=country,
            provider=secondary.provider,
            reason=secondary.reason,
        )

    provider = "maxmind"
    if settings.SECONDARY_VPN_CHECK_URL:
        provider = "maxmind+secondary_vpn"
    return IpValidationResult(allowed=True, country_code=country, provider=provider)


async def assert_ip_allowed_for_order(
    client_ip: Optional[str],
    phone_e164: str,
) -> None:
    """
    Geo + anonymizer gate for COD orders: KSA only, no VPN/proxy/tor/hosting (optional), risk score below threshold.
    Bypass list skips all checks (for trusted test numbers in production).
    Set SKIP_ORDER_GEO_CHECK=true to skip MaxMind for all phones (testing / leads).
    In development, checks are skipped if MaxMind credentials are unset. In production, missing credentials block orders (except bypass phones).
    """
    if phone_bypasses_geo_check(phone_e164):
        logger.info(
            "Geo check skipped for bypass-listed phone %s", mask_phone(phone_e164)
        )
        return
    result = await evaluate_ip_for_ksa_traffic(client_ip)
    if result.allowed:
        return
    if result.reason in {
        "maxmind_credentials_missing",
        "maxmind_request_failed",
        "maxmind_auth_rejected",
    } or (result.reason or "").startswith("maxmind_http_"):
        raise HTTPException(
            status_code=503,
            detail="خدمة التحقق غير متاحة مؤقتاً. حاول مرة أخرى.",
        )
    raise HTTPException(status_code=403, detail=_GEO_REJECT_DETAIL)

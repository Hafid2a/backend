from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import List
from urllib.parse import parse_qsl, quote_plus, urlencode, urlsplit, urlunsplit


def _normalize_postgres_url(url: str) -> str:
    """Coerce a Postgres URL into a shape SQLAlchemy + asyncpg accept.

    - ``postgres://`` and ``postgresql://`` (no driver suffix) are upgraded
      to ``postgresql+asyncpg://``. SQLAlchemy dropped support for the
      ``postgres`` plugin name, so pasting Easypanel's default connection
      string verbatim raises ``NoSuchModuleError`` without this rewrite.
    - libpq's ``sslmode=...`` query parameter is rewritten to asyncpg's
      ``ssl=...`` (asyncpg accepts ``disable|allow|prefer|require|...``).
      Easypanel's pgweb URL includes ``?sslmode=disable``; left as-is it
      crashes asyncpg's connect path.

    Idempotent: any already-normalized URL passes through unchanged.
    """

    if not url:
        return url

    if url.startswith("postgres://"):
        url = "postgresql+asyncpg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://"):
        url = "postgresql+asyncpg://" + url[len("postgresql://"):]

    parts = urlsplit(url)
    if not parts.query:
        return url

    pairs = parse_qsl(parts.query, keep_blank_values=True)
    rewritten = [
        ("ssl", value) if key.lower() == "sslmode" else (key, value)
        for key, value in pairs
    ]
    return urlunsplit(
        (parts.scheme, parts.netloc, parts.path, urlencode(rewritten), parts.fragment)
    )


class Settings(BaseSettings):
    APP_ENV: str = "development"
    API_BASE_URL: str = "http://localhost:8000"
    FRONTEND_BASE_URL: str = "http://localhost:3000"

    DATABASE_URL: str = "postgresql+asyncpg://najd:localdev@localhost:5432/najd"
    # Substituted into DATABASE_URL when that string contains "${DB_PASSWORD}"
    # (Docker Compose substitutes this in YAML; Easypanel / plain .env do not).
    DB_PASSWORD: str = ""

    CORS_ORIGINS: str = "http://localhost:3000"

    ADMIN_USERNAME: str = ""
    ADMIN_PASSWORD: str = ""

    SHEET_WEBHOOK_URL: str = ""
    SHEET_WEBHOOK_SECRET: str = ""

    META_PIXEL_ID: str = ""
    META_ACCESS_TOKEN: str = ""
    META_TEST_EVENT_CODE: str = ""
    META_CAPI_VERSION: str = "v19.0"

    TIKTOK_PIXEL_ID: str = ""
    TIKTOK_ACCESS_TOKEN: str = ""
    TIKTOK_TEST_EVENT_CODE: str = ""

    SNAP_PIXEL_ID: str = ""
    SNAP_ACCESS_TOKEN: str = ""
    SNAP_TEST_EVENT_CODE: str = ""

    # MaxMind GeoIP Insights (https://dev.maxmind.com/geoip/docs/web-services)
    # Account ID = numeric account id; License Key = secret from MaxMind "Generate a License Key"
    MAXMIND_ACCOUNT_ID: str = ""
    MAXMIND_LICENSE_KEY: str = ""
    # When traits.ip_risk_snapshot is present, block at or above this value (1–99 scale).
    MAXMIND_IP_RISK_THRESHOLD: float = 50.0
    # Block datacenter / hosting IPs (helps catch VPNs that only set is_hosting_provider).
    MAXMIND_BLOCK_HOSTING_PROVIDER: bool = True
    # If True, allow orders when MaxMind is unreachable (default: fail closed).
    MAXMIND_FAIL_OPEN: bool = False
    # Optional second VPN/proxy provider. URL can contain "{ip}" and should return JSON
    # with common booleans like vpn/proxy/tor/hosting or a fraud/risk score.
    SECONDARY_VPN_CHECK_URL: str = ""
    SECONDARY_VPN_CHECK_API_KEY: str = ""
    SECONDARY_VPN_FAIL_OPEN: bool = False
    SECONDARY_VPN_RISK_THRESHOLD: float = 50.0
    # رقم NAJD للاختبار من برّا السعودية — مُدمَج دائماً مع القائمة (انظر maxmind_geo._CANONICAL_NAJD_TEST_LINE_E164).
    # أرقام إضافية عبر GEO_ORDER_BYPASS_PHONES مفصولة بفاصلة. عطّل الإضافات فقط: اترك القيمة الافتراضية.
    # If True: skip MaxMind for ALL orders (any Saudi mobile from any country). Risk: fraud / non-KSA traffic. Use for testing or special campaigns only.
    SKIP_ORDER_GEO_CHECK: bool = False
    # Comma-separated Saudi mobile numbers that bypass MaxMind geo check (test orders).
    # The canonical NAJD test line (+966550505044) is always included via the code path
    # in maxmind_geo._CANONICAL_NAJD_TEST_LINE_E164, so it can stay empty in normal setups.
    GEO_ORDER_BYPASS_PHONES: str = ""

    LOG_LEVEL: str = "INFO"

    @model_validator(mode="after")
    def finalize_database_url(self) -> "Settings":
        marker = "${DB_PASSWORD}"
        url = self.DATABASE_URL

        if marker in url:
            if not self.DB_PASSWORD:
                raise ValueError(
                    "DB_PASSWORD is required when DATABASE_URL contains "
                    f"{marker!r}; set Easypanel/Postgres user password "
                    "(or paste a full DATABASE_URL without placeholders)."
                )
            url = url.replace(marker, quote_plus(self.DB_PASSWORD))

        url = _normalize_postgres_url(url)

        if url != self.DATABASE_URL:
            object.__setattr__(self, "DATABASE_URL", url)
        return self

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

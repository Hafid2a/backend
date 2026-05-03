from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import List
from urllib.parse import quote_plus


class Settings(BaseSettings):
    APP_ENV: str = "development"
    API_BASE_URL: str = "http://localhost:8000"
    FRONTEND_BASE_URL: str = "http://localhost:3000"

    DATABASE_URL: str = "postgresql+asyncpg://najd:localdev@localhost:5432/najd"
    # Substituted into DATABASE_URL when that string contains "${DB_PASSWORD}"
    # (Docker Compose substitutes this in YAML; Easypanel / plain .env do not).
    DB_PASSWORD: str = ""

    CORS_ORIGINS: str = "http://localhost:3000"

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
    # رقم NAJD للاختبار من برّا السعودية — مُدمَج دائماً مع القائمة (انظر maxmind_geo._CANONICAL_NAJD_TEST_LINE_E164).
    # أرقام إضافية عبر GEO_ORDER_BYPASS_PHONES مفصولة بفاصلة. عطّل الإضافات فقط: اترك القيمة الافتراضية.
    # If True: skip MaxMind for ALL orders (any Saudi mobile from any country). Risk: fraud / non-KSA traffic. Use for testing or special campaigns only.
    SKIP_ORDER_GEO_CHECK: bool = False

    LOG_LEVEL: str = "INFO"

    @model_validator(mode="after")
    def interpolate_database_password(self) -> "Settings":
        marker = "${DB_PASSWORD}"
        if marker not in self.DATABASE_URL:
            return self
        if not self.DB_PASSWORD:
            raise ValueError(
                "DB_PASSWORD is required when DATABASE_URL contains "
                f"{marker!r}; set Easypanel/Postgres user password "
                "(or paste a full DATABASE_URL without placeholders)."
            )
        interpolated = self.DATABASE_URL.replace(marker, quote_plus(self.DB_PASSWORD))
        object.__setattr__(self, "DATABASE_URL", interpolated)
        return self

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

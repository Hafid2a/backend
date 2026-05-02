from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_ENV: str = "development"
    API_BASE_URL: str = "http://localhost:8000"
    FRONTEND_BASE_URL: str = "http://localhost:3000"

    DATABASE_URL: str = "postgresql+asyncpg://najd:localdev@localhost:5432/najd"

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
    MAXMIND_ACCOUNT_ID: str = ""
    MAXMIND_LICENSE_KEY: str = ""
    # When traits.ip_risk_snapshot is present, block at or above this value (1–99 scale).
    MAXMIND_IP_RISK_THRESHOLD: float = 50.0
    # If True, allow orders when MaxMind is unreachable (default: fail closed).
    MAXMIND_FAIL_OPEN: bool = False
    # Comma-separated phones that skip geo/IP checks (E.164, 05xxxxxxxx, or 9 digits after 5).
    GEO_ORDER_BYPASS_PHONES: str = "643281895"

    LOG_LEVEL: str = "INFO"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

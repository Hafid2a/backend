# NAJD Backend API

FastAPI + PostgreSQL backend for the NAJD Men's Grooming e-commerce store.

## Stack

- **Python 3.12**, FastAPI 0.111, Uvicorn
- **SQLAlchemy 2** async + asyncpg
- **Alembic** migrations
- **Pydantic v2** settings & validation
- **httpx** async HTTP client (CAPI integrations)
- **structlog / JSON logging**

---

## Local Development

### Prerequisites

- Docker & Docker Compose

### 1. Configure environment

**Docker Compose (موصى به):** انسخ ملف البيئة المحلي — لا تستخدم `.env.example` مباشرة إذا كان فيه `DATABASE_URL` مع `${DB_PASSWORD}` وفاضي؛ التطبيق يوقف عند الإقلاع.

```bash
cd backend
copy env.local.example .env
```

**أو** يدوياً: تأكد أن `DATABASE_URL` **بدون** placeholder، مثل:

`postgresql+asyncpg://najd:localdev@db:5432/najd` داخل Docker، أو
`postgresql+asyncpg://najd:localdev@localhost:5432/najd` إذا شغّلت Postgres على جهازك فقط.

**إنتاج / Easypanel:** انسخ من `.env.example` واملأ `DB_PASSWORD` أو ضع `DATABASE_URL` كاملاً.

### 2. Start services

```bash
docker compose up --build
```

This will:

1. Start PostgreSQL 16
2. Build and start the API — **`entrypoint.sh` runs `alembic upgrade head` automatically**, then Uvicorn
3. On startup, products are **seeded** (if tables exist and seed rows are missing)

API: **http://localhost:8000** — `GET /health` should return `{"ok":true}`.

### Troubleshooting

| Symptom | Fix |
|--------|-----|
| **Startup error: DB_PASSWORD is required** | Do not leave `${DB_PASSWORD}` in `DATABASE_URL` without a password. Use `env.local.example` → `.env`. |
| **`relation "products" does not exist`** | From the `backend` folder: `docker compose run --rm backend alembic upgrade head`, or rebuild/restart the app container after fixing `entrypoint.sh`. |
| **POST /orders fails or IP/geo issues** | **Production:** MaxMind credentials مطلوبة لغير رقم الاختبار الثابت. **0550505044** يتجاوز الموقع دائماً (في الكود). **Development:** بدون MaxMind يتخطى التحقق لغير أرقام القائمة الإضافية. |
| **Frontend cannot reach the API** | In the frontend `.env`: `NEXT_PUBLIC_API_URL=http://localhost:8000` |
| **CORS** | `CORS_ORIGINS` must include `http://localhost:3000` |

### 3. Verify

```
GET http://localhost:8000/health       → {"ok": true}
GET http://localhost:8000/products     → list of products with offers
GET http://localhost:8000/docs         → Swagger UI
```

---

## Running Tests

Install dependencies locally (use a virtualenv):

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Run tests:

```bash
pytest tests/ -v
```

Tests are unit-only and do not require a running database.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `APP_ENV` | no | `development` or `production` (controls SQL echo) |
| `DATABASE_URL` | yes | asyncpg connection string |
| `CORS_ORIGINS` | no | Comma-separated allowed origins |
| `SHEET_WEBHOOK_URL` | no | Google Apps Script deployment URL |
| `SHEET_WEBHOOK_SECRET` | no | Shared secret verified by the webhook |
| `META_PIXEL_ID` | no | Meta Conversions API pixel ID |
| `META_ACCESS_TOKEN` | no | Meta Conversions API access token |
| `META_TEST_EVENT_CODE` | no | Test event code for Meta (dev only) |
| `TIKTOK_PIXEL_ID` | no | TikTok Events API pixel ID |
| `TIKTOK_ACCESS_TOKEN` | no | TikTok Events API access token |
| `TIKTOK_TEST_EVENT_CODE` | no | Test event code for TikTok (dev only) |
| `SNAP_PIXEL_ID` | no | Snapchat Conversions API pixel ID |
| `SNAP_ACCESS_TOKEN` | no | Snapchat Conversions API access token |
| `SNAP_TEST_EVENT_CODE` | no | Test event code for Snapchat (dev only) |
| `LOG_LEVEL` | no | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `MAXMIND_ACCOUNT_ID` | **yes in production** | [GeoIP Insights](https://dev.maxmind.com/geoip/docs/web-services) — numeric account ID |
| `MAXMIND_LICENSE_KEY` | **yes in production** | Secret license key from MaxMind |
| `MAXMIND_IP_RISK_THRESHOLD` | no | Block when `traits.ip_risk_snapshot` ≥ this (default 50) |
| `MAXMIND_BLOCK_HOSTING_PROVIDER` | no | Block datacenter/hosting IPs (default `true`; set `false` if false positives) |
| `MAXMIND_FAIL_OPEN` | no | If `true`, allow orders when MaxMind HTTP fails |
| `GEO_ORDER_BYPASS_PHONES` | no | أرقام **إضافية** تتجاوز MaxMind مع الرقم الثابت في الكود `0550505044` (+966550505044). الطلب يُعلَّم `is_test_order=true` (بدون Sheet/CAPI/pixel) |

---

## Database Migrations

Migrations live in `alembic/versions/`. **Docker / this repo’s image:** `entrypoint.sh` runs `alembic upgrade head` before Uvicorn starts. For local venv without Docker, run `alembic upgrade head` yourself after pulling schema changes. In multi-replica production setups, you may prefer a dedicated migration job instead of every replica running upgrades.

### Create a new migration

```bash
# Inside the container or with the venv active
alembic revision --autogenerate -m "describe your change"
```

### Manual upgrade / downgrade

```bash
alembic upgrade head
alembic downgrade -1
alembic history
```

---

## API Endpoint Summary

### Health

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness check |

### Products

| Method | Path | Description |
|---|---|---|
| GET | `/products` | List all active products with offers |
| GET | `/products/{slug}` | Get a single product by slug |

### Orders

| Method | Path | Description |
|---|---|---|
| POST | `/orders` | Create a new order (COD) |
| GET | `/orders/{order_id}` | Get order detail by order number |
| POST | `/orders/{order_id}/upsell` | Accept post-purchase upsell (idempotent) |

#### POST /orders — Request body example

```json
{
  "customer_name": "محمد عبدالله",
  "phone": "0512345678",
  "items": [
    { "product_id": "najd-clear", "offer_qty": 2, "price_sar": 279 }
  ],
  "utm": { "utm_source": "tiktok", "utm_medium": "paid" },
  "click_ids": { "ttclid": "abc123" },
  "browser": { "user_agent": "Mozilla/5.0...", "fbp": "_fbp_..." },
  "event_ids": { "purchase": "uuid-v4-here" },
  "landing_page": "https://najdofficial.com/najd-clear"
}
```

Prices are always recalculated server-side from `offer_qty` — the `price_sar` field from the frontend is ignored.

---

## Easypanel Deployment

1. Push your code to a Git repository.
2. In Easypanel, create a new **App** and connect to your repo.
   - **If the build uses Nixpacks**, deploy from **latest `main`** (this repo includes `Procfile` and `nixpacks.toml`). If the build log’s `GIT_SHA` is **not** the current tip of `main` on GitHub, Easypanel is still pulling an **old** archive—open **Source**, branch `main`, redeploy; or use **Dockerfile** build instead.
   - **If the build uses Dockerfile** (recommended if Nixpacks misbehaves), use the repo root `Dockerfile`; **Build** / **Start** commands are taken from the image.
3. Set **Build command**: _(none when using Dockerfile image)_
4. Set **Start command**: _(none when using Dockerfile; image `CMD` runs Uvicorn via `entrypoint.sh`)_
5. Add a **PostgreSQL** service and copy the connection string.
6. Set all environment variables from `.env.example` in the Easypanel environment editor.
7. Set `DATABASE_URL` to point at the Easypanel Postgres service.
8. Deploy the app. The container **`entrypoint.sh`** runs **`alembic upgrade head`** on each start; you can still run migrations manually from Easypanel **Script** / one-off task if you disable that behaviour or need to run upgrades before traffic arrives.

### Test order from outside Saudi Arabia (one number only)

Only numbers in **`GEO_ORDER_BYPASS_PHONES`** (comma-separated) *plus* the **fixed** NAJD test line **`0550505044`** (`+966550505044`) skip MaxMind. The fixed line cannot be removed via env (it is in `maxmind_geo.py`); extra numbers add more bypasses.

For **only** the NAJD test SIM, you can use:

```env
GEO_ORDER_BYPASS_PHONES=0550505044
```

or even omit extra entries — `0550505044` still bypasses geo because it is hard-coded. Adding `0550505044,05…` adds more bypass numbers.

### Health check

Configure the health check path to `/health` with a 30-second interval.

### Latest commit not updating?

Easypanel chooses the Git revision when **a deploy runs**; repo files cannot “force” SHA by themselves.

| Check | Action |
|-------|--------|
| Builder | Prefer **Dockerfile** in the service build settings (matches this repo). You can use **Nixpacks** if `Procfile` / `nixpacks.toml` stay on `main`. |
| Source | Branch must be **`main`**, not a pinned tag or old release. |
| Environment | Remove a **manually added `GIT_SHA`** variable if you added one; it can lock logs to an old hash. |
| Webhook / Auto Deploy | Turn on **Auto Deploy** (GitHub PAT with webhooks scope) or POST the service **Deploy Webhook** URL once per release. |
| GitHub Actions | This repo has `.github/workflows/easypanel-deploy-hook.yml`: add secret **`EASYPANEL_DEPLOY_WEBHOOK`** (the panel’s deploy URL) so each push to `main` can trigger a new deploy. If the secret is unset, the workflow does nothing. |

### MaxMind credentials

`MAXMIND_ACCOUNT_ID` / `MAXMIND_LICENSE_KEY` are read from env (see `.env.example`). If a key was exposed, rotate it in [MaxMind Manage License Keys](https://www.maxmind.com/en/accounts/current/license-key) (generate a new key, update Easypanel, verify, then deactivate the old key)—see [Replace my License Key](https://support.maxmind.com/hc/en-us/articles/4407111761435-Replace-my-License-Key).

---

## Google Sheets Webhook

1. Create a new Google Sheet.
2. Open **Extensions > Apps Script**.
3. Paste the contents of `scripts/google-sheets-webhook.gs`.
4. Set the `SECRET` variable to match `SHEET_WEBHOOK_SECRET` in `.env`.
5. Deploy as a Web App (Execute as: Me, Access: Anyone).
6. Copy the deployment URL to `SHEET_WEBHOOK_URL` in `.env`.

Each new order is appended as a row. Re-sending the same `order_number` updates the existing row.

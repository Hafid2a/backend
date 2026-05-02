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

```bash
cp .env.example .env
# Edit .env — set DB_PASSWORD and any pixel credentials you want to test
```

### 2. Start services

```bash
docker compose up --build
```

This will:
1. Start a PostgreSQL 16 container
2. Build the backend image
3. Seed the 3 initial products (najd-clear, najd-align, najd-rest) *(requires schema already applied — run migrations manually first, see below)*
4. Start the API on http://localhost:8000

Apply the schema once before first run, e.g. `docker compose run --rm backend alembic upgrade head` *(or another container with the same `DATABASE_URL`)*.

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

---

## Database Migrations

Migrations live in `alembic/versions/`. They are **not** run automatically on container start — run `alembic upgrade head` yourself (local shell, one-off job, CI, or Easypanel script) whenever you deploy schema changes.

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
8. Deploy the app, then run **`alembic upgrade head`** when needed (Easypanel **Script** / one-off task, or your DB pipeline) — it is no longer part of the container start command.

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

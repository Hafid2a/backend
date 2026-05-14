# HANDOFF — NAJD Storefront (Production Live)

> سلام علي اللي قاري — هاد الملف هو "حالة الإنتاج" الكاملة ديال متجر **نجد**. كل ما تحتاج باش تكمل الخدمة موجود هنا.
> Last verified: 2026-05-13.

---

## 1. Production URLs (Live)

| Component | URL | Notes |
|---|---|---|
| Storefront | <https://najdofficial.com> | Next.js 15 |
| Storefront (www) | <https://www.najdofficial.com> | Same content, served from Easypanel |
| Backend API | <https://api.najdofficial.com> | FastAPI |
| API health | <https://api.najdofficial.com/health> | `{"ok": true}` |
| API products | <https://api.najdofficial.com/products> | 3 active products |
| API docs (Swagger) | <https://api.najdofficial.com/docs> | |
| Easypanel direct (backup) | <https://hafidv1-backend.njyqce.easypanel.host> | Bypasses DNS — useful when domain breaks |
| Easypanel direct (frontend) | <https://hafidv1-frontend.njyqce.easypanel.host> | Same |

**Test order line** (bypasses geo check, marks `is_test_order=true`): `0550505044`

---

## 2. Repositories

| Repo | URL | Branch |
|---|---|---|
| Backend | <https://github.com/Hafid2a/backend> | `main` |
| Frontend | <https://github.com/Hafid2a/frontend> | `main` |

**Local clones:**

- Backend: `C:\Users\usuario\Documents\ai killer`
- Frontend: `C:\Users\usuario\Documents\najd-frontend`

---

## 3. Infrastructure

```
┌──────────────────────────────┐
│         Cloudflare DNS       │  ← najdofficial.com → 153.92.211.192
│      (gray cloud / DNS only) │     api / www / @ all A records, DNS only
└──────────────────────────────┘
                │
                ▼
┌──────────────────────────────┐
│   Easypanel @ 153.92.211.192 │  ← Traefik reverse proxy + Let's Encrypt
│   project: hafidv1           │
└──────────────────────────────┘
   │              │              │
   ▼              ▼              ▼
┌─────────┐  ┌──────────┐  ┌─────────────┐
│ backend │  │ frontend │  │  database   │
│ :8000   │  │ :3000    │  │ Postgres 16 │
│ FastAPI │  │ Next.js  │  │             │
└─────────┘  └──────────┘  └─────────────┘
```

- **Server IP**: `153.92.211.192`
- **Easypanel project**: `hafidv1`
- **Services**: `backend` (FastAPI), `frontend` (Next.js 15), `database` (Postgres)

---

## 4. Product catalog (3 slugs)

| Slug | SKU | Name (ar) | Hero image |
|---|---|---|---|
| `face-primer` | NAJD-STAY-PRIMER | ثبات الخط | `hero-lifestyle-vanity.png` |
| `face-sunscreen-spf50` | NAJD-DAY-SPF-50 | درع النهار | `hero-promo.png` |
| `forehead-serum` | NAJD-HAIRLINE-SERUM | صفاء الجبهة | `hero-promo.png` |

**Offers (kollshi nfs l-prix)**: 1 × 199 SAR · 2 × 279 SAR · 3 × 349 SAR · upsell 99 SAR

**Upsell rotation** (`app/services/order_service.py`):

- face-primer → forehead-serum
- face-sunscreen-spf50 → face-primer
- forehead-serum → face-sunscreen-spf50

**URL / DB migration:** الـ slug القديم (`najd-thabat-al-khat` وحدودو) بدّلات. الباكند: تشغّل `alembic upgrade head` (هجرة `003_rename_product_slugs`). الفرونت: اعمل إعادة تسمية لمجلّدات الصور تحت `public/products/` لتطابق الـ slugs الجديدة؛ الروابط القديمة ديال المتجر تنحوّل تلقائياً (`redirects` فـ `next.config.ts`).

---

## 5. Auto-Deploy (push → live)

Push to `main` → GitHub Actions webhook → Easypanel rebuilds the service.

### How it works

| Repo | Workflow | Secret name (GitHub) | Easypanel URL source |
|---|---|---|---|
| `Hafid2a/backend` | `.github/workflows/easypanel-deploy-hook.yml` | `EASYPANEL_BACKEND_HOOK` | Easypanel → backend → Deployments → Deployment Trigger |
| `Hafid2a/frontend` | `.github/workflows/easypanel-deploy-hook.yml` | `EASYPANEL_FRONTEND_HOOK` | Easypanel → frontend → Deployments → Deployment Trigger |

### To rotate a deploy webhook

1. Easypanel → service → **Deployments** → **Refresh Deploy Token**
2. Copy new URL
3. GitHub → repo → Settings → Secrets and variables → Actions → update existing secret value
4. Done. Next push triggers rebuild.

### Verifying a webhook fired

- GitHub repo → **Actions** tab → look at latest `Easypanel deploy hook` run
- Job duration **0 seconds** = secret missing/empty (skip)
- Job duration **> 5 seconds** = curl actually called Easypanel

---

## 6. Environment variables (production)

### Backend (`hafidv1-backend`)

| Variable | Value (prod) |
|---|---|
| `APP_ENV` | `production` |
| `DATABASE_URL` | `postgresql+asyncpg://najd:****@hafidv1_database:5432/najd` (set in Easypanel from Postgres service) |
| `CORS_ORIGINS` | `https://najdofficial.com,https://www.najdofficial.com,https://hafidv1-frontend.njyqce.easypanel.host` |
| `GEO_ORDER_BYPASS_PHONES` | `0550505044` (extra; the same number is also hard-coded) |
| `MAXMIND_ACCOUNT_ID` | (set in Easypanel) |
| `MAXMIND_LICENSE_KEY` | (set in Easypanel) |
| `SHEET_WEBHOOK_URL` | (Google Apps Script deployment) |
| `SHEET_WEBHOOK_SECRET` | (shared secret) |

### Frontend (`hafidv1-frontend`)

| Variable | Value (prod) |
|---|---|
| `NEXT_PUBLIC_API_URL` | `https://api.najdofficial.com` |
| `NEXT_PUBLIC_SITE_URL` | `https://najdofficial.com` |
| `API_BASE_URL` | `https://api.najdofficial.com` |
| `NEXT_PUBLIC_MOCK_ORDERS` | `false` |
| `NEXT_PUBLIC_META_PIXEL_ID` | (optional — fill when ready) |
| `NEXT_PUBLIC_TIKTOK_PIXEL_ID` | (optional) |
| `NEXT_PUBLIC_SNAP_PIXEL_ID` | (optional) |

> ⚠️ `NEXT_PUBLIC_*` vars are **baked in at build time**. After changing them, you MUST trigger a rebuild (push empty commit OR Easypanel → Deploy button).

---

## 7. Common operations

### Push code → see it live

```powershell
# Backend
cd "C:\Users\usuario\Documents\ai killer"
git add .
git commit -m "your message"
git push origin main
# Wait 2-3 min, then verify at https://api.najdofficial.com/health

# Frontend
cd C:\Users\usuario\Documents\najd-frontend
git add .
git commit -m "your message"
git push origin main
# Wait 2-3 min, then verify at https://najdofficial.com
```

### Force a rebuild (no code change)

```powershell
git commit --allow-empty -m "deploy: rebuild"
git push origin main
```

OR: Easypanel → service → click **Deploy** button.

### View logs

Easypanel → service → tab **Logs** (live stream).

### Run a DB query

Easypanel → service `database` → click **pgweb** (or use Postgres connection string from the Postgres service env).

### Test a checkout from outside Saudi Arabia

Use phone `0550505044` in the checkout form. Geo bypass is hard-coded for that number. Orders created with it have `is_test_order=true` and are NOT sent to Google Sheet / Meta / TikTok / Snap (so no garbage data in your dashboards).

### Reset DB products to seed defaults

Backend reseeds on startup (`app/db/seed.py`). Push any commit → Easypanel rebuilds + seeds. Obsolete products are soft-deactivated (`status='inactive'`).

To wipe & reseed completely (destructive — only when needed):

```sql
-- in pgweb or psql
TRUNCATE products, product_offers RESTART IDENTITY CASCADE;
```

Then redeploy backend (seed runs on startup).

---

## 8. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `https://najdofficial.com` → 404 Easypanel page | Domain not bound to frontend service | Easypanel → frontend → Domains → Add Domain |
| SSL errors on a new domain | Let's Encrypt not yet issued | Wait 60-120s after adding domain |
| Frontend calls old API URL | `NEXT_PUBLIC_API_URL` baked from old build | Update env var + force rebuild (empty commit) |
| Order POST returns 422 | Missing field in body | Check `app/schemas/order.py` for required fields |
| Order POST returns 403 / geo blocked | Phone not in bypass list + IP outside KSA | Use `0550505044` for testing |
| Backend deploys but products stale | Seed only skips existing slugs | Truncate tables manually OR rename slug in seed |
| Webhook fires but Easypanel doesn't deploy | Wrong URL in secret or token rotated | Refresh deploy token + update secret |

---

## 9. Pending / optional work

- [ ] **Tracking pixels** — fill `NEXT_PUBLIC_META_PIXEL_ID`, `NEXT_PUBLIC_TIKTOK_PIXEL_ID`, `NEXT_PUBLIC_SNAP_PIXEL_ID` (frontend env) once you have ad accounts. Frontend already imports `PixelProvider`.
- [ ] **CAPI server-side** — set `META_PIXEL_ID` + `META_ACCESS_TOKEN` (backend env) for server-side event matching.
- [ ] **TikTok / Snap CAPI** — same pattern (`TIKTOK_ACCESS_TOKEN`, `SNAP_ACCESS_TOKEN`).
- [ ] **Google Sheet logging** — paste `scripts/google-sheets-webhook.gs` in Apps Script, deploy as Web App, copy URL to `SHEET_WEBHOOK_URL` + matching `SHEET_WEBHOOK_SECRET`.
- [ ] **MaxMind production credentials** — see [README → MaxMind](./README.md#maxmind-credentials).
- [ ] **First real order test** — place an order from a real KSA phone (not `0550505044`) and confirm it appears in the Sheet + Meta Events Manager.
- [ ] **DB backups** — Easypanel has a Backups tab on the Postgres service. Configure daily snapshot.
- [ ] **Monitoring / alerts** — pingdom / uptime-robot on `/health` and storefront homepage.

---

## 10. Key files / where to look

### Backend

- `app/main.py` — FastAPI app, CORS, lifespan (seed on startup)
- `app/db/seed.py` — product seed data
- `app/db/models.py` — ORM models
- `app/api/routes/products.py` — `/products` endpoints
- `app/api/routes/orders.py` — `/orders` endpoints
- `app/services/order_service.py` — order creation, upsell map, product names
- `app/services/sheet_webhook.py` — Google Sheet POST
- `app/services/maxmind_geo.py` — geo bypass & risk check
- `app/core/config.py` — settings (env vars)

### Frontend

- `config/products.ts` — full product catalog (hero copy, mechanism, reviews, FAQs, offers)
- `config/site.ts` — brand metadata
- `public/products/{slug}/*.png` — product images (hero, mechanism-point-1..4, how-to-step-1..3)
- `app/page.tsx` — homepage
- `app/products/[slug]/page.tsx` — product detail page
- `components/checkout/CheckoutModal.tsx` — checkout form
- `lib/api.ts` — backend HTTP client
- `lib/phone.ts` — KSA phone normalization

---

## 11. Last session summary (2026-05-13)

**What was done:**

1. ✅ Restored the original 3-product Najd lineup (face-primer, face-sunscreen-spf50, forehead-serum) — backend seed + frontend config + 14 product PNGs + all copy.
2. ✅ Hero images updated to latest brand assets (LANBENA acne ref, KSA vanity lifestyle, SKINEVER SPF50 ref).
3. ✅ Soft-deactivated obsolete night-mask products (preserves order history).
4. ✅ Auto-deploy webhooks wired (push main → Easypanel rebuilds within 30s).
5. ✅ DNS production setup (`najdofficial.com`, `www`, `api` → `153.92.211.192`, DNS-only / no Cloudflare proxy).
6. ✅ SSL Let's Encrypt issued for all 3 domains.
7. ✅ CORS configured for production domain.
8. ✅ End-to-end test order verified (`POST /orders` → `NAJD-20260513-000002`).

**Commits:**

- Backend: `fee1e1c..49ce2fb` (seed + services), `..fe22f09` (workflow fix)
- Frontend: `f649932..1b7fba2` (catalog restore), `..59a316a` (workflow fix), `..650db00` (rebuild trigger)

---

موفقين 🤲 — أي مشكل، راجع `Logs` فـ Easypanel أول حاجة، باين كاملة فاش كاتنوض غادية.

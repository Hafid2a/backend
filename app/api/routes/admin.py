import secrets
from datetime import date, datetime, time, timedelta, timezone
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db

router = APIRouter(prefix="/admin", tags=["admin"])
security = HTTPBasic()


def require_admin(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
) -> str:
    expected_user = settings.ADMIN_USERNAME
    expected_password = settings.ADMIN_PASSWORD
    if not expected_user or not expected_password:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin credentials are not configured.",
        )

    user_ok = secrets.compare_digest(credentials.username, expected_user)
    password_ok = secrets.compare_digest(credentials.password, expected_password)
    if not (user_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials.",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def _date_bounds(
    start: Optional[date],
    end: Optional[date],
) -> tuple[datetime, datetime]:
    today = datetime.now(timezone.utc).date()
    start_date = start or (today - timedelta(days=6))
    end_date = end or today
    start_dt = datetime.combine(start_date, time.min, tzinfo=timezone.utc)
    end_dt = datetime.combine(end_date + timedelta(days=1), time.min, tzinfo=timezone.utc)
    return start_dt, end_dt


async def _fetch_mappings(db: AsyncSession, sql: str, params: dict) -> list[dict]:
    result = await db.execute(text(sql), params)
    return [dict(row) for row in result.mappings().all()]


@router.get("", response_class=HTMLResponse)
async def admin_dashboard(_: str = Depends(require_admin)) -> HTMLResponse:
    return HTMLResponse(ADMIN_HTML)


@router.get("/api/overview")
async def admin_overview(
    _: str = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    start: Optional[date] = Query(default=None),
    end: Optional[date] = Query(default=None),
) -> dict:
    start_dt, end_dt = _date_bounds(start, end)
    params = {"start": start_dt, "end": end_dt}

    summary_rows = await _fetch_mappings(
        db,
        """
        WITH click_stats AS (
            SELECT
                count(*)::int AS total_clicks,
                count(*) FILTER (WHERE is_valid_ksa_ip)::int AS clicks,
                count(*) FILTER (WHERE NOT is_valid_ksa_ip)::int AS rejected_clicks
            FROM click_events
            WHERE created_at >= :start
              AND created_at < :end
        ),
        order_stats AS (
            SELECT
                count(*)::int AS orders,
                coalesce(sum(total_sar), 0)::int AS revenue_sar,
                coalesce(avg(total_sar), 0)::numeric(10, 2) AS avg_order_value_sar
            FROM orders
            WHERE created_at >= :start
              AND created_at < :end
              AND is_test_order = false
        ),
        upsell_stats AS (
            SELECT count(DISTINCT oi.order_id)::int AS upsell_orders
            FROM order_items oi
            JOIN orders o ON o.id = oi.order_id
            WHERE o.created_at >= :start
              AND o.created_at < :end
              AND o.is_test_order = false
              AND oi.is_upsell = true
        )
        SELECT *
        FROM click_stats, order_stats, upsell_stats
        """,
        params,
    )
    summary = summary_rows[0] if summary_rows else {}
    clicks = int(summary.get("clicks") or 0)
    total_clicks = int(summary.get("total_clicks") or 0)
    rejected_clicks = int(summary.get("rejected_clicks") or 0)
    orders = int(summary.get("orders") or 0)
    summary["conversion_rate"] = round((orders / clicks) * 100, 2) if clicks else 0
    summary["upsell_rate"] = (
        round((int(summary.get("upsell_orders") or 0) / orders) * 100, 2)
        if orders
        else 0
    )
    summary["avg_order_value_sar"] = float(summary.get("avg_order_value_sar") or 0)
    summary["rejection_rate"] = (
        round((rejected_clicks / total_clicks) * 100, 2) if total_clicks else 0
    )

    daily = await _fetch_mappings(
        db,
        """
        WITH days AS (
            SELECT generate_series(
                date_trunc('day', CAST(:start AS timestamptz)),
                date_trunc('day', (CAST(:end AS timestamptz) - interval '1 day')),
                interval '1 day'
            ) AS day
        ),
        clicks AS (
            SELECT date_trunc('day', created_at) AS day, count(*)::int AS clicks
            FROM click_events
            WHERE created_at >= :start AND created_at < :end AND is_valid_ksa_ip = true
            GROUP BY 1
        ),
        orders_by_day AS (
            SELECT
                date_trunc('day', created_at) AS day,
                count(*)::int AS orders,
                coalesce(sum(total_sar), 0)::int AS revenue_sar
            FROM orders
            WHERE created_at >= :start AND created_at < :end AND is_test_order = false
            GROUP BY 1
        )
        SELECT
            to_char(days.day, 'YYYY-MM-DD') AS day,
            coalesce(clicks.clicks, 0)::int AS clicks,
            coalesce(orders_by_day.orders, 0)::int AS orders,
            coalesce(orders_by_day.revenue_sar, 0)::int AS revenue_sar
        FROM days
        LEFT JOIN clicks ON clicks.day = days.day
        LEFT JOIN orders_by_day ON orders_by_day.day = days.day
        ORDER BY days.day
        """,
        params,
    )
    for row in daily:
        row["conversion_rate"] = (
            round((row["orders"] / row["clicks"]) * 100, 2) if row["clicks"] else 0
        )

    status_counts = await _fetch_mappings(
        db,
        """
        SELECT status, count(*)::int AS count
        FROM orders
        WHERE created_at >= :start AND created_at < :end AND is_test_order = false
        GROUP BY status
        ORDER BY count DESC
        """,
        params,
    )

    products = await _fetch_mappings(
        db,
        """
        SELECT
            oi.product_slug,
            max(oi.product_name_ar) AS product_name_ar,
            sum(oi.quantity)::int AS units,
            sum(oi.line_total_sar)::int AS revenue_sar,
            count(DISTINCT o.id)::int AS orders
        FROM order_items oi
        JOIN orders o ON o.id = oi.order_id
        WHERE o.created_at >= :start AND o.created_at < :end AND o.is_test_order = false
        GROUP BY oi.product_slug
        ORDER BY revenue_sar DESC
        """,
        params,
    )

    sources = await _fetch_mappings(
        db,
        """
        WITH clicks AS (
            SELECT coalesce(nullif(utm_source, ''), 'direct') AS source, count(*)::int AS clicks
            FROM click_events
            WHERE created_at >= :start AND created_at < :end AND is_valid_ksa_ip = true
            GROUP BY 1
        ),
        orders_by_source AS (
            SELECT
                coalesce(nullif(utm_source, ''), 'direct') AS source,
                count(*)::int AS orders,
                coalesce(sum(total_sar), 0)::int AS revenue_sar
            FROM orders
            WHERE created_at >= :start AND created_at < :end AND is_test_order = false
            GROUP BY 1
        )
        SELECT
            coalesce(clicks.source, orders_by_source.source) AS source,
            coalesce(clicks.clicks, 0)::int AS clicks,
            coalesce(orders_by_source.orders, 0)::int AS orders,
            coalesce(orders_by_source.revenue_sar, 0)::int AS revenue_sar
        FROM clicks
        FULL OUTER JOIN orders_by_source ON orders_by_source.source = clicks.source
        ORDER BY revenue_sar DESC, clicks DESC
        """,
        params,
    )
    for row in sources:
        row["conversion_rate"] = (
            round((row["orders"] / row["clicks"]) * 100, 2) if row["clicks"] else 0
        )

    rejection_reasons = await _fetch_mappings(
        db,
        """
        SELECT
            coalesce(nullif(ip_reject_reason, ''), 'unknown') AS reason,
            coalesce(nullif(ip_check_provider, ''), 'unknown') AS provider,
            count(*)::int AS count
        FROM click_events
        WHERE created_at >= :start
          AND created_at < :end
          AND is_valid_ksa_ip = false
        GROUP BY 1, 2
        ORDER BY count DESC
        LIMIT 20
        """,
        params,
    )

    rejection_countries = await _fetch_mappings(
        db,
        """
        SELECT
            coalesce(nullif(country_code, ''), 'unknown') AS country_code,
            count(*)::int AS count
        FROM click_events
        WHERE created_at >= :start
          AND created_at < :end
          AND is_valid_ksa_ip = false
        GROUP BY 1
        ORDER BY count DESC
        LIMIT 20
        """,
        params,
    )

    return {
        "summary": summary,
        "daily": daily,
        "status_counts": status_counts,
        "products": products,
        "sources": sources,
        "rejection_reasons": rejection_reasons,
        "rejection_countries": rejection_countries,
    }


@router.get("/api/orders")
async def admin_orders(
    _: str = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    start: Optional[date] = Query(default=None),
    end: Optional[date] = Query(default=None),
    status_filter: Optional[str] = Query(default=None, alias="status"),
    q: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
) -> dict:
    start_dt, end_dt = _date_bounds(start, end)
    params = {
        "start": start_dt,
        "end": end_dt,
        "status": status_filter,
        "q": f"%{q.strip()}%" if q and q.strip() else None,
        "limit": limit,
    }
    orders = await _fetch_mappings(
        db,
        """
        SELECT
            order_number,
            customer_name,
            phone_last4,
            status,
            confirmation_status,
            total_sar,
            currency,
            payment_method,
            landing_page,
            referrer,
            utm_source,
            utm_campaign,
            sheet_sync_status,
            created_at
        FROM orders
        WHERE created_at >= :start
          AND created_at < :end
          AND is_test_order = false
          AND (:status IS NULL OR status = :status)
          AND (
            :q IS NULL
            OR order_number ILIKE :q
            OR customer_name ILIKE :q
            OR phone_last4 ILIKE :q
          )
        ORDER BY created_at DESC
        LIMIT :limit
        """,
        params,
    )
    for order in orders:
        if order.get("created_at"):
            order["created_at"] = order["created_at"].isoformat()
    return {"orders": orders}


@router.get("/api/orders/{order_number}")
async def admin_order_detail(
    order_number: str,
    _: str = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    rows = await _fetch_mappings(
        db,
        """
        SELECT
            id,
            order_number,
            customer_name,
            phone_e164,
            phone_last4,
            status,
            confirmation_status,
            subtotal_sar,
            discount_sar,
            total_sar,
            currency,
            payment_method,
            landing_page,
            referrer,
            user_agent,
            client_ip,
            utm_source,
            utm_medium,
            utm_campaign,
            utm_content,
            utm_term,
            fbclid,
            ttclid,
            sc_click_id,
            sheet_sync_status,
            sheet_synced_at,
            notes,
            created_at,
            updated_at
        FROM orders
        WHERE order_number = :order_number
        """,
        {"order_number": order_number},
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Order not found")
    order = rows[0]
    order_id = order.pop("id")
    for key in ("created_at", "updated_at", "sheet_synced_at"):
        if order.get(key):
            order[key] = order[key].isoformat()

    items = await _fetch_mappings(
        db,
        """
        SELECT product_slug, product_name_ar, quantity, unit_price_sar, line_total_sar, offer_type, is_upsell
        FROM order_items
        WHERE order_id = :order_id
        ORDER BY is_upsell, created_at
        """,
        {"order_id": order_id},
    )
    tracking = await _fetch_mappings(
        db,
        """
        SELECT platform, event_name, event_id, status, error_message, created_at
        FROM tracking_events
        WHERE order_id = :order_id
        ORDER BY created_at DESC
        """,
        {"order_id": order_id},
    )
    for event in tracking:
        if event.get("created_at"):
            event["created_at"] = event["created_at"].isoformat()

    return {"order": order, "items": items, "tracking": tracking}


ADMIN_HTML = r"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>NAJD Admin Dashboard</title>
  <style>
    :root { color-scheme: dark; --bg:#080b12; --panel:#111827; --muted:#93a4b8; --text:#edf2f7; --line:#223044; --brand:#d4af37; --ok:#22c55e; --bad:#fb7185; --blue:#38bdf8; }
    * { box-sizing: border-box; }
    body { margin:0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Arial; background: radial-gradient(circle at top left, #162033, var(--bg) 40%); color:var(--text); }
    .shell { max-width: 1240px; margin: 0 auto; padding: 28px; }
    .hero { display:flex; justify-content:space-between; gap:16px; align-items:flex-end; margin-bottom:22px; }
    h1 { margin:0; font-size:32px; letter-spacing:-0.04em; }
    .sub { color:var(--muted); margin-top:6px; }
    .filters { display:flex; gap:10px; flex-wrap:wrap; align-items:center; background:rgba(17,24,39,.78); border:1px solid var(--line); border-radius:18px; padding:12px; }
    input, select, button { border:1px solid var(--line); border-radius:12px; background:#0b1220; color:var(--text); padding:10px 12px; }
    button { cursor:pointer; font-weight:700; background:linear-gradient(135deg, #d4af37, #f7df72); color:#111827; border:0; }
    .tabs { display:flex; gap:10px; margin:18px 0; }
    .tab { background:#0b1220; color:var(--muted); border:1px solid var(--line); }
    .tab.active { background:var(--brand); color:#111827; }
    .grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(180px,1fr)); gap:14px; }
    .card { background:rgba(17,24,39,.86); border:1px solid var(--line); border-radius:22px; padding:18px; box-shadow:0 18px 40px rgba(0,0,0,.22); }
    .metric .label { color:var(--muted); font-size:13px; }
    .metric .value { font-size:28px; font-weight:800; margin-top:6px; letter-spacing:-0.03em; }
    .section { margin-top:16px; }
    .two { display:grid; grid-template-columns: 1.4fr .9fr; gap:14px; }
    table { width:100%; border-collapse:collapse; font-size:14px; }
    th, td { text-align:left; padding:12px 10px; border-bottom:1px solid var(--line); vertical-align:top; }
    th { color:var(--muted); font-weight:700; }
    .badge { display:inline-flex; align-items:center; border-radius:999px; padding:5px 9px; background:#0b1220; border:1px solid var(--line); color:#cbd5e1; font-size:12px; }
    .ok { color:var(--ok); } .bad { color:var(--bad); } .blue { color:var(--blue); }
    .bar { height:8px; border-radius:99px; background:#0b1220; overflow:hidden; margin-top:6px; }
    .bar span { display:block; height:100%; background:linear-gradient(90deg, var(--brand), var(--blue)); }
    .hidden { display:none; }
    .drawer { position:fixed; inset:0 0 0 auto; width:min(520px, 100%); background:#0b1220; border-left:1px solid var(--line); transform:translateX(100%); transition:.2s ease; padding:24px; overflow:auto; z-index:10; box-shadow:-30px 0 80px rgba(0,0,0,.45); }
    .drawer.open { transform:translateX(0); }
    .drawer-head { display:flex; justify-content:space-between; gap:12px; align-items:flex-start; }
    .line { display:flex; justify-content:space-between; gap:16px; border-bottom:1px solid var(--line); padding:10px 0; }
    .line span:first-child { color:var(--muted); }
    .items { display:grid; gap:10px; margin-top:12px; }
    .item { border:1px solid var(--line); border-radius:16px; padding:12px; background:#111827; }
    @media (max-width: 920px) { .grid { grid-template-columns: repeat(2, 1fr); } .two { grid-template-columns:1fr; } .hero { align-items:stretch; flex-direction:column; } }
  </style>
</head>
<body>
  <div class="shell">
    <div class="hero">
      <div>
        <h1>NAJD Admin Dashboard</h1>
        <div class="sub">COD performance, KSA-valid clicks, orders, products, sources, and order previews.</div>
      </div>
      <div class="filters">
        <input id="start" type="date" />
        <input id="end" type="date" />
        <button onclick="loadAll()">Apply Dates</button>
      </div>
    </div>

    <div class="tabs">
      <button class="tab active" id="tab-overview" onclick="showTab('overview')">Overview</button>
      <button class="tab" id="tab-orders" onclick="showTab('orders')">Orders</button>
    </div>

    <main id="overview">
      <div class="grid" id="metrics"></div>
      <div class="two section">
        <div class="card">
          <h3>Daily Performance</h3>
          <table><thead><tr><th>Date</th><th>Clicks</th><th>Orders</th><th>CVR</th><th>Revenue</th></tr></thead><tbody id="daily"></tbody></table>
        </div>
        <div class="card">
          <h3>Status Mix</h3>
          <div id="statuses"></div>
        </div>
      </div>
      <div class="two section">
        <div class="card">
          <h3>Click Rejections <span class="sub" style="font-weight:400">(why is_valid_ksa_ip = false)</span></h3>
          <table><thead><tr><th>Reason</th><th>Provider</th><th>Count</th></tr></thead><tbody id="rejectionReasons"></tbody></table>
          <p class="sub" id="rejectionsHint" style="margin-top:10px"></p>
        </div>
        <div class="card">
          <h3>Rejected by Country</h3>
          <table><thead><tr><th>Country</th><th>Count</th></tr></thead><tbody id="rejectionCountries"></tbody></table>
        </div>
      </div>
      <div class="two section">
        <div class="card">
          <h3>Products</h3>
          <table><thead><tr><th>Product</th><th>Units</th><th>Orders</th><th>Revenue</th></tr></thead><tbody id="products"></tbody></table>
        </div>
        <div class="card">
          <h3>Sources</h3>
          <table><thead><tr><th>Source</th><th>Clicks</th><th>Orders</th><th>CVR</th></tr></thead><tbody id="sources"></tbody></table>
        </div>
      </div>
    </main>

    <main id="orders" class="hidden">
      <div class="card">
        <div class="filters" style="margin-bottom:12px">
          <input id="q" placeholder="Search order, name, last 4" />
          <select id="status"><option value="">All statuses</option><option>pending_confirmation</option><option>confirmed</option><option>cancelled</option></select>
          <button onclick="loadOrders()">Search</button>
        </div>
        <table><thead><tr><th>Order</th><th>Customer</th><th>Status</th><th>Total</th><th>Source</th><th>Date</th></tr></thead><tbody id="ordersBody"></tbody></table>
      </div>
    </main>
  </div>

  <aside id="drawer" class="drawer"></aside>

  <script>
    const fmt = new Intl.NumberFormat('en-SA');
    const sar = value => `${fmt.format(Number(value || 0))} SAR`;
    const byId = id => document.getElementById(id);
    const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    const dates = () => {
      const p = new URLSearchParams();
      if (byId('start').value) p.set('start', byId('start').value);
      if (byId('end').value) p.set('end', byId('end').value);
      return p;
    };
    function setDefaultDates() {
      const end = new Date();
      const start = new Date();
      start.setDate(end.getDate() - 6);
      byId('start').value = start.toISOString().slice(0,10);
      byId('end').value = end.toISOString().slice(0,10);
    }
    function showTab(name) {
      byId('overview').classList.toggle('hidden', name !== 'overview');
      byId('orders').classList.toggle('hidden', name !== 'orders');
      byId('tab-overview').classList.toggle('active', name === 'overview');
      byId('tab-orders').classList.toggle('active', name === 'orders');
      if (name === 'orders') loadOrders();
    }
    async function loadOverview() {
      const res = await fetch(`/admin/api/overview?${dates()}`);
      const data = await res.json();
      const s = data.summary || {};
      const totalClicks = s.total_clicks || 0;
      const rejectedClicks = s.rejected_clicks || 0;
      const validClass = totalClicks && !s.clicks ? 'bad' : 'blue';
      byId('metrics').innerHTML = [
        ['Valid KSA Clicks', `${fmt.format(s.clicks || 0)} / ${fmt.format(totalClicks)}`, validClass],
        ['Rejected Clicks', `${fmt.format(rejectedClicks)} (${s.rejection_rate || 0}%)`, rejectedClicks ? 'bad' : 'blue'],
        ['Orders', fmt.format(s.orders || 0), 'ok'],
        ['Conversion Rate', `${s.conversion_rate || 0}%`, 'ok'],
        ['Revenue', sar(s.revenue_sar), 'ok'],
        ['AOV / Upsell', `${sar(s.avg_order_value_sar)} / ${s.upsell_rate || 0}%`, 'blue'],
      ].map(m => `<div class="card metric"><div class="label">${m[0]}</div><div class="value ${m[2]}">${m[1]}</div></div>`).join('');
      byId('daily').innerHTML = data.daily.map(r => `<tr><td>${esc(r.day)}</td><td>${r.clicks}</td><td>${r.orders}</td><td>${r.conversion_rate}%</td><td>${sar(r.revenue_sar)}</td></tr>`).join('');
      const maxStatus = Math.max(1, ...data.status_counts.map(r => r.count));
      byId('statuses').innerHTML = data.status_counts.map(r => `<div class="line"><span>${esc(r.status)}</span><b>${r.count}</b></div><div class="bar"><span style="width:${(r.count / maxStatus) * 100}%"></span></div>`).join('') || '<p class="sub">No orders in this period.</p>';
      byId('products').innerHTML = data.products.map(r => `<tr><td>${esc(r.product_name_ar)}<br><span class="sub">${esc(r.product_slug)}</span></td><td>${r.units}</td><td>${r.orders}</td><td>${sar(r.revenue_sar)}</td></tr>`).join('');
      byId('sources').innerHTML = data.sources.map(r => `<tr><td>${esc(r.source)}</td><td>${r.clicks}</td><td>${r.orders}</td><td>${r.conversion_rate}%</td></tr>`).join('');
      const reasons = data.rejection_reasons || [];
      byId('rejectionReasons').innerHTML = reasons.length
        ? reasons.map(r => `<tr><td><code>${esc(r.reason)}</code></td><td><span class="sub">${esc(r.provider)}</span></td><td>${fmt.format(r.count)}</td></tr>`).join('')
        : '<tr><td colspan="3" class="sub">No rejected clicks in this period.</td></tr>';
      const topReason = reasons[0]?.reason || '';
      const hints = {
        maxmind_credentials_missing: 'MaxMind env vars (MAXMIND_ACCOUNT_ID / MAXMIND_LICENSE_KEY) missing in backend — all clicks get rejected.',
        non_sa_country: 'Ads are sending traffic from outside Saudi Arabia.',
        non_public_ip: 'Backend sees private/loopback IPs — reverse proxy is not forwarding X-Forwarded-For.',
        missing_ip: 'Backend received no client IP — reverse proxy / Traefik headers missing.',
        anonymous_vpn: 'Visitors connecting through VPNs.',
        anonymizer_vpn: 'Visitors connecting through VPNs (MaxMind anonymizer flag).',
        hosting_provider: 'Visitors on datacenter / hosting IPs — toggle MAXMIND_BLOCK_HOSTING_PROVIDER=false if too aggressive.',
        anonymizer_hosting_provider: 'Datacenter / hosting IPs flagged by MaxMind anonymizer.',
        maxmind_404: 'MaxMind has no record for those IPs.',
        maxmind_auth_rejected: 'MaxMind credentials are wrong / expired.',
        maxmind_request_failed: 'Backend cannot reach MaxMind (network / outbound firewall).',
      };
      byId('rejectionsHint').textContent = topReason && hints[topReason] ? `Top reason: ${hints[topReason]}` : '';
      const countries = data.rejection_countries || [];
      byId('rejectionCountries').innerHTML = countries.length
        ? countries.map(r => `<tr><td>${esc(r.country_code)}</td><td>${fmt.format(r.count)}</td></tr>`).join('')
        : '<tr><td colspan="2" class="sub">No rejected clicks in this period.</td></tr>';
    }
    async function loadOrders() {
      const p = dates();
      if (byId('q').value) p.set('q', byId('q').value);
      if (byId('status').value) p.set('status', byId('status').value);
      const res = await fetch(`/admin/api/orders?${p}`);
      const data = await res.json();
      byId('ordersBody').innerHTML = data.orders.map(o => `<tr onclick="previewOrder('${esc(o.order_number)}')" style="cursor:pointer"><td><b>${esc(o.order_number)}</b><br><span class="sub">${esc(o.sheet_sync_status)}</span></td><td>${esc(o.customer_name)}<br><span class="sub">****${esc(o.phone_last4 || '')}</span></td><td><span class="badge">${esc(o.status)}</span></td><td>${sar(o.total_sar)}</td><td>${esc(o.utm_source || 'direct')}<br><span class="sub">${esc(o.utm_campaign || '')}</span></td><td>${new Date(o.created_at).toLocaleString()}</td></tr>`).join('');
    }
    async function previewOrder(orderNumber) {
      const res = await fetch(`/admin/api/orders/${orderNumber}`);
      const data = await res.json();
      const o = data.order;
      byId('drawer').innerHTML = `
        <div class="drawer-head"><div><h2>${esc(o.order_number)}</h2><div class="sub">${new Date(o.created_at).toLocaleString()}</div></div><button onclick="byId('drawer').classList.remove('open')">Close</button></div>
        <div class="card section">
          <div class="line"><span>Customer</span><b>${esc(o.customer_name)}</b></div>
          <div class="line"><span>Phone</span><b>${esc(o.phone_e164)}</b></div>
          <div class="line"><span>Status</span><b>${esc(o.status)}</b></div>
          <div class="line"><span>Total</span><b>${sar(o.total_sar)}</b></div>
          <div class="line"><span>Payment</span><b>${esc(o.payment_method)}</b></div>
          <div class="line"><span>IP</span><b>${esc(o.client_ip || '-')}</b></div>
        </div>
        <h3>Items</h3><div class="items">${data.items.map(i => `<div class="item"><b>${esc(i.product_name_ar)}</b><div class="sub">${esc(i.product_slug)} · qty ${i.quantity} · ${esc(i.offer_type)}${i.is_upsell ? ' · upsell' : ''}</div><div>${sar(i.line_total_sar)}</div></div>`).join('')}</div>
        <h3>Attribution</h3><div class="card">${['utm_source','utm_medium','utm_campaign','utm_content','utm_term','fbclid','ttclid','sc_click_id','landing_page','referrer'].map(k => `<div class="line"><span>${k}</span><b>${esc(o[k] || '-')}</b></div>`).join('')}</div>
        <h3>CAPI / Tracking</h3><div class="items">${data.tracking.map(t => `<div class="item"><b>${esc(t.platform)} · ${esc(t.event_name)}</b><div class="sub">${esc(t.status)} · ${esc(t.event_id)}</div>${t.error_message ? `<div class="bad">${esc(t.error_message)}</div>` : ''}</div>`).join('') || '<p class="sub">No tracking events yet.</p>'}</div>
      `;
      byId('drawer').classList.add('open');
    }
    async function loadAll() { await loadOverview(); if (!byId('orders').classList.contains('hidden')) await loadOrders(); }
    setDefaultDates();
    loadAll();
  </script>
</body>
</html>
"""

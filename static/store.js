/* ═══════════════════════════════════════════════════════
   NAJD STORE — store.js
   ═══════════════════════════════════════════════════════ */

/* ─── Product Meta: ICP-targeted copy, benefits, ingredients ─── */
const productMeta = {
  "face-sunscreen-spf50": {
    tagline: "حماية بدون ثقل — لا يبيّض ولا يكسر الأساس",
    badge: "الأكثر طلباً",
    badgeStyle: "primary",
    rating: "4.9",
    reviewCount: "47",
    benefits: [
      "يقلّل التعرض للأشعة UVA/UVB — <strong lang=\"en\">SPF 50</strong>",
      "ملمس خفيف جداً · لا يكسر الفونداشن",
      "لا يُبيّض وجهك في الصور والإضاءة",
    ],
    ingredients: [
      { en: "Zinc Oxide", ar: "أكسيد الزنك" },
      { en: "Niacinamide", ar: "نياسيناميد" },
      { en: "Vitamin E", ar: "فيتامين E" },
    ],
    mini_review: {
      quote: "ما حسّيتُه يبيّض وجهي زي الواقيات الثانية — خفيف وماشي تحت الأساس",
      author: "شهد · الخبر",
    },
  },
  "face-primer": {
    tagline: "مكياج يثبت — حتى مع الحرّ والتكييف",
    badge: "مُوصى به",
    badgeStyle: "secondary",
    rating: "4.8",
    reviewCount: "53",
    benefits: [
      "يثبّت المكياج ساعات أطول مع الحرّ",
      "يقلّل اللمعة ويهيّئ البشرة للأساس",
      "خفيف على الحسّ · مناسب تحت الإيشارب",
    ],
    ingredients: [
      { en: "Dimethicone", ar: "ديميثيكون" },
      { en: "Kaolin Clay", ar: "طين الكاولين" },
      { en: "Hyaluronic Acid", ar: "هيالورونيك" },
    ],
    mini_review: {
      quote: "المكياج ما ذاب بنفس السرعة وقت الدوام الطويل مع التكييف",
      author: "دانة · الرياض",
    },
  },
  "forehead-serum": {
    tagline: "جبهة أصفى — من أول الاستخدام",
    badge: "للإيشارب",
    badgeStyle: "accent",
    rating: "4.8",
    reviewCount: "27",
    benefits: [
      "يهيّئ ملمس الجبهة وخط الإيشارب",
      "يلطّف مظهر الحبوب الصغيرة والخشونة",
      "سيروم موضّع سريع الامتصاص — مو كريم عام",
    ],
    ingredients: [
      { en: "Salicylic Acid", ar: "ساليسيليك" },
      { en: "Niacinamide", ar: "نياسيناميد" },
      { en: "Centella", ar: "سينتيلا" },
    ],
    mini_review: {
      quote: "الجبهة أنعم وما شفت الحبوب الزغيرة بنفس الشكل — وسيروم خفيف ما يثقل",
      author: "ريم · جدة",
    },
  },
};

/* ─── Fallback product data ─── */
const fallbackProducts = [
  {
    slug: "face-sunscreen-spf50",
    name_ar: "درع النهار",
    short_description_ar:
      "واقٍ يومي SPF 50 بملمس خفيف — لا يبيّض وجهك ولا يكسر الأساس. مناسب للجو الحار والتكييف.",
    hero_image_url: "products/face-sunscreen-spf50/hero.png",
    offers: [
      { quantity: 1, price_sar: 199, label_ar: "عبوّة واحدة" },
      { quantity: 2, price_sar: 279, label_ar: "عبوتين — وفّري 119 ر.س" },
      { quantity: 3, price_sar: 349, label_ar: "ثلاث عبوات — أفضل قيمة" },
    ],
  },
  {
    slug: "face-primer",
    name_ar: "ثبات الخط",
    short_description_ar:
      "برايمر خفيف قبل الأساس — يهيّئ البشرة ويثبّت المكياج ساعات أطول مع الحرّ والتكييف والإيشارب.",
    hero_image_url: "products/face-primer/hero.png",
    offers: [
      { quantity: 1, price_sar: 199, label_ar: "عبوّة واحدة" },
      { quantity: 2, price_sar: 279, label_ar: "عبوتين — وفّري 119 ر.س" },
      { quantity: 3, price_sar: 349, label_ar: "ثلاث عبوات — أفضل قيمة" },
    ],
  },
  {
    slug: "forehead-serum",
    name_ar: "صفاء الجبهة",
    short_description_ar:
      "سيروم موضّع للجبهة وخط الإيشارب — يهيّئ الملمس ويلطّف مظهر الحبوب الصغيرة والخشونة الخفيفة.",
    hero_image_url: "products/forehead-serum/hero.png",
    offers: [
      { quantity: 1, price_sar: 199, label_ar: "عبوّة واحدة" },
      { quantity: 2, price_sar: 279, label_ar: "عبوتين — وفّري 119 ر.س" },
      { quantity: 3, price_sar: 349, label_ar: "ثلاث عبوات — أفضل قيمة" },
    ],
  },
];

const grid = document.querySelector("#productGrid");

/* ─── Product image with fallback ─── */
function createProductImage(product) {
  const imageWrap = document.createElement("div");
  imageWrap.className = "product-image";

  const image = document.createElement("img");
  image.src = product.hero_image_url;
  image.alt = product.name_ar;
  image.loading = "lazy";

  image.addEventListener("error", () => {
    image.remove();
    const placeholder = document.createElement("div");
    placeholder.className = "product-placeholder";
    placeholder.textContent = product.name_ar.slice(0, 1);
    imageWrap.append(placeholder);
  });

  imageWrap.append(image);
  return imageWrap;
}

/* ─── Enhanced product card render ─── */
function renderProducts(products) {
  grid.innerHTML = "";

  products.forEach((product) => {
    const meta = productMeta[product.slug] || {};

    const card = document.createElement("article");
    card.className = "product-card";
    if (product.slug) card.id = product.slug;

    /* ── Image + badge ── */
    const imgWrap = createProductImage(product);

    if (meta.badge) {
      const badge = document.createElement("span");
      badge.className = `product-badge product-badge--${meta.badgeStyle || "primary"}`;
      badge.textContent = meta.badge;
      imgWrap.append(badge);
    }

    /* ── Body container ── */
    const body = document.createElement("div");
    body.className = "product-card__body";

    /* ── Stars + rating ── */
    const ratingRow = document.createElement("div");
    ratingRow.className = "product-card__meta";
    ratingRow.innerHTML = `
      <span class="product-card__stars" aria-hidden="true">★★★★★</span>
      <span class="product-card__rating-label">${meta.rating || "4.8"} · ${meta.reviewCount || "47"} تقييم</span>
    `;

    /* ── Name ── */
    const title = document.createElement("h3");
    title.textContent = product.name_ar;

    /* ── Tagline ── */
    if (meta.tagline) {
      const tagline = document.createElement("p");
      tagline.className = "product-tagline";
      tagline.textContent = meta.tagline;
      body.append(tagline);
    }

    /* ── Short description ── */
    const desc = document.createElement("p");
    desc.className = "product-card__desc";
    desc.textContent = product.short_description_ar || "";

    /* ── Benefits checklist ── */
    if (meta.benefits && meta.benefits.length) {
      const benefitsList = document.createElement("ul");
      benefitsList.className = "product-benefits";
      meta.benefits.forEach((benefit) => {
        const li = document.createElement("li");
        li.innerHTML = `<span class="benefit-check" aria-hidden="true">✓</span><span>${benefit}</span>`;
        benefitsList.append(li);
      });
      body.append(benefitsList);
    }

    /* ── Ingredient chips ── */
    if (meta.ingredients && meta.ingredients.length) {
      const ingWrap = document.createElement("div");
      ingWrap.className = "product-ingredients";
      ingWrap.innerHTML = `<span class="product-ingredients__label">مكوّنات رئيسية</span>`;
      const tags = document.createElement("div");
      tags.className = "ingredient-tags";
      meta.ingredients.forEach((ing) => {
        const tag = document.createElement("span");
        tag.className = "ingredient-tag";
        tag.innerHTML = `<strong lang="en">${ing.en}</strong><small>${ing.ar}</small>`;
        tags.append(tag);
      });
      ingWrap.append(tags);
      body.append(ingWrap);
    }

    /* ── Offers / Pricing ── */
    const offersWrap = document.createElement("div");
    offersWrap.className = "offers";

    [...(product.offers || [])]
      .sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
      .forEach((offer) => {
        const row = document.createElement("div");
        const qty = offer.quantity ?? 1;
        if (qty === 2) {
          row.className = "offer offer--featured";
          row.innerHTML = `
            <span class="offer__badge">الأكثر اختياراً</span>
            <strong>${offer.label_ar || `${qty} عبوّة`}</strong>
            <span class="offer__price">${offer.price_sar} ر.س</span>
          `;
        } else {
          row.className = "offer";
          row.innerHTML = `
            <strong>${offer.label_ar || `${qty} عبوّة`}</strong>
            <span class="offer__price">${offer.price_sar} ر.س</span>
          `;
        }
        offersWrap.append(row);
      });

    /* ── Action Buttons ── */
    const actionsWrap = document.createElement("div");
    actionsWrap.style.display = "flex";
    actionsWrap.style.gap = "0.5rem";
    
    const cta = document.createElement("a");
    cta.className = "button button--primary product-cta-primary";
    cta.href = "#contact";
    cta.innerHTML = "اطلبي الآن ←";
    cta.style.flex = "2";

    const detailsLink = document.createElement("a");
    detailsLink.className = "button button--secondary";
    detailsLink.href = `product.html?slug=${product.slug}`;
    detailsLink.innerHTML = "التفاصيل";
    detailsLink.style.flex = "1";
    detailsLink.style.textAlign = "center";
    detailsLink.style.border = "1px solid var(--primary)";
    detailsLink.style.background = "transparent";
    detailsLink.style.color = "var(--primary)";
    
    actionsWrap.append(cta, detailsLink);

    /* ── Trust strip ── */
    const trust = document.createElement("div");
    trust.className = "product-trust-strip";
    trust.innerHTML = `
      <span>✓ الدفع عند الاستلام</span>
      <span>✓ ضمان 30 يوم</span>
      <span>✓ شحن سريع</span>
    `;

    /* ── Mini review ── */
    if (meta.mini_review) {
      const miniReview = document.createElement("blockquote");
      miniReview.className = "product-mini-review";
      miniReview.innerHTML = `
        <p>"${meta.mini_review.quote}"</p>
        <cite>${meta.mini_review.author}</cite>
      `;
      body.append(miniReview);
    }

    /* ── Assemble body ── */
    body.prepend(offersWrap);
    body.prepend(desc);
    body.prepend(title);
    body.prepend(ratingRow);
    body.append(actionsWrap);
    body.append(trust);

    /* ── Assemble card ── */
    card.append(imgWrap, body);
    grid.append(card);
  });
}

/* ─── Load products (API → fallback) ─── */
async function loadProducts() {
  try {
    const response = await fetch("/products");
    if (!response.ok) throw new Error("Products API unavailable");
    const products = await response.json();
    renderProducts(products);
  } catch {
    renderProducts(fallbackProducts);
  }
}

/* ─── Rotating announcement bar ─── */
const announcements = [
  "فحص وتغليف قبل خروج الطلب",
  "الدفع عند الاستلام · لا تحتاجين بطاقة أونلاين",
  "ضمان رضا 30 يوم · استرجاع بدون تعقيد",
  "توصيل خلال 2–5 أيام عمل داخل المملكة",
];

let announcementIdx = 0;
function rotateAnnouncement() {
  const el = document.getElementById("announcementText");
  if (!el) return;
  el.style.opacity = "0";
  el.style.transform = "translateY(-6px)";
  setTimeout(() => {
    announcementIdx = (announcementIdx + 1) % announcements.length;
    el.textContent = announcements[announcementIdx];
    el.style.opacity = "1";
    el.style.transform = "translateY(0)";
  }, 320);
}
setInterval(rotateAnnouncement, 4200);

/* ─── Dynamic scroll-padding-top (matches sticky header height) ─── */
function updateScrollPadding() {
  const wrap = document.querySelector(".site-header-wrap");
  if (wrap) {
    const h = wrap.offsetHeight;
    document.documentElement.style.scrollPaddingTop = h + 8 + "px";
  }
}
window.addEventListener("resize", updateScrollPadding);
updateScrollPadding();

/* ─── Sticky CTA — show after hero leaves viewport ─── */
const stickyCta = document.getElementById("stickyCta");
const heroSection = document.querySelector(".hero");

function updateStickyCta() {
  if (!stickyCta || !heroSection) return;
  const heroBottom = heroSection.getBoundingClientRect().bottom;
  if (heroBottom < 0) {
    stickyCta.classList.add("sticky-cta--visible");
  } else {
    stickyCta.classList.remove("sticky-cta--visible");
  }
}

window.addEventListener("scroll", updateStickyCta, { passive: true });
updateStickyCta();

/* ─── Smooth scroll: prevent overscroll to page top on anchor clicks ─── */
document.querySelectorAll('a[href^="#"]').forEach((link) => {
  link.addEventListener("click", (e) => {
    const href = link.getAttribute("href");
    if (!href || href === "#") return;
    const target = document.querySelector(href);
    if (!target) return;
    e.preventDefault();
    target.scrollIntoView({ behavior: "smooth", block: "start" });
  });
});

/* ─── Announcement text transition style ─── */
(function initAnnouncement() {
  const el = document.getElementById("announcementText");
  if (el) {
    el.style.transition = "opacity 0.3s ease, transform 0.3s ease";
  }
})();

/* ═══════════════════════════════════════════════════════
   TRACKING — pixel init, helpers, order form
   ═══════════════════════════════════════════════════════ */

/* ─── Loaded products (populated by loadProducts API call) ─── */
let _apiProducts = [];

/* ─── Tiny helpers ─── */
function _getCookie(name) {
  const m = document.cookie.match(new RegExp("(?:^|; )" + name + "=([^;]*)"));
  return m ? decodeURIComponent(m[1]) : undefined;
}

function _getUTM() {
  const p = new URLSearchParams(window.location.search);
  const obj = {
    utm_source:   p.get("utm_source")   || undefined,
    utm_medium:   p.get("utm_medium")   || undefined,
    utm_campaign: p.get("utm_campaign") || undefined,
    utm_content:  p.get("utm_content")  || undefined,
    utm_term:     p.get("utm_term")     || undefined,
  };
  return Object.values(obj).some(Boolean) ? obj : undefined;
}

function _getClickIds() {
  const p = new URLSearchParams(window.location.search);
  const obj = {
    fbclid:      p.get("fbclid")      || undefined,
    ttclid:      p.get("ttclid")      || undefined,
    sc_click_id: p.get("ScCid") || p.get("sc_click_id") || undefined,
  };
  return Object.values(obj).some(Boolean) ? obj : undefined;
}

function _genEventId() {
  return "ev_" + Date.now().toString(36) + "_" + Math.random().toString(36).slice(2, 9);
}

/* ─── Meta Pixel init ─── */
function _initMeta(pixelId) {
  /* eslint-disable */
  !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
  n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
  n.push=n;n.loaded=!0;n.version="2.0";n.queue=[];t=b.createElement(e);t.async=!0;
  t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,
  document,"script","https://connect.facebook.net/en_US/fbevents.js");
  /* eslint-enable */
  window.fbq("init", pixelId);
  window.fbq("track", "PageView");
}

/* ─── TikTok Pixel init ─── */
function _initTikTok(pixelId) {
  /* eslint-disable */
  !function(w,d,t){w.TiktokAnalyticsObject=t;var ttq=w[t]=w[t]||[];
  ttq.methods=["page","track","identify","instances","debug","on","off","once","ready","alias","group","enableCookie","disableCookie"];
  ttq.setAndDefer=function(t,e){t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}};
  for(var i=0;i<ttq.methods.length;i++)ttq.setAndDefer(ttq,ttq.methods[i]);
  ttq.instance=function(t){for(var e=ttq._i[t]||[],n=0;n<ttq.methods.length;n++)ttq.setAndDefer(e,ttq.methods[n]);return e};
  ttq.load=function(e,n){var i="https://analytics.tiktok.com/i18n/pixel/events.js";
  ttq._i=ttq._i||{},ttq._i[e]=[],ttq._i[e]._u=i,ttq._t=ttq._t||{},ttq._t[e]=+new Date,
  ttq._o=ttq._o||{},ttq._o[e]=n||{};var o=document.createElement("script");
  o.type="text/javascript",o.async=!0,o.src=i+"?sdkid="+e+"&lib="+t;
  var a=document.getElementsByTagName("script")[0];a.parentNode.insertBefore(o,a)};
  ttq.load(pixelId);ttq.page()}(window,document,"ttq");
  /* eslint-enable */
}

/* ─── Snapchat Pixel init ─── */
function _initSnap(pixelId) {
  /* eslint-disable */
  (function(e,t,n){if(e.snaptr)return;var a=e.snaptr=function(){
  a.handleRequest?a.handleRequest.apply(a,arguments):a.queue.push(arguments)};
  a.queue=[];var s="script",r=t.createElement(s);r.async=!0;
  r.src=n;var u=t.getElementsByTagName(s)[0];u.parentNode.insertBefore(r,u);
  })(window,document,"https://sc-static.net/scevent.min.js");
  /* eslint-enable */
  window.snaptr("init", pixelId, {});
  window.snaptr("track", "PAGE_VIEW");
}

/* ─── Load config + initialise pixels ─── */
async function loadConfig() {
  try {
    const res = await fetch("/config");
    if (!res.ok) return;
    const cfg = await res.json();
    if (cfg.meta_pixel_id)    _initMeta(cfg.meta_pixel_id);
    if (cfg.tiktok_pixel_id)  _initTikTok(cfg.tiktok_pixel_id);
    if (cfg.snap_pixel_id)    _initSnap(cfg.snap_pixel_id);
  } catch (_) {
    // pixel init is best-effort — never block the storefront
  }
}

/* ─── Fire ViewContent when a product card enters the viewport ─── */
function _observeProductCards() {
  if (!("IntersectionObserver" in window)) return;
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      const slug = entry.target.id;
      const product = _apiProducts.find((p) => p.slug === slug);
      if (!product) return;
      const price = (product.offers[0] || {}).price_sar;
      if (window.fbq)   window.fbq("track", "ViewContent", { content_ids: [product.id], content_type: "product", value: price, currency: "SAR" });
      if (window.ttq)   window.ttq.track("ViewContent", { content_id: product.id, value: price, currency: "SAR" });
      if (window.snaptr) window.snaptr("track", "VIEW_CONTENT", { item_ids: [product.id], price: price, currency: "SAR" });
      observer.unobserve(entry.target);
    });
  }, { threshold: 0.3 });

  document.querySelectorAll(".product-card[id]").forEach((el) => observer.observe(el));
}

/* ─── Order form: populate product dropdown ─── */
function _populateOrderSelect(products) {
  const sel = document.getElementById("orderProduct");
  if (!sel) return;
  products.forEach((p) => {
    const opt = document.createElement("option");
    opt.value = p.id;
    opt.textContent = p.name_ar;
    sel.append(opt);
  });
}

/* ─── Order form: update displayed price when product/qty changes ─── */
function _updateOrderPrice() {
  const productId = document.getElementById("orderProduct")?.value;
  const qty = parseInt(document.getElementById("orderQty")?.value || "1", 10);
  const row = document.getElementById("orderPriceRow");
  if (!row) return;
  if (!productId) { row.textContent = ""; return; }
  const product = _apiProducts.find((p) => p.id === productId);
  if (!product) { row.textContent = ""; return; }
  const offer = product.offers.find((o) => o.quantity === qty);
  row.textContent = offer ? `السعر: ${offer.price_sar} ر.س` : "";
}

/* ─── Order form: pre-select product from CTA click ─── */
function _preselectProduct(slug) {
  const product = _apiProducts.find((p) => p.slug === slug);
  if (!product) return;
  const sel = document.getElementById("orderProduct");
  if (sel) { sel.value = product.id; _updateOrderPrice(); }
}

/* ─── Order form: wire change events ─── */
function _initOrderFormListeners() {
  document.getElementById("orderProduct")?.addEventListener("change", _updateOrderPrice);
  document.getElementById("orderQty")?.addEventListener("change", _updateOrderPrice);

  // Pre-select product when clicking any product CTA
  document.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-order-product]");
    if (btn) _preselectProduct(btn.dataset.orderProduct);
  });

  const form = document.getElementById("orderForm");
  if (!form) return;
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    await _handleOrderSubmit(form);
  });
}

/* ─── Order form: handle submission ─── */
async function _handleOrderSubmit(form) {
  const feedback = document.getElementById("orderFeedback");
  const submitBtn = document.getElementById("orderSubmitBtn");

  const name      = form.orderName?.value.trim();
  const phone     = form.orderPhone?.value.trim();
  const productId = form.orderProduct?.value;
  const qty       = parseInt(form.orderQty?.value || "1", 10);

  // Basic client-side validation
  if (!name || name.length < 2) {
    _showFeedback(feedback, "يرجى إدخال اسمك (حرفان على الأقل)", false);
    form.orderName?.focus();
    return;
  }
  if (!phone || !/^(05\d{8}|\+9665\d{8})$/.test(phone)) {
    _showFeedback(feedback, "يرجى إدخال رقم جوال سعودي صحيح (مثال: 0512345678)", false);
    form.orderPhone?.focus();
    return;
  }
  if (!productId) {
    _showFeedback(feedback, "يرجى اختيار منتج", false);
    form.orderProduct?.focus();
    return;
  }

  const product = _apiProducts.find((p) => p.id === productId);
  const offer   = product?.offers.find((o) => o.quantity === qty);
  if (!offer) {
    _showFeedback(feedback, "حدث خطأ في بيانات المنتج — يرجى تحديث الصفحة", false);
    return;
  }

  submitBtn.disabled = true;
  submitBtn.textContent = "جاري الإرسال...";
  _showFeedback(feedback, "", null);

  const purchaseEventId = _genEventId();
  const clickIds        = _getClickIds();
  const fbclid          = clickIds?.fbclid;

  const payload = {
    customer_name: name,
    phone,
    items: [{ product_id: productId, offer_qty: qty, price_sar: offer.price_sar }],
    utm:       _getUTM(),
    click_ids: clickIds,
    browser: {
      user_agent: navigator.userAgent,
      fbp: _getCookie("_fbp"),
      fbc: _getCookie("_fbc") || (fbclid ? "fb.1." + Date.now() + "." + fbclid : undefined),
      ttp: _getCookie("_ttp"),
    },
    event_ids:   { purchase: purchaseEventId },
    landing_page: window.location.href,
    referrer:    document.referrer || undefined,
  };

  try {
    const res = await fetch("/orders", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "حدث خطأ — يرجى المحاولة مرة أخرى");
    }

    const order = await res.json();

    // Fire browser-side Purchase events (CAPI fires the same event server-side for deduplication)
    const purchaseData = { value: offer.price_sar, currency: "SAR", content_ids: [productId], num_items: qty };
    if (window.fbq)    window.fbq("track", "Purchase", purchaseData, { eventID: purchaseEventId });
    if (window.ttq)    window.ttq.track("CompletePayment", { value: offer.price_sar, currency: "SAR", content_id: productId });
    if (window.snaptr) window.snaptr("track", "PURCHASE", { price: offer.price_sar, currency: "SAR", transaction_id: order.order_id });

    _showFeedback(
      feedback,
      `تم استلام طلبك ✓ — رقم الطلب: ${order.order_id}\nسيتواصل معك فريقنا لتأكيد العنوان قريباً.`,
      true
    );
    form.reset();
    _updateOrderPrice();

  } catch (err) {
    _showFeedback(feedback, err.message, false);
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "أكّدي الطلب ←";
  }
}

function _showFeedback(el, msg, success) {
  if (!el) return;
  el.textContent = msg;
  el.className = "order-form__feedback" + (success === true ? " order-form__feedback--success" : success === false ? " order-form__feedback--error" : "");
}

/* ─── Patch renderProducts to store API data + wire CTAs ─── */
const _originalRenderProducts = renderProducts;
renderProducts = function (products) {
  _apiProducts = products; // store for order form + pixel events
  _originalRenderProducts(products);
  _populateOrderSelect(products);
  _updateOrderPrice();
  _observeProductCards();

  // Add data-order-product attribute to every CTA so clicks pre-select the product
  document.querySelectorAll(".product-cta-primary").forEach((btn) => {
    const card = btn.closest(".product-card");
    if (card?.id) btn.dataset.orderProduct = card.id;
  });
};

/* ─── Boot ─── */
_initOrderFormListeners();
loadProducts();
loadConfig();

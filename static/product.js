/* ═══════════════════════════════════════════════════════
   NAJD STORE — product.js
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

let currentProduct = null;

/* ─── Tracking helpers (mirrored from store.js so product page is self-contained) ─── */
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

async function initProductPage() {
  const params = new URLSearchParams(window.location.search);
  const slug = params.get('slug');

  if (!slug) {
    document.getElementById('productDetails').innerHTML = '<div style="text-align: center; padding: 4rem;">لم يتم العثور على المنتج. <a href="index.html">العودة للرئيسية</a></div>';
    return;
  }

  try {
    const res = await fetch(`/products/${slug}`);
    if (!res.ok) throw new Error('Product not found');
    currentProduct = await res.json();
    renderProductDetails(currentProduct);
    setupOrderForm(currentProduct);

    const firstOffer = (currentProduct.offers || [])[0] || {};
    const vcPayload = {
      content_ids:  [currentProduct.id],
      content_type: "product",
      content_name: currentProduct.name_ar,
      value:        firstOffer.price_sar,
      currency:     "SAR",
    };
    if (window.fbq)    window.fbq("track", "ViewContent", vcPayload);
    if (window.ttq)    window.ttq.track("ViewContent",   { content_id: currentProduct.id, value: firstOffer.price_sar, currency: "SAR" });
    if (window.snaptr) window.snaptr("track", "VIEW_CONTENT", { item_ids: [currentProduct.id], price: firstOffer.price_sar, currency: "SAR" });
  } catch (err) {
    document.getElementById('productDetails').innerHTML = '<div style="text-align: center; padding: 4rem;">المنتج غير موجود. <a href="index.html">العودة للرئيسية</a></div>';
  }
}

function renderProductDetails(product) {
  const meta = productMeta[product.slug] || {};
  document.title = `${product.name_ar} | نجد`;

  const container = document.getElementById('productDetails');
  
  let benefitsHtml = '';
  if (meta.benefits) {
    benefitsHtml = '<ul class="product-benefits" style="margin: 2rem 0; list-style: none; padding: 0;">';
    meta.benefits.forEach(b => {
      benefitsHtml += `<li style="display: flex; gap: 0.75rem; margin-bottom: 0.75rem; font-size: 1.1rem;"><span style="color: var(--primary);">✓</span><span>${b}</span></li>`;
    });
    benefitsHtml += '</ul>';
  }

  let ingredientsHtml = '';
  if (meta.ingredients) {
    ingredientsHtml = '<div class="product-ingredients" style="margin-top: 2rem;"><span class="product-ingredients__label">مكوّنات رئيسية</span><div class="ingredient-tags">';
    meta.ingredients.forEach(i => {
      ingredientsHtml += `<span class="ingredient-tag"><strong lang="en">${i.en}</strong><small>${i.ar}</small></span>`;
    });
    ingredientsHtml += '</div></div>';
  }

  container.innerHTML = `
    <div style="max-width: 1000px; margin: 0 auto; display: grid; grid-template-columns: 1fr 1fr; gap: 4rem; padding: 4rem 1.5rem; align-items: start;">
      <div class="product-image">
        <img src="${product.hero_image_url}" alt="${product.name_ar}" style="width: 100%; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.05);" />
      </div>
      <div>
        ${meta.badge ? `<span class="product-badge product-badge--${meta.badgeStyle || 'primary'}" style="position: static; margin-bottom: 1rem; display: inline-block;">${meta.badge}</span>` : ''}
        <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem; color: var(--text-dark);">${product.name_ar}</h1>
        ${meta.tagline ? `<p style="font-size: 1.25rem; color: var(--primary); margin-bottom: 1.5rem; font-weight: 500;">${meta.tagline}</p>` : ''}
        
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 2rem;">
          <span style="color: #fbbf24;">★★★★★</span>
          <span style="color: var(--text-light); font-size: 0.95rem;">${meta.rating || '4.8'} · ${meta.reviewCount || '47'} تقييم</span>
        </div>

        <p style="font-size: 1.15rem; line-height: 1.8; color: var(--text);">${product.short_description_ar || ''}</p>

        ${benefitsHtml}
        ${ingredientsHtml}
        
        <div style="margin-top: 3rem;">
          <a href="#contact" class="button button--primary button--lg" style="width: 100%; text-align: center;">اطلبي الآن</a>
        </div>
      </div>
    </div>
  `;

  // Responsive styles
  const style = document.createElement('style');
  style.innerHTML = `
    @media (max-width: 768px) {
      #productDetails > div {
        grid-template-columns: 1fr !important;
        gap: 2rem !important;
        padding: 2rem 1.5rem !important;
      }
    }
  `;
  document.head.appendChild(style);
}

function setupOrderForm(product) {
  const selProduct = document.getElementById('orderProduct');
  selProduct.innerHTML = `<option value="${product.id}" selected>${product.name_ar}</option>`;
  
  const selQty = document.getElementById('orderQty');
  selQty.innerHTML = '';
  
  const offers = [...(product.offers || [])].sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0));
  offers.forEach(o => {
    const opt = document.createElement('option');
    opt.value = o.quantity;
    opt.textContent = `${o.label_ar || o.quantity + ' عبوة'} - ${o.price_sar} ر.س`;
    if (o.quantity === 2) opt.selected = true;
    selQty.appendChild(opt);
  });

  _updateOrderPrice();
  
  document.getElementById("orderQty")?.addEventListener("change", _updateOrderPrice);
  document.getElementById("orderForm")?.addEventListener("submit", _handleOrderSubmit);
}

function _updateOrderPrice() {
  if (!currentProduct) return;
  const qty = parseInt(document.getElementById("orderQty")?.value || "1", 10);
  const row = document.getElementById("orderPriceRow");
  if (!row) return;
  
  const offer = currentProduct.offers.find((o) => o.quantity === qty);
  row.textContent = offer ? `السعر الإجمالي: ${offer.price_sar} ر.س` : "";
}

async function _handleOrderSubmit(e) {
  e.preventDefault();
  const form = e.target;
  const feedback = document.getElementById("orderFeedback");
  const submitBtn = document.getElementById("orderSubmitBtn");

  const name      = form.orderName?.value.trim();
  const phone     = form.orderPhone?.value.trim();
  const productId = currentProduct.id;
  const qty       = parseInt(form.orderQty?.value || "1", 10);

  if (!name || name.length < 2) {
    _showFeedback(feedback, "يرجى إدخال اسمك (حرفان على الأقل)", false);
    return;
  }
  if (!phone || !/^(05\\d{8}|\\+9665\\d{8})$/.test(phone)) {
    _showFeedback(feedback, "يرجى إدخال رقم جوال سعودي صحيح (مثال: 0512345678)", false);
    return;
  }

  const offer = currentProduct.offers.find((o) => o.quantity === qty);
  if (!offer) return;

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
    event_ids:    { purchase: purchaseEventId },
    landing_page: window.location.href,
    referrer:     document.referrer || undefined,
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

initProductPage();

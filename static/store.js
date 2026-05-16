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

    /* ── Primary CTA button ── */
    const cta = document.createElement("a");
    cta.className = "button button--primary product-cta-primary";
    cta.href = "#contact";
    cta.innerHTML = "اطلبي الآن ←";

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
    body.append(cta);
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

/* ─── Boot ─── */
loadProducts();

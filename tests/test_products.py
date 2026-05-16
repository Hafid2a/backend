from app.db.models import Product


def test_product_hero_image_url_matches_slug() -> None:
    product = Product(slug="face-primer")

    assert product.hero_image_url == "/static/products/face-primer/hero.png"

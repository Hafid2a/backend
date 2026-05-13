from app.core.config import _normalize_postgres_url


def test_upgrades_postgres_scheme_to_asyncpg():
    url = "postgres://user:pass@host:5432/db"
    assert _normalize_postgres_url(url) == "postgresql+asyncpg://user:pass@host:5432/db"


def test_upgrades_postgresql_scheme_to_asyncpg():
    url = "postgresql://user:pass@host:5432/db"
    assert _normalize_postgres_url(url) == "postgresql+asyncpg://user:pass@host:5432/db"


def test_rewrites_libpq_sslmode_to_asyncpg_ssl():
    # The exact shape Easypanel hands out for the internal Postgres service.
    url = "postgres://postgres:Hafid.anna@hafidv1_database:5432/najdv1?sslmode=disable"
    assert (
        _normalize_postgres_url(url)
        == "postgresql+asyncpg://postgres:Hafid.anna@hafidv1_database:5432/najdv1?ssl=disable"
    )


def test_preserves_dot_in_password():
    # Dot is RFC 3986 unreserved, so it must survive untouched.
    url = "postgresql+asyncpg://user:has.dots@host:5432/db"
    assert _normalize_postgres_url(url) == url


def test_passthrough_for_already_asyncpg_url_without_query():
    url = "postgresql+asyncpg://najd:pw@db:5432/najd"
    assert _normalize_postgres_url(url) == url


def test_empty_input_passes_through():
    assert _normalize_postgres_url("") == ""


def test_other_query_params_are_preserved():
    url = "postgres://u:p@h:5432/db?application_name=najd&sslmode=disable"
    out = _normalize_postgres_url(url)
    assert out.startswith("postgresql+asyncpg://")
    assert "application_name=najd" in out
    assert "ssl=disable" in out
    assert "sslmode" not in out

CREATE TABLE IF NOT EXISTS click_events (
    id uuid PRIMARY KEY,
    event_id varchar NOT NULL UNIQUE,
    client_ip varchar,
    country_code varchar,
    is_valid_ksa_ip boolean NOT NULL DEFAULT false,
    ip_check_provider varchar,
    ip_reject_reason text,
    landing_page text,
    referrer text,
    user_agent text,
    utm_source varchar,
    utm_medium varchar,
    utm_campaign varchar,
    utm_content varchar,
    utm_term varchar,
    fbclid varchar,
    ttclid varchar,
    sc_click_id varchar,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_click_events_event_id ON click_events (event_id);
CREATE INDEX IF NOT EXISTS ix_click_events_is_valid_ksa_ip ON click_events (is_valid_ksa_ip);
CREATE INDEX IF NOT EXISTS ix_click_events_created_at ON click_events (created_at);
CREATE INDEX IF NOT EXISTS ix_click_events_created_valid ON click_events (created_at, is_valid_ksa_ip);
CREATE INDEX IF NOT EXISTS ix_click_events_utm_campaign ON click_events (utm_campaign);

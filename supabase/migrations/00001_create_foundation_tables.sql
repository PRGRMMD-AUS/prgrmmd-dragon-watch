-- Dragon Watch Foundation Tables
-- Migration 00001: Create all 7 core tables with realtime support

-- Articles: News articles from GDELT
CREATE TABLE articles (
    id BIGSERIAL PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    domain TEXT NOT NULL,
    published_at TIMESTAMPTZ NOT NULL,
    tone_score FLOAT,
    language TEXT,
    source_country TEXT,
    raw_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Social Posts: Telegram channel posts
CREATE TABLE social_posts (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT,
    channel TEXT NOT NULL,
    text TEXT,
    timestamp TIMESTAMPTZ NOT NULL,
    views INTEGER,
    raw_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vessel Positions: AIS maritime tracking data
CREATE TABLE vessel_positions (
    id BIGSERIAL PRIMARY KEY,
    mmsi INTEGER NOT NULL,
    ship_name TEXT,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    speed FLOAT,
    course FLOAT,
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Narrative Events: LLM-detected coordination events
CREATE TABLE narrative_events (
    id BIGSERIAL PRIMARY KEY,
    event_type TEXT NOT NULL,
    summary TEXT NOT NULL,
    confidence FLOAT,
    source_ids JSONB,
    detected_at TIMESTAMPTZ DEFAULT NOW()
);

-- Movement Events: Anomalous vessel movement patterns
CREATE TABLE movement_events (
    id BIGSERIAL PRIMARY KEY,
    event_type TEXT NOT NULL,
    vessel_mmsi INTEGER,
    location_lat FLOAT,
    location_lon FLOAT,
    description TEXT,
    detected_at TIMESTAMPTZ DEFAULT NOW()
);

-- Alerts: High-priority warnings from correlation engine
CREATE TABLE alerts (
    id BIGSERIAL PRIMARY KEY,
    severity TEXT NOT NULL CHECK (severity IN ('low','medium','high','critical')),
    title TEXT NOT NULL,
    description TEXT,
    event_ids JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

-- Briefs: Periodic intelligence summaries
CREATE TABLE briefs (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    key_developments JSONB,
    generated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable realtime replication for all tables
ALTER PUBLICATION supabase_realtime ADD TABLE articles, social_posts, vessel_positions, narrative_events, movement_events, alerts, briefs;

-- Create indexes for common query patterns
CREATE INDEX idx_articles_domain_published ON articles(domain, published_at);
CREATE INDEX idx_social_posts_channel_timestamp ON social_posts(channel, timestamp);
CREATE INDEX idx_vessel_positions_mmsi_timestamp ON vessel_positions(mmsi, timestamp);
CREATE INDEX idx_alerts_severity_created ON alerts(severity, created_at);

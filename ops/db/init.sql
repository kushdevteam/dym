-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Raw mentions table
CREATE TABLE mention (
  id BIGSERIAL PRIMARY KEY,
  source TEXT NOT NULL,                 -- twitter, reddit, telegram, dexscreener, tiktok
  source_id TEXT NOT NULL,              -- tweet_id, post_id, message_id, video_id
  author TEXT,
  text TEXT,
  url TEXT,
  created_at TIMESTAMPTZ NOT NULL,
  metrics JSONB DEFAULT '{}'::jsonb,    -- likes, rts, replies, views, shares
  lang TEXT,
  entities JSONB DEFAULT '{}'::jsonb,   -- hashtags, tickers, urls, tokens, sounds
  ingest_ts TIMESTAMPTZ DEFAULT now(),
  UNIQUE (source, source_id)
);

CREATE INDEX mention_created_idx ON mention (created_at);
CREATE INDEX mention_gin_text ON mention USING gin (to_tsvector('english', text));
CREATE INDEX mention_source_idx ON mention (source);
CREATE INDEX mention_ingest_ts_idx ON mention (ingest_ts);

-- Enriched mentions table
CREATE TABLE mention_enriched (
  mention_id BIGINT PRIMARY KEY REFERENCES mention(id) ON DELETE CASCADE,
  sentiment REAL,               -- -1..1
  embedding VECTOR(384),        -- pgvector
  keywords TEXT[],
  influencers_score REAL,       -- author influence percentile
  platform_features JSONB,      -- tiktok: sound_id, trending_score, shares
  toxicity REAL                 -- optional safety score
);

-- Add pgvector index for similarity search on embeddings
CREATE INDEX mention_enriched_embedding_idx ON mention_enriched USING ivfflat (embedding vector_cosine_ops);

-- Narratives table
CREATE TABLE narrative (
  id BIGSERIAL PRIMARY KEY,
  label TEXT,                    -- e.g., "Shrek 2 meme", "SEC vs X", "WIF dog"
  created_at TIMESTAMPTZ DEFAULT now(),
  last_seen TIMESTAMPTZ,
  centroid VECTOR(384),
  keywords TEXT[],
  category TEXT                  -- crypto, pop, tech, politics, ai, etc.
);

CREATE INDEX narrative_created_idx ON narrative (created_at);
CREATE INDEX narrative_last_seen_idx ON narrative (last_seen);
CREATE INDEX narrative_category_idx ON narrative (category);

-- Add pgvector index for similarity search on narrative centroids
CREATE INDEX narrative_centroid_idx ON narrative USING ivfflat (centroid vector_cosine_ops);

-- Narrative window stats table
CREATE TABLE narrative_window_stats (
  narrative_id BIGINT REFERENCES narrative(id) ON DELETE CASCADE,
  window_start TIMESTAMPTZ,
  window_end TIMESTAMPTZ,
  mentions INT,
  unique_authors INT,
  avg_engagement REAL,
  growth_rate REAL,              -- % vs prior window
  sentiment REAL,
  sources JSONB,
  PRIMARY KEY (narrative_id, window_start)
);

CREATE INDEX narrative_window_stats_window_start_idx ON narrative_window_stats (window_start);
CREATE INDEX narrative_window_stats_growth_rate_idx ON narrative_window_stats (growth_rate);

-- Coin ideas table
CREATE TABLE coin_idea (
  id BIGSERIAL PRIMARY KEY,
  narrative_id BIGINT REFERENCES narrative(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  symbol TEXT NOT NULL,
  description TEXT,
  tagline TEXT,
  emoji_set TEXT[],
  risk_flags JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Deployed tokens table
CREATE TABLE deployed_token (
  id BIGSERIAL PRIMARY KEY,
  coin_idea_id BIGINT REFERENCES coin_idea(id),
  mint_address TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  symbol TEXT NOT NULL,
  decimals INT NOT NULL,
  initial_supply BIGINT NOT NULL,
  metadata_uri TEXT,
  raydium_pool_address TEXT,
  deployment_tx TEXT,
  deployed_at TIMESTAMPTZ DEFAULT now(),
  deployed_by TEXT
);

-- Alerts table
CREATE TABLE alert (
  id BIGSERIAL PRIMARY KEY,
  narrative_id BIGINT REFERENCES narrative(id) ON DELETE CASCADE,
  alert_type TEXT NOT NULL,     -- spike, growth, sentiment_shift
  threshold_config JSONB NOT NULL,
  triggered_at TIMESTAMPTZ DEFAULT now(),
  acknowledged_at TIMESTAMPTZ,
  acknowledged_by TEXT
);
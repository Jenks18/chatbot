-- ToxicoGPT Database Schema
-- Run this in Supabase SQL Editor: https://supabase.com/dashboard/project/zzeycmksnujfdvasxoti/sql

-- Sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    user_agent TEXT,
    ip_address VARCHAR(50),
    country VARCHAR(100),
    city VARCHAR(100),
    region VARCHAR(100),
    timezone VARCHAR(50),
    latitude VARCHAR(20),
    longitude VARCHAR(20),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    extra_metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_sessions_session_id ON sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_last_active ON sessions(last_active);

-- Chat logs table
CREATE TABLE IF NOT EXISTS chat_logs (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    user_id VARCHAR(100),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    model_used VARCHAR(50),
    response_time_ms INTEGER,
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    extra_metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_chat_logs_session_id ON chat_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_logs_created_at ON chat_logs(created_at);

-- Interactions table
CREATE TABLE IF NOT EXISTS interactions (
    id SERIAL PRIMARY KEY,
    drug_name VARCHAR(200) NOT NULL,
    title VARCHAR(300),
    summary TEXT NOT NULL,
    mechanism TEXT,
    food_groups JSONB,
    recommended_actions TEXT,
    evidence_quality VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_interactions_drug_name ON interactions(drug_name);

-- References table
CREATE TABLE IF NOT EXISTS references (
    id SERIAL PRIMARY KEY,
    interaction_id INTEGER REFERENCES interactions(id),
    title VARCHAR(500) NOT NULL,
    url VARCHAR(1000) NOT NULL,
    excerpt TEXT
);

CREATE INDEX IF NOT EXISTS idx_references_interaction_id ON references(interaction_id);

-- API Cache table
CREATE TABLE IF NOT EXISTS api_cache (
    id SERIAL PRIMARY KEY,
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    api_source VARCHAR(50) NOT NULL,
    response_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_api_cache_key ON api_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_api_cache_expires ON api_cache(expires_at);

-- Grant permissions (run if needed)
-- ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE chat_logs ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE interactions ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE references ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE api_cache ENABLE ROW LEVEL SECURITY;

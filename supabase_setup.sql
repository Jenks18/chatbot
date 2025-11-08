-- Setup script for Supabase PostgreSQL database
-- Run this in your Supabase SQL Editor

-- Create chat_logs table with all necessary columns
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
    created_at TIMESTAMP DEFAULT NOW(),
    extra_metadata JSONB
);

-- Add columns if they don't exist (for existing tables)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='chat_logs' AND column_name='ip_address') THEN
        ALTER TABLE chat_logs ADD COLUMN ip_address VARCHAR(50);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='chat_logs' AND column_name='user_agent') THEN
        ALTER TABLE chat_logs ADD COLUMN user_agent TEXT;
    END IF;
END $$;

-- Create sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    user_agent TEXT,
    ip_address VARCHAR(50),
    started_at TIMESTAMP DEFAULT NOW(),
    last_active TIMESTAMP DEFAULT NOW()
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_chat_logs_session_id ON chat_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_logs_created_at ON chat_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_session_id ON sessions(session_id);

-- View for analytics
CREATE OR REPLACE VIEW chat_analytics AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_queries,
    AVG(response_time_ms) as avg_response_time,
    COUNT(DISTINCT session_id) as unique_sessions
FROM chat_logs
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Grant permissions (if needed)
-- GRANT ALL ON chat_logs TO postgres;
-- GRANT ALL ON sessions TO postgres;

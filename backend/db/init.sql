-- Initialize the toxicology GPT database

CREATE TABLE IF NOT EXISTS chat_logs (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    user_id VARCHAR(100),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    model_used VARCHAR(50),
    response_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    extra_metadata JSONB
);

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

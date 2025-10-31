-- Migration to add geolocation and tracking fields
-- Run this to update your existing database

-- Add new columns to chat_logs table
ALTER TABLE chat_logs 
ADD COLUMN IF NOT EXISTS ip_address VARCHAR(50),
ADD COLUMN IF NOT EXISTS user_agent TEXT;

-- Add new columns to sessions table
ALTER TABLE sessions 
ADD COLUMN IF NOT EXISTS country VARCHAR(100),
ADD COLUMN IF NOT EXISTS city VARCHAR(100),
ADD COLUMN IF NOT EXISTS region VARCHAR(100),
ADD COLUMN IF NOT EXISTS timezone VARCHAR(50),
ADD COLUMN IF NOT EXISTS latitude VARCHAR(20),
ADD COLUMN IF NOT EXISTS longitude VARCHAR(20),
ADD COLUMN IF NOT EXISTS extra_metadata JSONB;

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_chat_logs_ip ON chat_logs(ip_address);
CREATE INDEX IF NOT EXISTS idx_sessions_country ON sessions(country);
CREATE INDEX IF NOT EXISTS idx_sessions_city ON sessions(city);

-- Create view for analytics with geolocation
CREATE OR REPLACE VIEW analytics_with_location AS
SELECT 
    cl.id,
    cl.session_id,
    cl.question,
    cl.answer,
    cl.model_used,
    cl.response_time_ms,
    cl.ip_address,
    cl.created_at,
    s.country,
    s.city,
    s.region,
    s.timezone,
    s.latitude,
    s.longitude,
    s.user_agent,
    s.extra_metadata as geo_metadata
FROM chat_logs cl
LEFT JOIN sessions s ON cl.session_id = s.session_id;

COMMENT ON VIEW analytics_with_location IS 'Combines chat logs with geolocation data for analytics';

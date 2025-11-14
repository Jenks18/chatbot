-- Migration: Add user_id to sessions table for Clerk authentication
-- Run this in Supabase SQL Editor: https://supabase.com/dashboard/project/jjlxktwczavrlefueawu/sql

-- Add user_id column to sessions table if it doesn't exist
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS user_id VARCHAR(100);

-- Create index for user_id lookups
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);

-- Verify the change
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'sessions' 
ORDER BY ordinal_position;

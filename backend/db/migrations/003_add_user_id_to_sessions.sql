-- Add user_id column to sessions table to link with Clerk authentication
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS user_id VARCHAR(100);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);

-- Clear all data from chat_logs table (fresh start)
-- Run this in Supabase SQL Editor to delete all conversation data

-- Delete all records from chat_logs
DELETE FROM chat_logs;

-- Optional: Reset the auto-increment ID counter
ALTER SEQUENCE chat_logs_id_seq RESTART WITH 1;

-- Verify the table is empty
SELECT COUNT(*) as remaining_records FROM chat_logs;

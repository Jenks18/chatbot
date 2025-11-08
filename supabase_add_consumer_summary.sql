-- Migration: Add consumer_summary column to chat_logs table
-- This stores the simple/layperson version of AI responses

DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='chat_logs' AND column_name='consumer_summary') THEN
        ALTER TABLE chat_logs ADD COLUMN consumer_summary TEXT;
        COMMENT ON COLUMN chat_logs.consumer_summary IS 'Simple, consumer-friendly version of the AI response';
    END IF;
END $$;

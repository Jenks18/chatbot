# Add Consumer Summary Column - Migration Guide

## Step 1: Run SQL Migration in Supabase

1. Go to your Supabase dashboard: https://zzeycmksnujfdvasxoti.supabase.co
2. Click on "SQL Editor" in the left sidebar
3. Click "New Query"
4. Copy and paste this SQL:

```sql
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
```

5. Click "Run" button
6. You should see "Success. No rows returned."

## Step 2: Deploy Updated Code

The code changes are ready to deploy. They will:
- Save both technical AND simple responses to the database
- Display a toggle button in admin panel to switch between versions
- Show better formatted, more readable responses

## What You'll See

In the admin panel, each message will have:

**📖 Simple** button - Shows the easy-to-understand consumer version
**🔬 Technical** button - Shows the detailed medical/scientific version

Both versions will be beautifully formatted with:
- Color-coded sections (green for simple, purple for technical)
- Clear headings and icons
- Better spacing and readability
- Left border accent for visual hierarchy

## Note

New conversations will have both versions saved. Old conversations (before this update) will only show the technical version since consumer_summary wasn't saved yet.

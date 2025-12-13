#!/usr/bin/env python3
"""
Migration: Add title to sessions table and status/error_message to chat_logs table
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from backend.db.database import engine
from sqlalchemy import text

def run_migration():
    """Add new columns to existing tables"""
    
    with engine.connect() as conn:
        print("🔄 Starting migration...")
        
        # Check if columns exist first
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='sessions' AND column_name='title'
        """))
        
        if not result.fetchone():
            print("📝 Adding 'title' column to sessions table...")
            conn.execute(text("""
                ALTER TABLE sessions 
                ADD COLUMN title VARCHAR(300)
            """))
            conn.commit()
            print("✅ Added 'title' column to sessions")
        else:
            print("ℹ️  'title' column already exists in sessions")
        
        # Check status column in chat_logs
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='chat_logs' AND column_name='status'
        """))
        
        if not result.fetchone():
            print("📝 Adding 'status' column to chat_logs table...")
            conn.execute(text("""
                ALTER TABLE chat_logs 
                ADD COLUMN status VARCHAR(20) DEFAULT 'success'
            """))
            conn.commit()
            print("✅ Added 'status' column to chat_logs")
        else:
            print("ℹ️  'status' column already exists in chat_logs")
        
        # Check error_message column in chat_logs
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='chat_logs' AND column_name='error_message'
        """))
        
        if not result.fetchone():
            print("📝 Adding 'error_message' column to chat_logs table...")
            conn.execute(text("""
                ALTER TABLE chat_logs 
                ADD COLUMN error_message TEXT
            """))
            conn.commit()
            print("✅ Added 'error_message' column to chat_logs")
        else:
            print("ℹ️  'error_message' column already exists in chat_logs")
        
        # Make answer nullable in chat_logs (for failed requests)
        print("📝 Making 'answer' column nullable in chat_logs...")
        conn.execute(text("""
            ALTER TABLE chat_logs 
            ALTER COLUMN answer DROP NOT NULL
        """))
        conn.commit()
        print("✅ Made 'answer' column nullable")
        
        print("\n🎉 Migration completed successfully!")
        print("\nNew features:")
        print("  • Chat titles will be generated from first message")
        print("  • Failed API requests will be tracked with status and error details")
        print("  • Admin dashboard will show readable chat titles")

if __name__ == "__main__":
    try:
        run_migration()
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

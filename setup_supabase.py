#!/usr/bin/env python3
"""
Test and setup Supabase database connection
"""
import psycopg2
from psycopg2 import sql

DATABASE_URL = "postgresql://postgres:Kifag102o25!@db.zzeycmksnujfdvasxoti.supabase.co:5432/postgres"

def main():
    print("🔗 Connecting to Supabase...")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("✅ Connected successfully!")
        
        # Check if tables exist
        print("\n📋 Checking tables...")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cur.fetchall()
        print(f"Found {len(tables)} tables: {[t[0] for t in tables]}")
        
        # Check chat_logs table structure
        print("\n🔍 Checking chat_logs table...")
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'chat_logs'
            ORDER BY ordinal_position
        """)
        columns = cur.fetchall()
        
        if not columns:
            print("⚠️  chat_logs table doesn't exist. Creating it...")
            with open('supabase_setup.sql', 'r') as f:
                setup_sql = f.read()
                cur.execute(setup_sql)
                conn.commit()
            print("✅ Tables created!")
        else:
            print("Columns in chat_logs:")
            for col in columns:
                print(f"  - {col[0]} ({col[1]})")
            
            # Check for required columns
            column_names = [col[0] for col in columns]
            if 'ip_address' not in column_names or 'user_agent' not in column_names:
                print("\n⚠️  Missing columns. Adding them...")
                if 'ip_address' not in column_names:
                    cur.execute("ALTER TABLE chat_logs ADD COLUMN ip_address VARCHAR(50)")
                if 'user_agent' not in column_names:
                    cur.execute("ALTER TABLE chat_logs ADD COLUMN user_agent TEXT")
                conn.commit()
                print("✅ Columns added!")
        
        # Count existing records
        cur.execute("SELECT COUNT(*) FROM chat_logs")
        count = cur.fetchone()[0]
        print(f"\n📊 Total chat logs: {count}")
        
        cur.close()
        conn.close()
        
        print("\n✅ Database is ready!")
        print("\nYour admin page should now show data at:")
        print("https://chatbot-y1ar.vercel.app/admin")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("1. The database URL is correct")
        print("2. The database is accessible")
        print("3. You have the correct permissions")

if __name__ == "__main__":
    main()

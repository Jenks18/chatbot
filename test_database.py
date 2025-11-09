#!/usr/bin/env python3
"""
Test database connection and check for chat logs
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.production')

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def test_database():
    """Test database connection and query chat logs"""
    
    # Get database URL from environment
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL not found in environment")
        return
    
    # Fix postgres:// to postgresql://
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    print(f"🔗 Connecting to database...")
    print(f"   URL: {db_url[:50]}...")
    
    try:
        # Create engine
        engine = create_engine(db_url, pool_pre_ping=True)
        SessionLocal = sessionmaker(bind=engine)
        
        with SessionLocal() as session:
            # Test connection
            result = session.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            
            # Check for tables
            tables_query = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = session.execute(tables_query).fetchall()
            print(f"\n📊 Found {len(tables)} tables:")
            for table in tables:
                print(f"   - {table[0]}")
            
            # Check chat_logs count
            try:
                count_query = text("SELECT COUNT(*) FROM chat_logs")
                count = session.execute(count_query).scalar()
                print(f"\n💬 Chat logs in database: {count}")
                
                if count > 0:
                    # Get recent chat logs
                    recent_query = text("""
                        SELECT session_id, question, created_at 
                        FROM chat_logs 
                        ORDER BY created_at DESC 
                        LIMIT 5
                    """)
                    recent = session.execute(recent_query).fetchall()
                    print("\n📝 Recent chat logs:")
                    for log in recent:
                        print(f"   - Session: {log[0][:20]}... | {log[2]}")
                        print(f"     Question: {log[1][:60]}...")
            except Exception as e:
                print(f"⚠️  Error querying chat_logs: {e}")
            
            # Check sessions count
            try:
                sessions_query = text("SELECT COUNT(*) FROM sessions")
                sessions_count = session.execute(sessions_query).scalar()
                print(f"\n👥 Sessions in database: {sessions_count}")
                
                if sessions_count > 0:
                    # Get recent sessions
                    recent_sessions = text("""
                        SELECT session_id, started_at, country, city
                        FROM sessions 
                        ORDER BY last_active DESC 
                        LIMIT 5
                    """)
                    recent_sess = session.execute(recent_sessions).fetchall()
                    print("\n🌍 Recent sessions:")
                    for sess in recent_sess:
                        location = f"{sess[3]}, {sess[2]}" if sess[3] and sess[2] else "Unknown"
                        print(f"   - {sess[0][:20]}... | {sess[1]} | {location}")
            except Exception as e:
                print(f"⚠️  Error querying sessions: {e}")
                
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database()

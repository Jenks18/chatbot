#!/usr/bin/env python3
"""
Initialize Supabase database tables
"""
import os
os.environ['DATABASE_URL'] = 'postgresql://postgres.zzeycmksnujfdvasxoti:kMOFPkWLvHmRWATc@aws-0-us-west-1.pooler.supabase.com:5432/postgres'

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from db.database import Base
from db.models import ChatLog, Session, Interaction, Reference, APICache

def init_database():
    """Initialize all database tables"""
    
    db_url = os.getenv('DATABASE_URL')
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    print(f"🔗 Connecting to Supabase...")
    print(f"   URL: {db_url[:60]}...")
    
    try:
        engine = create_engine(db_url, pool_pre_ping=True)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful!")
        
        # Create all tables
        print("📊 Creating tables...")
        Base.metadata.create_all(engine)
        print("✅ All tables created successfully!")
        
        # List tables
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = result.fetchall()
            print(f"\n✅ Database initialized with {len(tables)} tables:")
            for table in tables:
                print(f"   - {table[0]}")
        
        print("\n🎉 Database initialization complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)

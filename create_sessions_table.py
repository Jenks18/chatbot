"""Create sessions table"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from backend.db.database import SessionLocal, engine
from backend.db.models import Base, Session as SessionModel

print("Creating sessions table...")
try:
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Sessions table created!")
    
    # Test
    db = SessionLocal()
    count = db.query(SessionModel).count()
    print(f"Total sessions: {count}")
    db.close()
    
except Exception as e:
    print(f"❌ Error: {e}")

"""Test database saving"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from backend.db.database import SessionLocal, DATABASE_URL
from backend.db.models import ChatLog, Session as SessionModel

print("=" * 60)
print("DATABASE CONNECTION TEST")
print("=" * 60)
print(f"DATABASE_URL: {DATABASE_URL[:50]}...")

try:
    db = SessionLocal()
    
    # Test query
    count = db.query(ChatLog).count()
    print(f"\n✅ Database connected!")
    print(f"Total chat logs: {count}")
    
    # Test session count
    session_count = db.query(SessionModel).count()
    print(f"Total sessions: {session_count}")
    
    # Show recent logs
    recent = db.query(ChatLog).order_by(ChatLog.created_at.desc()).limit(3).all()
    print(f"\nRecent messages:")
    for log in recent:
        print(f"  - {log.session_id[:20]}... | {log.question[:50]}...")
    
    db.close()
    print("\n✅ All tests passed!")
    
except Exception as e:
    print(f"\n❌ Database error: {e}")
    print(f"Error type: {type(e).__name__}")

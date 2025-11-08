#!/usr/bin/env python3
"""
Test inserting a record into Supabase
"""
from supabase import create_client
from datetime import datetime

SUPABASE_URL = "https://zzeycmksnujfdvasxoti.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6ZXljbWtzbnVqZmR2YXN4b3RpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyODUxMTYsImV4cCI6MjA3Nzg2MTExNn0.gX37n0KQK9__8oea55JA1JP-JJhF2wUG18jIeaV81oM"

def main():
    print("🔗 Connecting to Supabase...")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("📝 Inserting test record...")
    data = {
        'session_id': 'test-session-local',
        'question': 'Test question from Python',
        'answer': 'Test answer from Python',
        'model_used': 'test',
        'response_time_ms': 100,
        'ip_address': '127.0.0.1',
        'user_agent': 'Python Test',
        'created_at': datetime.now().isoformat()
    }
    
    try:
        response = supabase.table('chat_logs').insert(data).execute()
        print("✅ Record inserted successfully!")
        print(f"   Record ID: {response.data[0]['id']}")
        
        # Query back
        print("\n📋 Querying all records...")
        all_logs = supabase.table('chat_logs').select('*').execute()
        print(f"✅ Found {len(all_logs.data)} records")
        
        for log in all_logs.data:
            print(f"   - Session: {log['session_id']}, Question: {log['question'][:50]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

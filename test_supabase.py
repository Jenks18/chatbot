#!/usr/bin/env python3
"""
Setup Supabase database table using REST API
"""
import os
from supabase import create_client, Client

SUPABASE_URL = "https://zzeycmksnujfdvasxoti.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6ZXljbWtzbnVqZmR2YXN4b3RpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyODUxMTYsImV4cCI6MjA3Nzg2MTExNn0.gX37n0KQK9__8oea55JA1JP-JJhF2wUG18jIeaV81oM"

def main():
    print("🔗 Connecting to Supabase...")
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected successfully!")
        
        # Try to query the chat_logs table
        print("\n📋 Checking chat_logs table...")
        response = supabase.table('chat_logs').select('*').limit(1).execute()
        
        print(f"✅ chat_logs table exists! Found {len(response.data)} records (showing 1)")
        
        # Count total records
        count_response = supabase.table('chat_logs').select('*', count='exact').execute()
        print(f"📊 Total chat logs: {count_response.count}")
        
        print("\n✅ Supabase is ready!")
        print("\nYour admin page should now show data at:")
        print("https://chatbot-y1ar.vercel.app/admin")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n⚠️  The chat_logs table might not exist yet.")
        print("\nTo create it, run this SQL in your Supabase SQL Editor:")
        print("(Go to https://supabase.com/dashboard → Your Project → SQL Editor)")
        print("\n" + "="*60)
        with open('supabase_setup.sql', 'r') as f:
            print(f.read())
        print("="*60)

if __name__ == "__main__":
    main()

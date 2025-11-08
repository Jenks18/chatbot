"""
Chat endpoint for Vercel
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import asyncio
import uuid
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ['VERCEL'] = '1'

# Supabase configuration
SUPABASE_URL = os.environ.get('NEXT_PUBLIC_SUPABASE_URL', 'https://zzeycmksnujfdvasxoti.supabase.co')
SUPABASE_KEY = os.environ.get('NEXT_PUBLIC_SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6ZXljbWtzbnVqZmR2YXN4b3RpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyODUxMTYsImV4cCI6MjA3Nzg2MTExNn0.gX37n0KQK9__8oea55JA1JP-JJhF2wUG18jIeaV81oM')
SUPABASE_REST_URL = f'{SUPABASE_URL}/rest/v1'

def log_to_database(session_id, question, answer, model_used, response_time_ms, ip_address, user_agent, consumer_summary=None):
    """Log chat interaction to Supabase using HTTP"""
    try:
        import httpx
        
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
        
        data = {
            'session_id': session_id,
            'question': question,
            'answer': answer,
            'consumer_summary': consumer_summary,
            'model_used': model_used,
            'response_time_ms': response_time_ms,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'created_at': datetime.now().isoformat()
        }
        
        response = httpx.post(
            f'{SUPABASE_REST_URL}/chat_logs',
            headers=headers,
            json=data,
            timeout=5.0
        )
        print(f"Supabase log status: {response.status_code}")
    except Exception as e:
        print(f"Failed to log to database: {e}")
        pass

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Import services
            from backend.services.model_router import model_service
            
            # Extract request data
            user_message = data.get('message', '')
            session_id = data.get('session_id') or str(uuid.uuid4())
            user_mode = data.get('user_mode', 'patient')
            
            if not user_message:
                raise ValueError("Message is required")
            
            # Generate response using Groq
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            start_time = datetime.now()
            
            # Generate technical response
            ai_response = loop.run_until_complete(
                model_service.generate_response(
                    query=user_message,
                    user_mode=user_mode,
                    max_tokens=2000,
                    temperature=0.7
                )
            )
            
            # Generate simple consumer summary
            consumer_summary = loop.run_until_complete(
                model_service.generate_consumer_summary(
                    technical_info=ai_response,
                    drug_name="",
                    question=user_message
                )
            )
            
            end_time = datetime.now()
            response_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            loop.close()
            
            # Log to database
            ip_address = self.headers.get('X-Forwarded-For', self.client_address[0])
            user_agent = self.headers.get('User-Agent', '')
            log_to_database(session_id, user_message, ai_response, "groq/compound", response_time_ms, ip_address, user_agent, consumer_summary)
            
            # Build response
            response = {
                "answer": ai_response,
                "consumer_summary": consumer_summary,
                "session_id": session_id,
                "model_used": "groq/compound",
                "response_time_ms": response_time_ms,
                "sources": []
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            error_response = {
                "error": str(e),
                "answer": f"Sorry, I encountered an error: {str(e)}",
                "session_id": data.get('session_id', 'error'),
                "model_used": "error",
                "response_time_ms": 0
            }
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

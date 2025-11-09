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
                    max_tokens=1200,  # Reduced to prevent "too large" errors
                    temperature=0.7
                )
            )
            
            # Generate simple consumer summary (mode-aware)
            consumer_summary = loop.run_until_complete(
                model_service.generate_consumer_summary(
                    technical_info=ai_response,
                    drug_name="",
                    question=user_message,
                    user_mode=user_mode  # Pass mode for appropriate summary style
                )
            )
            
            end_time = datetime.now()
            response_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            loop.close()
            
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

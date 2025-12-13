"""
Chat history endpoint for Vercel
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from urllib.parse import urlparse, parse_qs

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ['VERCEL'] = '1'

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Parse URL to get session_id
            parsed_path = urlparse(self.path)
            path_parts = parsed_path.path.split('/')
            
            # Extract session_id from /api/history/{session_id}
            if len(path_parts) >= 4 and path_parts[2] == 'history':
                session_id = path_parts[3]
            else:
                raise ValueError("Invalid path format. Expected /api/history/{session_id}")
            
            # Parse query parameters
            query_params = parse_qs(parsed_path.query)
            limit = int(query_params.get('limit', [100])[0])
            
            # Import database
            from backend.db.database import SessionLocal
            from backend.db.models import ChatLog
            
            db = SessionLocal()
            
            # Query chat history
            logs = db.query(ChatLog).filter(
                ChatLog.session_id == session_id
            ).order_by(ChatLog.created_at).limit(limit).all()
            
            # Format response
            history = [
                {
                    "id": log.id,
                    "session_id": log.session_id,
                    "question": log.question,
                    "answer": log.answer,
                    "model_used": log.model_used,
                    "response_time_ms": log.response_time_ms,
                    "created_at": str(log.created_at),
                    "ip_address": log.ip_address,
                    "user_agent": log.user_agent,
                    "extra_metadata": log.extra_metadata
                }
                for log in logs
            ]
            
            response = {
                "session_id": session_id,
                "history": history,
                "count": len(history)
            }
            
            db.close()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"[ERROR] History endpoint failed: {str(e)}")
            print(f"[ERROR] Traceback: {error_details}")
            
            error_response = {
                "error": str(e),
                "session_id": None,
                "history": []
            }
            self.send_response(500 if "Invalid path" not in str(e) else 400)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

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
        db = None
        try:
            # Parse URL to get session_id
            parsed_path = urlparse(self.path)
            path_parts = parsed_path.path.split('/')
            
            # Extract session_id from /api/history/{session_id}
            if len(path_parts) >= 4 and path_parts[2] == 'history':
                session_id = path_parts[3]
                # Remove query string from session_id if present
                if '?' in session_id:
                    session_id = session_id.split('?')[0]
            else:
                raise ValueError("Invalid path format. Expected /api/history/{session_id}")
            
            if not session_id or session_id == '':
                raise ValueError("Session ID is required")
            
            # Parse query parameters
            query_params = parse_qs(parsed_path.query)
            limit = int(query_params.get('limit', [100])[0])
            
            print(f"[HISTORY] Fetching history for session: {session_id}, limit: {limit}")
            
            # Import database
            from backend.db.database import SessionLocal
            print(f"[HISTORY] Found {len(logs)} chat logs for session {session_id}")
            
            # Format response
            history = []
            for log in logs:
                try:
                    history.append({
                        "id": log.id,
                        "session_id": log.session_id,
                        "question": log.question,
                        "answer": log.answer,
                        "model_used": log.model_used,
                        "response_time_ms": log.response_time_ms,
                        "created_at": str(log.created_at),
                        "ip_address": log.ip_address,
                        "user_agent": log.user_agent,
                        "extra_metadata": log.extra_metadata if log.extra_metadata else {}
                    })
                except Exception as log_error:
                    print(f"[HISTORY WARNING] Failed to serialize log {log.id}: {str(log_error)}")
                    continue
            
            response = {
                "session_id": session_id,
                "history": history,
                "count": len(history)
            }
            
            if db:
                    for log in logs
            ]
            
            response = {
                "session_id": session_id,
                "history": history,
                "count": len(history)
            }
            # Close database connection if it exists
            if db:
                try:
                    db.close()
                except:
                    pass
            
            error_response = {
                "error": str(e),
                "session_id": None,
                "history": [],
                "count": 0
            }
            
            status_code = 400 if "Invalid" in str(e) or "required" in str(e) else 500
            self.send_response(status_code
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

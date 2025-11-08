"""
Admin session history endpoint for Vercel
"""
from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import re

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Extract session_id from URL path
            # Path will be like: /api/admin/sessions/[sessionId]/history
            path_match = re.search(r'/([^/]+)/history', self.path)
            session_id = path_match.group(1) if path_match else None
            
            if not session_id:
                raise ValueError("Session ID not found in path")
            
            # Return empty session data for now (will be populated when DB is connected)
            response = {
                "session_id": session_id,
                "started_at": datetime.utcnow().isoformat(),
                "last_active": datetime.utcnow().isoformat(),
                "user_agent": "Unknown",
                "message_count": 0,
                "messages": []
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            error_response = {
                "error": str(e),
                "message": "Session history endpoint"
            }
            self.send_response(500)
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

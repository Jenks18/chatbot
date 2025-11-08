"""
Minimal test endpoint to verify Python execution on Vercel
"""
from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "ok",
            "message": "Python is working on Vercel!",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.wfile.write(json.dumps(response).encode())
        return

# Vercel expects lowercase 'handler'
handler = Handler


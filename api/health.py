"""
Health check endpoint for Vercel
"""
from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ['VERCEL'] = '1'

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Check if GROQ_API_KEY is configured
            groq_key = os.getenv('GROQ_API_KEY')
            
            if groq_key:
                model_status = "healthy"
            else:
                model_status = "unhealthy: GROQ_API_KEY not configured"
            
            overall_status = "healthy" if model_status == "healthy" else "degraded"
            
            response = {
                "status": overall_status,
                "database": "not_configured (using in-memory)",
                "model_server": model_status,
                "timestamp": datetime.utcnow().isoformat(),
                "message": "API is running"
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            error_response = {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())

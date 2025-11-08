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
            # Try to import and check services
            from backend.services.model_router import model_service
            
            # Check model service
            if not hasattr(model_service, 'api_key') or not model_service.api_key:
                model_status = "unhealthy: GROQ_API_KEY not configured"
            else:
                model_status = "healthy"
            
            response = {
                "status": "degraded" if "unhealthy" in model_status else "healthy",
                "database": "not_configured",
                "model_server": model_status,
                "timestamp": datetime.utcnow().isoformat()
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

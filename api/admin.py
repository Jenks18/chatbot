"""
Consolidated admin endpoint for Vercel - handles all admin routes
Reduces serverless function count by combining all admin endpoints
"""
from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs

# Database connection (if available)
DATABASE_URL = os.environ.get('DATABASE_URL')

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)
            
            # Get route from query parameter
            route = query_params.get('route', [''])[0]
            
            # Route to appropriate handler
            if route == 'logs/recent':
                self.handle_logs_recent(query_params)
            elif route == 'logs':
                self.handle_logs(query_params)
            elif 'sessions/' in route and '/history' in route:
                self.handle_session_history(route, query_params)
            elif route == 'sessions':
                self.handle_sessions(query_params)
            elif route == 'stats/overview':
                self.handle_stats_overview(query_params)
            elif route == 'interactions':
                self.handle_interactions(query_params)
            elif route == 'search':
                self.handle_search(query_params)
            else:
                self.send_error_response(404, f"Admin route '{route}' not found")
                
        except Exception as e:
            self.send_error_response(500, str(e))
    
    def do_POST(self):
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)
            
            # Get route from query parameter
            route = query_params.get('route', [''])[0]
            
            # Route to appropriate handler
            if 'pipeline/fetch-references' in route:
                self.handle_fetch_references(query_params)
            else:
                self.send_error_response(404, f"Admin POST route '{route}' not found")
                
        except Exception as e:
            self.send_error_response(500, str(e))
    
    def handle_logs(self, query_params):
        """Get all logs with pagination"""
        limit = int(query_params.get('limit', ['100'])[0])
        offset = int(query_params.get('offset', ['0'])[0])
        
        # TODO: Query database when DATABASE_URL is set
        response = []
        self.send_json_response(response)
    
    def handle_logs_recent(self, query_params):
        """Get recent logs (last N hours)"""
        hours = int(query_params.get('hours', ['24'])[0])
        limit = int(query_params.get('limit', ['100'])[0])
        
        # TODO: Query database when DATABASE_URL is set
        response = []
        self.send_json_response(response)
    
    def handle_sessions(self, query_params):
        """Get all sessions"""
        limit = int(query_params.get('limit', ['50'])[0])
        
        # TODO: Query database when DATABASE_URL is set
        response = []
        self.send_json_response(response)
    
    def handle_session_history(self, route, query_params):
        """Get history for a specific session"""
        # Extract session ID from route: sessions/{sessionId}/history
        parts = route.split('/')
        session_id = None
        for i, part in enumerate(parts):
            if part == 'sessions' and i + 1 < len(parts):
                session_id = parts[i + 1]
                break
        
        if not session_id:
            self.send_error_response(400, "Session ID required")
            return
        
        # TODO: Query database when DATABASE_URL is set
        response = {
            "session_id": session_id,
            "started_at": datetime.utcnow().isoformat(),
            "last_active": datetime.utcnow().isoformat(),
            "message_count": 0,
            "messages": []
        }
        self.send_json_response(response)
    
    def handle_stats_overview(self, query_params):
        """Get statistics overview"""
        # TODO: Query database when DATABASE_URL is set
        response = {
            "total_queries": 0,
            "unique_sessions": 0,
            "avg_response_time_ms": 0,
            "daily_queries": []
        }
        self.send_json_response(response)
    
    def handle_interactions(self, query_params):
        """Get drug interactions"""
        limit = int(query_params.get('limit', ['100'])[0])
        
        # TODO: Query database when DATABASE_URL is set
        response = []
        self.send_json_response(response)
    
    def handle_search(self, query_params):
        """Search logs"""
        query = query_params.get('query', [''])[0]
        limit = int(query_params.get('limit', ['50'])[0])
        
        # TODO: Query database when DATABASE_URL is set
        response = []
        self.send_json_response(response)
    
    def handle_fetch_references(self, query_params):
        """Run fetch references pipeline"""
        limit = int(query_params.get('limit', ['100'])[0])
        
        # TODO: Implement pipeline when DATABASE_URL is set
        response = {
            "status": "completed",
            "processed": 0,
            "message": "Pipeline not yet implemented"
        }
        self.send_json_response(response)
    
    def send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_error_response(self, status_code, message):
        """Send error response"""
        error_response = {
            "error": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

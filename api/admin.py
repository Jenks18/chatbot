"""
Consolidated admin endpoint for Vercel - handles all admin routes
Reduces serverless function count by combining all admin endpoints
"""
from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
import httpx

# Supabase configuration
SUPABASE_URL = os.environ.get('NEXT_PUBLIC_SUPABASE_URL', 'https://zzeycmksnujfdvasxoti.supabase.co')
SUPABASE_KEY = os.environ.get('NEXT_PUBLIC_SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6ZXljbWtzbnVqZmR2YXN4b3RpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyODUxMTYsImV4cCI6MjA3Nzg2MTExNn0.gX37n0KQK9__8oea55JA1JP-JJhF2wUG18jIeaV81oM')
SUPABASE_REST_URL = f'{SUPABASE_URL}/rest/v1'

def query_supabase(table, select='*', order_by=None, limit=None, offset=None):
    """Query Supabase using REST API"""
    try:
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json'
        }
        
        url = f'{SUPABASE_REST_URL}/{table}?select={select}'
        if order_by:
            url += f'&order={order_by}'
        if limit:
            url += f'&limit={limit}'
        if offset:
            url += f'&offset={offset}'
        
        response = httpx.get(url, headers=headers, timeout=10.0)
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        print(f"Supabase query error: {e}")
        return []

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
        
        logs = query_supabase('chat_logs', select='*', order_by='created_at.desc', limit=limit, offset=offset)
        self.send_json_response(logs)
    
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
        
        logs = query_supabase('chat_logs', select='session_id,created_at,user_agent,ip_address', order_by='created_at.desc')
        
        # Group by session_id
        sessions_dict = {}
        for log in logs:
            sid = log['session_id']
            if sid not in sessions_dict:
                sessions_dict[sid] = {
                    'session_id': sid,
                    'started_at': log['created_at'],
                    'last_active': log['created_at'],
                    'message_count': 0,
                    'user_agent': log.get('user_agent', ''),
                    'ip_address': log.get('ip_address', '')
                }
            sessions_dict[sid]['message_count'] += 1
            # Update last_active if this is more recent
            if log['created_at'] > sessions_dict[sid]['last_active']:
                sessions_dict[sid]['last_active'] = log['created_at']
            # Update started_at if this is earlier
            if log['created_at'] < sessions_dict[sid]['started_at']:
                sessions_dict[sid]['started_at'] = log['created_at']
        
        # Convert to list and sort by last_active
        sessions = list(sessions_dict.values())
        sessions.sort(key=lambda x: x['last_active'], reverse=True)
        
        self.send_json_response(sessions[:limit])
    
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
        logs = query_supabase('chat_logs', select='session_id,created_at,response_time_ms')
        
        if not logs:
            self.send_json_response({
                "total_queries": 0,
                "unique_sessions": 0,
                "avg_response_time_ms": 0,
                "daily_queries": []
            })
            return
        
        # Calculate stats
        total_queries = len(logs)
        unique_sessions = len(set(log['session_id'] for log in logs))
        
        # Calculate average response time
        response_times = [log.get('response_time_ms', 0) for log in logs if log.get('response_time_ms')]
        avg_response_time = int(sum(response_times) / len(response_times)) if response_times else 0
        
        # Calculate daily queries for last 7 days
        daily_dict = {}
        for log in logs:
            date_str = log['created_at'][:10]  # Extract YYYY-MM-DD
            daily_dict[date_str] = daily_dict.get(date_str, 0) + 1
        
        daily_queries = [
            {"date": date, "count": count}
            for date, count in sorted(daily_dict.items(), reverse=True)[:7]
        ]
        
        response_data = {
            "total_queries": total_queries,
            "unique_sessions": unique_sessions,
            "avg_response_time_ms": avg_response_time,
            "daily_queries": daily_queries
        }
        
        self.send_json_response(response_data)
    
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

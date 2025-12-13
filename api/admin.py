"""
Admin API endpoints for Vercel serverless deployment
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ['VERCEL'] = '1'

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            parsed_path = urlparse(self.path)
            path_parts = parsed_path.path.split('/')
            query_params = parse_qs(parsed_path.query)
            
            # Import database
            from backend.db.database import SessionLocal
            from backend.db.models import ChatLog, Session as SessionModel, Interaction
            from sqlalchemy import func, desc, text
            
            db = SessionLocal()
            
            # Route based on path
            if '/api/admin/health' in self.path:
                # Health check
                try:
                    db.execute(text("SELECT 1"))
                    db_status = "connected"
                except Exception as e:
                    db_status = f"error: {str(e)}"
                
                response = {
                    "status": "ok",
                    "database": db_status
                }
            
            elif '/api/admin/logs' in self.path:
                # Get chat logs
                limit = int(query_params.get('limit', [100])[0])
                offset = int(query_params.get('offset', [0])[0])
                
                logs = db.query(ChatLog).order_by(desc(ChatLog.created_at)).offset(offset).limit(limit).all()
                response = [
                    {
                        "id": log.id,
                        "session_id": log.session_id,
                        "question": log.question,
                        "answer": log.answer,
                        "model_used": log.model_used,
                        "response_time_ms": log.response_time_ms,
                        "created_at": str(log.created_at),
                        "ip_address": log.ip_address,
                        "user_agent": log.user_agent
                    }
                    for log in logs
                ]
            
            elif '/api/admin/stats/overview' in self.path:
                # Get overview statistics
                total_queries = db.query(func.count(ChatLog.id)).scalar() or 0
                unique_sessions = db.query(func.count(func.distinct(ChatLog.session_id))).scalar() or 0
                avg_response_time = db.query(func.avg(ChatLog.response_time_ms)).scalar()
                
                # Convert Decimal to float for JSON serialization
                avg_response_time = float(avg_response_time) if avg_response_time else 0.0
                
                week_ago = datetime.utcnow() - timedelta(days=7)
                daily_queries = db.query(
                    func.date(ChatLog.created_at).label('date'),
                    func.count(ChatLog.id).label('count')
                ).filter(ChatLog.created_at >= week_ago).group_by(func.date(ChatLog.created_at)).all()
                
                response = {
                    "total_queries": int(total_queries),
                    "unique_sessions": int(unique_sessions),
                    "avg_response_time_ms": round(avg_response_time, 2),
                    "daily_queries": [{"date": str(date), "count": int(count)} for date, count in daily_queries]
                }
            
            elif '/api/admin/sessions/' in self.path and '/history' in self.path:
                # Get session history - /api/admin/sessions/{session_id}/history
                path_parts = [p for p in parsed_path.path.split('/') if p]
                
                if len(path_parts) < 4:
                    response = {"error": "Invalid path format. Expected /api/admin/sessions/{session_id}/history"}
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode())
                    db.close()
                    return
                
                # Extract session_id (should be at index 3)
                session_id_index = path_parts.index('sessions') + 1
                session_id = path_parts[session_id_index] if session_id_index < len(path_parts) else None
                
                if not session_id:
                    response = {"error": "Session ID not provided"}
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode())
                    db.close()
                    return
                
                # Get session info
                session = db.query(SessionModel).filter(
                    SessionModel.session_id == session_id
                ).first()
                
                if not session:
                    response = {
                        "error": "Session not found",
                        "session_id": session_id,
                        "messages": []
                    }
                    self.send_response(404)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode())
                    db.close()
                    return
                
                # Get all messages for this session
                messages = db.query(ChatLog).filter(
                    ChatLog.session_id == session_id
                ).order_by(ChatLog.created_at).all()
                
                response = {
                    "session_id": session.session_id,
                    "started_at": str(session.started_at),
                    "last_active": str(session.last_active),
                    "user_agent": session.user_agent or "",
                    "country": session.country,
                    "city": session.city,
                    "region": session.region,
                    "timezone": session.timezone,
                    "latitude": session.latitude,
                    "longitude": session.longitude,
                    "message_count": len(messages),
                    "messages": [
                        {
                            "id": msg.id,
                            "question": msg.question,
                            "answer": msg.answer,
                            "created_at": str(msg.created_at),
                            "response_time_ms": msg.response_time_ms or 0,
                            "model_used": msg.model_used or "unknown",
                            "ip_address": msg.ip_address or ""
                        }
                        for msg in messages
                    ]
                }
            
            elif '/api/admin/sessions' in self.path:
                # Get all sessions (must come AFTER the history check)
                limit = int(query_params.get('limit', [100])[0])
                
                # Query only columns that exist in database (user_id may not exist yet)
                try:
                    sessions = db.query(
                        SessionModel.id,
                        SessionModel.session_id,
                        SessionModel.user_agent,
                        SessionModel.ip_address,
                        SessionModel.country,
                        SessionModel.city,
                        SessionModel.region,
                        SessionModel.timezone,
                        SessionModel.latitude,
                        SessionModel.longitude,
                        SessionModel.started_at,
                        SessionModel.last_active
                    ).order_by(desc(SessionModel.last_active)).limit(limit).all()
                except Exception as e:
                    # Fallback: try with raw SQL if model has issues
                    sessions = db.execute(
                        text("SELECT id, session_id, user_agent, ip_address, country, city, region, timezone, latitude, longitude, started_at, last_active FROM sessions ORDER BY last_active DESC LIMIT :limit"),
                        {"limit": limit}
                    ).fetchall()
                
                result = []
                for session in sessions:
                    # Handle both ORM objects and tuples from raw SQL
                    session_id = session.session_id if hasattr(session, 'session_id') else session[1]
                    
                    message_count = db.query(func.count(ChatLog.id)).filter(
                        ChatLog.session_id == session_id
                    ).scalar() or 0
                    
                    first_message = db.query(ChatLog).filter(
                        ChatLog.session_id == session_id
                    ).order_by(ChatLog.created_at).first()
                    
                    result.append({
                        "session_id": session_id,
                        "started_at": str(session.started_at if hasattr(session, 'started_at') else session[11]),
                        "last_active": str(session.last_active if hasattr(session, 'last_active') else session[12]),
                        "message_count": message_count,
                        "user_agent": (session.user_agent if hasattr(session, 'user_agent') else session[2]) or "",
                        "country": session.country if hasattr(session, 'country') else session[4],
                        "city": session.city if hasattr(session, 'city') else session[5],
                        "first_message_preview": first_message.question[:100] if first_message else None
                    })
                
                response = result
            
            elif '/api/admin/interactions' in self.path:
                # Get interactions
                limit = int(query_params.get('limit', [100])[0])
                
                interactions = db.query(Interaction).limit(limit).all()
                response = [
                    {
                        "id": i.id,
                        "drug_name": i.drug_name,
                        "title": i.title,
                        "summary": i.summary,
                        "mechanism": i.mechanism,
                        "food_groups": i.food_groups,
                        "recommended_actions": i.recommended_actions,
                        "evidence_quality": i.evidence_quality
                    }
                    for i in interactions
                ]
            
            else:
                response = {"error": "Unknown endpoint"}
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                db.close()
                return
            
            db.close()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            error_response = {
                "error": str(e),
                "type": type(e).__name__
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


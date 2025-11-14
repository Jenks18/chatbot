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
            user_id = data.get('user_id')  # Get Clerk user ID
            
            if not user_message:
                raise ValueError("Message is required")
            
            # Get conversation history for context
            conversation_history = []
            try:
                from backend.db.database import SessionLocal
                from backend.db.models import ChatLog
                
                db = SessionLocal()
                
                # Fetch last 10 messages from this session for context
                previous_messages = db.query(ChatLog).filter(
                    ChatLog.session_id == session_id
                ).order_by(ChatLog.created_at.desc()).limit(10).all()
                
                # Reverse to get chronological order
                previous_messages = list(reversed(previous_messages))
                
                # Build conversation history
                for msg in previous_messages:
                    conversation_history.append({
                        "role": "user",
                        "content": msg.question
                    })
                    conversation_history.append({
                        "role": "assistant",
                        "content": msg.answer
                    })
                
                db.close()
            except Exception as hist_error:
                print(f"Error loading history: {hist_error}")
                # Continue without history if there's an error
            
            # Generate response using Groq with persona-based prompts
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            start_time = datetime.now()
            
            # Generate persona-specific response with conversation history
            ai_response = loop.run_until_complete(
                model_service.generate_response(
                    query=user_message,
                    user_mode=user_mode,
                    max_tokens=1200,  # Reduced to prevent "too large" errors
                    temperature=0.7,
                    conversation_history=conversation_history  # Pass history for context
                )
            )
            
            # No consumer_summary needed - using three-tier persona system
            
            end_time = datetime.now()
            response_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            loop.close()
            
            # Save to database
            db = None
            try:
                from backend.db.database import SessionLocal
                from backend.db.models import ChatLog, Session as SessionModel
                from backend.services.geo_service import geo_service
                
                print(f"[SAVE] Attempting to save chat to database for session: {session_id}")
                db = SessionLocal()
                print(f"[SAVE] Database connection established")
                
                # Get client IP
                client_ip = self.headers.get('X-Forwarded-For', '').split(',')[0].strip() or \
                           self.headers.get('X-Real-IP', '') or \
                           self.client_address[0]
                
                user_agent = self.headers.get('User-Agent', 'unknown')
                print(f"[SAVE] Client IP: {client_ip}, User Agent: {user_agent[:50]}")
                
                # Skip geolocation for now - causes async issues
                geo_data = None
                
                # Create or update session with location data
                existing_session = db.query(SessionModel).filter(
                    SessionModel.session_id == session_id
                ).first()
                
                if not existing_session:
                    new_session = SessionModel(
                        session_id=session_id,
                        user_agent=user_agent,
                        ip_address=client_ip,
                        city=geo_data.get("city") if geo_data else None,
                        region=geo_data.get("region") if geo_data else None,
                        country=geo_data.get("country") if geo_data else None,
                        latitude=geo_data.get("lat") if geo_data else None,
                        longitude=geo_data.get("lon") if geo_data else None
                    )
                    db.add(new_session)
                else:
                    # Update last_active and location data if not already set
                    from sqlalchemy import func
                    existing_session.last_active = func.now()
                    if geo_data and not existing_session.city:
                        existing_session.city = geo_data.get("city")
                        existing_session.region = geo_data.get("region")
                        existing_session.country = geo_data.get("country")
                        existing_session.latitude = geo_data.get("lat")
                        existing_session.longitude = geo_data.get("lon")
                
                # Save chat log
                # Extract references from response
                import re
                references = []
                refs_match = re.search(r'References?:\s*\n([\s\S]+)$', ai_response, re.IGNORECASE)
                if refs_match:
                    refs_text = refs_match.group(1)
                    for line in refs_text.split('\n'):
                        ref_match = re.match(r'^\[(\d+)\]\s*(.+)$', line.strip())
                        if ref_match:
                            references.append({
                                "number": int(ref_match.group(1)),
                                "citation": ref_match.group(2).strip()
                            })
                
                chat_log = ChatLog(
                    session_id=session_id,
                    user_id=user_id,  # Store Clerk user ID
                    question=user_message,
                    answer=ai_response,
                    model_used="groq/compound+free-apis",
                    response_time_ms=response_time_ms,
                    ip_address=client_ip,
                    user_agent=user_agent,
                    extra_metadata={
                        "user_mode": user_mode,
                        "references": references,
                        "geolocation": {
                            "city": geo_data.get("city") if geo_data else None,
                            "region": geo_data.get("region") if geo_data else None,
                            "country": geo_data.get("country") if geo_data else None,
                            "timezone": geo_data.get("timezone") if geo_data else None,
                            "isp": geo_data.get("isp") if geo_data else None
                        } if geo_data else None
                    }
                )
                print(f"[SAVE] ChatLog object created, adding to session")
                db.add(chat_log)
                db.flush()  # Flush to assign ID
                print(f"[SAVE] Flushed, now committing to database")
                db.commit()
                print(f"[SAVE] ✅ Successfully saved chat log ID {chat_log.id} for session {session_id}")
                db.close()
            except Exception as db_error:
                print(f"[SAVE ERROR] Database save failed: {db_error}")
                print(f"[SAVE ERROR] Error type: {type(db_error).__name__}")
                import traceback
                print(f"[SAVE ERROR] Traceback: {traceback.format_exc()}")
                if db:
                    db.rollback()
                    db.close()
                # Continue even if database fails
            
            # Build response
            response = {
                "answer": ai_response,
                "consumer_summary": None,  # No longer using dual-view system
                "session_id": session_id,
                "model_used": "groq/compound+free-apis",
                "response_time_ms": response_time_ms,
                "sources": [],
                "evidence": None,
                "provenance": None
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

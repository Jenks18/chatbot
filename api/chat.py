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
            
            # Get conversation history from request (frontend sends it)
            conversation_history = data.get('conversation_history', [])
            print(f"[MEMORY] Received {len(conversation_history)} messages from frontend")
            
            # Validate and clean conversation history
            if conversation_history:
                # Keep only last 20 messages to avoid token limits
                conversation_history = conversation_history[-20:]
                print(f"[MEMORY] Using {len(conversation_history)} messages for AI context")
            
            # Generate response using Groq with persona-based prompts
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            start_time = datetime.now()
            
            # Generate persona-specific response with conversation history
            # Mode-specific token allocation (reduced to prevent timeouts)
            token_limits = {
                'patient': 1400,
                'doctor': 1500,
                'researcher': 1600
            }
            max_tokens = token_limits.get(user_mode, 1400)
            
            # Track if this is the first message in a session
            is_first_message = len(conversation_history) == 0
            
            # Variables for tracking request status
            ai_response = None
            request_status = 'success'
            error_details = None
            
            try:
                ai_response = loop.run_until_complete(
                    model_service.generate_response(
                        query=user_message,
                        user_mode=user_mode,
                        max_tokens=max_tokens,
                        temperature=0.7,
                        conversation_history=conversation_history  # Pass history for context
                    )
                )
            except Exception as ai_error:
                # Track the error but we'll still save to database
                error_str = str(ai_error)
                if '429' in error_str or 'rate limit' in error_str.lower():
                    request_status = 'rate_limited'
                    ai_response = "Sorry, I've reached my rate limit. Please try again in a moment."
                else:
                    request_status = 'error'
                    ai_response = f"Sorry, I encountered an error: {error_str}"
                error_details = error_str
                print(f"[AI ERROR] {request_status}: {error_str}")
            
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
                from sqlalchemy import text
                
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
                # Query only existing columns (user_id may not exist)
                try:
                    existing_session = db.execute(
                        text("SELECT id, session_id FROM sessions WHERE session_id = :sid LIMIT 1"),
                        {"sid": session_id}
                    ).fetchone()
                except Exception as query_err:
                    print(f"[SAVE] Session query failed: {query_err}")
                    existing_session = None
                
                # Generate title for new sessions from first message
                chat_title = None
                if not existing_session and is_first_message:
                    # Generate a short title from the question
                    chat_title = user_message[:50].strip()
                    if len(user_message) > 50:
                        # Find last complete word
                        last_space = chat_title.rfind(' ')
                        if last_space > 20:  # Keep at least 20 chars
                            chat_title = chat_title[:last_space]
                        chat_title += "..."
                    print(f"[SAVE] Generated title for new session: {chat_title}")
                
                if not existing_session:
                    new_session = SessionModel(
                        session_id=session_id,
                        title=chat_title,
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
                    # Note: existing_session is a Row object from raw SQL, not ORM object
                    # We need to update using raw SQL
                    db.execute(
                        text("UPDATE sessions SET last_active = NOW() WHERE session_id = :sid"),
                        {"sid": session_id}
                    )
                
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
                    status=request_status,  # success, rate_limited, error
                    error_message=error_details,  # Error details if failed
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
            import traceback
            error_details = traceback.format_exc()
            print(f"[ERROR] Chat endpoint failed: {str(e)}")
            print(f"[ERROR] Traceback: {error_details}")
            
            error_response = {
                "error": str(e),
                "answer": f"Sorry, I encountered an error: {str(e)}",
                "session_id": data.get('session_id', 'error') if 'data' in locals() else 'error',
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

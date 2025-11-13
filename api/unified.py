"""
Unified API handler for Vercel serverless functions
Consolidates all endpoints into a single function to stay within Hobby plan limits
"""
from fastapi import FastAPI, Request, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.db.database import get_db, engine, Base
from backend.db.models import ChatLog, Session as SessionModel, Interaction
from backend.schemas import ChatMessage, ChatResponse, ChatLogResponse
from backend.services.model_router import model_service
from backend.services.log_service import log_service
from backend.services.geo_service import geo_service
from backend.services.interaction_service import interaction_service, build_consumer_summary_from_evidence
from backend.services.data_aggregator_service import DrugDataAggregator, extract_drug_names
from backend.scripts.fetch_references import fetch_references_for_interactions
from sqlalchemy import func, desc
import uuid
import time
import json

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Kandih ToxWiki API", version="2.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        from backend.db.database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "database": db_status,
        "model_server": "deepseek" if model_service.enabled else "disabled",
        "timestamp": time.time()
    }

# ============================================================================
# CHAT ENDPOINTS
# ============================================================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(message: ChatMessage, request: Request, db: Session = Depends(get_db)):
    """Main chat endpoint - processes user questions and returns AI responses"""
    session_id = message.session_id or str(uuid.uuid4())
    user_agent = request.headers.get("user-agent", "unknown")
    client_ip = request.client.host if request.client else "unknown"
    geo_data = await geo_service.get_location_data(client_ip)
    
    log_service.create_or_update_session(db, session_id, user_agent, client_ip, geo_data=geo_data)
    start_time = time.time()
    
    try:
        user_mode = getattr(message, 'user_mode', 'patient') or 'patient'
        aggregator = DrugDataAggregator(db)
        drug_names = extract_drug_names(message.message)
        
        external_context = None
        if drug_names:
            drugs_data = await aggregator.get_multiple_drugs_data(drug_names)
            context_parts = []
            for drug_data in drugs_data:
                if isinstance(drug_data, dict) and not drug_data.get("error"):
                    context_parts.append(f"""
Drug: {drug_data.get('drug_name', 'Unknown')}
Identifiers: {json.dumps(drug_data.get('identifiers', {}), indent=2)}
FDA Label Info: {json.dumps(drug_data.get('fda_label', {}), indent=2)}
Chemical Data: {json.dumps(drug_data.get('chemical_data', {}), indent=2)}
Known Interactions: {json.dumps(drug_data.get('interactions', []), indent=2)}
Adverse Events: {json.dumps(drug_data.get('adverse_events', [])[:10], indent=2)}
Literature: {json.dumps(drug_data.get('literature', []), indent=2)}
""")
            if context_parts:
                external_context = "\n\n=== COMPREHENSIVE DRUG DATABASE ===\n" + "\n---\n".join(context_parts)
        
        answer = await model_service.generate_response(
            question=message.message,
            context=external_context,
            user_mode=user_mode
        )

        if not answer or not answer.strip():
            raise RuntimeError("model-unavailable")
        
        response_time_ms = int((time.time() - start_time) * 1000)
        metadata = {"geo_data": geo_data}
        
        evidence = interaction_service.search_interactions_in_text(db, message.message)
        evidence_serializable = []
        for e in evidence:
            refs = [{"id": r.id, "title": r.title, "url": r.url, "excerpt": r.excerpt} 
                   for r in getattr(e, 'references', []) or []]
            evidence_serializable.append({
                "id": e.id, "drug_name": e.drug_name, "title": e.title,
                "summary": e.summary, "mechanism": e.mechanism,
                "food_groups": e.food_groups, "recommended_actions": e.recommended_actions,
                "evidence_quality": e.evidence_quality, "references": refs
            })
        
        metadata["evidence"] = evidence_serializable
        
        log_service.create_chat_log(
            db=db, session_id=session_id, question=message.message,
            answer=answer, model_used=model_service.model_name,
            response_time_ms=response_time_ms, ip_address=client_ip,
            user_agent=user_agent, extra_metadata=metadata
        )
        
        return ChatResponse(
            answer=answer, session_id=session_id,
            model_used=model_service.model_name,
            response_time_ms=response_time_ms,
            consumer_summary=None,  # No longer using dual-view system
            sources=None, evidence=evidence_serializable,
            provenance=None
        )
        
    except Exception as e:
        response_time_ms = int((time.time() - start_time) * 1000)
        error_msg = str(e)
        
        fallback_parts = []
        if 'evidence_serializable' in locals() and evidence_serializable:
            for ev in evidence_serializable:
                part = f"{ev.get('title') or ev.get('drug_name')}: {ev.get('summary')}"
                if ev.get('recommended_actions'):
                    part += f" Recommendation: {ev.get('recommended_actions')}"
                fallback_parts.append(part)
        
        answer = "\n\n".join(fallback_parts) if fallback_parts else \
                "I can't reach the AI model right now. Please try again later."
        
        metadata = {"error": error_msg}
        log_service.create_chat_log(
            db=db, session_id=session_id, question=message.message,
            answer=answer, model_used="fallback", response_time_ms=response_time_ms,
            ip_address=client_ip, user_agent=user_agent, extra_metadata=metadata
        )
        
        return ChatResponse(
            answer=answer, session_id=session_id,
            model_used="fallback", response_time_ms=response_time_ms,
            consumer_summary=None,  # No longer using dual-view system
            sources=None,
            evidence=evidence_serializable if 'evidence_serializable' in locals() else None,
            provenance=None
        )

@app.get("/api/history/{session_id}")
async def get_chat_history(session_id: str, limit: int = 50, db: Session = Depends(get_db)):
    """Retrieve chat history for a specific session"""
    logs = log_service.get_chat_logs(db, session_id=session_id, limit=limit)
    return {"session_id": session_id, "history": logs}

@app.get("/api/session/{session_id}/stats")
async def get_session_stats(session_id: str, db: Session = Depends(get_db)):
    """Get statistics for a specific session"""
    return log_service.get_session_stats(db, session_id)

# ============================================================================
# ADMIN ENDPOINTS (Consolidated)
# ============================================================================

@app.get("/api/admin/logs", response_model=List[ChatLogResponse])
async def get_all_logs(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get all chat logs with pagination"""
    logs = db.query(ChatLog).order_by(desc(ChatLog.created_at)).offset(offset).limit(limit).all()
    return logs

@app.get("/api/admin/stats/overview")
async def get_stats_overview(db: Session = Depends(get_db)):
    """Get overview statistics"""
    from datetime import datetime, timedelta
    
    total_queries = db.query(func.count(ChatLog.id)).scalar()
    unique_sessions = db.query(func.count(func.distinct(ChatLog.session_id))).scalar()
    avg_response_time = db.query(func.avg(ChatLog.response_time_ms)).scalar()
    
    week_ago = datetime.utcnow() - timedelta(days=7)
    daily_queries = db.query(
        func.date(ChatLog.created_at).label('date'),
        func.count(ChatLog.id).label('count')
    ).filter(ChatLog.created_at >= week_ago).group_by(func.date(ChatLog.created_at)).all()
    
    return {
        "total_queries": total_queries,
        "unique_sessions": unique_sessions,
        "avg_response_time_ms": round(avg_response_time, 2) if avg_response_time else 0,
        "daily_queries": [{"date": str(date), "count": count} for date, count in daily_queries]
    }

@app.get("/api/admin/sessions")
async def get_all_sessions(limit: int = Query(50, ge=1, le=500), db: Session = Depends(get_db)):
    """Get all sessions with message counts and metadata"""
    sessions = db.query(SessionModel).order_by(desc(SessionModel.last_active)).limit(limit).all()
    
    result = []
    for session in sessions:
        message_count = db.query(func.count(ChatLog.id)).filter(
            ChatLog.session_id == session.session_id
        ).scalar()
        
        first_message = db.query(ChatLog).filter(
            ChatLog.session_id == session.session_id
        ).order_by(ChatLog.created_at).first()
        
        result.append({
            "session_id": session.session_id,
            "started_at": session.started_at,
            "last_active": session.last_active,
            "message_count": message_count,
            "user_agent": session.user_agent,
            "country": session.country,
            "city": session.city,
            "first_message_preview": first_message.question[:100] if first_message else None
        })
    
    return result

@app.get("/api/admin/sessions/{session_id}/history")
async def get_session_history(session_id: str, db: Session = Depends(get_db)):
    """Get full conversation history for a specific session"""
    session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
    
    if not session:
        return {"error": "Session not found"}
    
    messages = db.query(ChatLog).filter(
        ChatLog.session_id == session_id
    ).order_by(ChatLog.created_at).all()
    
    return {
        "session_id": session.session_id,
        "started_at": session.started_at,
        "last_active": session.last_active,
        "user_agent": session.user_agent,
        "country": session.country,
        "city": session.city,
        "message_count": len(messages),
        "messages": [
            {
                "id": msg.id, "question": msg.question, "answer": msg.answer,
                "created_at": msg.created_at, "response_time_ms": msg.response_time_ms,
                "model_used": msg.model_used, "ip_address": msg.ip_address
            }
            for msg in messages
        ]
    }

@app.get("/api/admin/interactions")
async def list_interactions(limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    """List stored interactions with references"""
    inters = db.query(Interaction).limit(limit).all()
    result = []
    for i in inters:
        refs = [{"id": r.id, "title": r.title, "url": r.url, "excerpt": r.excerpt}
               for r in getattr(i, 'references', []) or []]
        result.append({
            "id": i.id, "drug_name": i.drug_name, "title": i.title,
            "summary": i.summary, "mechanism": i.mechanism,
            "food_groups": i.food_groups, "recommended_actions": i.recommended_actions,
            "evidence_quality": i.evidence_quality, "references": refs
        })
    return result

# Export for Vercel
handler = app

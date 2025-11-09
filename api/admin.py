"""
Admin API endpoints for Vercel serverless deployment
"""
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.db.database import get_db, engine, Base
from backend.db.models import ChatLog, Session as SessionModel, Interaction
from backend.schemas import ChatLogResponse

# Initialize database
Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/admin/logs")
async def get_all_logs(limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0)):
    """Get all chat logs with pagination"""
    try:
        db = next(get_db())
        logs = db.query(ChatLog).order_by(desc(ChatLog.created_at)).offset(offset).limit(limit).all()
        result = [
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
        db.close()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/admin/stats/overview")
async def get_stats_overview():
    """Get overview statistics"""
    try:
        from datetime import datetime, timedelta
        db = next(get_db())
        
        total_queries = db.query(func.count(ChatLog.id)).scalar() or 0
        unique_sessions = db.query(func.count(func.distinct(ChatLog.session_id))).scalar() or 0
        avg_response_time = db.query(func.avg(ChatLog.response_time_ms)).scalar() or 0
        
        week_ago = datetime.utcnow() - timedelta(days=7)
        daily_queries = db.query(
            func.date(ChatLog.created_at).label('date'),
            func.count(ChatLog.id).label('count')
        ).filter(ChatLog.created_at >= week_ago).group_by(func.date(ChatLog.created_at)).all()
        
        result = {
            "total_queries": total_queries,
            "unique_sessions": unique_sessions,
            "avg_response_time_ms": round(avg_response_time, 2),
            "daily_queries": [{"date": str(date), "count": count} for date, count in daily_queries]
        }
        db.close()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/admin/sessions")
async def get_all_sessions(limit: int = Query(100, ge=1, le=500)):
    """Get all sessions with message counts"""
    try:
        db = next(get_db())
        
        # Get sessions
        sessions = db.query(SessionModel).order_by(desc(SessionModel.last_active)).limit(limit).all()
        
        result = []
        for session in sessions:
            message_count = db.query(func.count(ChatLog.id)).filter(
                ChatLog.session_id == session.session_id
            ).scalar() or 0
            
            first_message = db.query(ChatLog).filter(
                ChatLog.session_id == session.session_id
            ).order_by(ChatLog.created_at).first()
            
            result.append({
                "session_id": session.session_id,
                "started_at": str(session.started_at),
                "last_active": str(session.last_active),
                "message_count": message_count,
                "user_agent": session.user_agent or "",
                "country": session.country,
                "city": session.city,
                "first_message_preview": first_message.question[:100] if first_message else None
            })
        
        db.close()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/admin/sessions/{session_id}/history")
async def get_session_history(session_id: str):
    """Get full conversation history for a session"""
    try:
        db = next(get_db())
        
        session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
        
        if not session:
            db.close()
            raise HTTPException(status_code=404, detail="Session not found")
        
        messages = db.query(ChatLog).filter(
            ChatLog.session_id == session_id
        ).order_by(ChatLog.created_at).all()
        
        result = {
            "session_id": session.session_id,
            "started_at": str(session.started_at),
            "last_active": str(session.last_active),
            "user_agent": session.user_agent,
            "country": session.country,
            "city": session.city,
            "message_count": len(messages),
            "messages": [
                {
                    "id": msg.id,
                    "question": msg.question,
                    "answer": msg.answer,
                    "created_at": str(msg.created_at),
                    "response_time_ms": msg.response_time_ms,
                    "model_used": msg.model_used,
                    "ip_address": msg.ip_address
                }
                for msg in messages
            ]
        }
        db.close()
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/admin/interactions")
async def list_interactions(limit: int = Query(100, ge=1, le=1000)):
    """List stored interactions"""
    try:
        db = next(get_db())
        interactions = db.query(Interaction).limit(limit).all()
        result = [
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
        db.close()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Export handler for Vercel
handler = app

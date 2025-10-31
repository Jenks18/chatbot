from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from db.database import get_db
from db.models import ChatLog, Session as SessionModel
from typing import List
from schemas import ChatLogResponse

router = APIRouter()

@router.get("/logs", response_model=List[ChatLogResponse])
async def get_all_logs(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get all chat logs with pagination
    """
    logs = db.query(ChatLog).order_by(
        desc(ChatLog.created_at)
    ).offset(offset).limit(limit).all()
    
    return logs

@router.get("/logs/recent")
async def get_recent_logs(
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get recent chat logs from the last N hours
    """
    from services.log_service import log_service
    logs = log_service.get_recent_logs(db, hours=hours, limit=limit)
    return logs

@router.get("/stats/overview")
async def get_stats_overview(db: Session = Depends(get_db)):
    """
    Get overview statistics
    """
    total_queries = db.query(func.count(ChatLog.id)).scalar()
    unique_sessions = db.query(func.count(func.distinct(ChatLog.session_id))).scalar()
    avg_response_time = db.query(func.avg(ChatLog.response_time_ms)).scalar()
    
    # Get queries per day for last 7 days
    from datetime import datetime, timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    daily_queries = db.query(
        func.date(ChatLog.created_at).label('date'),
        func.count(ChatLog.id).label('count')
    ).filter(
        ChatLog.created_at >= week_ago
    ).group_by(
        func.date(ChatLog.created_at)
    ).all()
    
    return {
        "total_queries": total_queries,
        "unique_sessions": unique_sessions,
        "avg_response_time_ms": round(avg_response_time, 2) if avg_response_time else 0,
        "daily_queries": [
            {"date": str(date), "count": count}
            for date, count in daily_queries
        ]
    }

@router.get("/sessions")
async def get_all_sessions(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Get all sessions with message counts and metadata
    """
    sessions = db.query(SessionModel).order_by(
        desc(SessionModel.last_active)
    ).limit(limit).all()
    
    result = []
    for session in sessions:
        message_count = db.query(func.count(ChatLog.id)).filter(
            ChatLog.session_id == session.session_id
        ).scalar()
        
        # Get first message preview
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

@router.get("/sessions/{session_id}/history")
async def get_session_history(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get full conversation history for a specific session
    """
    # Get session metadata
    session = db.query(SessionModel).filter(
        SessionModel.session_id == session_id
    ).first()
    
    if not session:
        return {"error": "Session not found"}
    
    # Get all messages in chronological order
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
                "created_at": msg.created_at,
                "response_time_ms": msg.response_time_ms,
                "model_used": msg.model_used,
                "ip_address": msg.ip_address
            }
            for msg in messages
        ]
    }

@router.get("/search")
async def search_logs(
    query: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Search through chat logs
    """
    logs = db.query(ChatLog).filter(
        (ChatLog.question.ilike(f"%{query}%")) | 
        (ChatLog.answer.ilike(f"%{query}%"))
    ).order_by(desc(ChatLog.created_at)).limit(limit).all()
    
    return logs

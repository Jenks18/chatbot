from sqlalchemy.orm import Session
from db.models import ChatLog, Session as SessionModel
from typing import List, Optional
from datetime import datetime, timedelta

class LogService:
    @staticmethod
    def create_chat_log(
        db: Session,
        session_id: str,
        question: str,
        answer: str,
        model_used: str,
        response_time_ms: int,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        extra_metadata: Optional[dict] = None
    ) -> ChatLog:
        """Create a new chat log entry with tracking data"""
        chat_log = ChatLog(
            session_id=session_id,
            user_id=user_id,
            question=question,
            answer=answer,
            model_used=model_used,
            response_time_ms=response_time_ms,
            ip_address=ip_address,
            user_agent=user_agent,
            extra_metadata=extra_metadata
        )
        db.add(chat_log)
        db.commit()
        db.refresh(chat_log)
        return chat_log

    @staticmethod
    def get_chat_logs(
        db: Session,
        session_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ChatLog]:
        """Retrieve chat logs, optionally filtered by session"""
        query = db.query(ChatLog)
        
        if session_id:
            query = query.filter(ChatLog.session_id == session_id)
        
        return query.order_by(ChatLog.created_at.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def get_recent_logs(db: Session, hours: int = 24, limit: int = 100) -> List[ChatLog]:
        """Get chat logs from the last N hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return db.query(ChatLog).filter(
            ChatLog.created_at >= cutoff_time
        ).order_by(ChatLog.created_at.desc()).limit(limit).all()

    @staticmethod
    def create_or_update_session(
        db: Session,
        session_id: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        geo_data: Optional[dict] = None,
        extra_metadata: Optional[dict] = None
    ) -> SessionModel:
        """Create a new session or update existing one with geolocation data"""
        session = db.query(SessionModel).filter(
            SessionModel.session_id == session_id
        ).first()

        if session:
            session.last_active = datetime.utcnow()
            # Update IP and geo data if changed
            if ip_address and ip_address != session.ip_address:
                session.ip_address = ip_address
                if geo_data:
                    session.country = geo_data.get("country")
                    session.city = geo_data.get("city")
                    session.region = geo_data.get("region")
                    session.latitude = geo_data.get("lat")
                    session.longitude = geo_data.get("lon")
                    session.timezone = geo_data.get("timezone")
                    session.extra_metadata = geo_data
        else:
            session = SessionModel(
                session_id=session_id,
                user_agent=user_agent,
                ip_address=ip_address,
                country=geo_data.get("country") if geo_data else None,
                city=geo_data.get("city") if geo_data else None,
                region=geo_data.get("region") if geo_data else None,
                latitude=geo_data.get("lat") if geo_data else None,
                longitude=geo_data.get("lon") if geo_data else None,
                timezone=geo_data.get("timezone") if geo_data else None,
                extra_metadata=extra_metadata or geo_data
            )
            db.add(session)
        
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_session_stats(db: Session, session_id: str) -> dict:
        """Get statistics for a specific session"""
        message_count = db.query(ChatLog).filter(
            ChatLog.session_id == session_id
        ).count()

        session = db.query(SessionModel).filter(
            SessionModel.session_id == session_id
        ).first()

        return {
            "session_id": session_id,
            "message_count": message_count,
            "started_at": session.started_at if session else None,
            "last_active": session.last_active if session else None
        }

log_service = LogService()

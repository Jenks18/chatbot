from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from db.database import get_db
from schemas import ChatMessage, ChatResponse
from services.groq_model_service import model_service
from services.log_service import log_service
from services.geo_service import geo_service
import uuid
import time

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    message: ChatMessage,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Main chat endpoint - processes user questions and returns AI responses
    """
    # Generate or use existing session ID
    session_id = message.session_id or str(uuid.uuid4())
    
    # Capture tracking information
    user_agent = request.headers.get("user-agent", "unknown")
    client_ip = request.client.host if request.client else "unknown"
    
    # Get geolocation data from IP
    geo_data = await geo_service.get_location_data(client_ip)
    
    # Update session tracking with geolocation
    log_service.create_or_update_session(
        db, 
        session_id, 
        user_agent, 
        client_ip,
        geo_data=geo_data
    )
    
    # Start timing
    start_time = time.time()
    
    try:
        # Generate response from model (RAG disabled for production)
        answer = await model_service.generate_response(
            question=message.message,
            context=None
        )
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Prepare metadata including geolocation
        metadata = {
            "geo_data": geo_data
        }
        
        # Log the interaction with tracking data
        log_service.create_chat_log(
            db=db,
            session_id=session_id,
            question=message.message,
            answer=answer,
            model_used=model_service.model_name,
            response_time_ms=response_time_ms,
            ip_address=client_ip,
            user_agent=user_agent,
            extra_metadata=metadata
        )
        
        return ChatResponse(
            answer=answer,
            session_id=session_id,
            model_used=model_service.model_name,
            response_time_ms=response_time_ms,
            sources=None
        )
        
    except Exception as e:
        # Log the error
        response_time_ms = int((time.time() - start_time) * 1000)
        error_msg = f"I apologize, but I encountered an error processing your question: {str(e)}"
        
        log_service.create_chat_log(
            db=db,
            session_id=session_id,
            question=message.message,
            answer=error_msg,
            model_used=model_service.model_name,
            response_time_ms=response_time_ms,
            ip_address=client_ip,
            user_agent=user_agent,
            extra_metadata={"error": str(e)}
        )
        
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Retrieve chat history for a specific session
    """
    logs = log_service.get_chat_logs(db, session_id=session_id, limit=limit)
    return {"session_id": session_id, "history": logs}

@router.get("/session/{session_id}/stats")
async def get_session_stats(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get statistics for a specific session
    """
    stats = log_service.get_session_stats(db, session_id)
    return stats

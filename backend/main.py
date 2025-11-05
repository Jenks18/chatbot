from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from db.database import engine, get_db, DATABASE_URL as DB_URL
from db.models import Base
from routers import chat, admin
from schemas import HealthResponse
from services.model_router import model_service
from services.interaction_service import seed_default_interactions
from sqlalchemy.orm import Session
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ToxicoGPT API",
    description="Self-hosted toxicology chatbot API with conversation logging",
    version="1.0.0"
)

# CORS configuration
CORS_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")]
print(f"🌐 CORS enabled for: {CORS_ORIGINS}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])

@app.get("/")
async def root():
    return {
        "message": "ToxicoGPT API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check the health of all system components
    """
    # Check database
    db_status = "healthy"
    try:
        from sqlalchemy import text
        db = next(get_db())
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Check model server
    try:
        model_status = await model_service.check_health()
        if model_status.get("status") == "healthy":
            model_status_str = "healthy"
        else:
            # Check if API key is missing
            if not model_service.api_key:
                model_status_str = "unhealthy: GROQ_API_KEY not configured"
            else:
                model_status_str = "unhealthy: Groq API unreachable"
    except Exception as e:
        model_status_str = f"unhealthy: {str(e)}"
    
    overall_status = "healthy" if db_status == "healthy" and model_status_str == "healthy" else "degraded"
    
    return HealthResponse(
        status=overall_status,
        database=db_status,
        model_server=model_status_str,
        timestamp=datetime.utcnow()
    )

@app.on_event("startup")
async def startup_event():
    print("=" * 60)
    print("🧬 ToxicoGPT API Starting Up")
    print("=" * 60)
    # Print the effective DB URL detected by the app (may differ from .env)
    print(f"📊 Database: {DB_URL[:200]}...")
    
    # Using Groq
    print(f"🤖 Model Provider: Groq API")
    print(f"🔬 Model: {os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')}")
    
    # Check model service health
    health_result = await model_service.check_health()
    if health_result.get("status") == "healthy":
        print("✓ Groq service is reachable")
    else:
        print("⚠ WARNING: Groq service is not reachable")
        print("  Check your GROQ_API_KEY in environment variables")
        print(f"  Error: {health_result.get('error', 'Unknown')}")
    
    print("=" * 60)
    print("🚀 API is ready at http://localhost:8000")
    print("📚 API docs at http://localhost:8000/docs")
    print("=" * 60)

    # Seed initial interactions if database empty
    try:
        db = next(get_db())
        seed_default_interactions(db)
        print("✓ Seeded default interaction data (if DB was empty)")
    except Exception as e:
        print(f"⚠ Could not seed interactions: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

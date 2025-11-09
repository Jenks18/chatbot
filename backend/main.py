from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
from dotenv import load_dotenv

# Only load .env if it exists (local dev), skip on serverless
is_vercel = os.getenv('VERCEL') == '1'
try:
    if not is_vercel:
        load_dotenv()
except:
    pass

# Import database components with error handling
try:
    # Try relative imports first (for Vercel)
    try:
        from .db.database import engine, get_db, DATABASE_URL as DB_URL
        from .db.models import Base
    except ImportError:
        # Fall back to backend.* imports (for local: python -m backend.main from project root)
        from backend.db.database import engine, get_db, DATABASE_URL as DB_URL
        from backend.db.models import Base
    from sqlalchemy.orm import Session
    
    # Create database tables (skip detailed logging in serverless)
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        if not is_vercel:
            print(f"⚠️  Database initialization warning: {e}")
    
    DB_AVAILABLE = True
except Exception as e:
    if not is_vercel:
        print(f"⚠️  Database not available: {e}")
    DB_AVAILABLE = False
    DB_URL = "not_configured"
    
    # Create a dummy get_db that returns None
    def get_db():
        yield None

# Import routers and services
try:
    # Try relative imports first (for Vercel/when module is backend.main)
    from .routers import chat, admin
    from .schemas import HealthResponse
    from .services.model_router import model_service
    from .services.interaction_service import seed_default_interactions
except ImportError:
    # Fall back to backend.* imports (for local: python -m backend.main from project root)
    from backend.routers import chat, admin
    from backend.schemas import HealthResponse
    from backend.services.model_router import model_service
    from backend.services.interaction_service import seed_default_interactions

app = FastAPI(
    title="ToxicoGPT API",
    description="Self-hosted toxicology chatbot API with conversation logging",
    version="1.0.0"
)

# CORS configuration
CORS_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")]
if not is_vercel:
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
    if not DB_AVAILABLE:
        db_status = "not_configured"
    else:
        db_status = "healthy"
        try:
            from sqlalchemy import text
            db = next(get_db())
            if db is not None:
                db.execute(text("SELECT 1"))
                db.close()
        except Exception as e:
            db_status = f"unhealthy: {str(e)[:100]}"
    
    # Check model server
    model_status_str = "unknown"
    try:
        if not model_service:
            model_status_str = "unhealthy: model service not initialized"
        elif not hasattr(model_service, 'api_key') or not model_service.api_key:
            model_status_str = "unhealthy: GROQ_API_KEY not configured"
        else:
            model_status = await model_service.check_health()
            if model_status.get("status") == "healthy":
                model_status_str = "healthy"
            else:
                model_status_str = "unhealthy: Groq API unreachable"
    except Exception as e:
        model_status_str = f"unhealthy: {str(e)[:100]}"
    
    overall_status = "healthy" if db_status == "healthy" and model_status_str == "healthy" else "degraded"
    
    return HealthResponse(
        status=overall_status,
        database=db_status,
        model_server=model_status_str,
        timestamp=datetime.utcnow()
    )

@app.on_event("startup")
async def startup_event():
    # Skip verbose logging in serverless environment
    if is_vercel:
        return
        
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

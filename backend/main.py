from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from db.database import engine, get_db
from db.models import Base
from routers import chat, admin
from schemas import HealthResponse
from services.model_service import model_service
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
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
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
    model_status = "healthy" if await model_service.check_health() else "unhealthy"
    
    overall_status = "healthy" if db_status == "healthy" and model_status == "healthy" else "degraded"
    
    return HealthResponse(
        status=overall_status,
        database=db_status,
        model_server=model_status,
        timestamp=datetime.utcnow()
    )

@app.on_event("startup")
async def startup_event():
    print("=" * 60)
    print("🧬 ToxicoGPT API Starting Up")
    print("=" * 60)
    print(f"📊 Database: {os.getenv('DATABASE_URL', 'Not configured')[:50]}...")
    print(f"🤖 Model Server: {os.getenv('MODEL_SERVER_URL', 'Not configured')}")
    print(f"🔬 Model: {os.getenv('MODEL_NAME', 'Not configured')}")
    
    # Check model server
    if await model_service.check_health():
        print("✓ Model server is reachable")
    else:
        print("⚠ WARNING: Model server is not reachable")
        print("  Make sure Ollama is running and the model is downloaded:")
        print(f"  docker exec -it toxicology-model ollama pull {os.getenv('MODEL_NAME', 'llama3:8b')}")
    
    print("=" * 60)
    print("🚀 API is ready at http://localhost:8000")
    print("📚 API docs at http://localhost:8000/docs")
    print("=" * 60)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

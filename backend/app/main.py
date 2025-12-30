"""
FastAPI application initialization.
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.config import settings
from app.db.session import get_db
from app.models import ErrorTag
from app.utils.ollama_client import get_ollama_client
from app.api import sources, review, library

app = FastAPI(
    title="Language Learning App API",
    description="AI-powered personalized German language learning",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(sources.router, prefix="/api")
app.include_router(review.router, prefix="/api")
app.include_router(library.router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "message": "Language Learning App API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/api/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    # Check database
    try:
        error_tag_count = db.query(ErrorTag).count()
        db_status = f"connected ({error_tag_count} error tags loaded)"
    except Exception as e:
        db_status = f"error: {str(e)}"

    # Check Ollama
    ollama_client = get_ollama_client()
    try:
        ollama_healthy = await ollama_client.check_health()
        if ollama_healthy:
            models = await ollama_client.list_models()
            ollama_status = f"connected ({len(models)} models available)"
        else:
            ollama_status = "not running"
    except Exception as e:
        ollama_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "database": db_status,
        "ollama": ollama_status
    }

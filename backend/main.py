"""
FastAPI main application entry point.
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from config import settings
from database import get_db, check_db_connection
from schemas import HealthCheckResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.project_name,
    description="ML-powered Steam game recommendation system with personalized suggestions",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.api_v1_prefix}/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# ============================================================
# Startup/Shutdown Events
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info(f"Starting {settings.project_name}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Check database connection
    if check_db_connection():
        logger.info("✅ Database connection successful")
    else:
        logger.error("❌ Database connection failed - check your DATABASE_URL")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info(f"Shutting down {settings.project_name}")


# ============================================================
# Root & Health Check Endpoints
# ============================================================

@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "message": "Steam Game Recommendation API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


@app.get(f"{settings.api_v1_prefix}/health", response_model=HealthCheckResponse)
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint.
    
    Verifies:
    - API is running
    - Database connection is working
    """
    try:
        # Test database query
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        logger.error(f"Health check database error: {e}")
        db_status = "disconnected"
    
    return HealthCheckResponse(
        status="healthy" if db_status == "connected" else "degraded",
        timestamp=datetime.utcnow(),
        database=db_status,
        version="1.0.0"
    )


# ============================================================
# Include Routers
# ============================================================

from routers import auth, profile, recommendations

# Register routers
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(recommendations.router)

# Will add feedback router in Phase 4:
# from routers import feedback
# app.include_router(feedback.router)


# ============================================================
# Run with: uvicorn backend.main:app --reload --port 8000
# ============================================================

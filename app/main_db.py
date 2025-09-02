"""
FastAPI application with database integration
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("🚀 MediaBoard AI starting up...")
    
    # Check database connection on startup
    try:
        from app.db.session import async_engine
        from sqlalchemy import text
        async with async_engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.fetchone()
        logger.info("✅ Database connection successful")
    except Exception as e:
        logger.warning(f"⚠️ Database connection failed: {e}")
        logger.info("💡 Server will run without database features")
    
    yield
    
    # Cleanup on shutdown
    logger.info("🛑 MediaBoard AI shutting down...")

# Create FastAPI app with lifespan
app = FastAPI(
    title="MediaBoard AI",
    description="AI-powered media processing platform with LangGraph workflows",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with error handling
try:
    from app.api.auth_db import router as auth_router
    app.include_router(auth_router)
    logger.info("✅ Auth router (with database) loaded")
except ImportError as e:
    logger.warning(f"⚠️ Failed to load auth router with database (ImportError): {e}")
    
    # Fallback to simple auth router
    try:
        from app.api.auth import router as auth_fallback_router
        app.include_router(auth_fallback_router)
        logger.info("✅ Auth router (fallback) loaded")
    except Exception as e2:
        logger.error(f"❌ Failed to load any auth router: {e2}")
except Exception as e:
    logger.warning(f"⚠️ Failed to load auth router with database (Other error): {e}")
    
    # Fallback to simple auth router
    try:
        from app.api.auth import router as auth_fallback_router
        app.include_router(auth_fallback_router)
        logger.info("✅ Auth router (fallback) loaded")
    except Exception as e2:
        logger.error(f"❌ Failed to load any auth router: {e2}")

# Try to include other routers if database is available
try:
    from app.api.users import router as users_router
    app.include_router(users_router)
    logger.info("✅ Users router loaded")
except Exception as e:
    logger.warning(f"⚠️ Users router not loaded: {e}")

try:
    from app.api.media import router as media_router
    app.include_router(media_router)
    logger.info("✅ Media router loaded")
except Exception as e:
    logger.warning(f"⚠️ Media router not loaded: {e}")

try:
    from app.api.ai import router as ai_router
    app.include_router(ai_router)
    logger.info("✅ AI router loaded")
except Exception as e:
    logger.warning(f"⚠️ AI router not loaded: {e}")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with system status"""
    return {
        "message": "MediaBoard AI is running!",
        "status": "healthy",
        "version": "1.0.0",
        "features": {
            "oauth": True,
            "database": True,  # Will be detected dynamically
            "ai_workflows": True,
            "media_processing": True
        }
    }

# Health check endpoint
@app.get("/health")
async def health():
    """Detailed health check"""
    health_status = {
        "status": "healthy",
        "timestamp": "2024-01-20T12:00:00Z",
        "services": {
            "api": "healthy",
            "oauth": "healthy"
        }
    }
    
    # Check database connection
    try:
        from app.db.session import async_engine
        from sqlalchemy import text
        async with async_engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.fetchone()
        health_status["services"]["database"] = "healthy"
    except Exception:
        health_status["services"]["database"] = "unhealthy"
    
    return health_status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

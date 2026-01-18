"""
Main FastAPI Application
Phishing Detection Backend Server
"""

import sys
import time
import os
from pathlib import Path
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Also add backend directory for relative imports
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from config.settings import settings
from api.routes import router as api_router
from services.ensemble_predictor import get_ensemble_predictor


# =============================================================================
# Logging Configuration
# =============================================================================

def setup_logging():
    """Configure loguru logging"""
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    logger.remove()  # Remove default handler
    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.LOG_LEVEL,
        colorize=True,
    )
    
    # File logging
    log_dir = Path(settings.LOG_FILE).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        settings.LOG_FILE,
        format=log_format,
        level=settings.LOG_LEVEL,
        rotation="10 MB",
        retention="7 days",
        compression="gz",
    )


setup_logging()


# =============================================================================
# Application Lifespan
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.
    Handles startup and shutdown tasks.
    """
    # Startup
    logger.info("=" * 60)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    logger.info("=" * 60)
    
    # Load models
    logger.info("Loading ML models...")
    start_time = time.time()
    
    try:
        predictor = get_ensemble_predictor()
        model_status = predictor.load_models()
        
        load_time = time.time() - start_time
        logger.info(f"Models loaded in {load_time:.2f}s")
        logger.info(f"Model status: {model_status}")
        
        if not any(model_status.values()):
            logger.warning("No models loaded! Service will run in limited mode.")
        
    except Exception as e:
        logger.error(f"Failed to load models: {e}")
        logger.warning("Service starting without models - limited functionality")
    
    # Store startup time for stats
    app.state.startup_time = datetime.utcnow()
    app.state.request_count = 0
    
    logger.info("Server startup complete!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down server...")
    logger.info("Cleanup complete. Goodbye!")


# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title=settings.APP_NAME,
    description="""
    ## Phishing Detection API
    
    Real-time phishing detection powered by ensemble machine learning models.
    
    ### Features
    - **URL Scanning**: Analyze URLs for phishing indicators
    - **Batch Processing**: Scan multiple URLs at once
    - **Domain Trust**: Evaluate domain trustworthiness
    - **Feature Extraction**: Understand URL characteristics
    
    ### Models
    - **ELECTRA**: Transformer-based text classification
    - **Biformer**: Character-level URL analysis
    - **LightGBM**: Feature-based gradient boosting
    
    ### Trust System
    - High-trust domains (Google, Microsoft, etc.)
    - Government and educational domain detection
    - Keyword-based trust evaluation
    - Suspicious pattern detection
    """,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# =============================================================================
# Middleware
# =============================================================================

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    
    # Increment request count
    if hasattr(app.state, 'request_count'):
        app.state.request_count += 1
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log request
    logger.debug(
        f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s"
    )
    
    return response


# =============================================================================
# Exception Handlers
# =============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


# =============================================================================
# Routes
# =============================================================================

# Include API routes
app.include_router(api_router, prefix="/api/v1", tags=["Phishing Detection"])


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with service information"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "api": "/api/v1",
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Quick health check endpoint"""
    try:
        predictor = get_ensemble_predictor()
        models_loaded = predictor.is_loaded()
        return {
            "status": "healthy" if models_loaded else "degraded",
            "models_loaded": models_loaded,
            "version": settings.APP_VERSION,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )


# Readiness probe (for Kubernetes)
@app.get("/ready", tags=["Health"])
async def readiness():
    """Readiness probe for orchestrators"""
    try:
        predictor = get_ensemble_predictor()
        if predictor.is_loaded():
            return {"status": "ready"}
        else:
            return JSONResponse(
                status_code=503,
                content={"status": "not ready", "reason": "models loading"}
            )
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "not ready", "reason": str(e)}
        )


# Liveness probe (for Kubernetes)
@app.get("/live", tags=["Health"])
async def liveness():
    """Liveness probe for orchestrators"""
    return {"status": "alive"}


# Stats endpoint
@app.get("/stats", tags=["Health"])
async def stats():
    """Service statistics"""
    uptime = 0
    if hasattr(app.state, 'startup_time'):
        uptime = (datetime.utcnow() - app.state.startup_time).total_seconds()
    
    request_count = getattr(app.state, 'request_count', 0)
    
    return {
        "uptime_seconds": uptime,
        "total_requests": request_count,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else settings.WORKERS,
        log_level=settings.LOG_LEVEL.lower(),
    )

"""
Main FastAPI application - Refactored with clean architecture.
"""
import logging
from typing import Dict, Any
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import config
from .exceptions import AppError
from .routes import auth_router, user_router, reviews_router
from .database import init_database, create_tables

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    description="A comprehensive CRM system for Google My Business automation with MySQL database",
    docs_url="/docs",
    redoc_url="/redoc"
)


# ============================================================================
# EVENT HANDLERS
# ============================================================================

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and create tables on startup."""
    try:
        logger.info(f"🚀 {config.APP_NAME} v{config.APP_VERSION} starting...")
        logger.info("🔧 Initializing MySQL database...")
        # Database is already initialized in database.py
        # Just create tables if they don't exist
        create_tables()
        logger.info("✅ MySQL database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown."""
    logger.info(f"{config.APP_NAME} shutting down...")


# ============================================================================
# GLOBAL EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    """Handle custom app exceptions."""
    logger.error(f"AppError on {request.url.path}: {exc.detail}")
    
    error_response = {
        "detail": exc.detail,
        "error": exc.detail,  # For backward compatibility
        "path": str(request.url.path)
    }
    
    # Add error code if available
    if hasattr(exc, 'error_code') and exc.error_code:
        error_response["code"] = exc.error_code
    
    # Add additional details if available
    if hasattr(exc, 'details') and exc.details:
        error_response["details"] = exc.details
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.exception(f"Unexpected error on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": config.ERROR_GENERIC,
            "path": str(request.url.path)
        }
    )


# ============================================================================
# MIDDLEWARE
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@app.get("/", tags=["Health"])
def root() -> Dict[str, str]:
    """API root endpoint."""
    return {
        "message": config.APP_NAME,
        "version": config.APP_VERSION,
        "status": "healthy"
    }


@app.get("/health", tags=["Health"])
def health_check() -> Dict[str, str]:
    """Detailed health check."""
    return {
        "status": "healthy",
        "version": config.APP_VERSION
    }


# ============================================================================
# INCLUDE ROUTERS
# ============================================================================

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(reviews_router)


# ============================================================================
# LEGACY ENDPOINTS (Backward Compatibility)
# ============================================================================

@app.get("/user/public/dashboard/stats", tags=["Legacy"], include_in_schema=False)
def legacy_dashboard_stats() -> Dict[str, Any]:
    """Legacy endpoint for dashboard stats."""
    from .sample_reviews import get_reviews, calculate_dashboard_stats
    reviews = get_reviews()
    stats = calculate_dashboard_stats(reviews)
    return {"reviews": reviews, "stats": stats}


@app.get("/api/reviews", tags=["Legacy"], include_in_schema=False)
def legacy_reviews() -> Dict[str, Any]:
    """Legacy endpoint for reviews."""
    from .sample_reviews import get_reviews
    reviews = get_reviews()
    return {"reviews": reviews, "total": len(reviews)}


# ============================================================================
# APPLICATION METADATA
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_refactored:app",
        host=config.HOST,
        port=config.PORT,
        reload=True
    )

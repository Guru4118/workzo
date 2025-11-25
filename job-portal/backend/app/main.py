"""
Job Portal API - Main Application Entry Point

A production-ready FastAPI application for job aggregation and management.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
import sys

from app.config import get_settings
from app.db import create_indexes, close_db
from app.scheduler import start_scheduler, stop_scheduler

# Import routers
from app.routers import ingest, admin, auth, jobs, health

# ===========================================
# Logging Configuration
# ===========================================

settings = get_settings()
log_level = logging.DEBUG if settings.DEBUG else logging.INFO

logging.basicConfig(
    level=log_level,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Reduce noise from third-party libraries
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("pymongo").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# ===========================================
# Rate Limiter
# ===========================================

limiter = Limiter(key_func=get_remote_address)


# ===========================================
# Application Lifespan
# ===========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler for startup and shutdown events.

    Startup:
    - Create database indexes
    - Start background scheduler

    Shutdown:
    - Stop scheduler
    - Close database connection
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")

    # Create database indexes
    try:
        create_indexes()
    except Exception as e:
        logger.error(f"Failed to create database indexes: {e}")
        # Don't fail startup - indexes might already exist

    # Start background scheduler
    try:
        start_scheduler()
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down application...")
    stop_scheduler()
    close_db()
    logger.info("Application shutdown complete")


# ===========================================
# Create FastAPI Application
# ===========================================

app = FastAPI(
    title=settings.APP_NAME,
    description="Job Portal API - Aggregates and manages job postings from multiple sources",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ===========================================
# Middleware
# ===========================================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===========================================
# Exception Handlers
# ===========================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors with consistent format.
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "loc": list(error.get("loc", [])),
            "msg": error.get("msg", "Validation error"),
            "type": error.get("type", "value_error")
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": errors
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions.
    Logs the error and returns a generic error response.
    """
    logger.exception(f"Unhandled exception on {request.url}: {exc}")

    # Don't expose internal errors in production
    if settings.DEBUG:
        detail = str(exc)
    else:
        detail = "Internal server error"

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": detail}
    )


# ===========================================
# Include Routers
# ===========================================

# Health check routes (no prefix, at root level)
app.include_router(health.router)

# Authentication routes
app.include_router(auth.router)

# Job ingestion routes (for scrapers)
app.include_router(ingest.router)

# Public job listings
app.include_router(jobs.router)

# Admin routes
app.include_router(admin.router)


# ===========================================
# Root Endpoint (handled by health router)
# ===========================================

# The root "/" endpoint is defined in health.router

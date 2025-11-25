"""
Health check router for monitoring and container orchestration.
"""
from fastapi import APIRouter, HTTPException, status
import logging

from app.db import get_client
from app.config import get_settings
from app.schemas.responses import HealthResponse, ReadyResponse

router = APIRouter(tags=["Health"])
logger = logging.getLogger(__name__)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Basic health check endpoint.

    Returns application status, version, and environment.
    Use this for basic liveness probes.
    """
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT
    )


@router.get("/ready", response_model=ReadyResponse)
async def readiness_check():
    """
    Readiness check endpoint.

    Verifies that all required services are available:
    - Database connection

    Use this for readiness probes in Kubernetes/container orchestration.
    Returns 503 if any required service is unavailable.
    """
    settings = get_settings()

    # Check MongoDB connection
    try:
        client = get_client()
        client.admin.command("ping")
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )

    # Check MinIO if configured (optional)
    storage_status = None
    if settings.MINIO_ACCESS_KEY:
        try:
            from app.utils.minio_client import get_minio_client
            minio = get_minio_client()
            minio.list_buckets()
            storage_status = "connected"
        except Exception as e:
            logger.warning(f"MinIO connection failed (non-critical): {e}")
            storage_status = "unavailable"

    return ReadyResponse(
        status="ready",
        database=db_status,
        storage=storage_status
    )


@router.get("/")
async def root():
    """
    Root endpoint - returns welcome message and links.
    """
    settings = get_settings()
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.DEBUG else "API documentation disabled in production",
        "health": "/health",
        "ready": "/ready"
    }

from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from typing import List
import os


class Settings(BaseSettings):
    """Application configuration settings."""

    # Application
    APP_NAME: str = "Job Portal API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # MongoDB
    MONGO_URI: str = Field(..., description="MongoDB connection string")
    MONGO_DB_NAME: str = "job_portal"

    # JWT Authentication
    JWT_SECRET_KEY: str = Field(..., description="Secret key for JWT signing")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # MinIO Storage (optional)
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str | None = None
    MINIO_SECRET_KEY: str | None = None
    MINIO_SECURE: bool = False
    MINIO_BUCKET: str = "job-snapshots"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Scraper Configuration
    BACKEND_URL: str = "http://127.0.0.1:8000"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to ensure settings are only loaded once.
    """
    # Look for .env in backend directory first, then app directory for backwards compatibility
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_file = os.path.join(backend_dir, ".env")

    if not os.path.exists(env_file):
        # Fallback to app directory (old location)
        app_dir = os.path.dirname(os.path.abspath(__file__))
        env_file = os.path.join(app_dir, ".env")

    return Settings(_env_file=env_file)

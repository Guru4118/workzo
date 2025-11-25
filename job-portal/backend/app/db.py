"""
Database connection and collection management.
"""
from pymongo import MongoClient, ASCENDING, TEXT
from pymongo.collection import Collection
from pymongo.database import Database
import certifi
import logging
from typing import Optional

from app.config import get_settings

logger = logging.getLogger(__name__)

# Module-level connection instances (lazy initialization)
_client: Optional[MongoClient] = None
_db: Optional[Database] = None


def get_client() -> MongoClient:
    """Get or create MongoDB client instance."""
    global _client
    if _client is None:
        settings = get_settings()
        logger.info("Initializing MongoDB connection...")
        _client = MongoClient(
            settings.MONGO_URI,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=30000,
        )
        # Verify connection
        _client.admin.command("ping")
        logger.info("MongoDB connection established successfully")
    return _client


def get_db() -> Database:
    """Get or create database instance."""
    global _db
    if _db is None:
        settings = get_settings()
        _db = get_client()[settings.MONGO_DB_NAME]
    return _db


def close_db() -> None:
    """Close database connection."""
    global _client, _db
    if _client is not None:
        logger.info("Closing MongoDB connection...")
        _client.close()
        _client = None
        _db = None


# ===========================================
# Collection Accessors
# ===========================================

def get_raw_jobs() -> Collection:
    """Get raw_jobs collection (archive of all ingested jobs)."""
    return get_db()["raw_jobs"]


def get_pending_jobs() -> Collection:
    """Get pending_jobs collection (jobs awaiting approval)."""
    return get_db()["pending_jobs"]


def get_approved_jobs() -> Collection:
    """Get approved_jobs collection (published jobs)."""
    return get_db()["approved_jobs"]


def get_rejected_jobs() -> Collection:
    """Get rejected_jobs collection (rejected jobs with reasons)."""
    return get_db()["rejected_jobs"]


def get_users() -> Collection:
    """Get users collection."""
    return get_db()["users"]


# ===========================================
# Index Management
# ===========================================

def create_indexes() -> None:
    """
    Create all required database indexes.
    Should be called once on application startup.
    """
    logger.info("Creating database indexes...")

    try:
        # Raw jobs indexes
        raw = get_raw_jobs()
        raw.create_index([("dedupe_hash", ASCENDING)], unique=True, sparse=True, background=True)
        raw.create_index([("ingested_at", ASCENDING)], background=True)
        raw.create_index([("source", ASCENDING)], background=True)
        logger.debug("Created indexes for raw_jobs collection")

        # Pending jobs indexes
        pending = get_pending_jobs()
        pending.create_index([("dedupe_hash", ASCENDING)], unique=True, sparse=True, background=True)
        pending.create_index(
            [("title", TEXT), ("company", TEXT)],
            default_language="english",
            background=True
        )
        pending.create_index([("ingested_at", ASCENDING)], background=True)
        pending.create_index([("source", ASCENDING)], background=True)
        logger.debug("Created indexes for pending_jobs collection")

        # Approved jobs indexes
        approved = get_approved_jobs()
        approved.create_index([("dedupe_hash", ASCENDING)], unique=True, sparse=True, background=True)
        approved.create_index(
            [("title", TEXT), ("company", TEXT), ("location", TEXT)],
            default_language="english",
            background=True
        )
        approved.create_index([("posted_date_parsed", ASCENDING)], background=True)
        approved.create_index([("approved_at", ASCENDING)], background=True)
        approved.create_index([("source", ASCENDING)], background=True)
        # Geospatial index for location-based searches
        approved.create_index([
            ("location_normalized.lat", ASCENDING),
            ("location_normalized.lon", ASCENDING)
        ], background=True)
        logger.debug("Created indexes for approved_jobs collection")

        # Rejected jobs indexes
        rejected = get_rejected_jobs()
        rejected.create_index([("dedupe_hash", ASCENDING)], background=True)
        rejected.create_index([("rejected_at", ASCENDING)], background=True)
        logger.debug("Created indexes for rejected_jobs collection")

        # Users indexes
        users = get_users()
        users.create_index([("email", ASCENDING)], unique=True, background=True)
        users.create_index([("username", ASCENDING)], unique=True, background=True)
        logger.debug("Created indexes for users collection")

        logger.info("Database indexes created successfully")

    except Exception as e:
        logger.error(f"Error creating indexes: {e}")
        raise


def drop_indexes() -> None:
    """Drop all non-_id indexes (useful for development/testing)."""
    logger.warning("Dropping all custom indexes...")
    collections = [
        get_raw_jobs(),
        get_pending_jobs(),
        get_approved_jobs(),
        get_rejected_jobs(),
        get_users()
    ]
    for collection in collections:
        collection.drop_indexes()
    logger.info("All custom indexes dropped")

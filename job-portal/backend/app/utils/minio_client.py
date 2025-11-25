"""
MinIO S3-compatible storage client for HTML snapshots.
"""
from minio import Minio
from minio.error import S3Error
from typing import Optional
from io import BytesIO
import hashlib
from datetime import datetime
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)

# Module-level client instance (lazy initialization)
_minio_client: Optional[Minio] = None


def get_minio_client() -> Optional[Minio]:
    """
    Get or create MinIO client instance.

    Returns None if MinIO is not configured.
    """
    global _minio_client

    settings = get_settings()

    # Check if MinIO is configured
    if not settings.MINIO_ACCESS_KEY or not settings.MINIO_SECRET_KEY:
        logger.debug("MinIO not configured (missing credentials)")
        return None

    if _minio_client is None:
        # Parse endpoint (remove http:// or https:// prefix if present)
        endpoint = settings.MINIO_ENDPOINT
        if endpoint.startswith("http://"):
            endpoint = endpoint[7:]
        elif endpoint.startswith("https://"):
            endpoint = endpoint[8:]

        _minio_client = Minio(
            endpoint=endpoint,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        logger.info(f"MinIO client initialized: {endpoint}")

    return _minio_client


def ensure_bucket_exists(bucket: str) -> bool:
    """
    Ensure the specified bucket exists, create if not.

    Returns True if bucket exists or was created, False on error.
    """
    client = get_minio_client()
    if client is None:
        return False

    try:
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
            logger.info(f"Created MinIO bucket: {bucket}")
        return True
    except S3Error as e:
        logger.error(f"MinIO bucket error: {e}")
        return False


def store_html(bucket: str, key: str, html_content: str) -> Optional[str]:
    """
    Store HTML content in MinIO.

    Args:
        bucket: Bucket name
        key: Object key (path)
        html_content: HTML string to store

    Returns:
        URL of stored object, or None on error
    """
    client = get_minio_client()
    if client is None:
        return None

    settings = get_settings()

    try:
        if not ensure_bucket_exists(bucket):
            return None

        html_bytes = html_content.encode("utf-8")
        data = BytesIO(html_bytes)

        client.put_object(
            bucket,
            key,
            data,
            length=len(html_bytes),
            content_type="text/html; charset=utf-8"
        )

        # Construct URL
        protocol = "https" if settings.MINIO_SECURE else "http"
        url = f"{protocol}://{settings.MINIO_ENDPOINT}/{bucket}/{key}"

        logger.debug(f"Stored HTML snapshot: {key}")
        return url

    except S3Error as e:
        logger.error(f"MinIO store error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error storing to MinIO: {e}")
        return None


def upload_html_snapshot(html: str, source: str) -> Optional[str]:
    """
    Upload HTML snapshot for a job source.

    Generates a unique key based on timestamp and content hash.

    Args:
        html: HTML content to store
        source: Source name (e.g., "indeed", "zoho")

    Returns:
        URL of stored snapshot, or None if MinIO unavailable or error
    """
    settings = get_settings()

    # Check if MinIO is configured
    if not settings.MINIO_ACCESS_KEY:
        logger.debug("MinIO not configured, skipping snapshot upload")
        return None

    try:
        # Generate unique key
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        content_hash = hashlib.md5(html.encode()).hexdigest()[:8]
        key = f"snapshots/{source}/{timestamp}_{content_hash}.html"

        url = store_html(settings.MINIO_BUCKET, key, html)
        return url

    except Exception as e:
        logger.error(f"Failed to upload snapshot: {e}")
        return None


def delete_snapshot(bucket: str, key: str) -> bool:
    """
    Delete a snapshot from MinIO.

    Args:
        bucket: Bucket name
        key: Object key

    Returns:
        True if deleted successfully, False otherwise
    """
    client = get_minio_client()
    if client is None:
        return False

    try:
        client.remove_object(bucket, key)
        logger.debug(f"Deleted snapshot: {bucket}/{key}")
        return True
    except S3Error as e:
        logger.error(f"MinIO delete error: {e}")
        return False


def list_snapshots(source: Optional[str] = None, limit: int = 100) -> list:
    """
    List snapshots in the bucket.

    Args:
        source: Optional source filter
        limit: Maximum number of results

    Returns:
        List of snapshot object info
    """
    client = get_minio_client()
    if client is None:
        return []

    settings = get_settings()

    try:
        prefix = f"snapshots/{source}/" if source else "snapshots/"
        objects = client.list_objects(
            settings.MINIO_BUCKET,
            prefix=prefix,
            recursive=True
        )

        snapshots = []
        for obj in objects:
            if len(snapshots) >= limit:
                break
            snapshots.append({
                "key": obj.object_name,
                "size": obj.size,
                "last_modified": obj.last_modified.isoformat() if obj.last_modified else None
            })

        return snapshots

    except S3Error as e:
        logger.error(f"MinIO list error: {e}")
        return []

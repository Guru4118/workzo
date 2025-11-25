"""
Public jobs router for accessing approved job listings.
"""
from fastapi import APIRouter, HTTPException, status, Query
from bson import ObjectId
from typing import Optional
import logging

from app.db import get_approved_jobs
from app.schemas.responses import PaginatedResponse
from app.utils.sanitize import sanitize_search_query

router = APIRouter(prefix="/jobs", tags=["Jobs"])
logger = logging.getLogger(__name__)


def convert_objectid(doc: dict) -> dict:
    """Convert MongoDB ObjectId to string id."""
    if doc and "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


@router.get("", response_model=PaginatedResponse)
async def get_approved_jobs_list(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    q: Optional[str] = Query(None, max_length=200, description="Search query"),
    source: Optional[str] = Query(None, max_length=50, description="Filter by source"),
    location: Optional[str] = Query(None, max_length=200, description="Filter by location"),
):
    """
    Get paginated list of approved jobs.

    This is a public endpoint - no authentication required.

    - **page**: Page number (default 1)
    - **per_page**: Items per page (default 20, max 100)
    - **q**: Optional search query (searches title, company, location)
    - **source**: Optional filter by source
    - **location**: Optional filter by location (partial match)
    """
    approved = get_approved_jobs()
    skip = (page - 1) * per_page

    # Build filter
    filter_q = {}

    if q:
        # Use text search if available, fallback to regex
        safe_q = sanitize_search_query(q)
        filter_q["$or"] = [
            {"title": {"$regex": safe_q, "$options": "i"}},
            {"company": {"$regex": safe_q, "$options": "i"}},
            {"location": {"$regex": safe_q, "$options": "i"}}
        ]

    if source:
        filter_q["source"] = source

    if location:
        safe_loc = sanitize_search_query(location)
        # Add to existing $or or create new location filter
        if "$or" not in filter_q:
            filter_q["location"] = {"$regex": safe_loc, "$options": "i"}
        else:
            # If we already have a search query, add location to the filters
            filter_q["location"] = {"$regex": safe_loc, "$options": "i"}

    total = approved.count_documents(filter_q)
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1

    docs = list(
        approved.find(filter_q)
        .sort("approved_at", -1)
        .skip(skip)
        .limit(per_page)
    )

    # Convert ObjectId to string and remove internal fields
    clean_docs = []
    for doc in docs:
        doc = convert_objectid(doc)
        # Remove admin-only fields from public response
        doc.pop("approved_by", None)
        clean_docs.append(doc)

    return PaginatedResponse(
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        data=clean_docs
    )


@router.get("/{job_id}")
async def get_job_detail(job_id: str):
    """
    Get a single approved job by ID.

    This is a public endpoint - no authentication required.
    """
    approved = get_approved_jobs()

    try:
        job = approved.find_one({"_id": ObjectId(job_id)})
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid job ID format"
        )

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    job = convert_objectid(job)
    # Remove admin-only fields from public response
    job.pop("approved_by", None)

    return job


@router.get("/source/{source}")
async def get_jobs_by_source(
    source: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    """
    Get approved jobs filtered by source.

    This is a public endpoint - no authentication required.

    - **source**: Source name (e.g., indeed, zoho, amazon)
    """
    approved = get_approved_jobs()
    skip = (page - 1) * per_page

    filter_q = {"source": source}

    total = approved.count_documents(filter_q)
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1

    docs = list(
        approved.find(filter_q)
        .sort("approved_at", -1)
        .skip(skip)
        .limit(per_page)
    )

    clean_docs = []
    for doc in docs:
        doc = convert_objectid(doc)
        doc.pop("approved_by", None)
        clean_docs.append(doc)

    return PaginatedResponse(
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        data=clean_docs
    )

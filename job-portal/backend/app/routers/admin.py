"""
Admin router for job approval, rejection, and management.
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from datetime import datetime, timezone, timedelta
from bson import ObjectId
from typing import Optional
import logging

from app.db import (
    get_pending_jobs,
    get_approved_jobs,
    get_rejected_jobs,
    get_raw_jobs
)
from app.schemas.job import (
    JobApproval,
    JobRejection,
    BulkJobApproval,
    BulkJobRejection,
    JobStats
)
from app.schemas.responses import SuccessResponse, PaginatedResponse, BulkOperationResult
from app.schemas.user import UserInDB
from app.utils.auth import require_admin, require_viewer_or_admin
from app.utils.sanitize import sanitize_search_query

router = APIRouter(prefix="/admin", tags=["Admin"])
logger = logging.getLogger(__name__)


def convert_objectid(doc: dict) -> dict:
    """Convert MongoDB ObjectId to string id."""
    if doc and "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


@router.get("/pending", response_model=PaginatedResponse)
async def get_pending_jobs_list(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    q: Optional[str] = Query(None, max_length=200, description="Search query (title/company)"),
    source: Optional[str] = Query(None, max_length=50, description="Filter by source"),
    current_user: UserInDB = Depends(require_viewer_or_admin)
):
    """
    Get paginated list of pending jobs for review.

    Requires viewer or admin role.

    - **page**: Page number (default 1)
    - **per_page**: Items per page (default 20, max 100)
    - **q**: Optional search query for title/company
    - **source**: Optional filter by source (indeed, zoho, etc.)
    """
    pending = get_pending_jobs()
    skip = (page - 1) * per_page

    # Build filter
    filter_q = {}
    if q:
        # Sanitize search query to prevent regex injection
        safe_q = sanitize_search_query(q)
        filter_q["$or"] = [
            {"title": {"$regex": safe_q, "$options": "i"}},
            {"company": {"$regex": safe_q, "$options": "i"}}
        ]
    if source:
        filter_q["source"] = source

    total = pending.count_documents(filter_q)
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1

    docs = list(
        pending.find(filter_q)
        .sort("ingested_at", -1)
        .skip(skip)
        .limit(per_page)
    )

    # Convert ObjectId to string
    docs = [convert_objectid(doc) for doc in docs]

    return PaginatedResponse(
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        data=docs
    )


@router.post("/approve", response_model=SuccessResponse)
async def approve_job(
    approval: JobApproval,
    current_user: UserInDB = Depends(require_admin)
):
    """
    Approve a pending job by ID.

    Requires admin role.

    The job will be:
    1. Marked with approval metadata (timestamp, approver)
    2. Moved from pending_jobs to approved_jobs collection
    3. Deleted from pending_jobs
    """
    pending = get_pending_jobs()
    approved = get_approved_jobs()

    try:
        job = pending.find_one({"_id": ObjectId(approval.job_id)})
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid job ID format"
        )

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found in pending queue"
        )

    # Add approval metadata
    job["approved_at"] = datetime.now(timezone.utc).isoformat()
    job["approved_by"] = current_user.username

    # Move to approved collection
    approved.insert_one(job)
    pending.delete_one({"_id": ObjectId(approval.job_id)})

    logger.info(
        f"Job approved by {current_user.username}: "
        f"{job.get('title')} at {job.get('company')}"
    )

    return SuccessResponse(message="Job approved successfully")


@router.post("/reject", response_model=SuccessResponse)
async def reject_job(
    rejection: JobRejection,
    current_user: UserInDB = Depends(require_admin)
):
    """
    Reject a pending job with a reason.

    Requires admin role.

    The job will be:
    1. Marked with rejection metadata (timestamp, rejector, reason)
    2. Moved from pending_jobs to rejected_jobs collection
    3. Deleted from pending_jobs
    """
    pending = get_pending_jobs()
    rejected = get_rejected_jobs()

    try:
        job = pending.find_one({"_id": ObjectId(rejection.job_id)})
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid job ID format"
        )

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found in pending queue"
        )

    # Add rejection metadata
    job["rejected_at"] = datetime.now(timezone.utc).isoformat()
    job["rejected_by"] = current_user.username
    job["rejection_reason"] = rejection.reason

    # Move to rejected collection
    rejected.insert_one(job)
    pending.delete_one({"_id": ObjectId(rejection.job_id)})

    logger.info(
        f"Job rejected by {current_user.username}: "
        f"{job.get('title')} at {job.get('company')} - Reason: {rejection.reason}"
    )

    return SuccessResponse(message="Job rejected successfully")


@router.post("/bulk-approve", response_model=SuccessResponse)
async def bulk_approve_jobs(
    bulk_approval: BulkJobApproval,
    current_user: UserInDB = Depends(require_admin)
):
    """
    Approve multiple jobs at once.

    Requires admin role.

    - **job_ids**: List of job IDs to approve (max 100)

    Returns summary of results.
    """
    pending = get_pending_jobs()
    approved = get_approved_jobs()

    results = BulkOperationResult()

    for job_id in bulk_approval.job_ids:
        try:
            job = pending.find_one({"_id": ObjectId(job_id)})
            if not job:
                results.not_found += 1
                continue

            job["approved_at"] = datetime.now(timezone.utc).isoformat()
            job["approved_by"] = current_user.username

            approved.insert_one(job)
            pending.delete_one({"_id": ObjectId(job_id)})
            results.success += 1

        except Exception as e:
            logger.error(f"Error approving job {job_id}: {e}")
            results.errors += 1

    logger.info(
        f"Bulk approve by {current_user.username}: "
        f"{results.success} approved, {results.not_found} not found, {results.errors} errors"
    )

    return SuccessResponse(
        message=f"Bulk approval complete: {results.success} approved, "
                f"{results.not_found} not found, {results.errors} errors",
        data=results.model_dump()
    )


@router.post("/bulk-reject", response_model=SuccessResponse)
async def bulk_reject_jobs(
    bulk_rejection: BulkJobRejection,
    current_user: UserInDB = Depends(require_admin)
):
    """
    Reject multiple jobs at once with the same reason.

    Requires admin role.

    - **job_ids**: List of job IDs to reject (max 100)
    - **reason**: Rejection reason applied to all jobs

    Returns summary of results.
    """
    pending = get_pending_jobs()
    rejected = get_rejected_jobs()

    results = BulkOperationResult()

    for job_id in bulk_rejection.job_ids:
        try:
            job = pending.find_one({"_id": ObjectId(job_id)})
            if not job:
                results.not_found += 1
                continue

            job["rejected_at"] = datetime.now(timezone.utc).isoformat()
            job["rejected_by"] = current_user.username
            job["rejection_reason"] = bulk_rejection.reason

            rejected.insert_one(job)
            pending.delete_one({"_id": ObjectId(job_id)})
            results.success += 1

        except Exception as e:
            logger.error(f"Error rejecting job {job_id}: {e}")
            results.errors += 1

    logger.info(
        f"Bulk reject by {current_user.username}: "
        f"{results.success} rejected, {results.not_found} not found, {results.errors} errors"
    )

    return SuccessResponse(
        message=f"Bulk rejection complete: {results.success} rejected, "
                f"{results.not_found} not found, {results.errors} errors",
        data=results.model_dump()
    )


@router.get("/stats", response_model=JobStats)
async def get_job_statistics(current_user: UserInDB = Depends(require_viewer_or_admin)):
    """
    Get job statistics.

    Requires viewer or admin role.

    Returns counts by collection, source breakdown, and recent activity.
    """
    raw = get_raw_jobs()
    pending = get_pending_jobs()
    approved = get_approved_jobs()
    rejected = get_rejected_jobs()

    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    week_start = (now - timedelta(days=7)).isoformat()

    # Count by source using aggregation
    source_pipeline = [
        {"$group": {"_id": "$source", "count": {"$sum": 1}}}
    ]
    source_counts = {
        doc["_id"] or "unknown": doc["count"]
        for doc in raw.aggregate(source_pipeline)
    }

    return JobStats(
        total_raw=raw.count_documents({}),
        total_pending=pending.count_documents({}),
        total_approved=approved.count_documents({}),
        total_rejected=rejected.count_documents({}),
        jobs_by_source=source_counts,
        jobs_today=raw.count_documents({"ingested_at": {"$gte": today_start}}),
        jobs_this_week=raw.count_documents({"ingested_at": {"$gte": week_start}}),
    )


@router.get("/rejected", response_model=PaginatedResponse)
async def get_rejected_jobs_list(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    q: Optional[str] = Query(None, max_length=200),
    current_user: UserInDB = Depends(require_viewer_or_admin)
):
    """
    Get paginated list of rejected jobs.

    Requires viewer or admin role.
    """
    rejected = get_rejected_jobs()
    skip = (page - 1) * per_page

    filter_q = {}
    if q:
        safe_q = sanitize_search_query(q)
        filter_q["$or"] = [
            {"title": {"$regex": safe_q, "$options": "i"}},
            {"company": {"$regex": safe_q, "$options": "i"}}
        ]

    total = rejected.count_documents(filter_q)
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1

    docs = list(
        rejected.find(filter_q)
        .sort("rejected_at", -1)
        .skip(skip)
        .limit(per_page)
    )

    docs = [convert_objectid(doc) for doc in docs]

    return PaginatedResponse(
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        data=docs
    )

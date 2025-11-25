"""
Job ingestion router for receiving job data from scrapers.
"""
from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError
import logging

from app.db import get_raw_jobs, get_pending_jobs
from app.schemas.job import JobCreate, JobBatchCreate
from app.schemas.responses import SuccessResponse, BatchResult
from app.utils.processing import (
    parse_posted_date,
    clean_salary,
    normalize_location,
    tag_source
)
from app.utils.hashing import compute_hash

router = APIRouter(prefix="/ingest", tags=["Ingestion"])
logger = logging.getLogger(__name__)


def process_job(job_data: JobCreate) -> dict:
    """
    Process a job and prepare it for database insertion.

    Applies the following transformations:
    - Compute deduplication hash
    - Parse posted date to ISO format
    - Clean and structure salary information
    - Normalize/geocode location
    - Generate tags based on content
    - Add ingestion timestamp

    Args:
        job_data: Raw job data from scraper

    Returns:
        Processed job dict ready for insertion
    """
    job_dict = job_data.model_dump()

    # Compute deduplication hash first (before modifications)
    job_dict["dedupe_hash"] = compute_hash(job_dict)

    # Process fields
    job_dict["posted_date_parsed"] = parse_posted_date(job_dict.get("posted_date"))
    job_dict["salary_parsed"] = clean_salary(job_dict.get("salary"))
    job_dict["location_normalized"] = normalize_location(job_dict.get("location"))
    job_dict["tags"] = tag_source(job_dict)
    job_dict["ingested_at"] = datetime.now(timezone.utc).isoformat()

    return job_dict


@router.post("", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def ingest_job(job: JobCreate):
    """
    Ingest a single job posting.

    The job will be:
    1. Processed (dates parsed, salary cleaned, location geocoded, tags generated)
    2. Stored in raw_jobs collection (archive)
    3. Stored in pending_jobs collection (for approval)

    Duplicate jobs (same title, company, location, posted_date) are rejected.

    Returns success response with dedupe_hash for reference.
    """
    job_dict = process_job(job)
    raw_jobs = get_raw_jobs()
    pending_jobs = get_pending_jobs()

    try:
        # Insert into raw_jobs (archive) - make a copy since MongoDB modifies the dict
        raw_jobs.insert_one(job_dict.copy())

        # Insert into pending_jobs (for review)
        pending_jobs.insert_one(job_dict)

        logger.info(f"Job ingested: {job.title} at {job.company}")

        return SuccessResponse(
            message="Job received successfully",
            data={"dedupe_hash": job_dict["dedupe_hash"]}
        )

    except DuplicateKeyError:
        logger.info(f"Duplicate job skipped: {job.title} at {job.company}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Job already exists (duplicate detected by dedupe_hash)"
        )

    except Exception as e:
        logger.exception(f"Database insert error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database insert failed"
        )


@router.post("/batch", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def ingest_jobs_batch(batch: JobBatchCreate):
    """
    Ingest multiple job postings in a single request.

    More efficient than individual requests when ingesting many jobs.
    Each job is processed independently - failures don't affect other jobs.

    - **jobs**: List of job objects (max 100 per request)

    Returns summary of results:
    - **inserted**: Number of jobs successfully inserted
    - **duplicates**: Number of duplicate jobs skipped
    - **errors**: Number of jobs that failed due to errors
    """
    raw_jobs = get_raw_jobs()
    pending_jobs = get_pending_jobs()

    results = BatchResult()

    for job in batch.jobs:
        job_dict = process_job(job)
        try:
            raw_jobs.insert_one(job_dict.copy())
            pending_jobs.insert_one(job_dict)
            results.inserted += 1

        except DuplicateKeyError:
            results.duplicates += 1
            logger.debug(f"Duplicate job in batch: {job.title} at {job.company}")

        except Exception as e:
            results.errors += 1
            logger.error(f"Error inserting job {job.title}: {e}")

    logger.info(
        f"Batch ingest completed: {results.inserted} inserted, "
        f"{results.duplicates} duplicates, {results.errors} errors"
    )

    return SuccessResponse(
        message=f"Batch processing complete: {results.inserted} inserted, "
                f"{results.duplicates} duplicates, {results.errors} errors",
        data=results.model_dump()
    )

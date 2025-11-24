# backend/app/routers/ingest.py

from fastapi import APIRouter, HTTPException
from datetime import datetime

from app.db import raw_jobs, pending_jobs
from app.schemas.job import Job

from app.utils.processing import (
    parse_posted_date,
    clean_salary,
    normalize_location,
    tag_source
)
from app.utils.hashing import compute_hash

import logging

router = APIRouter()
logger = logging.getLogger("ingest")

@router.post("/ingest")
def ingest_job(job: Job):
    job_dict = job.dict()

    # processing
    job_dict["posted_date_parsed"] = parse_posted_date(job_dict.get("posted_date"))
    job_dict["salary_parsed"] = clean_salary(job_dict.get("salary"))
    job_dict["location_normalized"] = normalize_location(job_dict.get("location"))
    job_dict["tags"] = tag_source(job_dict)
    job_dict["ingested_at"] = datetime.utcnow().isoformat()
    job_dict["dedupe_hash"] = compute_hash(job_dict)

    try:
        raw_jobs.insert_one(job_dict)
        pending_jobs.insert_one(job_dict)
    except Exception as e:
        logger.exception("DB insert error: %s", e)
        raise HTTPException(status_code=500, detail="DB insert failed")

    return {"status": "success", "msg": "Job received"}

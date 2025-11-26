# scrapers/run_scrapers.py
"""
Job scraper orchestrator - fetches jobs from legal public APIs
and sends them to the backend for processing.

Legal APIs used:
- RemoteOK: https://remoteok.com/api
- Remotive: https://remotive.com/api/remote-jobs
- Arbeitnow: https://www.arbeitnow.com/api/job-board-api
"""
import logging
import requests
from datetime import datetime
from typing import List, Tuple, Optional

from config import BACKEND_URL, BATCH_SIZE
from sites.remoteok_api import fetch_remoteok_jobs
from sites.remotive_api import fetch_remotive_jobs
from sites.arbeitnow_api import fetch_arbeitnow_jobs, fetch_arbeitnow_all_pages

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("run_scrapers")


def send_batch_to_backend(jobs: List[dict]) -> Tuple[Optional[int], dict]:
    """
    Send a batch of jobs to the backend via /ingest/batch endpoint.

    Args:
        jobs: List of job dictionaries

    Returns:
        Tuple of (status_code, response_dict)
    """
    try:
        response = requests.post(
            f"{BACKEND_URL}/ingest/batch",
            json={"jobs": jobs},
            timeout=120  # 2 minutes for larger batches
        )
        return response.status_code, response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to send batch to backend: {e}")
        return None, {"error": str(e)}


def send_single_to_backend(job: dict) -> Tuple[Optional[int], str]:
    """
    Send a single job to the backend via /ingest endpoint.

    Args:
        job: Job dictionary

    Returns:
        Tuple of (status_code, response_text)
    """
    try:
        response = requests.post(
            f"{BACKEND_URL}/ingest",
            json=job,
            timeout=30
        )
        return response.status_code, response.text
    except requests.RequestException as e:
        logger.error(f"Failed to send job to backend: {e}")
        return None, str(e)


def run_all_scrapers() -> List[dict]:
    """
    Run all legal API scrapers and collect jobs.

    Returns:
        List of all fetched job dictionaries
    """
    logger.info("Starting job scraper run...")
    all_jobs = []

    # Fetch from RemoteOK
    logger.info("Fetching jobs from RemoteOK...")
    try:
        remoteok_jobs = fetch_remoteok_jobs()
        all_jobs.extend(remoteok_jobs)
        logger.info(f"RemoteOK: {len(remoteok_jobs)} jobs")
    except Exception as e:
        logger.error(f"RemoteOK scraper failed: {e}")

    # Fetch from Remotive
    # Note: May fail due to SSL/proxy issues in some corporate networks
    logger.info("Fetching jobs from Remotive...")
    try:
        remotive_jobs = fetch_remotive_jobs(limit=200)
        all_jobs.extend(remotive_jobs)
        logger.info(f"Remotive: {len(remotive_jobs)} jobs")
    except Exception as e:
        logger.warning(f"Remotive scraper failed (may be network/SSL issue): {e}")

    # Fetch from Arbeitnow (multiple pages)
    logger.info("Fetching jobs from Arbeitnow...")
    try:
        arbeitnow_jobs = fetch_arbeitnow_all_pages(max_pages=3)
        all_jobs.extend(arbeitnow_jobs)
        logger.info(f"Arbeitnow: {len(arbeitnow_jobs)} jobs")
    except Exception as e:
        logger.error(f"Arbeitnow scraper failed: {e}")

    logger.info(f"Total jobs fetched: {len(all_jobs)}")
    return all_jobs


def run_and_send() -> dict:
    """
    Run all scrapers and send jobs to backend in batches.

    Returns:
        Summary statistics
    """
    all_jobs = run_all_scrapers()

    if not all_jobs:
        logger.warning("No jobs fetched from any source")
        return {"total_fetched": 0, "batches_sent": 0, "successful": 0, "failed": 0}

    # Send in batches
    total_batches = (len(all_jobs) + BATCH_SIZE - 1) // BATCH_SIZE
    successful = 0
    failed = 0
    new_jobs = 0
    duplicates = 0

    logger.info(f"Sending {len(all_jobs)} jobs in {total_batches} batches...")

    for i in range(0, len(all_jobs), BATCH_SIZE):
        batch = all_jobs[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1

        status, response = send_batch_to_backend(batch)

        if status in (200, 201):  # 200 OK or 201 Created
            successful += 1
            # Backend returns: {"data": {"inserted": N, "duplicates": N, "errors": N}}
            data = response.get("data", {})
            batch_new = data.get("inserted", 0)
            batch_dup = data.get("duplicates", 0)
            new_jobs += batch_new
            duplicates += batch_dup
            logger.info(f"Batch {batch_num}/{total_batches}: {batch_new} new, {batch_dup} duplicates")
        else:
            failed += 1
            logger.error(f"Batch {batch_num}/{total_batches} failed (status {status}): {response}")

    summary = {
        "total_fetched": len(all_jobs),
        "batches_sent": total_batches,
        "successful_batches": successful,
        "failed_batches": failed,
        "new_jobs": new_jobs,
        "duplicates": duplicates
    }

    logger.info(f"Scraper run complete: {summary}")
    return summary


def run_all_scrapers_for_date_range(start_date, end_date) -> List[dict]:
    """
    Run scrapers and filter jobs by date range.
    Used by scheduler for incremental scraping.

    Args:
        start_date: Start date (datetime.date)
        end_date: End date (datetime.date)

    Returns:
        List of jobs within date range
    """
    logger.info(f"Scheduler-run scraping for {start_date} to {end_date}")
    all_jobs = run_all_scrapers()

    filtered = []
    for job in all_jobs:
        posted = job.get("posted_date")
        if not posted:
            continue
        try:
            posted_dt = datetime.strptime(posted, "%Y-%m-%d").date()
        except ValueError:
            continue
        if start_date <= posted_dt <= end_date:
            filtered.append(job)

    logger.info(f"Filtered to {len(filtered)} jobs within date range")

    # Send filtered jobs
    if filtered:
        for i in range(0, len(filtered), BATCH_SIZE):
            batch = filtered[i:i + BATCH_SIZE]
            send_batch_to_backend(batch)

    return filtered


if __name__ == "__main__":
    run_and_send()

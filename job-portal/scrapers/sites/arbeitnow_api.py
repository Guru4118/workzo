# scrapers/sites/arbeitnow_api.py
import logging
import requests
from typing import List, Optional
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ARBEITNOW_API, REQUEST_TIMEOUT, POLITE_DELAY_MIN, POLITE_DELAY_MAX
from utils.scraper_utils import polite_sleep

logger = logging.getLogger("arbeitnow_api")


def fetch_arbeitnow_jobs(page: int = 1) -> List[dict]:
    """
    Fetch jobs from Arbeitnow public API.

    API: https://www.arbeitnow.com/api/job-board-api
    Supports pagination with ?page= parameter.
    Jobs from ATS systems: Greenhouse, Lever, SmartRecruiters, etc.

    Args:
        page: Page number (1-indexed)

    Returns:
        List of normalized job dictionaries
    """
    jobs = []

    try:
        headers = {
            "User-Agent": "JobPortalScraper/1.0 (contact@jobportal.com)",
            "Accept": "application/json"
        }

        params = {"page": page}

        response = requests.get(
            ARBEITNOW_API,
            headers=headers,
            params=params,
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()

        data = response.json()
        job_listings = data.get("data", [])

        for item in job_listings:
            try:
                job = normalize_arbeitnow_job(item)
                if job:
                    jobs.append(job)
            except Exception as e:
                logger.warning(f"Failed to parse Arbeitnow job: {e}")
                continue

        logger.info(f"Fetched {len(jobs)} jobs from Arbeitnow (page {page})")
        polite_sleep(POLITE_DELAY_MIN, POLITE_DELAY_MAX)

    except requests.RequestException as e:
        logger.error(f"Failed to fetch Arbeitnow jobs: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error fetching Arbeitnow jobs: {e}")

    return jobs


def fetch_arbeitnow_all_pages(max_pages: int = 5) -> List[dict]:
    """
    Fetch jobs from multiple pages of Arbeitnow.

    Args:
        max_pages: Maximum number of pages to fetch

    Returns:
        List of all normalized job dictionaries
    """
    all_jobs = []

    for page in range(1, max_pages + 1):
        jobs = fetch_arbeitnow_jobs(page=page)
        if not jobs:
            # No more jobs, stop pagination
            break
        all_jobs.extend(jobs)
        polite_sleep(POLITE_DELAY_MIN, POLITE_DELAY_MAX)

    logger.info(f"Fetched {len(all_jobs)} total jobs from Arbeitnow ({max_pages} pages max)")
    return all_jobs


def normalize_arbeitnow_job(item: dict) -> Optional[dict]:
    """
    Normalize Arbeitnow job data to standard format.

    Arbeitnow fields: slug, company_name, title, description, remote,
                      url, tags, job_types, location, created_at
    """
    # Required fields - handle both string and other types
    title = item.get("title", "")
    if isinstance(title, str):
        title = title.strip()
    else:
        title = str(title) if title else ""

    company = item.get("company_name", "")
    if isinstance(company, str):
        company = company.strip()
    else:
        company = str(company) if company else ""

    apply_url = item.get("url", "")
    if isinstance(apply_url, str):
        apply_url = apply_url.strip()
    else:
        apply_url = str(apply_url) if apply_url else ""

    if not title or not company or not apply_url:
        return None

    # Location
    location = item.get("location", "")
    if isinstance(location, str):
        location = location.strip()
    else:
        location = str(location) if location else ""
    if not location:
        location = "Not specified"

    # Remote flag
    is_remote = item.get("remote", False)
    if is_remote and "remote" not in location.lower():
        location = f"{location} (Remote)" if location != "Not specified" else "Remote"

    # Posted date - created_at is a Unix timestamp (integer)
    posted_date = None
    created_at = item.get("created_at")
    if created_at:
        try:
            if isinstance(created_at, int):
                posted_date = datetime.fromtimestamp(created_at).date().isoformat()
            elif isinstance(created_at, str):
                posted_date = datetime.fromisoformat(created_at.replace("Z", "+00:00")).date().isoformat()
        except Exception:
            pass

    # Job type
    job_types = item.get("job_types", [])
    if isinstance(job_types, list) and job_types:
        jt = job_types[0]
        job_type = str(jt).lower().replace("_", "-") if jt else "full-time"
    else:
        job_type = "full-time"

    # Tags
    tags = item.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    elif isinstance(tags, list):
        tags = [str(t) for t in tags if t]

    # Description (HTML)
    description = item.get("description", "")
    if not isinstance(description, str):
        description = str(description) if description else ""

    return {
        "title": title,
        "company": company,
        "location": location,
        "apply_url": apply_url,
        "posted_date": posted_date,
        "source": "arbeitnow",
        "description": description,
        "salary": None,
        "job_type": job_type,
        "tags": tags,
        "remote": is_remote
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    jobs = fetch_arbeitnow_jobs(page=1)
    print(f"Fetched {len(jobs)} jobs from Arbeitnow")
    if jobs:
        print(f"Sample job: {jobs[0]['title']} at {jobs[0]['company']}")

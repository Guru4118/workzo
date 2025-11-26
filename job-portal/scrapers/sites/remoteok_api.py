# scrapers/sites/remoteok_api.py
import logging
import requests
from typing import List, Optional
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import REMOTEOK_API, REQUEST_TIMEOUT, POLITE_DELAY_MIN, POLITE_DELAY_MAX
from utils.scraper_utils import polite_sleep, to_iso_date

logger = logging.getLogger("remoteok_api")


def fetch_remoteok_jobs() -> List[dict]:
    """
    Fetch jobs from RemoteOK public API.

    API: https://remoteok.com/api
    Returns JSON array where first element is metadata (skip it).

    Returns:
        List of normalized job dictionaries
    """
    jobs = []

    try:
        headers = {
            "User-Agent": "JobPortalScraper/1.0 (contact@jobportal.com)",
            "Accept": "application/json"
        }

        response = requests.get(
            REMOTEOK_API,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()

        data = response.json()

        # First element is metadata/legal notice, skip it
        job_listings = data[1:] if len(data) > 1 else []

        for item in job_listings:
            try:
                job = normalize_remoteok_job(item)
                if job:
                    jobs.append(job)
            except Exception as e:
                logger.warning(f"Failed to parse RemoteOK job: {e}")
                continue

        logger.info(f"Fetched {len(jobs)} jobs from RemoteOK")
        polite_sleep(POLITE_DELAY_MIN, POLITE_DELAY_MAX)

    except requests.RequestException as e:
        logger.error(f"Failed to fetch RemoteOK jobs: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error fetching RemoteOK jobs: {e}")

    return jobs


def normalize_remoteok_job(item: dict) -> Optional[dict]:
    """
    Normalize RemoteOK job data to standard format.

    RemoteOK fields: id, slug, company, company_logo, position, tags,
                     location, description, url, date, salary_min, salary_max
    """
    # Required fields
    title = item.get("position", "").strip()
    company = item.get("company", "").strip()

    if not title or not company:
        return None

    # Location - default to "Remote" if not specified
    location = item.get("location", "").strip() or "Remote"

    # Apply URL
    apply_url = item.get("url", "")
    if not apply_url and item.get("slug"):
        apply_url = f"https://remoteok.com/remote-jobs/{item['slug']}"

    if not apply_url:
        return None

    # Posted date
    posted_date = None
    if item.get("date"):
        posted_date = to_iso_date(item["date"])

    # Salary
    salary = None
    salary_min = item.get("salary_min")
    salary_max = item.get("salary_max")
    if salary_min and salary_max:
        salary = f"${salary_min:,} - ${salary_max:,}"
    elif salary_min:
        salary = f"${salary_min:,}+"
    elif salary_max:
        salary = f"Up to ${salary_max:,}"

    # Tags/skills
    tags = item.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]

    # Description (HTML)
    description = item.get("description", "")

    return {
        "title": title,
        "company": company,
        "location": location,
        "apply_url": apply_url,
        "posted_date": posted_date,
        "source": "remoteok",
        "description": description,
        "salary": salary,
        "job_type": "full-time",
        "tags": tags,
        "remote": True
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    jobs = fetch_remoteok_jobs()
    print(f"Fetched {len(jobs)} jobs from RemoteOK")
    if jobs:
        print(f"Sample job: {jobs[0]['title']} at {jobs[0]['company']}")

# scrapers/sites/remotive_api.py
import logging
import requests
from typing import List, Optional

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import REMOTIVE_API, REQUEST_TIMEOUT, POLITE_DELAY_MIN, POLITE_DELAY_MAX
from utils.scraper_utils import polite_sleep, to_iso_date

logger = logging.getLogger("remotive_api")

# Available categories on Remotive
REMOTIVE_CATEGORIES = [
    "software-dev",
    "customer-support",
    "design",
    "marketing",
    "sales",
    "product",
    "business",
    "data",
    "devops",
    "finance-legal",
    "hr",
    "qa",
    "writing",
    "all-others"
]


def fetch_remotive_jobs(category: Optional[str] = None, limit: int = 100) -> List[dict]:
    """
    Fetch jobs from Remotive public API.

    API: https://remotive.com/api/remote-jobs
    Query params: category, limit, search

    Args:
        category: Job category (e.g., "software-dev", "marketing")
        limit: Maximum number of jobs to fetch

    Returns:
        List of normalized job dictionaries
    """
    jobs = []

    try:
        headers = {
            "User-Agent": "JobPortalScraper/1.0 (contact@jobportal.com)",
            "Accept": "application/json"
        }

        params = {"limit": limit}
        if category and category in REMOTIVE_CATEGORIES:
            params["category"] = category

        response = requests.get(
            REMOTIVE_API,
            headers=headers,
            params=params,
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()

        data = response.json()
        job_listings = data.get("jobs", [])

        for item in job_listings:
            try:
                job = normalize_remotive_job(item)
                if job:
                    jobs.append(job)
            except Exception as e:
                logger.warning(f"Failed to parse Remotive job: {e}")
                continue

        logger.info(f"Fetched {len(jobs)} jobs from Remotive (category: {category or 'all'})")
        polite_sleep(POLITE_DELAY_MIN, POLITE_DELAY_MAX)

    except requests.RequestException as e:
        logger.error(f"Failed to fetch Remotive jobs: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error fetching Remotive jobs: {e}")

    return jobs


def fetch_all_remotive_categories(limit_per_category: int = 50) -> List[dict]:
    """
    Fetch jobs from all Remotive categories.

    Args:
        limit_per_category: Maximum jobs per category

    Returns:
        List of all normalized job dictionaries (deduplicated)
    """
    all_jobs = []
    seen_urls = set()

    for category in REMOTIVE_CATEGORIES:
        jobs = fetch_remotive_jobs(category=category, limit=limit_per_category)
        for job in jobs:
            if job["apply_url"] not in seen_urls:
                seen_urls.add(job["apply_url"])
                all_jobs.append(job)
        polite_sleep(POLITE_DELAY_MIN, POLITE_DELAY_MAX)

    logger.info(f"Fetched {len(all_jobs)} total jobs from all Remotive categories")
    return all_jobs


def normalize_remotive_job(item: dict) -> Optional[dict]:
    """
    Normalize Remotive job data to standard format.

    Remotive fields: id, url, title, company_name, company_logo, category,
                     candidate_required_location, salary, publication_date,
                     job_type, description, tags
    """
    # Required fields
    title = item.get("title", "").strip()
    company = item.get("company_name", "").strip()
    apply_url = item.get("url", "").strip()

    if not title or not company or not apply_url:
        return None

    # Location
    location = item.get("candidate_required_location", "").strip()
    if not location:
        location = "Worldwide"

    # Posted date
    posted_date = None
    if item.get("publication_date"):
        posted_date = to_iso_date(item["publication_date"])

    # Salary
    salary = item.get("salary", "")
    if salary:
        salary = salary.strip()

    # Job type
    job_type = item.get("job_type", "").lower().replace("_", "-")
    if not job_type:
        job_type = "full-time"

    # Tags
    tags = item.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]

    # Category as tag
    category = item.get("category", "")
    if category and category not in tags:
        tags.append(category)

    # Description (HTML)
    description = item.get("description", "")

    return {
        "title": title,
        "company": company,
        "location": location,
        "apply_url": apply_url,
        "posted_date": posted_date,
        "source": "remotive",
        "description": description,
        "salary": salary if salary else None,
        "job_type": job_type,
        "tags": tags,
        "remote": True
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Test single category
    jobs = fetch_remotive_jobs(category="software-dev", limit=10)
    print(f"Fetched {len(jobs)} software dev jobs from Remotive")
    if jobs:
        print(f"Sample job: {jobs[0]['title']} at {jobs[0]['company']}")

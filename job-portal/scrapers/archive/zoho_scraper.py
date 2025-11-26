# scrapers/sites/zoho_scraper.py
import logging
import time
from typing import List
from bs4 import BeautifulSoup
from scrapers.utils.scraper_utils import requests_session, maybe_upload_snapshot, polite_sleep

logger = logging.getLogger("zoho_scraper")
BASE = "https://careers.zohocorp.com"

def scrape_zoho(max_pages=3, sleep_between=1) -> List[dict]:
    s = requests_session()
    jobs = []
    list_url = f"{BASE}/jobs"
    try:
        r = s.get(list_url, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        # Zoho sometimes uses JSON embed; try job card selectors first
        cards = soup.select(".job-card, .job-listing, .jobItem, li.job")
        for c in cards:
            try:
                title = (c.select_one(".job-title") or c.select_one("a")).get_text(strip=True) if c.select_one("a") else None
                company = "Zoho"
                location = c.select_one(".job-location") and c.select_one(".job-location").get_text(strip=True) or None
                a = c.select_one("a")
                apply_url = a["href"] if a and a.has_attr("href") else None
                raw_html = str(c)
                snapshot_url = maybe_upload_snapshot(raw_html, "zoho")
                jobs.append({
                    "title": title,
                    "company": company,
                    "location": location,
                    "apply_url": apply_url,
                    "posted_date": None,
                    "source": "zoho",
                    "snapshot_url": snapshot_url
                })
            except Exception:
                logger.exception("Zoho parse error for one card")
        polite_sleep(0.8, sleep_between + 0.5)
    except Exception:
        logger.exception("Zoho listings fetch failed")
    return jobs

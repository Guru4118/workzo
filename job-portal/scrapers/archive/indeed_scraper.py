# scrapers/sites/indeed_scraper.py
import logging
import time
from typing import List
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode
from scrapers.utils.scraper_utils import maybe_upload_snapshot, to_iso_date, requests_session, polite_sleep

logger = logging.getLogger("indeed_scraper")
BASE = "https://www.indeed.com"

def scrape_indeed(query="software engineer", location="India", max_pages=3, sleep_between=1) -> List[dict]:
    s = requests_session()
    jobs = []
    for page in range(max_pages):
        params = {"q": query, "l": location, "start": page * 10}
        url = f"{BASE}/jobs?{urlencode(params)}"
        try:
            r = s.get(url, timeout=20)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            cards = soup.select(".jobsearch-SerpJobCard, .result, .job_seen_beacon")
            for c in cards:
                try:
                    title_tag = c.select_one("h2.jobTitle") or c.select_one("a.jobtitle")
                    title = title_tag.get_text(strip=True) if title_tag else None

                    comp = c.select_one(".company") or c.select_one(".companyName")
                    company = comp.get_text(strip=True) if comp else None

                    loc = c.select_one(".location") or c.select_one(".companyLocation")
                    location_text = loc.get_text(strip=True) if loc else None

                    a = c.select_one("a")
                    href = a["href"] if a and a.has_attr("href") else None
                    apply_url = urljoin(BASE, href) if href else None

                    date_tag = c.select_one(".date") or c.select_one(".result-link-bar span.date")
                    posted_date = to_iso_date(date_tag.get_text(strip=True)) if date_tag else None

                    raw_html = str(c)
                    snapshot_url = maybe_upload_snapshot(raw_html, "indeed")

                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": location_text,
                        "apply_url": apply_url,
                        "posted_date": posted_date,
                        "source": "indeed",
                        "snapshot_url": snapshot_url
                    })
                except Exception:
                    logger.exception("Failed to parse one Indeed card")
            polite_sleep(0.8, sleep_between + 0.5)
        except Exception:
            logger.exception("Failed to fetch Indeed page %s", url)
            time.sleep(2)
    return jobs

# scrapers/utils/scraper_utils.py
import time
import hashlib
import logging
import random
from datetime import datetime
from typing import Optional
from requests.adapters import HTTPAdapter, Retry
import requests

logger = logging.getLogger("scraper_utils")
logging.getLogger("urllib3").setLevel(logging.WARNING)

USER_AGENTS = [
    # a short list — expand if needed
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
]

def random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

def requests_session(retries=3, backoff_factor=0.5, status_forcelist=(500,502,503,504)):
    s = requests.Session()
    r = Retry(total=retries, backoff_factor=backoff_factor,
              status_forcelist=status_forcelist, allowed_methods=["GET","POST"])
    s.mount("https://", HTTPAdapter(max_retries=r))
    s.mount("http://", HTTPAdapter(max_retries=r))
    s.headers.update(random_headers())
    return s

def to_iso_date(date_str: str) -> Optional[str]:
    if not date_str:
        return None
    date_str = date_str.strip()
    fmts = ["%Y-%m-%d", "%d-%m-%Y", "%d %b %Y", "%b %d, %Y", "%d %B %Y", "%Y/%m/%d", "%d %b, %Y"]
    for f in fmts:
        try:
            return datetime.strptime(date_str, f).date().isoformat()
        except:
            pass
    try:
        from dateutil import parser
        return parser.parse(date_str, fuzzy=True).date().isoformat()
    except Exception:
        return None

def compute_job_hash(job: dict) -> str:
    key = (job.get("title","")+"|"+job.get("company","")+"|"+job.get("location","")+"|"+str(job.get("posted_date",""))).strip().lower()
    return hashlib.sha256(key.encode("utf-8")).hexdigest()

def maybe_upload_snapshot(html: str, source: str) -> Optional[str]:
    """
    Tries to call backend MinIO upload helper if available in sys.path (app.utils.minio_client.upload_html_snapshot).
    If not available, returns None.
    """
    try:
        from app.utils.minio_client import upload_html_snapshot
        url = upload_html_snapshot(html, source)
        return url
    except Exception:
        logger.debug("MinIO upload not available or failed; skipping snapshot")
        return None

def polite_sleep(min_s=0.6, max_s=1.5):
    time.sleep(random.uniform(min_s, max_s))

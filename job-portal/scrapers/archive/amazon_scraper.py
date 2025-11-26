# scrapers/sites/amazon_scraper.py
import logging
import time
from typing import List
from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
from scrapers.utils.scraper_utils import maybe_upload_snapshot, polite_sleep

logger = logging.getLogger("amazon_scraper")
BASE = "https://www.amazon.jobs"

def scrape_amazon(keyword="software development", max_pages=3, headless=True, sleep_between=1) -> List[dict]:
    jobs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        try:
            start_url = f"{BASE}/en/search?keyword={keyword.replace(' ', '+')}"
            page.goto(start_url, timeout=60000)
            for pg in range(max_pages):
                page.wait_for_load_state("networkidle", timeout=30000)
                items = page.query_selector_all(".job-tile, .job-card, .job")
                for it in items:
                    try:
                        title = it.query_selector(".job-title, h3") and it.query_selector(".job-title, h3").inner_text().strip()
                        company = "Amazon"
                        loc = it.query_selector(".job-location") and it.query_selector(".job-location").inner_text().strip()
                        a = it.query_selector("a")
                        href = a.get_attribute("href") if a else None
                        apply_url = urljoin(BASE, href) if href else None
                        raw_html = it.inner_html()
                        snapshot_url = maybe_upload_snapshot(raw_html, "amazon")
                        jobs.append({
                            "title": title,
                            "company": company,
                            "location": loc,
                            "apply_url": apply_url,
                            "posted_date": None,
                            "source": "amazon",
                            "snapshot_url": snapshot_url
                        })
                    except Exception:
                        logger.exception("Amazon item parse failed")
                # click next if exists
                nxt = page.query_selector("a[aria-label='Next'], a.next, button.next")
                if nxt:
                    try:
                        nxt.click()
                        page.wait_for_load_state("networkidle", timeout=30000)
                        polite_sleep(0.8, sleep_between + 0.5)
                    except:
                        break
                else:
                    break
        except Exception:
            logger.exception("Amazon scraping error")
        finally:
            browser.close()
    return jobs

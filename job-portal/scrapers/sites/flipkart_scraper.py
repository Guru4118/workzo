# scrapers/sites/flipkart_scraper.py
import logging
from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
from scrapers.utils.scraper_utils import maybe_upload_snapshot, polite_sleep
import time

logger = logging.getLogger("flipkart_scraper")
BASE = "https://www.flipkartcareers.com"

def scrape_flipkart(max_pages=3, headless=True, sleep_between=1):
    jobs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        try:
            page.goto(BASE, timeout=60000)
            for page_no in range(max_pages):
                page.wait_for_load_state("networkidle", timeout=30000)
                cards = page.query_selector_all(".job-card, .career-card, .job-listing-item")
                for c in cards:
                    try:
                        title = c.query_selector(".title, .job-title") and c.query_selector(".title, .job-title").inner_text().strip()
                        company = "Flipkart"
                        location = c.query_selector(".location, .job-location") and c.query_selector(".location, .job-location").inner_text().strip()
                        a = c.query_selector("a")
                        href = a.get_attribute("href") if a else None
                        apply_url = urljoin(BASE, href) if href else None
                        raw_html = c.inner_html()
                        snapshot_url = maybe_upload_snapshot(raw_html, "flipkart")
                        jobs.append({
                            "title": title,
                            "company": company,
                            "location": location,
                            "apply_url": apply_url,
                            "posted_date": None,
                            "source": "flipkart",
                            "snapshot_url": snapshot_url
                        })
                    except Exception:
                        logger.exception("Flipkart card parse failed")
                # pagination attempt
                next_btn = page.query_selector("a.next, button.next, .pagination-next")
                if next_btn:
                    try:
                        next_btn.click()
                        page.wait_for_load_state("networkidle", timeout=30000)
                        polite_sleep(0.8, sleep_between + 0.5)
                    except:
                        break
                else:
                    break
        except Exception:
            logger.exception("Flipkart scraping failed")
        finally:
            browser.close()
    return jobs

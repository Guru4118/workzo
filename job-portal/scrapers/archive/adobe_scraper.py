# scrapers/sites/adobe_scraper.py
import logging
from playwright.sync_api import sync_playwright
from scrapers.utils.scraper_utils import maybe_upload_snapshot, polite_sleep

logger = logging.getLogger("adobe_scraper")
BASE = "https://careers.adobe.com"

def scrape_adobe(max_pages=3, headless=True, sleep_between=1):
    jobs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        try:
            page.goto(BASE, timeout=60000)
            for pg in range(max_pages):
                page.wait_for_load_state("networkidle", timeout=30000)
                cards = page.query_selector_all(".job-card, .job, .opening")
                for c in cards:
                    try:
                        title = c.query_selector(".title, h3") and c.query_selector(".title, h3").inner_text().strip()
                        company = "Adobe"
                        location = c.query_selector(".location") and c.query_selector(".location").inner_text().strip()
                        a = c.query_selector("a")
                        href = a.get_attribute("href") if a else None
                        apply_url = href
                        raw_html = c.inner_html()
                        snapshot_url = maybe_upload_snapshot(raw_html, "adobe")
                        jobs.append({
                            "title": title,
                            "company": company,
                            "location": location,
                            "apply_url": apply_url,
                            "posted_date": None,
                            "source": "adobe",
                            "snapshot_url": snapshot_url
                        })
                    except Exception:
                        logger.exception("Adobe job parse failed")
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
            logger.exception("Adobe scraping failed")
        finally:
            browser.close()
    return jobs

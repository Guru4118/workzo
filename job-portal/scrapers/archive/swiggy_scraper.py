# scrapers/sites/swiggy_scraper.py
import logging
from playwright.sync_api import sync_playwright
from scrapers.utils.scraper_utils import maybe_upload_snapshot, polite_sleep

logger = logging.getLogger("swiggy_scraper")
BASE = "https://careers.swiggy.com"

def scrape_swiggy(max_pages=3, headless=True, sleep_between=1):
    jobs = []
    # Swiggy often exposes API endpoints — but we'll use Playwright to be robust
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        try:
            page.goto(BASE, timeout=60000)
            for pg in range(max_pages):
                page.wait_for_load_state("networkidle", timeout=30000)
                cards = page.query_selector_all(".job, .job-card, .career-card")
                for c in cards:
                    try:
                        title = c.query_selector(".job-title, h3") and c.query_selector(".job-title, h3").inner_text().strip()
                        company = "Swiggy"
                        location = c.query_selector(".location") and c.query_selector(".location").inner_text().strip()
                        a = c.query_selector("a")
                        href = a.get_attribute("href") if a else None
                        apply_url = href
                        raw_html = c.inner_html()
                        snapshot_url = maybe_upload_snapshot(raw_html, "swiggy")
                        jobs.append({
                            "title": title,
                            "company": company,
                            "location": location,
                            "apply_url": apply_url,
                            "posted_date": None,
                            "source": "swiggy",
                            "snapshot_url": snapshot_url
                        })
                    except Exception:
                        logger.exception("Swiggy job parse failed")
                next_btn = page.query_selector("a.next, button.next")
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
            logger.exception("Swiggy scraping failed")
        finally:
            browser.close()
    return jobs

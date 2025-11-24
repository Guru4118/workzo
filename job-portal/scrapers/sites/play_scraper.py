# scrapers/sites/play_scraper.py
from playwright.sync_api import sync_playwright
import logging
from urllib.parse import urljoin
from time import sleep

logger = logging.getLogger("scraper")

def scrape_dynamic_site(start_url, max_pages=5):
    jobs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(start_url, timeout=60000)
            current = 0
            while current < max_pages:
                logger.info("Scraping page %s", current + 1)
                # adjust selectors per site
                items = page.query_selector_all(".job-card")
                for it in items:
                    try:
                        title = it.query_selector(".job-title").inner_text().strip()
                        company = it.query_selector(".company").inner_text().strip()
                        link = urljoin(start_url, it.query_selector("a").get_attribute("href"))
                        raw_html = it.inner_html()
                        jobs.append({
                            "title": title,
                            "company": company,
                            "apply_url": link,
                            "raw_html": raw_html,
                            "source": "play_site"
                        })
                    except Exception as e:
                        logger.exception("Item parse error: %s", e)

                # try clicking next or break
                next_btn = page.query_selector("a.next")
                if next_btn and "disabled" not in next_btn.get_attribute("class") and current+1 < max_pages:
                    next_btn.click()
                    page.wait_for_load_state("networkidle", timeout=60000)
                    sleep(1)
                    current += 1
                else:
                    break
        except Exception as e:
            logger.exception("Page scrape failed: %s", e)
        finally:
            browser.close()
    return jobs

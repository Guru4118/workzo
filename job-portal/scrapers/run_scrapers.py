# scrapers/run_scrapers.py
import requests
from datetime import datetime
from sites.indeed_scraper import scrape_indeed
from sites.zoho_scraper import scrape_zoho
from sites.amazon_scraper import scrape_amazon
from sites.flipkart_scraper import scrape_flipkart
from sites.swiggy_scraper import scrape_swiggy
from sites.adobe_scraper import scrape_adobe

def send_to_backend(job):
    try:
        res = requests.post("http://127.0.0.1:8000/ingest", json=job, timeout=30)
        return res.status_code, res.text
    except Exception as e:
        return None, str(e)

def run_all_scrapers():
    print("Running all scrapers...")
    jobs = []
    jobs += scrape_indeed(max_pages=2)
    jobs += scrape_zoho(max_pages=2)
    jobs += scrape_amazon(max_pages=2)
    jobs += scrape_flipkart(max_pages=2)
    jobs += scrape_swiggy(max_pages=2)
    jobs += scrape_adobe(max_pages=2)
    # send to backend
    for job in jobs:
        status, text = send_to_backend(job)
        print("Sent job:", job.get("title"), "status:", status)
    return jobs

def run_all_scrapers_for_date_range(start_date, end_date):
    print("Scheduler-run scraping for", start_date, "to", end_date)
    all_jobs = run_all_scrapers()
    filtered = []
    for job in all_jobs:
        posted = job.get("posted_date")
        if not posted:
            continue
        try:
            posted_dt = datetime.strptime(posted, "%Y-%m-%d").date()
        except:
            continue
        if start_date <= posted_dt <= end_date:
            filtered.append(job)
    # send filtered to backend (already sent above in run_all_scrapers; adjust if needed)
    return filtered

if __name__ == "__main__":
    run_all_scrapers()

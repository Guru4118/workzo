import os
import sys

# -----------------------------------------
# FIX: Add project root to sys.path
# -----------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCRAPERS_DIR = os.path.join(BASE_DIR, "scrapers")

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if SCRAPERS_DIR not in sys.path:
    sys.path.insert(0, SCRAPERS_DIR)

print("PYTHONPATH:", sys.path)   # debug output

# Now safe to import
from run_scrapers import run_all_scrapers_for_date_range

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta


def start_scheduler():
    scheduler = BackgroundScheduler()

    @scheduler.scheduled_job("cron", hour=2, minute=0)
    def scheduled_scrape():
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)

        print("Scheduler executing...")
        run_all_scrapers_for_date_range(start_date=yesterday, end_date=today)

    scheduler.start()

"""
Background scheduler for automated job scraping.
"""
import logging
import sys
import os
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import Optional

logger = logging.getLogger(__name__)

# Module-level scheduler instance
_scheduler: Optional[BackgroundScheduler] = None


def run_daily_scrape():
    """
    Execute daily scraping job.

    Runs all scrapers for the previous day and today,
    then sends results to the backend ingest endpoint.
    """
    try:
        # Add scrapers to path dynamically
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        scrapers_dir = os.path.join(base_dir, "scrapers")

        if base_dir not in sys.path:
            sys.path.insert(0, base_dir)
        if scrapers_dir not in sys.path:
            sys.path.insert(0, scrapers_dir)

        # Import scraper module
        from run_scrapers import run_all_scrapers_for_date_range

        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)

        logger.info(f"Starting scheduled scrape for {yesterday} to {today}")
        run_all_scrapers_for_date_range(start_date=yesterday, end_date=today)
        logger.info("Scheduled scrape completed successfully")

    except ImportError as e:
        logger.error(f"Failed to import scraper module: {e}")
    except Exception as e:
        logger.exception(f"Scheduled scrape failed: {e}")


def start_scheduler():
    """
    Start the background scheduler.

    Schedules:
    - Daily scrape at 2:00 AM UTC
    """
    global _scheduler

    if _scheduler is not None:
        logger.warning("Scheduler already running, skipping start")
        return

    _scheduler = BackgroundScheduler(
        timezone="UTC",
        job_defaults={
            "coalesce": True,  # Combine missed runs into one
            "max_instances": 1,  # Only one instance at a time
            "misfire_grace_time": 3600,  # 1 hour grace period for missed jobs
        }
    )

    # Schedule daily scrape at 2 AM UTC
    _scheduler.add_job(
        run_daily_scrape,
        CronTrigger(hour=2, minute=0, timezone="UTC"),
        id="daily_scrape",
        name="Daily Job Scraping",
        replace_existing=True
    )

    _scheduler.start()
    logger.info("Background scheduler started - Daily scrape scheduled for 2:00 AM UTC")


def stop_scheduler():
    """
    Stop the background scheduler gracefully.
    """
    global _scheduler

    if _scheduler is not None:
        logger.info("Stopping background scheduler...")
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("Background scheduler stopped")
    else:
        logger.debug("Scheduler not running, nothing to stop")


def get_scheduler_status() -> dict:
    """
    Get the current scheduler status and scheduled jobs.

    Returns:
        Dictionary with scheduler state and job information
    """
    if _scheduler is None:
        return {"status": "stopped", "jobs": []}

    jobs = []
    for job in _scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
        })

    return {
        "status": "running",
        "jobs": jobs
    }


def trigger_scrape_now():
    """
    Manually trigger an immediate scrape job.
    Useful for testing or manual updates.
    """
    logger.info("Manual scrape triggered")
    run_daily_scrape()

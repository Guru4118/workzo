# scrapers/config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Backend Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# Adzuna API (optional - requires free registration)
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID", "")
ADZUNA_API_KEY = os.getenv("ADZUNA_API_KEY", "")

# Request Settings
REQUEST_TIMEOUT = 30
POLITE_DELAY_MIN = 1.0
POLITE_DELAY_MAX = 2.0

# Batch Settings
BATCH_SIZE = 25  # Smaller batches for reliable processing

# API Endpoints
REMOTEOK_API = "https://remoteok.com/api"
REMOTIVE_API = "https://remotive.com/api/remote-jobs"
ARBEITNOW_API = "https://www.arbeitnow.com/api/job-board-api"
ADZUNA_API_BASE = "https://api.adzuna.com/v1/api/jobs"

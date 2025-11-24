from pymongo import MongoClient
from dotenv import load_dotenv
import certifi
import os
from pathlib import Path

# Load .env from the app directory
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

MONGO_URI = os.getenv("MONGO_URI")

# Debug: print to verify it's loaded (remove after testing)
if not MONGO_URI:
    print("WARNING: MONGO_URI not found in environment variables")
else:
    print(f"MONGO_URI loaded: {MONGO_URI[:20]}...")

client = MongoClient(
    MONGO_URI,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=5000,
    socketTimeoutMS=5000
)
db = client["job_portal"]

raw_jobs = db["raw_jobs"]
pending_jobs = db["pending_jobs"]
approved_jobs = db["approved_jobs"]

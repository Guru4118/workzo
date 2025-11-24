# backend/app/utils/hashing.py
import hashlib
import json

def compute_hash(job_dict: dict) -> str:
    parts = {
        "title": (job_dict.get("title") or "").strip().lower(),
        "company": (job_dict.get("company") or "").strip().lower(),
        "location": (job_dict.get("location") or "").strip().lower(),
        "posted_date": (job_dict.get("posted_date") or "").strip().lower(),
    }
    raw = json.dumps(parts, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

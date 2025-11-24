from fastapi import APIRouter
from app.db import pending_jobs, approved_jobs

router = APIRouter()

@router.get("/admin/pending")
def get_pending_jobs(page: int = 1, per_page: int = 20, q: str = None):
    skip = (page - 1) * per_page
    filter_q = {}
    if q:
        # simple text match on title/company
        filter_q = {"$or": [{"title": {"$regex": q, "$options": "i"}}, {"company": {"$regex": q, "$options": "i"}}]}
    total = pending_jobs.count_documents(filter_q)
    docs = list(pending_jobs.find(filter_q, {"_id": 0}).skip(skip).limit(per_page))
    return {"page": page, "per_page": per_page, "total": total, "jobs": docs}


@router.post("/admin/approve/{title}")
def approve_job(title: str):
    job = pending_jobs.find_one({"title": title})
    if job:
        approved_jobs.insert_one(job)
        pending_jobs.delete_one({"title": title})
        return {"status": "approved"}

    return {"status": "not_found"}

@router.get("/jobs")
def get_approved_jobs():
    return list(approved_jobs.find({}, {"_id": 0}))


@router.get("/admin/search")
def search_jobs(q: str = "", page: int = 1, per_page: int = 20):
    filter_q = {"$text": {"$search": q}} if q else {}
    skip = (page - 1) * per_page
    docs = list(pending_jobs.find(filter_q, {"_id":0}).skip(skip).limit(per_page))
    return {"jobs": docs}



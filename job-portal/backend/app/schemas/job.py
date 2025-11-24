from pydantic import BaseModel
from typing import Optional

class Job(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    apply_url: Optional[str] = None
    posted_date: Optional[str] = None
    salary: Optional[str] = None
    source: Optional[str] = None
    raw_snapshot_url: Optional[str] = None

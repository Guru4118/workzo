from pydantic import BaseModel
from typing import Optional, List

class Job(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    description: Optional[str] = None
    apply_url: Optional[str] = None
    posted_date: Optional[str] = None
    source: Optional[str] = None

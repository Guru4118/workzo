"""
Job schemas for ingestion, storage, and API responses.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict
from datetime import datetime


class SalaryParsed(BaseModel):
    """Schema for parsed salary information."""
    min: Optional[int] = None
    max: Optional[int] = None


class LocationNormalized(BaseModel):
    """Schema for normalized/geocoded location."""
    raw: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    display_name: Optional[str] = None


class JobBase(BaseModel):
    """Base job schema with common fields."""
    title: str = Field(..., min_length=1, max_length=500)
    company: str = Field(..., min_length=1, max_length=200)
    location: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=50000)
    apply_url: Optional[str] = Field(None, max_length=2000)
    posted_date: Optional[str] = Field(None, max_length=100)
    salary: Optional[str] = Field(None, max_length=200)
    source: Optional[str] = Field(None, max_length=50)
    raw_snapshot_url: Optional[str] = Field(None, max_length=500)

    @field_validator("title", "company")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        """Strip leading/trailing whitespace from required fields."""
        return v.strip() if v else v


class JobCreate(JobBase):
    """Schema for creating/ingesting a new job."""
    pass


class JobInDB(JobBase):
    """Schema for job as stored in database."""
    id: Optional[str] = None
    dedupe_hash: Optional[str] = None
    posted_date_parsed: Optional[str] = None
    salary_parsed: Optional[SalaryParsed] = None
    location_normalized: Optional[LocationNormalized] = None
    tags: List[str] = []
    ingested_at: Optional[str] = None

    # Approval fields
    approved_at: Optional[str] = None
    approved_by: Optional[str] = None

    # Rejection fields
    rejected_at: Optional[str] = None
    rejected_by: Optional[str] = None
    rejection_reason: Optional[str] = None


class JobResponse(JobInDB):
    """Schema for job API response."""
    pass


class JobBatchCreate(BaseModel):
    """Schema for batch job ingestion."""
    jobs: List[JobCreate] = Field(..., min_length=1, max_length=100)


class JobApproval(BaseModel):
    """Schema for job approval request."""
    job_id: str = Field(..., min_length=1)


class JobRejection(BaseModel):
    """Schema for job rejection request."""
    job_id: str = Field(..., min_length=1)
    reason: str = Field(..., min_length=1, max_length=500)


class BulkJobApproval(BaseModel):
    """Schema for bulk job approval request."""
    job_ids: List[str] = Field(..., min_length=1, max_length=100)


class BulkJobRejection(BaseModel):
    """Schema for bulk job rejection request."""
    job_ids: List[str] = Field(..., min_length=1, max_length=100)
    reason: str = Field(..., min_length=1, max_length=500)


class JobStats(BaseModel):
    """Schema for job statistics response."""
    total_raw: int
    total_pending: int
    total_approved: int
    total_rejected: int
    jobs_by_source: Dict[str, int]
    jobs_today: int
    jobs_this_week: int

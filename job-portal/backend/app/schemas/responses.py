"""
Standard API response schemas for consistent response formatting.
"""
from pydantic import BaseModel
from typing import Optional, Any, List, Dict


class ErrorDetail(BaseModel):
    """Schema for validation error details."""
    loc: Optional[List[str]] = None
    msg: str
    type: str


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    detail: str
    errors: Optional[List[ErrorDetail]] = None


class SuccessResponse(BaseModel):
    """Schema for successful operation responses."""
    message: str
    data: Optional[Any] = None


class PaginatedResponse(BaseModel):
    """Schema for paginated list responses."""
    page: int
    per_page: int
    total: int
    total_pages: int
    data: List[Any]


class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: str
    version: str
    environment: str


class ReadyResponse(BaseModel):
    """Schema for readiness check response."""
    status: str
    database: str
    storage: Optional[str] = None


class BatchResult(BaseModel):
    """Schema for batch operation results."""
    inserted: int = 0
    duplicates: int = 0
    errors: int = 0


class BulkOperationResult(BaseModel):
    """Schema for bulk operation results (approve/reject)."""
    success: int = 0
    not_found: int = 0
    errors: int = 0

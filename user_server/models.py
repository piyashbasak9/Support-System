"""
Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class AskRequest(BaseModel):
    """Request model for ask endpoint."""
    query: str = Field(..., min_length=1, max_length=5000)
    # file is handled separately in Form data


class AskResponse(BaseModel):
    """Response model for ask endpoint."""
    status: str  # "success" or "ticket_created"
    answer: Optional[str] = None
    ticket_id: Optional[str] = None
    message: Optional[str] = None
    sources: Optional[List[dict]] = None


class Source(BaseModel):
    """Source information for retrieved chunks."""
    chunk_id: str
    text: str
    score: float
    metadata: dict


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: datetime
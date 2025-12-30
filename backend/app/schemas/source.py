"""
Pydantic schemas for text ingestion API.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SourceTextRequest(BaseModel):
    """Request to ingest German text."""
    text: str = Field(..., min_length=1, max_length=500, description="German text to analyze")
    source_name: Optional[str] = Field(None, description="Optional name/title of source")
    source_url: Optional[str] = Field(None, description="Optional URL of source")


class ExtractedItemSummary(BaseModel):
    """Summary of an extracted item."""
    id: int
    canonical_form: str
    type: str
    source_sentence: Optional[str] = None


class ExtractedEdgeSummary(BaseModel):
    """Summary of an extracted edge."""
    source: str
    target: str
    type: str


class SourceTextResponse(BaseModel):
    """Response from text ingestion."""
    status: str
    items_extracted: int
    edges_created: int
    items: List[ExtractedItemSummary]
    edges: List[ExtractedEdgeSummary] = Field(default_factory=list)

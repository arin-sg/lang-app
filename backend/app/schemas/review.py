"""
Pydantic schemas for review API.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ReviewItem(BaseModel):
    """A single item in the review deck."""
    item_id: int
    type: str
    canonical_form: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    last_seen: Optional[str] = None


class ReviewDeckResponse(BaseModel):
    """Response containing review deck."""
    deck: List[ReviewItem]
    total_items: int


class ReviewResultRequest(BaseModel):
    """Request to record a review result."""
    item_id: int
    correct: bool
    prompt: str
    actual_answer: str
    expected_answer: str
    response_time_ms: int = 0


class ReviewResultResponse(BaseModel):
    """Response after recording review result."""
    encounter_id: int
    item_id: int
    correct: bool
    timestamp: str

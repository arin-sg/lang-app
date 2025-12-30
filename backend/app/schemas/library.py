"""
Pydantic schemas for library/collection view API.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ItemStats(BaseModel):
    """Statistics for a single item's learning history."""
    total_encounters: int = Field(0, description="Total times this item was encountered")
    correct_count: int = Field(0, description="Number of correct responses")
    incorrect_count: int = Field(0, description="Number of incorrect responses")
    success_rate: float = Field(0.0, description="Percentage of correct responses (0.0-1.0)")
    last_seen: Optional[str] = Field(None, description="Timestamp of last encounter")


class LibraryItemSummary(BaseModel):
    """Summary of an item for library list view (rich preview)."""
    item_id: int
    type: str = Field(..., description="Item type: word, chunk, or pattern")
    canonical_form: str = Field(..., description="Dictionary/base form")
    english_gloss: Optional[str] = Field(None, description="English translation/meaning")
    cefr_level: Optional[str] = Field(None, description="CEFR proficiency level (A1-C2)")
    gender: Optional[str] = Field(None, description="Grammatical gender (der/die/das)")
    stats: ItemStats = Field(..., description="Learning statistics")
    created_at: str = Field(..., description="When item was first ingested")


class RelatedItem(BaseModel):
    """An item related to another through an edge."""
    item_id: int
    canonical_form: str
    english_gloss: Optional[str] = None
    relation_type: str = Field(..., description="Raw relation type from edge")
    relation_label: str = Field(..., description="Human-friendly label")


class EncounterSummary(BaseModel):
    """Summary of a single encounter."""
    encounter_id: int
    mode: str = Field(..., description="Context: review, drill, chat, extract")
    correct: bool
    timestamp: str
    response_time_ms: Optional[int] = None
    context_sentence: Optional[str] = Field(None, description="Source sentence where item was encountered")


class LibraryItemDetail(BaseModel):
    """Full details for a single item including relationships."""
    item_id: int
    type: str
    canonical_form: str
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Full metadata JSON")
    stats: ItemStats
    related_items: List[RelatedItem] = Field(default_factory=list)
    recent_encounters: List[EncounterSummary] = Field(default_factory=list, description="Last 5 encounters")
    created_at: str


class LibraryResponse(BaseModel):
    """Paginated list of library items."""
    items: List[LibraryItemSummary]
    total_count: int = Field(..., description="Total items matching filter")
    has_more: bool = Field(..., description="Whether more items exist beyond this page")


class DeleteItemsRequest(BaseModel):
    """Request to delete one or more items."""
    item_ids: List[int] = Field(..., description="List of item IDs to delete", min_length=1)


class DeleteItemsResponse(BaseModel):
    """Response after deleting items."""
    deleted_items: int = Field(..., description="Number of items deleted")
    deleted_encounters: int = Field(..., description="Number of encounters deleted")
    deleted_edges: int = Field(..., description="Number of edges deleted")
    message: str = Field(..., description="Success message")

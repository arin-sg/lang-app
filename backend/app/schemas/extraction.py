"""
Pydantic schemas for LLM extraction output.
Matches the PRD Section 6.1 JSON structure.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ExtractionEvidence(BaseModel):
    """Evidence for where an item appears in the text."""
    sentence_idx: int
    sentence: str
    left_context: str = ""
    right_context: str = ""


class ExtractionMetadata(BaseModel):
    """Metadata about an extracted item."""
    gender: Optional[str] = None
    plural: Optional[str] = None
    pos_hint: Optional[str] = None
    cefr_guess: Optional[str] = None


class ExtractionItem(BaseModel):
    """A single extracted learnable item."""
    type: str = Field(..., description="Type: word, chunk, or pattern")
    surface_form: str = Field(..., description="EXACT form as it appears in text")
    canonical: str = Field(..., description="The canonical form (for backward compatibility)")
    english_gloss: str = Field(..., description="English translation/meaning")
    pos_hint: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    why_worth_learning: Optional[str] = None
    evidence: ExtractionEvidence


class ExtractionEdge(BaseModel):
    """A relationship between two items."""
    src_canonical: str
    dst_canonical: str
    type: str = Field(..., description="Relationship type")
    weight: Optional[float] = Field(None, ge=0.0, le=1.0)
    note: Optional[str] = None


class ExtractionSentence(BaseModel):
    """A sentence from the input text."""
    idx: int
    text: str


class ExtractionOutput(BaseModel):
    """Complete output from LLM extraction."""
    sentences: List[ExtractionSentence]
    items: List[ExtractionItem]
    edges: List[ExtractionEdge] = Field(default_factory=list)


class ExtractionError(Exception):
    """Raised when extraction fails."""
    pass


class VerifiedExtractionItem(BaseModel):
    """Item after verification and canonicalization."""
    type: str
    surface_form: str = Field(..., description="As extracted from text")
    canonical_form: str = Field(..., description="Computed lemma/base form")
    english_gloss: str
    pos_hint: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    why_worth_learning: Optional[str] = None
    evidence: ExtractionEvidence
    existing_item_id: Optional[int] = Field(None, description="If deduplicated, ID of existing item")


class VerifiedExtractionOutput(BaseModel):
    """Complete verified extraction output."""
    sentences: List[ExtractionSentence]
    items: List[VerifiedExtractionItem]
    edges: List[ExtractionEdge]
    verification_stats: Dict[str, int] = Field(..., description="Statistics: hallucinated, verified, deduplicated")

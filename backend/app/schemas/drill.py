"""
Pydantic schemas for drill generation and grading.
"""
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class DrillType(str, Enum):
    """Types of drill exercises."""
    CLOZE = "cloze"
    PATTERN = "pattern"
    SABOTEUR = "saboteur"


class DrillRequest(BaseModel):
    """Request to grade a drill answer."""
    drill_type: DrillType
    user_answer: str
    target_lemma: str = Field(..., description="Canonical form of the target item")
    context: Optional[str] = None  # Original sentence for cloze
    question_meta: Dict[str, Any] = Field(default_factory=dict)


class DrillGradeResult(BaseModel):
    """Result of grading a drill."""
    is_correct: bool
    feedback: str = Field(..., description="Explanation for the user")
    detected_error_type: Optional[str] = None  # e.g., "error_case", "error_gender"


class DrillResponse(BaseModel):
    """A generated drill question."""
    type: DrillType
    question: str = Field(..., description="The drill prompt/question")
    target_id: int = Field(..., description="Item ID being drilled")
    target_lemma: str = Field(..., description="Canonical form")
    meta: Dict[str, Any] = Field(
        default_factory=dict,
        description="Hints, original sentence, error focus, etc."
    )

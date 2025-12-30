"""
API endpoints for review functionality.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.review import (
    ReviewDeckResponse,
    ReviewItem,
    ReviewResultRequest,
    ReviewResultResponse
)
from app.services.review_service import get_review_service
from app.services.graph_store import get_graph_store

router = APIRouter(prefix="/review", tags=["review"])


@router.get("/today", response_model=ReviewDeckResponse)
def get_review_deck(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get today's review deck.

    For Iteration 1: Returns least recently seen items.
    """
    try:
        graph_store = get_graph_store(db)
        review_service = get_review_service(db, graph_store)

        deck_items = review_service.generate_deck(limit=limit)

        # Convert to response model
        review_items = [
            ReviewItem(**item)
            for item in deck_items
        ]

        return ReviewDeckResponse(
            deck=review_items,
            total_items=len(review_items)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate review deck: {str(e)}"
        )


@router.post("/result", response_model=ReviewResultResponse)
def record_review_result(
    request: ReviewResultRequest,
    db: Session = Depends(get_db)
):
    """
    Record the result of a review attempt.
    """
    try:
        graph_store = get_graph_store(db)
        review_service = get_review_service(db, graph_store)

        result = review_service.record_result(
            item_id=request.item_id,
            correct=request.correct,
            prompt=request.prompt,
            actual_answer=request.actual_answer,
            expected_answer=request.expected_answer,
            response_time_ms=request.response_time_ms
        )

        return ReviewResultResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to record review result: {str(e)}"
        )

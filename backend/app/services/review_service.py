"""
Review Service - Manages review deck generation and result recording.
"""
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.services.graph_store import GraphStore


class ReviewService:
    """Service for review deck operations."""

    def __init__(self, db: Session, graph_store: GraphStore):
        """
        Initialize with dependencies.

        Args:
            db: Database session
            graph_store: Graph store for database operations
        """
        self.db = db
        self.graph_store = graph_store

    def generate_deck(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Generate a review deck.

        For Iteration 1: Simple prioritization (least recently seen items).

        Args:
            limit: Maximum number of items in deck

        Returns:
            List of item dictionaries ready for review
        """
        return self.graph_store.get_items_for_review(limit=limit)

    def record_result(
        self,
        item_id: int,
        correct: bool,
        prompt: str,
        actual_answer: str,
        expected_answer: str,
        response_time_ms: int = 0
    ) -> Dict[str, Any]:
        """
        Record the result of a review attempt.

        Args:
            item_id: ID of the item being reviewed
            correct: Whether the answer was correct
            prompt: The question/prompt shown
            actual_answer: User's answer
            expected_answer: The correct answer
            response_time_ms: Time taken to respond

        Returns:
            Dictionary with encounter details
        """
        encounter = self.graph_store.create_encounter(
            item_id=item_id,
            mode='review',
            correct=correct,
            prompt=prompt,
            actual_answer=actual_answer,
            expected_answer=expected_answer,
            response_time_ms=response_time_ms
        )

        return {
            'encounter_id': encounter.id,
            'item_id': encounter.item_id,
            'correct': encounter.correct,
            'timestamp': encounter.timestamp.isoformat()
        }


def get_review_service(db: Session, graph_store: GraphStore) -> ReviewService:
    """Factory function to get a ReviewService instance."""
    return ReviewService(db, graph_store)

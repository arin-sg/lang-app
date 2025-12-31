"""
Graph Store - Data access layer for all database operations.

This module provides CRUD operations for the graph-shaped database,
abstracting all direct database interactions.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import json

from app.models import Item, Edge, Encounter


class GraphStore:
    """Repository pattern for graph database operations."""

    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db

    # ==================== ITEM OPERATIONS ====================

    def upsert_item(
        self,
        canonical_form: str,
        item_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Item:
        """
        Create or update an item.

        Args:
            canonical_form: The base form of the item
            item_type: Type of item (word, chunk, pattern)
            metadata: Optional metadata dictionary

        Returns:
            The created or updated Item
        """
        # Check if item already exists
        existing_item = self.db.query(Item).filter(
            Item.canonical_form == canonical_form,
            Item.type == item_type
        ).first()

        if existing_item:
            # Update existing item
            if metadata:
                existing_item.metadata_json = json.dumps(metadata)
            existing_item.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing_item)
            return existing_item
        else:
            # Create new item
            new_item = Item(
                type=item_type,
                canonical_form=canonical_form,
                metadata_json=json.dumps(metadata) if metadata else None
            )
            self.db.add(new_item)
            self.db.commit()
            self.db.refresh(new_item)
            return new_item

    def get_item_by_id(self, item_id: int) -> Optional[Item]:
        """Get an item by ID."""
        return self.db.query(Item).filter(Item.id == item_id).first()

    def get_item_by_canonical(self, canonical_form: str) -> Optional[Item]:
        """Get an item by its canonical form."""
        return self.db.query(Item).filter(Item.canonical_form == canonical_form).first()

    def get_all_items(self, limit: int = 100) -> List[Item]:
        """Get all items with optional limit."""
        return self.db.query(Item).limit(limit).all()

    # ==================== EDGE OPERATIONS ====================

    def upsert_edge(
        self,
        source_id: int,
        target_id: int,
        relation_type: str,
        weight: Optional[float] = None
    ) -> Edge:
        """
        Create or update an edge between two items.

        Args:
            source_id: Source item ID
            target_id: Target item ID
            relation_type: Type of relationship
            weight: Optional relationship strength (0.0-1.0)

        Returns:
            The created or updated Edge
        """
        # Check if edge already exists
        existing_edge = self.db.query(Edge).filter(
            Edge.source_id == source_id,
            Edge.target_id == target_id,
            Edge.relation_type == relation_type
        ).first()

        if existing_edge:
            # Update weight if provided
            if weight is not None:
                existing_edge.weight = weight
            self.db.commit()
            self.db.refresh(existing_edge)
            return existing_edge
        else:
            # Create new edge
            new_edge = Edge(
                source_id=source_id,
                target_id=target_id,
                relation_type=relation_type,
                weight=weight
            )
            self.db.add(new_edge)
            self.db.commit()
            self.db.refresh(new_edge)
            return new_edge

    def get_edges_for_item(self, item_id: int) -> List[Edge]:
        """Get all edges where item is source or target."""
        return self.db.query(Edge).filter(
            (Edge.source_id == item_id) | (Edge.target_id == item_id)
        ).all()

    # ==================== ENCOUNTER OPERATIONS ====================

    def create_encounter(
        self,
        item_id: int,
        mode: str,
        correct: bool,
        prompt: Optional[str] = None,
        actual_answer: Optional[str] = None,
        expected_answer: Optional[str] = None,
        context_sentence: Optional[str] = None,
        error_type: Optional[str] = None,
        confusion_target_id: Optional[int] = None,
        response_time_ms: Optional[int] = None
    ) -> Encounter:
        """
        Create a new encounter (learning event).

        Args:
            item_id: The item being practiced
            mode: Context (review, drill, chat)
            correct: Whether the answer was correct
            prompt: The question/prompt
            actual_answer: User's answer
            expected_answer: Correct answer
            context_sentence: Full sentence context
            error_type: Classified error type
            confusion_target_id: ID of confused item (if applicable)
            response_time_ms: Response time in milliseconds

        Returns:
            The created Encounter
        """
        encounter = Encounter(
            item_id=item_id,
            mode=mode,
            correct=correct,
            prompt=prompt,
            actual_answer=actual_answer,
            expected_answer=expected_answer,
            context_sentence=context_sentence,
            error_type=error_type,
            confusion_target_id=confusion_target_id,
            response_time_ms=response_time_ms
        )
        self.db.add(encounter)
        self.db.commit()
        self.db.refresh(encounter)
        return encounter

    def get_encounters_for_item(self, item_id: int, limit: int = 50) -> List[Encounter]:
        """Get encounters for a specific item, most recent first."""
        return self.db.query(Encounter).filter(
            Encounter.item_id == item_id
        ).order_by(desc(Encounter.timestamp)).limit(limit).all()

    def get_item_encounters(
        self,
        item_id: int,
        limit: int = 10,
        mode_filter: Optional[str] = None
    ) -> List[Encounter]:
        """
        Get encounters for a specific item with optional mode filtering.

        Args:
            item_id: Item ID
            limit: Max encounters to return
            mode_filter: Optional filter by mode (e.g., 'extract', 'review', 'drill')

        Returns:
            List of Encounter objects
        """
        query = self.db.query(Encounter).filter(
            Encounter.item_id == item_id
        )

        if mode_filter:
            query = query.filter(Encounter.mode == mode_filter)

        query = query.order_by(desc(Encounter.timestamp)).limit(limit)

        return query.all()

    # ==================== REVIEW DECK OPERATIONS ====================

    def get_items_for_review(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get items for review deck.
        For Iteration 1: Simple prioritization (least recently seen).

        Args:
            limit: Maximum number of items to return

        Returns:
            List of item dictionaries with last_seen timestamp
        """
        # Query items with their last encounter timestamp
        query = (
            self.db.query(
                Item,
                func.max(Encounter.timestamp).label('last_seen')
            )
            .outerjoin(Encounter, Item.id == Encounter.item_id)
            .group_by(Item.id)
            .order_by(func.coalesce(func.max(Encounter.timestamp), '1970-01-01'))
            .limit(limit)
        )

        items = []
        for item, last_seen in query:
            # Parse metadata JSON
            metadata = {}
            if item.metadata_json:
                try:
                    metadata = json.loads(item.metadata_json)
                except json.JSONDecodeError:
                    metadata = {}

            items.append({
                'item_id': item.id,
                'type': item.type,
                'canonical_form': item.canonical_form,
                'metadata': metadata,
                'last_seen': last_seen.isoformat() if last_seen else None
            })

        return items

    # ==================== STATISTICS ====================

    def get_item_stats(self, item_id: int) -> Dict[str, Any]:
        """Get statistics for an item."""
        # Count total encounters
        total = self.db.query(Encounter).filter(
            Encounter.item_id == item_id
        ).count()

        # Count correct/incorrect
        correct = self.db.query(Encounter).filter(
            Encounter.item_id == item_id,
            Encounter.correct == True
        ).count()

        incorrect = total - correct

        # Get most recent encounter
        recent = self.db.query(Encounter).filter(
            Encounter.item_id == item_id
        ).order_by(desc(Encounter.timestamp)).first()

        return {
            'total_encounters': total,
            'correct_count': correct,
            'incorrect_count': incorrect,
            'success_rate': correct / total if total > 0 else 0.0,
            'last_seen': recent.timestamp.isoformat() if recent else None
        }


    # ==================== LIBRARY OPERATIONS ====================

    def get_all_items_with_stats(
        self,
        limit: int = 50,
        offset: int = 0,
        type_filter: Optional[str] = None
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        Get paginated list of items with learning statistics.

        Args:
            limit: Maximum items to return
            offset: Number of items to skip
            type_filter: Filter by item type (word, chunk, pattern)

        Returns:
            Tuple of (items_list, total_count)
        """
        # Build base query
        base_query = self.db.query(Item)

        # Apply type filter if provided
        if type_filter:
            base_query = base_query.filter(Item.type == type_filter)

        # Get total count
        total_count = base_query.count()

        # Get items with stats
        query = (
            base_query
            .outerjoin(Encounter, Item.id == Encounter.item_id)
            .group_by(Item.id)
            .order_by(desc(Item.created_at))
            .limit(limit)
            .offset(offset)
        )

        items = []
        for item in query:
            # Parse metadata
            metadata = {}
            if item.metadata_json:
                try:
                    metadata = json.loads(item.metadata_json)
                except json.JSONDecodeError:
                    metadata = {}

            # Get stats for this item
            stats = self.get_item_stats(item.id)

            items.append({
                'item_id': item.id,
                'type': item.type,
                'canonical_form': item.canonical_form,
                'english_gloss': metadata.get('english_gloss'),
                'cefr_level': metadata.get('cefr_guess'),
                'gender': metadata.get('gender'),
                'stats': stats,
                'created_at': item.created_at.isoformat()
            })

        return items, total_count

    def get_item_detail_with_relations(self, item_id: int) -> Optional[Dict[str, Any]]:
        """
        Get full item details including relationships and history.

        Args:
            item_id: ID of the item to retrieve

        Returns:
            Dictionary with full item details, or None if not found
        """
        # Get the item
        item = self.db.query(Item).filter(Item.id == item_id).first()
        if not item:
            return None

        # Parse metadata
        metadata = {}
        if item.metadata_json:
            try:
                metadata = json.loads(item.metadata_json)
            except json.JSONDecodeError:
                metadata = {}

        # Get stats
        stats = self.get_item_stats(item_id)

        # Get edges and related items
        edges = self.get_edges_for_item(item_id)
        related_items = []

        # Relation type to human-friendly label mapping
        relation_labels = {
            'collocates_with': 'Often used with',
            'confusable_with': "Don't confuse with",
            'near_synonym': 'Similar meaning',
            'governs_case': 'Grammar rule',
            'minimal_pair': 'Similar sounding'
        }

        for edge in edges:
            # Get the related item (either source or target)
            related_id = edge.target_id if edge.source_id == item_id else edge.source_id
            related_item = self.db.query(Item).filter(Item.id == related_id).first()

            if related_item:
                # Parse related item metadata
                related_metadata = {}
                if related_item.metadata_json:
                    try:
                        related_metadata = json.loads(related_item.metadata_json)
                    except json.JSONDecodeError:
                        related_metadata = {}

                related_items.append({
                    'item_id': related_item.id,
                    'canonical_form': related_item.canonical_form,
                    'english_gloss': related_metadata.get('english_gloss'),
                    'relation_type': edge.relation_type,
                    'relation_label': relation_labels.get(edge.relation_type, edge.relation_type)
                })

        # Get recent encounters (last 5)
        encounters = self.get_encounters_for_item(item_id, limit=5)
        encounter_summaries = []
        for enc in encounters:
            encounter_summaries.append({
                'encounter_id': enc.id,
                'mode': enc.mode,
                'correct': enc.correct,
                'timestamp': enc.timestamp.isoformat(),
                'response_time_ms': enc.response_time_ms,
                'context_sentence': enc.context_sentence
            })

        return {
            'item_id': item.id,
            'type': item.type,
            'canonical_form': item.canonical_form,
            'metadata': metadata,
            'stats': stats,
            'related_items': related_items,
            'recent_encounters': encounter_summaries,
            'created_at': item.created_at.isoformat()
        }

    def delete_items(self, item_ids: List[int]) -> Dict[str, Any]:
        """
        Delete items and their associated data (cascade delete).

        Deletes:
        - All encounters associated with the items
        - All edges where items are source or target
        - The items themselves

        Args:
            item_ids: List of item IDs to delete

        Returns:
            Dictionary with deletion statistics
        """
        if not item_ids:
            return {
                'deleted_items': 0,
                'deleted_encounters': 0,
                'deleted_edges': 0
            }

        # Count deletions for response
        deleted_encounters = self.db.query(Encounter).filter(
            Encounter.item_id.in_(item_ids)
        ).delete(synchronize_session=False)

        deleted_edges = self.db.query(Edge).filter(
            (Edge.source_id.in_(item_ids)) | (Edge.target_id.in_(item_ids))
        ).delete(synchronize_session=False)

        deleted_items = self.db.query(Item).filter(
            Item.id.in_(item_ids)
        ).delete(synchronize_session=False)

        self.db.commit()

        return {
            'deleted_items': deleted_items,
            'deleted_encounters': deleted_encounters,
            'deleted_edges': deleted_edges
        }

    def get_item_by_id(self, item_id: int) -> Optional[Item]:
        """
        Get item by ID.

        Args:
            item_id: ID of the item

        Returns:
            Item if found, None otherwise
        """
        return self.db.query(Item).filter(Item.id == item_id).first()

    def get_items_by_type(
        self,
        item_type: str,
        limit: int = 100
    ) -> List[Item]:
        """
        Get recent items of specific type (for deduplication context).

        Args:
            item_type: Type of item (word, chunk, pattern)
            limit: Maximum number of items to return

        Returns:
            List of recent items
        """
        return self.db.query(Item)\
            .filter(Item.type == item_type)\
            .order_by(desc(Item.created_at))\
            .limit(limit)\
            .all()


def get_graph_store(db: Session) -> GraphStore:
    """Factory function to get a GraphStore instance."""
    return GraphStore(db)

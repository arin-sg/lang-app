"""
Ingest Service - Orchestrates the full text ingestion pipeline.
"""
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.services.extract_service import ExtractService
from app.services.verification_service import VerificationService
from app.services.graph_store import GraphStore
from app.schemas.extraction import ExtractionOutput, VerifiedExtractionOutput
from app.config import settings


class IngestService:
    """Service for ingesting text and storing extracted items."""

    def __init__(
        self,
        db: Session,
        extract_service: ExtractService,
        verification_service: VerificationService,
        graph_store: GraphStore
    ):
        """
        Initialize with dependencies.

        Args:
            db: Database session
            extract_service: Extraction service
            verification_service: Verification service
            graph_store: Graph store for database operations
        """
        self.db = db
        self.extract_service = extract_service
        self.verification_service = verification_service
        self.graph_store = graph_store

    async def process_text(self, text: str) -> Dict[str, Any]:
        """
        Process raw German text through the full pipeline.

        Pipeline:
        1. Extract items and edges using LLM
        2. Verify and canonicalize items (NEW)
        3. Store verified items in database
        4. Store edges in database
        5. Create initial EXTRACT_SEEN encounters

        Args:
            text: Raw German text

        Returns:
            Summary dictionary with extraction and verification results
        """
        # Step 1: Extract using LLM
        # Use batched extraction if enabled and text is long enough
        if settings.enable_parallel_batching and len(text) > 100:
            extraction: ExtractionOutput = await self.extract_service.extract_items_batched(
                text,
                batch_size=settings.batch_size_sentences,
                max_items_per_type=settings.max_items_per_type
            )
        else:
            # Fallback to single-batch extraction
            extraction: ExtractionOutput = await self.extract_service.extract_items(
                text,
                max_items_per_type=settings.max_items_per_type
            )

        # Step 2: Verify and canonicalize (NEW)
        verified: VerifiedExtractionOutput = await self.verification_service.verify_and_canonicalize(
            extraction=extraction,
            source_text=text
        )

        # Step 3: Store verified items and track item IDs
        item_id_map = {}  # Maps canonical form to database ID
        stored_items = []

        for verified_item in verified.items:
            # If item was deduplicated, reuse existing
            if verified_item.existing_item_id:
                item = self.graph_store.get_item_by_id(verified_item.existing_item_id)
            else:
                # Create new item
                # Handle pattern metadata - support both pattern_meta (new) and meta (current)
                if verified_item.type == "pattern" and verified_item.pattern_meta:
                    # NEW: Serialize pattern_meta to dict for storage
                    metadata = verified_item.pattern_meta.dict()
                else:
                    # Use generic meta (works for words/chunks/patterns)
                    metadata = verified_item.meta or {}

                # Add additional info if available
                if verified_item.pos_hint:
                    metadata['pos_hint'] = verified_item.pos_hint
                if verified_item.why_worth_learning:
                    metadata['why_worth_learning'] = verified_item.why_worth_learning
                if verified_item.english_gloss:
                    metadata['english_gloss'] = verified_item.english_gloss

                # Upsert item using canonical form
                item = self.graph_store.upsert_item(
                    canonical_form=verified_item.canonical_form,
                    item_type=verified_item.type,
                    metadata=metadata
                )

            item_id_map[verified_item.canonical_form] = item.id
            stored_items.append({
                'id': item.id,
                'canonical_form': item.canonical_form,
                'surface_form': verified_item.surface_form,  # Track what we saw
                'type': item.type,
                'was_deduplicated': verified_item.existing_item_id is not None,
                'source_sentence': verified_item.evidence.sentence  # Add source context
            })

            # Create EXTRACT_SEEN encounter with surface_form in context
            self.graph_store.create_encounter(
                item_id=item.id,
                mode='extract',
                correct=True,  # Not applicable for extraction
                context_sentence=verified_item.evidence.sentence
            )

        # Step 4: Store edges
        stored_edges = []
        for extracted_edge in verified.edges:
            # Get source and target IDs
            source_id = item_id_map.get(extracted_edge.src_canonical)
            target_id = item_id_map.get(extracted_edge.dst_canonical)

            # Only create edge if both items exist
            if source_id and target_id:
                edge = self.graph_store.upsert_edge(
                    source_id=source_id,
                    target_id=target_id,
                    relation_type=extracted_edge.type,
                    weight=extracted_edge.weight
                )
                stored_edges.append({
                    'source': extracted_edge.src_canonical,
                    'target': extracted_edge.dst_canonical,
                    'type': extracted_edge.type
                })

        # Return summary with verification stats
        return {
            'status': 'success',
            'items_extracted': len(stored_items),
            'items_hallucinated': verified.verification_stats.get('hallucinated', 0),
            'items_deduplicated': verified.verification_stats.get('deduplicated', 0),
            'edges_created': len(stored_edges),
            'items': stored_items,
            'edges': stored_edges,
            'verification_stats': verified.verification_stats
        }


def get_ingest_service(
    db: Session,
    extract_service: ExtractService,
    verification_service: VerificationService,
    graph_store: GraphStore
) -> IngestService:
    """Factory function to get an IngestService instance."""
    return IngestService(db, extract_service, verification_service, graph_store)

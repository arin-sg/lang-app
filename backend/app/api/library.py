"""
API endpoints for library/collection view.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.library import (
    LibraryResponse,
    LibraryItemSummary,
    LibraryItemDetail,
    ItemStats,
    DeleteItemsRequest,
    DeleteItemsResponse
)
from app.services.graph_store import get_graph_store

router = APIRouter(prefix="/library", tags=["library"])


@router.get("/items", response_model=LibraryResponse)
async def get_library_items(
    type_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get paginated list of learned items with statistics.

    Query Parameters:
    - type_filter: Filter by item type (word, chunk, pattern)
    - limit: Maximum items to return (default: 50, max: 100)
    - offset: Number of items to skip for pagination (default: 0)

    Returns:
    - Paginated list of items with rich preview data
    - Total count of items matching filter
    - has_more flag for pagination
    """
    # Validate type_filter
    if type_filter and type_filter not in ['word', 'chunk', 'pattern']:
        raise HTTPException(
            status_code=400,
            detail="type_filter must be one of: word, chunk, pattern"
        )

    # Limit maximum page size
    if limit > 100:
        limit = 100

    # Get graph store
    graph_store = get_graph_store(db)

    # Fetch items with stats
    items_data, total_count = graph_store.get_all_items_with_stats(
        limit=limit,
        offset=offset,
        type_filter=type_filter
    )

    # Convert to response models
    items = []
    for item_dict in items_data:
        # Extract stats dict and convert to model
        stats_dict = item_dict['stats']
        stats = ItemStats(**stats_dict)

        item = LibraryItemSummary(
            item_id=item_dict['item_id'],
            type=item_dict['type'],
            canonical_form=item_dict['canonical_form'],
            english_gloss=item_dict['english_gloss'],
            cefr_level=item_dict['cefr_level'],
            gender=item_dict['gender'],
            stats=stats,
            created_at=item_dict['created_at']
        )
        items.append(item)

    # Determine if more items exist
    has_more = (offset + limit) < total_count

    return LibraryResponse(
        items=items,
        total_count=total_count,
        has_more=has_more
    )


@router.get("/items/{item_id}", response_model=LibraryItemDetail)
async def get_item_detail(
    item_id: int,
    db: Session = Depends(get_db)
):
    """
    Get full details for a single item including relationships and history.

    Path Parameters:
    - item_id: ID of the item to retrieve

    Returns:
    - Full item details with metadata
    - Learning statistics
    - Related items (grouped by relationship type in frontend)
    - Recent encounter history (last 5)
    """
    graph_store = get_graph_store(db)

    # Get item details
    item_data = graph_store.get_item_detail_with_relations(item_id)

    if not item_data:
        raise HTTPException(
            status_code=404,
            detail=f"Item with id {item_id} not found"
        )

    # Convert to response model
    from app.schemas.library import RelatedItem, EncounterSummary

    stats = ItemStats(**item_data['stats'])

    related_items = [
        RelatedItem(**rel) for rel in item_data['related_items']
    ]

    encounters = [
        EncounterSummary(**enc) for enc in item_data['recent_encounters']
    ]

    return LibraryItemDetail(
        item_id=item_data['item_id'],
        type=item_data['type'],
        canonical_form=item_data['canonical_form'],
        metadata=item_data['metadata'],
        stats=stats,
        related_items=related_items,
        recent_encounters=encounters,
        created_at=item_data['created_at']
    )


@router.post("/delete", response_model=DeleteItemsResponse)
async def delete_items(
    request: DeleteItemsRequest,
    db: Session = Depends(get_db)
):
    """
    Delete one or more items and their associated data.

    This performs a cascade delete:
    - Deletes all encounters for the items
    - Deletes all edges where items are source or target
    - Deletes the items themselves

    Request Body:
    - item_ids: List of item IDs to delete (at least 1)

    Returns:
    - Statistics about what was deleted
    """
    graph_store = get_graph_store(db)

    # Perform deletion
    result = graph_store.delete_items(request.item_ids)

    # Construct response message
    item_word = "item" if result['deleted_items'] == 1 else "items"
    message = f"Successfully deleted {result['deleted_items']} {item_word}"

    return DeleteItemsResponse(
        deleted_items=result['deleted_items'],
        deleted_encounters=result['deleted_encounters'],
        deleted_edges=result['deleted_edges'],
        message=message
    )

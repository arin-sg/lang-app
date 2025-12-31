"""
API endpoints for drill generation and grading.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.services.graph_store import get_graph_store, GraphStore
from app.services.drill_service import get_drill_service, DrillService
from app.providers.factory import get_llm_provider, LLMTask
from app.schemas.drill import DrillResponse, DrillRequest, DrillGradeResult

router = APIRouter(prefix="/drills", tags=["drills"])


@router.get("/today", response_model=List[DrillResponse])
async def get_drill_session(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Generate a drill session for today.

    Logic:
    1. Get weakest items (future: use weakness scores)
    2. For each item, determine drill type based on:
       - Item type (word → cloze, pattern → pattern builder)
       - User error profile (future: use error history)
    3. Generate drills using DrillService

    Returns:
        List of DrillResponse objects
    """
    graph_store = get_graph_store(db)
    llm_provider = get_llm_provider(LLMTask.DRILL_GENERATION)
    drill_service = get_drill_service(llm_provider, graph_store)

    # Phase 1: Simple implementation - get least recently seen items
    items = graph_store.get_items_for_review(limit=limit)

    drills = []
    for item_dict in items:
        try:
            item_id = item_dict['item_id']
            item_type = item_dict['type']

            # Determine drill type based on item type
            if item_type == 'pattern':
                drill = await drill_service.create_pattern_drill(item_id)
            elif item_type in ['word', 'chunk']:
                # Alternate between cloze and saboteur
                if len(drills) % 2 == 0:
                    drill = await drill_service.create_cloze_drill(item_id)
                else:
                    drill = await drill_service.create_saboteur_drill(item_id)
            else:
                continue  # Skip unknown types

            drills.append(drill)
        except Exception as e:
            # Log error but continue generating other drills
            print(f"Error generating drill for item {item_id}: {e}")
            continue

    return drills


@router.post("/grade", response_model=DrillGradeResult)
async def grade_drill_answer(
    request: DrillRequest,
    db: Session = Depends(get_db)
):
    """
    Grade a drill answer and record encounter.

    Logic:
    1. Grade answer using LLM judge
    2. Record encounter with mode='drill'
    3. Return grading result with feedback

    Args:
        request: DrillRequest with user's answer

    Returns:
        DrillGradeResult with is_correct + feedback
    """
    graph_store = get_graph_store(db)
    llm_provider = get_llm_provider(LLMTask.DRILL_GENERATION)
    drill_service = get_drill_service(llm_provider, graph_store)

    # Grade the drill
    result = await drill_service.grade_drill(request)

    # Record encounter
    # Note: We need to get item_id from target_lemma
    # This requires querying by canonical_form
    item = graph_store.get_item_by_canonical(request.target_lemma)

    if item:
        graph_store.create_encounter(
            item_id=item.id,
            mode='drill',
            correct=result.is_correct,
            prompt=request.question_meta.get('question', ''),
            actual_answer=request.user_answer,
            expected_answer=request.target_lemma,
            error_type=result.detected_error_type
        )

    return result

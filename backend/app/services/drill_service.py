"""
Service for generating and grading drill exercises.
"""
import json
import re
from typing import Dict, Any, Optional
from app.providers.base import LLMProvider
from app.schemas.drill import DrillType, DrillResponse, DrillRequest, DrillGradeResult
from app.services.graph_store import GraphStore


class DrillService:
    """Service for drill generation and grading."""

    def __init__(self, llm_provider: LLMProvider, graph_store: GraphStore):
        self.llm_provider = llm_provider
        self.graph_store = graph_store

    async def create_cloze_drill(self, item_id: int) -> DrillResponse:
        """
        Generate a cloze (fill-in-the-blank) drill.

        Logic:
        1. Get item with encounters (for context sentence)
        2. Take most recent encounter's context_sentence
        3. Replace target_lemma with "________" (case-insensitive)
        4. Return DrillResponse with hint in meta

        Args:
            item_id: ID of item to drill

        Returns:
            DrillResponse with type='cloze'
        """
        item = self.graph_store.get_item_by_id(item_id)

        # Parse metadata JSON
        metadata = {}
        if item.metadata_json:
            try:
                metadata = json.loads(item.metadata_json)
            except json.JSONDecodeError:
                metadata = {}

        # Get most recent encounter for context
        encounters = self.graph_store.get_item_encounters(
            item_id,
            limit=1,
            mode_filter='extract'
        )

        if not encounters:
            # Fallback: Use item metadata if available
            context_sentence = metadata.get('context_snippet', '')
        else:
            context_sentence = encounters[0].context_sentence or ''

        # Replace lemma with blank (case-insensitive)
        question = re.sub(
            rf'\b{re.escape(item.canonical_form)}\b',
            '________',
            context_sentence,
            flags=re.IGNORECASE
        )

        return DrillResponse(
            type=DrillType.CLOZE,
            question=question,
            target_id=item.id,
            target_lemma=item.canonical_form,
            meta={
                'hint': metadata.get('english_gloss', ''),
                'original_sentence': context_sentence
            }
        )

    async def create_saboteur_drill(
        self,
        item_id: int,
        error_profile: Optional[str] = None
    ) -> DrillResponse:
        """
        Generate a saboteur drill (identify/fix grammar error).

        Logic:
        1. Get item with valid context sentence
        2. Call LLM with SABOTEUR_GEN_PROMPT to introduce error
        3. LLM returns sabotaged_sentence + hint
        4. Return DrillResponse with broken sentence as question

        Args:
            item_id: ID of item to drill
            error_profile: User's weakness (e.g., "error_gender")

        Returns:
            DrillResponse with type='saboteur'
        """
        item = self.graph_store.get_item_by_id(item_id)

        # Get context sentence
        encounters = self.graph_store.get_item_encounters(
            item_id,
            limit=1,
            mode_filter='extract'
        )
        context_sentence = encounters[0].context_sentence if encounters else ''

        if not context_sentence:
            raise ValueError(f"No context sentence for item {item_id}")

        # Determine error type to introduce
        error_type = error_profile or "GENDER"  # Default to gender errors

        # Call LLM to sabotage the sentence
        from app.services.prompts import SABOTEUR_GEN_PROMPT

        prompt = SABOTEUR_GEN_PROMPT.format(
            sentence=context_sentence,
            error_type=error_type
        )

        response = await self.llm_provider.generate_json(
            prompt=prompt,
            system_prompt="You are a German Language Saboteur."
        )

        return DrillResponse(
            type=DrillType.SABOTEUR,
            question=response['sabotaged_sentence'],
            target_id=item.id,
            target_lemma=item.canonical_form,
            meta={
                'hint': response.get('hint', ''),
                'original_sentence': context_sentence,
                'error_type': error_type
            }
        )

    async def create_pattern_drill(self, item_id: int) -> DrillResponse:
        """
        Generate a pattern builder drill (construct sentence from template).

        Logic:
        1. Get pattern item (type='pattern')
        2. Extract template from canonical_form (e.g., "Je [KOMPARATIV], desto [KOMPARATIV]")
        3. Provide scenario/prompt for user to fill in
        4. Return DrillResponse with template as context

        Args:
            item_id: ID of pattern item to drill

        Returns:
            DrillResponse with type='pattern'
        """
        item = self.graph_store.get_item_by_id(item_id)

        if item.type != 'pattern':
            raise ValueError(f"Item {item_id} is not a pattern")

        # Parse metadata JSON
        metadata = {}
        if item.metadata_json:
            try:
                metadata = json.loads(item.metadata_json)
            except json.JSONDecodeError:
                metadata = {}

        template = item.canonical_form
        english_gloss = metadata.get('english_gloss', '')

        # Create scenario prompt
        question = f"Use the pattern '{template}' to complete the sentence."

        return DrillResponse(
            type=DrillType.PATTERN,
            question=question,
            target_id=item.id,
            target_lemma=template,
            meta={
                'template': template,
                'english_gloss': english_gloss,
                'hint': f"Follow the structure: {template}"
            }
        )

    async def grade_drill(self, request: DrillRequest) -> DrillGradeResult:
        """
        Grade user's drill answer using LLM judge.

        Logic:
        1. Call LLM with JUDGE_PROMPT
        2. Provide context based on drill_type
        3. LLM returns is_correct, feedback, error_type
        4. Return DrillGradeResult

        Args:
            request: DrillRequest with user's answer

        Returns:
            DrillGradeResult with grading + feedback
        """
        from app.services.prompts import JUDGE_PROMPT

        prompt = JUDGE_PROMPT.format(
            drill_type=request.drill_type.value,
            target=request.target_lemma,
            user_input=request.user_answer,
            context=request.context or request.question_meta.get('original_sentence', '')
        )

        response = await self.llm_provider.generate_json(
            prompt=prompt,
            system_prompt="You are a German Grammar Judge."
        )

        return DrillGradeResult(
            is_correct=response['is_correct'],
            feedback=response['feedback'],
            detected_error_type=response.get('error_type')
        )


def get_drill_service(
    llm_provider: LLMProvider,
    graph_store: GraphStore
) -> DrillService:
    """Factory function to get DrillService instance."""
    return DrillService(llm_provider, graph_store)

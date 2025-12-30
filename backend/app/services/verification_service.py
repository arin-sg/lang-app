"""
Verification Service - Verifies extracted items and prevents hallucination.

This service implements a two-phase extraction pipeline:
1. Mechanical verification: Check items appear in source text
2. Canonical form computation: Lemmatize surface forms using LLM
3. Semantic deduplication: Match against existing items
"""
import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from difflib import SequenceMatcher

from app.utils.ollama_client import OllamaClient
from app.schemas.extraction import (
    ExtractionOutput,
    ExtractionItem,
    VerifiedExtractionItem,
    VerifiedExtractionOutput
)
from app.models.item import Item
from app.config import settings


class TextVerifier:
    """Verifies extracted items appear in source text (hallucination prevention)."""

    def __init__(self, source_text: str, sentences: List[str]):
        """
        Initialize with source text and sentences.

        Args:
            source_text: Raw source text
            sentences: List of sentences extracted from text
        """
        self.source_text = source_text.lower()
        self.sentences = [s.lower() for s in sentences]

    def verify_surface_form(
        self,
        surface_form: str,
        sentence_idx: int,
        left_context: str = "",
        right_context: str = ""
    ) -> bool:
        """
        Verify that surface_form appears in the specified sentence.

        Args:
            surface_form: The exact form to verify
            sentence_idx: Index of sentence in which it should appear
            left_context: Text that should appear before surface_form
            right_context: Text that should appear after surface_form

        Returns:
            True if verified, False if hallucinated
        """
        if sentence_idx >= len(self.sentences):
            return False

        sentence = self.sentences[sentence_idx]
        surface_lower = surface_form.lower()

        # Check exact substring match
        if surface_lower not in sentence:
            # Also check in full source text as fallback
            if surface_lower not in self.source_text:
                return False

        # Verify context if provided
        if left_context or right_context:
            context_pattern = f"{left_context.lower()}{surface_lower}{right_context.lower()}"
            if context_pattern not in sentence and context_pattern not in self.source_text:
                return False

        return True


class CanonicalFormComputer:
    """Computes canonical forms from surface forms using LLM."""

    def __init__(self, ollama_client: OllamaClient, use_llm: Optional[bool] = None):
        """
        Initialize with Ollama client.

        Args:
            ollama_client: Client for LLM communication
            use_llm: Whether to use LLM for canonicalization. If None, uses settings value.
        """
        self.ollama_client = ollama_client
        self.use_llm = use_llm if use_llm is not None else settings.use_llm_for_canonicalization

    async def compute_canonical(
        self,
        surface_form: str,
        item_type: str,
        pos_hint: Optional[str] = None
    ) -> str:
        """
        Compute canonical form from surface form.

        For words: lemmatize (Hund, not Hunde)
        For chunks: keep as-is or normalize
        For patterns: keep as-is

        Args:
            surface_form: The inflected/conjugated form
            item_type: Type of item (word, chunk, pattern)
            pos_hint: Part of speech hint

        Returns:
            Canonical (lemmatized) form
        """
        if item_type == "pattern":
            return surface_form

        if item_type == "chunk":
            # Keep chunks as-is for now
            return surface_form

        if self.use_llm:
            return await self._llm_lemmatize(surface_form, item_type, pos_hint)
        else:
            return self._fallback_lemmatize(surface_form)

    async def _llm_lemmatize(
        self,
        surface: str,
        item_type: str,
        pos: Optional[str]
    ) -> str:
        """
        Use LLM for lemmatization.

        Args:
            surface: Surface form
            item_type: Type (word, chunk, pattern)
            pos: Part of speech hint

        Returns:
            Lemma
        """
        prompt = f"""Lemmatize this German {item_type}:

Surface form: {surface}
POS: {pos or 'unknown'}

Return ONLY the lemma (base dictionary form), nothing else.

Examples:
- "Hunde" → "Hund"
- "ging" → "gehen"
- "schönen" → "schön"
- "Entscheidungen" → "Entscheidung"

Lemma:"""

        try:
            response = await self.ollama_client.generate(
                prompt=prompt,
                system_prompt="You are a German language expert. Return only the lemma, no explanations."
            )
            # Extract lemma from response (should be just one word)
            lemma = response.strip().split()[0] if response.strip() else surface
            return lemma
        except Exception:
            # Fallback to surface form
            return surface

    def _fallback_lemmatize(self, surface: str) -> str:
        """
        Fallback lemmatization (just return surface form).

        Args:
            surface: Surface form

        Returns:
            Surface form as-is (fallback)
        """
        return surface

    async def batch_compute_canonical(
        self,
        items: List[ExtractionItem]
    ) -> Dict[str, str]:
        """
        Lemmatize multiple items in one LLM call (performance optimization).

        Args:
            items: List of extraction items

        Returns:
            Dictionary mapping surface_form -> canonical_form
        """
        if not items:
            return {}

        # Build batch prompt
        items_json = [{
            'surface': item.surface_form,
            'type': item.type,
            'pos': item.pos_hint
        } for item in items if item.type == 'word']  # Only lemmatize words in batch

        if not items_json:
            # No words to lemmatize
            return {item.surface_form: item.surface_form for item in items}

        prompt = f"""Lemmatize these German words. Return JSON mapping surface → lemma:

Items:
{json.dumps(items_json, ensure_ascii=False, indent=2)}

Return ONLY a JSON object like:
{{"Hunde": "Hund", "ging": "gehen", "schönen": "schön"}}

JSON:"""

        try:
            response_dict = await self.ollama_client.generate_json(
                prompt=prompt,
                system_prompt="You are a German language expert. Return only valid JSON with lemmas."
            )
            return response_dict
        except Exception:
            # Fallback: return surface forms
            return {item.surface_form: item.surface_form for item in items}


class SemanticDeduplicator:
    """Finds and merges semantically similar items using fuzzy matching."""

    def __init__(
        self,
        db: Session,
        similarity_threshold: float = 0.85
    ):
        """
        Initialize with database session.

        Args:
            db: Database session
            similarity_threshold: Minimum similarity score (0.0-1.0) for deduplication
        """
        self.db = db
        self.threshold = similarity_threshold

    def find_similar_items(
        self,
        candidate_canonical: str,
        item_type: str
    ) -> Optional[Item]:
        """
        Find existing items similar to candidate.

        Uses:
        1. Exact match on (canonical_form, type)
        2. Fuzzy string matching (Levenshtein-based similarity)

        Args:
            candidate_canonical: Canonical form to match
            item_type: Type of item (word, chunk, pattern)

        Returns:
            Existing item if found, None otherwise
        """
        # Exact match first
        exact = self.db.query(Item).filter(
            Item.canonical_form == candidate_canonical,
            Item.type == item_type
        ).first()

        if exact:
            return exact

        # Fuzzy match using string similarity
        # Query recent items of same type for comparison
        candidates = self.db.query(Item).filter(
            Item.type == item_type
        ).order_by(Item.created_at.desc()).limit(100).all()

        for candidate in candidates:
            similarity = self._string_similarity(
                candidate_canonical,
                candidate.canonical_form
            )
            if similarity >= self.threshold:
                return candidate

        return None

    def _string_similarity(self, s1: str, s2: str) -> float:
        """
        Compute normalized string similarity using SequenceMatcher.

        Args:
            s1: First string
            s2: Second string

        Returns:
            Similarity score 0.0-1.0 where 1.0 is identical
        """
        return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()


class VerificationService:
    """Main verification pipeline orchestrator."""

    def __init__(
        self,
        db: Session,
        ollama_client: OllamaClient,
        enable_deduplication: Optional[bool] = None,
        batch_canonicalization: Optional[bool] = None
    ):
        """
        Initialize verification service.

        Args:
            db: Database session
            ollama_client: Ollama client for LLM calls
            enable_deduplication: Whether to perform semantic deduplication. If None, uses settings value.
            batch_canonicalization: Whether to batch LLM calls for performance. If None, uses settings value.
        """
        self.db = db
        self.ollama_client = ollama_client
        self.enable_deduplication = enable_deduplication if enable_deduplication is not None else settings.enable_semantic_deduplication
        self.batch_canonicalization = batch_canonicalization if batch_canonicalization is not None else settings.batch_canonicalization

    async def verify_and_canonicalize(
        self,
        extraction: ExtractionOutput,
        source_text: str
    ) -> VerifiedExtractionOutput:
        """
        Verify extraction against source text and compute canonical forms.

        Steps:
        1. Verify each item appears in source text
        2. Drop hallucinated items
        3. Compute canonical forms
        4. Deduplicate against existing items
        5. Return verified extraction

        Args:
            extraction: Raw LLM extraction output
            source_text: Original source text

        Returns:
            Verified and canonicalized extraction output
        """
        verified_items = []
        verification_stats = {
            'total': len(extraction.items),
            'verified': 0,
            'hallucinated': 0,
            'deduplicated': 0,
            'invalid': 0
        }

        # Initialize components
        sentences = [s.text for s in extraction.sentences]
        text_verifier = TextVerifier(source_text, sentences)
        canonical_computer = CanonicalFormComputer(self.ollama_client, use_llm=None)  # Uses settings
        deduplicator = SemanticDeduplicator(self.db) if self.enable_deduplication else None

        # Batch canonicalization if enabled
        if self.batch_canonicalization:
            canonical_map = await canonical_computer.batch_compute_canonical(extraction.items)
        else:
            canonical_map = {}

        for item in extraction.items:
            # Step 1: Verify surface form appears in text
            is_verified = text_verifier.verify_surface_form(
                surface_form=item.surface_form,
                sentence_idx=item.evidence.sentence_idx,
                left_context=item.evidence.left_context,
                right_context=item.evidence.right_context
            )

            if not is_verified:
                verification_stats['hallucinated'] += 1
                continue  # DROP hallucinated item

            # Step 2: Compute canonical form
            if item.surface_form in canonical_map:
                canonical_form = canonical_map[item.surface_form]
            else:
                canonical_form = await canonical_computer.compute_canonical(
                    surface_form=item.surface_form,
                    item_type=item.type,
                    pos_hint=item.pos_hint
                )

            # Step 3: Semantic deduplication
            existing_item = None
            if deduplicator:
                existing_item = deduplicator.find_similar_items(
                    candidate_canonical=canonical_form,
                    item_type=item.type
                )

            if existing_item:
                # Use existing item's canonical form for consistency
                canonical_form = existing_item.canonical_form
                verification_stats['deduplicated'] += 1

            # Step 4: Validate canonical_form and surface_form are not empty (NEW)
            if not canonical_form or not canonical_form.strip():
                verification_stats['invalid'] += 1
                continue  # DROP items with blank canonical_form

            if not item.surface_form or not item.surface_form.strip():
                verification_stats['invalid'] += 1
                continue  # DROP items with blank surface_form

            # Create verified item
            verified_item = VerifiedExtractionItem(
                type=item.type,
                surface_form=item.surface_form,
                canonical_form=canonical_form,
                english_gloss=item.english_gloss,
                pos_hint=item.pos_hint,
                meta=item.meta,
                why_worth_learning=item.why_worth_learning,
                evidence=item.evidence,
                existing_item_id=existing_item.id if existing_item else None
            )

            verified_items.append(verified_item)
            verification_stats['verified'] += 1

        return VerifiedExtractionOutput(
            sentences=extraction.sentences,
            items=verified_items,
            edges=extraction.edges,
            verification_stats=verification_stats
        )

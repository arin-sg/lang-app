"""
Extraction Service - Extracts learnable items from German text using LLM.
"""
import json
import re
import asyncio
from typing import Dict, Any, List
from pydantic import ValidationError

from app.utils.ollama_client import OllamaClient, OllamaConnectionError, OllamaTimeoutError
from app.schemas.extraction import ExtractionOutput, ExtractionError, ExtractionItem


# Post-LLM validation constants
FILTER_LIST = {'und', 'aber', 'oder', 'denn', 'der', 'die', 'das', 'ein', 'eine', 'einem', 'einen', 'einer'}

KNOWN_PROPER_NOUNS = {
    # Cities
    'berlin', 'münchen', 'hamburg', 'köln', 'frankfurt', 'stuttgart', 'düsseldorf', 'dortmund',
    'essen', 'leipzig', 'bremen', 'dresden', 'hannover', 'nürnberg', 'duisburg', 'bochum',
    # Countries
    'deutschland', 'österreich', 'schweiz', 'frankreich', 'italien', 'spanien', 'england',
    'polen', 'niederlande', 'belgien', 'dänemark', 'schweden', 'norwegen',
    # Common person names
    'silke', 'julia', 'hans', 'peter', 'maria', 'anna', 'michael', 'thomas', 'christian',
    'sebastian', 'alexander', 'florian', 'jan', 'max', 'martin', 'david', 'daniel',
    'laura', 'sarah', 'lisa', 'katharina', 'stefanie', 'claudia', 'nicole', 'andrea'
}


def is_likely_proper_noun(word: str) -> bool:
    """
    Heuristic to detect if a capitalized word is a proper noun.

    German nouns are always capitalized, but we can filter known proper nouns
    (cities, countries, person names).

    Args:
        word: The word to check (should be capitalized)

    Returns:
        True if likely a proper noun, False otherwise
    """
    word_lower = word.lower().strip()

    # Check against known proper nouns list
    if word_lower in KNOWN_PROPER_NOUNS:
        return True

    return False


def validate_and_filter_items(items: List[ExtractionItem]) -> List[ExtractionItem]:
    """
    Post-process LLM extraction to filter invalid items.

    Filters out:
    - Items with blank/empty canonical or surface_form
    - Proper nouns (known cities, countries, person names)
    - Simple connectors (und, aber, oder, denn)
    - Articles alone (der, die, das, ein, eine)
    - Patterns without required metadata (NEW)

    Args:
        items: List of items extracted by LLM

    Returns:
        List of validated items
    """
    validated = []

    for item in items:
        # 1. Reject blank canonical/surface_form
        if not item.canonical or not item.canonical.strip():
            continue
        if not item.surface_form or not item.surface_form.strip():
            continue

        canonical_stripped = item.canonical.strip()
        surface_stripped = item.surface_form.strip()

        # 2. NEW: Pattern-specific validation
        if item.type == "pattern":
            # Require pattern_meta for patterns
            if not item.pattern_meta:
                continue

            # Validate grammar_rule is non-empty
            if not item.pattern_meta.grammar_rule or not item.pattern_meta.grammar_rule.strip():
                continue

            # Validate structure_type (Pydantic already enforces Literal, but double-check)
            valid_types = {"connector", "verb_prep", "sentence_structure", "idiom"}
            if item.pattern_meta.structure_type not in valid_types:
                continue

            # Validate slots is a list
            if not isinstance(item.pattern_meta.slots, list):
                continue

        # 3. Skip proper noun filtering for patterns (they're grammatical structures)
        if item.type != "pattern":
            # Reject low-value items (connectors, articles)
            if canonical_stripped.lower() in FILTER_LIST:
                continue
            if surface_stripped.lower() in FILTER_LIST:
                continue

            # Reject known proper nouns
            if is_likely_proper_noun(canonical_stripped):
                continue
            if is_likely_proper_noun(surface_stripped):
                continue

        validated.append(item)

    return validated


# Harden the system prompt to enforce JSON-only outputs and reduce hallucinations.
EXTRACTION_SYSTEM_PROMPT = """You are a German language learning assistant. Extract learnable items from German text.

GLOBAL OUTPUT RULES (quality safeguards):
- Return exactly ONE JSON object. No prose, no markdown/code fences, no prefixes/suffixes.
- If surface_form, canonical, or evidence.sentence would be empty, SKIP the item; for english_gloss give a concise best-effort gloss (do not leave blank).
- evidence.sentence must be copied verbatim from the provided sentences; do not paraphrase or write "full sentence".
- Stay within the numeric limits stated in the user message; ignore template placeholders like {{max_items_per_type}} if present.
- Patterns and chunks are REQUIRED when observable: emit at least one pattern if any sentence shows verb position, subordinate clause verb-final, case-governing preposition, modal+infinitive, or separable verb behavior. Emit chunks for meaningful multi-word spans (collocations/phrases) you see.

CRITICAL RULES (follow exactly):

1. DO NOT extract these - skip completely:
   - People names (Silke, Julia, Hans, Peter, Maria)
   - Cities (Berlin, München, Hamburg, Frankfurt)
   - Countries (Deutschland, Österreich, Schweiz)
   - Simple words (und, aber, oder, denn, der, die, das)

2. For VERBS - always use INFINITIVE:
   - "kennengelernt" → extract "kennenlernen"
   - "gemacht" → extract "machen"
   - "haben sich kennengelernt" → extract "sich kennenlernen" (include "sich")
   - "rufe ... an" → extract "anrufen" (combine separated verb)

3. For VERB PHRASES - put object first:
   - Text "machen Ferien" → extract "Ferien machen"
   - Text "suchen ein Taxi" → extract "ein Taxi suchen"

4. REQUIRED fields for EVERY item:
   - surface_form: EXACT text from input (copy exactly as appears)
   - canonical: Dictionary form (infinitive for verbs, with rules above)
   - evidence.sentence: FULL sentence where found (NOT "full sentence" - copy the actual German sentence)

5. Extract up to {{max_items_per_type}} valuable learning items per type.
   # NOTE: Use the numeric cap provided in the user prompt; do not fabricate items to hit the cap, and include ALL three types (words, chunks/phrases, patterns) when present.

6. EXTRACT PATTERNS - Identify grammatical structures and abstract them into templates:

   PATTERN TYPES (structure_type):
   - connector: Multi-part connectors (e.g., "je ... desto", "entweder ... oder")
   - verb_prep: Verb + preposition + case (e.g., "warten auf + AKK")
   - sentence_structure: Word order patterns (e.g., "Verb-Position-2")
   - idiom: Fixed expressions with grammatical significance (e.g., "es gibt + AKK")

   PLACEHOLDER SYNTAX (use UPPERCASE in square brackets for variable parts):
   - [ADJ] = adjective slot, [NOUN] = noun slot, [VERB] = verb slot
   - [KOMPARATIV] = comparative form
   - [AKK] = accusative object, [DAT] = dative object, [GEN] = genitive object
   - [SUBJECT] = subject slot

   PATTERN METADATA REQUIRED:
   - structure_type: One of: connector | verb_prep | sentence_structure | idiom
   - slots: List of placeholders used (e.g., ["KOMPARATIV", "KOMPARATIV"])
   - grammar_rule: Brief explanation of when/how to use this pattern

   EXAMPLES:
   Input: "Je schneller du fährst, desto früher kommst du an."
   Output canonical: "Je [KOMPARATIV], desto [KOMPARATIV]"
   Output pattern_meta: {"structure_type": "connector", "slots": ["KOMPARATIV", "KOMPARATIV"], "grammar_rule": "Correlative conjunction expressing proportional relationship"}

   Input: "Ich warte auf den Bus."
   Output canonical: "warten auf + [AKK]"
   Output pattern_meta: {"structure_type": "verb_prep", "slots": ["AKK"], "grammar_rule": "Verb 'warten' requires preposition 'auf' with accusative case"}

Return only valid JSON."""


def build_extraction_prompt(text: str, max_items_per_type: int = 5) -> str:
    """
    Build the extraction prompt for the LLM.

    Args:
        text: German text to extract from
        max_items_per_type: Maximum items to extract per type (words/chunks/patterns)

    Note: surface_form is for verification (exact match in text)
          canonical is for learning (dictionary form with German grammar rules applied)
    """
    # Add explicit JSON-only and no-markdown guidance to reduce parse errors.
    return f"""Extract up to {max_items_per_type} key German items per type from this text.

Return exactly ONE JSON object. Do not add markdown/code fences, prose, or extra text. If unsure about an item, skip it entirely unless you can give a best-effort english_gloss.

{text}

JSON format:
{{
  "sentences": [{{"idx": 0, "text": "Ich muss heute eine wichtige Entscheidung treffen."}}],
  "items": [
    {{
      "type": "word",
      "surface_form": "Entscheidung",
      "canonical": "Entscheidung",
      "english_gloss": "decision",
      "pos_hint": "NOUN",
      "meta": {{"gender": "die"}},
      "why_worth_learning": "common noun",
      "evidence": {{"sentence_idx": 0, "sentence": "Ich muss heute eine wichtige Entscheidung treffen.", "left_context": "", "right_context": ""}}
    }},
    {{
      "type": "chunk",
      "surface_form": "suchen ein Taxi",
      "canonical": "ein Taxi suchen",
      "english_gloss": "to look for a taxi",
      "pos_hint": "VERB_PHRASE",
      "meta": {{}},
      "why_worth_learning": "common verb phrase pattern",
      "evidence": {{"sentence_idx": 0, "sentence": "Sie verlassen das Hotel und suchen ein Taxi.", "left_context": "", "right_context": ""}}
    }},
    {{
      "type": "pattern",
      "surface_form": "verb in position 2",
      "canonical": "Verb-Position-2 (V2)",
      "english_gloss": "Main clause verb must be in second position",
      "pos_hint": "SYNTAX_PATTERN",
      "pattern_meta": {{
        "structure_type": "sentence_structure",
        "slots": ["SUBJECT", "VERB"],
        "grammar_rule": "In main clauses, the finite verb always occupies the second position (V2 rule)",
        "cefr_level": "A2"
      }},
      "why_worth_learning": "fundamental German word order rule",
      "evidence": {{"sentence_idx": 0, "sentence": "Heute esse ich Pizza.", "left_context": "", "right_context": ""}}
    }}
  ],
  "edges": []
}}

Return valid JSON only."""


def split_into_sentence_batches(text: str, batch_size: int = 2) -> List[str]:
    """
    Split text into batches of N sentences each.

    Args:
        text: Input text
        batch_size: Number of sentences per batch

    Returns:
        List of text batches, each containing batch_size sentences
    """
    # Split by sentence boundaries (., !, ?)
    # Use regex with negative lookbehind to avoid splitting on abbreviations
    sentences = re.split(r'(?<![A-Z])(?<=[.!?])\s+', text.strip())

    # Filter out empty sentences
    sentences = [s for s in sentences if s.strip()]

    # If no sentences found, return original text
    if not sentences:
        return [text]

    # Group into batches
    batches = []
    for i in range(0, len(sentences), batch_size):
        batch = ' '.join(sentences[i:i + batch_size])
        batches.append(batch)

    return batches


class ExtractService:
    """Service for extracting learnable items from text."""

    def __init__(self, ollama_client: OllamaClient):
        """Initialize with Ollama client."""
        self.ollama_client = ollama_client

    async def extract_items(self, text: str, max_items_per_type: int = 5) -> ExtractionOutput:
        """
        Extract learnable items from German text (single batch).

        This is the main public method that extracts items from a single text chunk.

        Args:
            text: Raw German text to analyze
            max_items_per_type: Maximum items to extract per type

        Returns:
            Validated ExtractionOutput

        Raises:
            ExtractionError: If extraction fails
            OllamaConnectionError: If cannot connect to Ollama
            OllamaTimeoutError: If request times out
        """
        # Build prompt
        prompt = build_extraction_prompt(text, max_items_per_type)

        try:
            # Call LLM with JSON format
            response_dict = await self.ollama_client.generate_json(
                prompt=prompt,
                system_prompt=EXTRACTION_SYSTEM_PROMPT
            )

            # Validate against schema
            extraction = ExtractionOutput(**response_dict)

            # NEW: Post-process to filter invalid items
            extraction.items = validate_and_filter_items(extraction.items)

            return extraction

        except json.JSONDecodeError as e:
            raise ExtractionError(
                f"LLM returned invalid JSON: {str(e)}"
            )
        except ValidationError as e:
            raise ExtractionError(
                f"LLM output doesn't match expected schema: {str(e)}"
            )
        except (OllamaConnectionError, OllamaTimeoutError):
            # Re-raise these as-is
            raise
        except Exception as e:
            raise ExtractionError(
                f"Extraction failed: {str(e)}"
            )

    async def extract_items_batched(
        self,
        text: str,
        batch_size: int = 2,
        max_items_per_type: int = 5
    ) -> ExtractionOutput:
        """
        Extract items using parallel sentence batching for performance.

        Args:
            text: German text to analyze
            batch_size: Number of sentences per batch
            max_items_per_type: Maximum items per type per batch

        Returns:
            Merged ExtractionOutput from all batches
        """
        # Split into sentence batches
        batches = split_into_sentence_batches(text, batch_size)

        # If only one batch, use single extraction
        if len(batches) == 1:
            return await self.extract_items(batches[0], max_items_per_type)

        # Process batches in parallel
        tasks = [
            self.extract_items(batch, max_items_per_type)
            for batch in batches
        ]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Merge results with improved error handling
        merged_sentences = []
        merged_items = []
        merged_edges = []

        successful_batches = 0
        failed_batches = 0

        sentence_offset = 0
        for i, result in enumerate(batch_results):
            if isinstance(result, Exception):
                # Log error with batch index
                print(f"[ERROR] Batch {i} failed: {type(result).__name__}: {str(result)}")
                failed_batches += 1
                continue

            # Validate result has items
            if not result.items and not result.sentences:
                print(f"[WARNING] Batch {i} returned no items or sentences")
                failed_batches += 1
                continue

            successful_batches += 1

            # Adjust sentence indices
            for sentence in result.sentences:
                sentence.idx += sentence_offset
                merged_sentences.append(sentence)

            sentence_offset += len(result.sentences)

            # Merge items and edges
            merged_items.extend(result.items)
            merged_edges.extend(result.edges)

        # Fallback to single extraction if too many batches failed
        if successful_batches < len(batches) / 2:
            print(f"[WARNING] Too many batch failures ({failed_batches}/{len(batches)}), falling back to single extraction")
            return await self.extract_items(text, max_items_per_type)

        return ExtractionOutput(
            sentences=merged_sentences,
            items=merged_items,
            edges=merged_edges
        )


def get_extract_service(ollama_client: OllamaClient) -> ExtractService:
    """Factory function to get an ExtractService instance."""
    return ExtractService(ollama_client)

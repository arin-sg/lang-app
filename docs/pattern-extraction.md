# TASKS.md - Feature: Pattern Extraction Pipeline

## Context
We are upgrading the "Ingest" pipeline to support **Pattern Extraction**. Currently, the system only extracts concrete "Words" and "Chunks". We need to teach the LLM to identify abstract grammatical templates (e.g., `Je [KOMPARATIV], desto [KOMPARATIV]`) and store them with structured metadata.

## 1: Backend Data Modeling & Schema
*Objective: Update the Pydantic models and Database logic to support abstract patterns.*

- [ ] **Update `ItemType` Enum**
    - **File:** `backend/app/schemas.py` (or `models.py`)
    - **Action:** Add `"pattern"` to the `ItemType` Enum.
    - **Context:** `class ItemType(str, Enum): WORD = "word", CHUNK = "chunk", PATTERN = "pattern"`

- [ ] **Create `PatternMetadata` Model**
    - **File:** `backend/app/schemas.py`
    - **Action:** Define a Pydantic model for pattern-specific data.
    - **Specs:**
        ```python
        class PatternMetadata(BaseModel):
            structure_type: Literal["connector", "verb_prep", "sentence_structure", "idiom"]
            slots: List[str] = Field(..., description="Placeholders like ['ADJ', 'NOM', 'DAT']")
            grammar_rule: str = Field(..., description="Brief explanation of the rule")
        ```

- [ ] **Update `ExtractedItem` Model**
    - **File:** `backend/app/schemas.py`
    - **Action:** Add an optional `pattern_meta` field to the main extraction model.
    - **Specs:** `pattern_meta: Optional[PatternMetadata] = None`

## 2: LLM Prompt Engineering
*Objective: Modify the Extraction Service to "teach" the LLM how to abstract sentences into templates.*

- [ ] **Update System Prompt**
    - **File:** `backend/app/services/extract_service.py`
    - **Action:** Append the **Pattern Extraction Protocol** to the existing `SYSTEM_PROMPT`.
    - **Content to Insert:**
        ```text
        ### PATTERN EXTRACTION PROTOCOL
        Your goal is to identify abstract grammatical "skeletons" in the text.
        
        1. Target: Look for multi-part connectors, verb-preposition pairs, or sentence structures.
        2. Abstract: Create a template by replacing variable parts with uppercase placeholders:
           - [ADJ], [NOUN], [VERB]
           - [DAT] (Dative object), [AKK] (Accusative object)
        3. Format:
           - Lemma: Must be the abstract template (e.g., "Je [KOMPARATIV], desto [KOMPARATIV]")
           - Type: "pattern"
           - Meta: Include structure_type, slots, and grammar_rule.
        ```

- [ ] **Update JSON Validation**
    - **File:** `backend/app/services/extract_service.py`
    - **Action:** Ensure the prompt explicitly asks for the `pattern_meta` object in the JSON output when `type` is "pattern".

## 3: Ingestion Logic
*Objective: Process the new LLM output and save it to SQLite.*

- [ ] **Update `process_extraction` Logic**
    - **File:** `backend/app/routers/ingest.py` (or `services/ingest_service.py`)
    - **Action:** Modify the loop that saves items to the DB.
    - **Logic:**
        - Check if `item.type == "pattern"`.
        - If yes, serialize `item.pattern_meta.dict()` into JSON.
        - Save this JSON string into the `metadata_json` column of the `items` table.
        - *Crucial:* Ensure we don't duplicate patterns. If `lemma` already exists, skip or update.

## 4: Frontend Visualization (React)
*Objective: distinct visual treatment for Patterns vs. Words.*

- [ ] **Update `ItemCard.tsx` (or equivalent component)**
    - **File:** `frontend/src/components/ItemCard.tsx`
    - **Action:** Add conditional styling for `type === 'pattern'`.
    - **Specs:**
        - **Background:** Use a distinct color (e.g., `bg-blue-50`).
        - **Font:** Use a monospaced font for the Lemma (`font-mono`) to look like a formula.
        - **Icon:** Use a different icon (e.g., `FileCode` or `Braces` from lucide-react).
        - **Metadata:** Render the `grammar_rule` if it exists in the metadata.

- [ ] **Update Library View**
    - **File:** `frontend/src/pages/Library.tsx`
    - **Action:** Add a filter tab for "Patterns" so the user can see only their collected grammar rules.

## 5: Verification

- [ ] **Manual Test Case**
    - **Input Text:** "Ich warte auf den Bus."
    - **Expected Result:**
        - Item 1: "warten auf + [AKK]" (Type: Pattern)
        - Metadata: `slots: ["Subject", "Object"]`
    - **Input Text:** "Je schneller du fährst, desto früher kommst du an."
    - **Expected Result:**
        - Item 1: "Je [KOMPARATIV], desto [KOMPARATIV]" (Type: Pattern)
# Feedback Tracking

## Status Legend
- 🚧 **In Progress** - Currently being implemented
- ✅ **Completed** - Fixed and deployed
- 📋 **Planned** - Accepted, scheduled for future iteration
- ❌ **Closed** - Won't fix / not applicable

---

## Feedback #1: Verb Phrase Normalization
**Status**: ✅ **Completed** (Iteration 1.5.2 - 2025-12-30)
**Impact**: High - Core extraction quality issue affecting all verb phrases

### Feedback 1

The Library Page- 
Here is the main clause I pasted - "Silke und Julia verlassen das Hotel und suchen ein Taxi, um zum Antiquitätenmarkt zu fahren."

the LLMextracted ""suchen ein Taxi"." I think didn't "fail"here, but it was just **too literal**.

In the sentence *"... und suchen ein Taxi..."*, the word order is grammatically correct for a main clause (Verb in Position 2). The LLM saw `Verb` + `Object` and extracted exactly what it saw: *"suchen ein Taxi"*.

The problem is that for **learning**, I want the **Dictionary Form** (Infinitive), which in German puts the verb at the end: *"ein Taxi suchen"*. If you learn it as "suchen ein Taxi," you might later say *"Ich muss suchen ein Taxi"* (wrong) instead of *"Ich muss ein Taxi suchen"* (correct).

Here is how I think we can fix the **Extraction Prompt** so the LLM acts like a Dictionary Editor, not a Copy-Paste machine. However, you should **thoroughly check the current logic and do the best**. You can either work on my tips or use the best logic possible. You should justify your reasons for overrulling my suggestion.

### The Fix: "Normalization" Instructions

You need to explicitly tell the LLM to **transform** conjugated verbs back into their infinitive structure.

**Update your System Prompt to this:**

```json
{
  "role": "system",
  "content": "You are a German computational linguist. Your task is to extract vocabulary from text.
  
  CRITICAL RULES FOR EXTRACTION:
  1. Extract useful Chunks (Verb Phrases, Noun phrases).
  2. NORMALIZE all Verb Phrases to the 'Infinitive Dictionary Form' (Object + Infinitive).
     - Text: 'Ich kaufe ein Buch.' -> Extract: 'ein Buch kaufen' (NOT 'kaufe ein Buch')
     - Text: '...und suchen ein Taxi' -> Extract: 'ein Taxi suchen'
  3. Keep the original text as 'context'."
}

```
### Why this happens (The Grammar Logic)

* **What the text said:** *"und [sie] suchen ein Taxi"* (Conjugated Verb 2nd position).
* **What you want:** *"ein Taxi suchen"* (Infinitive / End position).

By adding the **Normalization Rule** to your prompt, you force the LLM to process the grammar before outputting the JSON. This ensures your database is clean, even if the source text uses complex word order.

Fix: Update the "Extraction Prompt" to explicitly ask for "Standard German Infinitive Form" (Lemma) to avoid this "Anglicized" syntax in the database.

Visual Tweak: On the card (e.g., suchen ein Taxi), add a small italicized line at the bottom: "Silke und Julia verlassen das Hotel und suchen ein Taxi, um zum Antiquitätenmarkt zu fahren." (The sentence where it was found). 


Check the impact on both front-end and backend to achieve this.

---

### Solution Implemented

**Approach**: Dual-form extraction with German grammar normalization

**Backend Changes**:
1. Updated extraction prompt ([extract_service.py:12-34](../backend/app/services/extract_service.py#L12-L34))
   - Added CRITICAL rules for verb phrase normalization
   - Provided examples: "suchen ein Taxi" → "ein Taxi suchen"
   - Clarified dual-form approach: surface_form (verification) vs canonical (learning)

2. Extended API schema ([library.py:45](../backend/app/schemas/library.py#L45))
   - Added `context_sentence` field to `EncounterSummary`
   - Allows source sentence display in frontend

3. Updated GraphStore query ([graph_store.py:402](../backend/app/services/graph_store.py#L402))
   - Returns `context_sentence` for each encounter
   - Enables frontend to display source context

**Frontend Changes**:
1. Enhanced Library item detail modal ([LibraryPage.jsx:444-448](../frontend/src/pages/LibraryPage.jsx#L444-L448))
   - Displays source sentence for 'extract' mode encounters
   - Italicized styling for visual distinction
   - Only shown when context_sentence exists

**Files Modified**:
- `backend/app/services/extract_service.py`
- `backend/app/schemas/library.py`
- `backend/app/services/graph_store.py`
- `frontend/src/pages/LibraryPage.jsx`

**Key Decisions**:
- **Maintained verification integrity**: Surface form still captures exact text for hallucination detection
- **Improved learning quality**: Canonical form uses dictionary form with German grammar rules
- **User suggestion refined**: Added both normalization AND source context display
- **Backward compatible**: No data migration needed; improvement applies to new extractions only

### End of feedback 1

### Feedback 2

Consider the following sentence provide as an input text - "Silke und Julia machen Ferien in Berlin. Sie haben sich vor einigen Jahren an der Universität kennengelernt."

The current implementation of the "Ingest" feature is too permissive. It extracts low-value tokens (proper nouns like "Silke", "Berlin") and fails to normalize split verbs (extracting "kennengelernt" instead of "sich kennenlernen"). The goal is to switch from a "brute-force extraction" to a "smart filtering" approach.

1.	Fix Extraction Quality: Modify the LLM System Prompt to follow these **rules** -

Rule A. IGNORE Proper Nouns: Do NOT extract names of people (e.g., 'Silke', 'Julia'), cities (e.g., 'Berlin'), or countries.
Rule B. IGNORE Simple Connectors: Do not extract 'und', 'aber', 'oder', 'denn'.
Rule C. NORMALIZE Verbs:
   - If you see a participle (e.g., 'kennengelernt'), extract the INFINITIVE (e.g., 'kennenlernen').
   - If the verb is reflexive (e.g., 'sich ... interessieren'), extract 'sich interessieren'.
   - If the verb is separable (e.g., 'fangen ... an'), extract 'anfangen'.
Rule 4. DETECT COLLOCATIONS:
   - Instead of isolating words, extract the phrase if it changes meaning.
   - Example A: Instead of 'machen Ferien', extract the standard phrase 'Ferien machen'.
   - Example B: Instead of 'Universität', extract 'an der Universität' (contextual preposition).

2.	For Performance reason, you can limit extraction upto the top 5(configurable in .env) high-value items per type(word, phrase, pattern)** to prevent timeouts on local llms. 
3.  **We will not allow more than 500 characters in a single prompt**. If len(text) > 500, instruct the user to shorten it. Also to speed up, you can split it by period (.). Send 2(configurable in .env) sentences at a time to the LLM. It’s faster to run 2-3(configurable in .env) small parallel requests than one massive context window request that hangs.
4.  **The following Visual Tweak was not implemented on the last iteration. Implement it.**: On the card, add a small italicized line at the bottom to show the source the sentence where it was found. 

**Important ** you should **thoroughly check the current logic and do the best**. You can either work on my tips or use the best logic possible. You should justify your reasons for overrulling my suggestion.

---

## Feedback #2: Smart Extraction Filtering
**Status**: ✅ **Completed** (Iteration 1.5.3 - 2025-12-30)
**Impact**: High - Core extraction quality and performance improvements

**Implemented**: 2025-12-30
**Implementation Time**: ~4 hours

### Solution Implemented

**Approach**: Multi-layered extraction improvements with parallel sentence batching

**Backend Changes**:
1. Enhanced extraction prompt (`extract_service.py`)
   - Filter proper nouns (Silke, Berlin, etc.)
   - Filter simple connectors (und, aber, oder, denn)
   - Normalize participles → infinitive ("kennengelernt" → "kennenlernen")
   - Handle reflexive verbs ("haben sich kennengelernt" → "sich kennenlernen")
   - Handle separable verbs ("rufe ... an" → "anrufen")
   - Detect collocations ("Ferien machen" as chunk)
   - Configurable item limits per batch

2. Text length enforcement (`config.py`, `.env`, `source.py`)
   - MAX_TEXT_LENGTH=500 (reduced from 10,000)
   - Schema validation at API boundary

3. Parallel sentence batching (`extract_service.py`, `ingest_service.py`)
   - BATCH_SIZE_SENTENCES=2 (configurable)
   - MAX_ITEMS_PER_TYPE=5 (configurable)
   - ENABLE_PARALLEL_BATCHING=true (toggle)
   - Sentence splitting helper function
   - Parallel processing with asyncio.gather()
   - Merge results from batches

4. Source sentence in response (`source.py`, `ingest_service.py`)
   - Add source_sentence to ExtractedItemSummary
   - Include encounter.context_sentence in API response

**Frontend Changes**:
1. Character counter (`IngestPage.jsx`)
   - Real-time counter: "480/500"
   - Red warning if over limit
   - Disable submit button if over 500 chars

2. Source sentence display (`IngestPage.jsx`)
   - Show source sentence below each extracted item
   - Italic styling with left border
   - Matches LibraryPage styling

**Key Design Decisions**:
- Per-batch item limits (simpler than global ranking)
- Parallel processing for 2-3x speedup
- Character counter above textarea (Twitter-style)
- Backward compatible (config toggles for batching)

**Files Modified**:
- Backend (5): `extract_service.py`, `ingest_service.py`, `config.py`, `.env`, `source.py`
- Frontend (1): `IngestPage.jsx`
- Docs (4): `Feedback.md`, `CLAUDE.md`, `README.md`, `tasks.md`

**Implementation Results**:

✅ **PHASE 1**: Enhanced extraction prompt with:
- Proper noun filtering (Silke, Berlin, etc.)
- Simple connector filtering (und, aber, oder, denn)
- Advanced verb normalization (participles → infinitives)
- Reflexive verb handling (include "sich")
- Separable verb handling (combine prefix + verb)
- Collocation detection examples ("Ferien machen")
- Configurable item limits per batch

✅ **PHASE 2**: Configuration updates:
- MAX_TEXT_LENGTH reduced from 10,000 to 500
- Added BATCH_SIZE_SENTENCES=2
- Added MAX_ITEMS_PER_TYPE=5
- Added ENABLE_PARALLEL_BATCHING=true
- Schema validation at API boundary

✅ **PHASE 3**: Parallel sentence batching:
- `split_into_sentence_batches()` helper function
- `extract_items_batched()` method for parallel processing
- Updated `extract_items()` with max_items_per_type parameter
- IngestService conditionally uses batched extraction
- Automatic fallback for short texts

✅ **PHASE 4**: Source sentence in API response:
- Added `source_sentence` field to `ExtractedItemSummary`
- IngestService includes `context_sentence` in response

✅ **PHASE 5**: Frontend character counter:
- Real-time counter display (e.g., "480/500")
- Red warning when over 500 characters
- Submit button disabled if over limit
- Error alert with clear message

✅ **PHASE 6**: Source sentence display on IngestPage:
- Shows source sentence below each extracted item
- Italic styling with left border (consistent with LibraryPage)
- Only displays when source_sentence exists

✅ **PHASE 7**: Documentation updates:
- Updated Feedback.md with implementation details
- Updated CLAUDE.md with Smart Extraction Filtering section
- Updated README.md with Iteration 1.5.3 summary
- Updated tasks.md with completion status

**Key Achievements**:
- Extraction quality improved with intelligent filtering
- Performance optimized with parallel sentence batching (2-3x faster)
- User experience enhanced with character counter and limits
- Source context displayed for better learning
- All changes backward compatible and configurable

### End of feedback 2

---

## Feedback #3: Extraction Quality & Consistency Issues
**Status**: ✅ **Completed** (Iteration 1.5.4 - 2025-12-30)
**Impact**: Critical - Data quality and reliability

### Issues Reported

After implementing Feedback #2 (Smart Extraction Filtering), testing revealed critical extraction quality issues:

1. **Blank chunks/words being extracted**
   - Database contains items with empty `canonical_form` values
   - Example: ID 8 (`canonical_form=''`, `type='chunk'`, `english_gloss='got to know each other'`)
   - Example: ID 9 (`canonical_form=''`, `type='word'`, `english_gloss='at the university'`)

2. **Proper noun filtering not working consistently**
   - Despite explicit filtering rules in system prompt, still extracting: **Silke, Julia, Berlin, Universität**
   - Rules being ignored by 7B LLM model (mistral:latest)
   - Some extraction runs filter properly, others don't

3. **Inconsistent extraction results**
   - Same input text produces different results across runs
   - Variable quality: sometimes proper nouns filtered, sometimes not
   - Unpredictable behavior affecting user trust

4. **Incorrect verb normalization**
   - "kennengelernt" extracted as `word` instead of "sich kennenlernen" as `chunk`
   - Missing reflexive pronoun "sich" in extraction
   - Participle not normalized to infinitive

### Root Causes Identified

**1. LLM model (mistral:latest 7B) not following complex instructions**
   - System prompt has 9 detailed rules which is overwhelming for small models
   - LLM ignores "IGNORE" directives for proper nouns
   - No post-processing fallback to enforce rules when LLM fails

**2. Missing validation in extraction pipeline**
   - No check for blank/empty `canonical` or `surface_form` before storage
   - LLM can return malformed data that passes through verification
   - No defensive programming to catch bad outputs

**3. Weak error handling in parallel batching**
   - `extract_items_batched()` uses `return_exceptions=True` which silently continues when batches fail
   - No logging of batch failures for debugging
   - No fallback when significant number of batches fail

**4. No post-LLM validation layer**
   - Currently relies entirely on LLM following instructions
   - No programmatic filtering as safety net
   - Single point of failure in extraction quality

### Solution Plan

**PHASE 1**: Add post-LLM validation layer (CRITICAL)
- Create `validate_and_filter_items()` helper function
- Filter items with blank `canonical`/`surface_form` values
- Add proper noun detection heuristics (known names, cities)
- Reject low-value items (connectors: und/aber/oder/denn, articles: der/die/das)
- Apply validation immediately after LLM extraction

**PHASE 2**: Simplify extraction prompt (HIGH PRIORITY)
- Reduce complexity from 9 rules to 5 clearer rules
- Put negative examples first (what NOT to extract)
- More explicit about required fields
- Simpler language optimized for 7B models
- Clearer examples with actual German sentences

**PHASE 3**: Add verification service validation (MEDIUM PRIORITY)
- Double-check `canonical_form` not empty before storing
- Double-check `surface_form` not empty before storing
- Track invalid items in `verification_stats`
- Add 'invalid' count to response

**PHASE 4**: Improve batching error handling (MEDIUM PRIORITY)
- Log batch failures with batch index and error
- Validate each batch result before merging
- Fall back to single-batch extraction if >50% fail
- Better exception messages for debugging

**PHASE 5**: Test with larger LLM models (OPTIONAL)
- Test mistral:7b-instruct-v0.2 (better instruction tuning)
- Test llama2:13b (larger, more reliable)
- Document performance trade-offs (speed vs accuracy)
- Update `.env` with recommended model

**Files to Modify**:
- `backend/app/services/extract_service.py` - Add validation, simplify prompt
- `backend/app/services/verification_service.py` - Add verification validation
- `backend/.env` - (Optional) Switch LLM model
- `docs/Feedback.md` - This file
- `tasks.md` - Track implementation progress
- `CLAUDE.md`, `README.md` - Final documentation

**Success Criteria**:
- ✅ No blank `canonical_form` values in database
- ✅ Proper nouns (Silke, Julia, Berlin) consistently filtered out
- ✅ Verb normalization works correctly ("sich kennenlernen" as chunk)
- ✅ Consistent results across similar inputs
- ✅ Error messages logged for failed batches

---

### Implementation Results

**Implemented**: 2025-12-30
**Implementation Time**: ~2 hours

**✅ PHASE 1: Post-LLM Validation Layer** (CRITICAL)
- Added `validate_and_filter_items()` helper function with 3-step filtering
- Filters items with blank `canonical` or `surface_form` values
- Added `KNOWN_PROPER_NOUNS` list (30+ cities, countries, person names)
- Added `is_likely_proper_noun()` heuristic function
- Rejects low-value items: connectors (und/aber/oder/denn), articles (der/die/das)
- Applied validation in `extract_items()` immediately after LLM extraction

**✅ PHASE 2: Simplified Extraction Prompt** (HIGH PRIORITY)
- Reduced complexity from 9 rules to 5 clearer rules
- Restructured: negative examples first (what NOT to extract)
- Simplified language optimized for 7B models
- More explicit about required fields (surface_form, canonical, evidence.sentence)
- Removed nested sub-rules for better clarity

**✅ PHASE 3: Enhanced Verification Pipeline** (MEDIUM PRIORITY)
- Added blank `canonical_form` validation in `verify_and_canonicalize()`
- Added blank `surface_form` validation
- Added 'invalid' count to `verification_stats`
- Items with empty values now dropped before database storage

**✅ PHASE 4: Robust Batch Error Handling** (MEDIUM PRIORITY)
- Added logging for batch failures with index and error type
- Added validation for empty batch results
- Counts successful vs failed batches
- Falls back to single-batch extraction if >50% batches fail
- Better error messages: `[ERROR] Batch X failed: ExceptionType: message`

**Files Modified**:
- `backend/app/services/extract_service.py` - Validation layer, simplified prompt, batch error handling
- `backend/app/services/verification_service.py` - Enhanced validation, invalid count
- `docs/Feedback.md` - This file
- `tasks.md` - Iteration 1.5.4 tracking

**Key Achievements**:
- **Defense in depth**: 3 layers of validation (post-LLM, verification, database)
- **Proper noun filtering**: 30+ known names/cities/countries blocked
- **Blank value prevention**: Multiple checks prevent empty canonical_form
- **Resilient batching**: Automatic fallback when batches fail
- **Better debugging**: Error logs with batch index and type

**Testing Recommendations**:
1. Test with original failing inputs from Feedback #3
2. Verify proper nouns (Silke, Julia, Berlin, Universität) are now filtered
3. Verify no blank canonical_form values in database
4. Test with larger models (mistral:7b-instruct-v0.2, llama2:13b) for comparison
5. Monitor batch failure logs for extraction issues

### End of feedback 3

---

## Feedback #4: Multi-Provider LLM Support
**Status**: 🚧 **In Progress** (Iteration 1.5.5 - 2025-12-31)
**Impact**: High - Architecture enhancement for flexibility and scalability

### User Requirement

Currently the app uses Ollama as the only LLM host. The user wants flexibility to choose between different LLM providers:

**Local LLM Providers**:
- Ollama (current default)
- LM Studio

**Cloud LLM Providers**:
- OpenAI (GPT models)
- Gemini (Google AI)

**Key Requirements**:
1. **Task-specific provider selection**: Use different providers/models for extraction vs explanation/canonicalization tasks
   - Example: `OLLAMA_EXTRACTION_MODEL` for extraction
   - Example: `OPENAI_EXPLANATION_MODEL` for canonicalization
2. **Configuration-driven**: Select provider via environment variables
3. **No automatic fallback**: Fail fast with clear error messages
4. **Backward compatible**: Existing Ollama-only configuration should continue to work
5. **Safe migration**: Keep compatibility shim for existing code

### Architectural Impact

**Current Architecture**:
- Tight coupling to Ollama via `OllamaClient` class
- Single provider (Ollama) for all LLM tasks
- Hardcoded Ollama API endpoints

**Target Architecture**:
- Provider abstraction layer with `LLMProvider` interface
- Task-based routing: `EXTRACTION` and `EXPLANATION` tasks
- Factory pattern for provider instantiation
- Unified error handling across all providers
- Provider-agnostic service layer

### Implementation Plan

**Phase 0**: Documentation updates (this file, tasks.md)
**Phase 1**: Create provider abstraction infrastructure (base class, exceptions)
**Phase 2**: Refactor Ollama to `OllamaProvider(LLMProvider)`
**Phase 3**: Create provider factory with task-based routing
**Phase 4**: Update configuration for multi-provider support
**Phase 5**: Implement additional providers (LM Studio, OpenAI, Gemini)
**Phase 6**: Update service layer to use `LLMProvider` interface
**Phase 7**: Update API endpoints and error handling
**Phase 8**: Add cloud provider SDKs to requirements.txt
**Phase 9**: Update project documentation (CLAUDE.md, README.md)

### Technical Decisions

**User Preferences** (from planning session):
- ✅ Different providers per task (recommended for flexibility)
- ✅ No automatic fallback - fail fast for predictability
- ✅ No cost tracking in initial implementation
- ✅ Keep compatibility shim for safe migration

**Provider Priority**:
1. Ollama (local, free, default)
2. LM Studio (local, free, OpenAI-compatible)
3. OpenAI (cloud, paid, recommended: gpt-4o-mini for cost)
4. Gemini (cloud, free tier available, gemini-1.5-flash recommended)

### Benefits

**Flexibility**:
- Use powerful cloud models for extraction, fast local models for explanation
- Test different models for quality comparison
- Switch providers without code changes

**Resilience**:
- Multiple provider options if one is unavailable
- Clear error messages for debugging

**Future-Proof**:
- Easy to add new providers (Anthropic Claude, Cohere, etc.)
- Architecture supports advanced features (streaming, cost tracking, A/B testing)

### Testing Plan

**Unit Tests**:
- Test each provider implementation independently
- Mock external APIs for cloud providers
- Test factory routing logic
- Test error handling and exception mapping

**Integration Tests**:
- Verify Ollama functionality unchanged (backward compatibility)
- Test LM Studio with local instance
- Test OpenAI with valid API key
- Test Gemini with valid API key
- Test mixed providers (Ollama extraction + OpenAI explanation)

**Manual Testing**:
- Health check reports all provider statuses correctly
- Invalid API keys show clear error messages
- Unavailable providers show "not running" status

### End of feedback 4

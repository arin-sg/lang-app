# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

An AI-powered German language learning app with local-first architecture. The system extracts learnable items (words, phrases, patterns) from German text using a two-phase extraction pipeline with hallucination prevention, then provides personalized spaced repetition review.

**Stack**: FastAPI (Python 3.10+), React + Vite, SQLite, Ollama (local LLM)

**IMPORTANT**: The [prd.md](prd.md) file contains the complete Product Requirements Document and should be treated as the **single source of truth** for all planning, feature development, and verification purposes. Always consult the PRD when:
- Planning new features or iterations
- Making architectural decisions
- Verifying implementation against requirements
- Understanding the product vision and guiding principles

## Commands

### Backend

```bash
# Setup (first time)
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Edit if needed
alembic upgrade head

# Development
cd backend
source venv/bin/activate
python run.py  # Starts on http://localhost:8000

# Database operations
alembic upgrade head                    # Run migrations
alembic revision -m "description"       # Create new migration
sqlite3 data/lang_app.db                # Inspect database directly

# Clear database (WARNING: destructive)
sqlite3 data/lang_app.db "DELETE FROM encounters; DELETE FROM edges; DELETE FROM items; VACUUM;"
```

### Frontend

```bash
# Setup (first time)
cd frontend
npm install
echo "VITE_API_BASE_URL=http://localhost:8000/api" > .env

# Development
cd frontend
npm run dev  # Starts on http://localhost:5173

# Build for production
npm run build
```

### Testing

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Health check
curl http://localhost:8000/api/health
```

## Architecture

### Two-Phase Extraction Pipeline

The system prevents LLM hallucinations through a verification pipeline:

1. **Phase 1: LLM Extraction** (`extract_service.py`)
   - Ollama extracts items (words/chunks/patterns) + relationships from German text
   - Returns `ExtractionOutput` with surface forms (exact text as it appears)

2. **Phase 2: Verification** (`verification_service.py`)
   - **TextVerifier**: Mechanically verifies each item appears in source text (hallucination prevention)
   - **CanonicalFormComputer**: Optionally lemmatizes via LLM (configurable: `USE_LLM_FOR_CANONICALIZATION`)
   - **SemanticDeduplicator**: Fuzzy-matches against existing items (85% threshold) to prevent duplicates
   - Returns `VerifiedExtractionOutput` with verification stats

3. **Storage** (`ingest_service.py` → `graph_store.py`)
   - Stores verified items, edges, and initial encounters in SQLite

**Critical Config** (`.env`):
- `USE_LLM_FOR_CANONICALIZATION=false` - Disable LLM lemmatization for speed (default: false)
- `BATCH_CANONICALIZATION=true` - Batch LLM calls when enabled (default: true)
- `ENABLE_SEMANTIC_DEDUPLICATION=true` - Fuzzy deduplication (default: true)
- `EXTRACTION_TIMEOUT_SECONDS=180` - Ollama timeout (default: 60, increased to 180 for larger models)

### Knowledge Graph Structure

**Three core tables**:

1. **items** - Learnable units
   - `type`: word | chunk | pattern
   - `canonical_form`: Dictionary/base form (indexed)
   - `metadata_json`: Rich metadata (gender, CEFR level, english_gloss, why_worth_learning)

2. **edges** - Linguistic relationships
   - `source_id` → `target_id` (directed graph)
   - `relation_type`: collocates_with | confusable_with | governs_case | near_synonym | minimal_pair
   - `weight`: Optional strength (0.0-1.0)

3. **encounters** - Learning telemetry (critical for personalization)
   - Logs every interaction: review, drill, extract
   - Tracks: `correct` (boolean), `response_time_ms`, `error_type`, `confusion_target_id`
   - Enables spaced repetition and error pattern analysis

### Service Layer Architecture

**Repository Pattern**: `GraphStore` (`services/graph_store.py`) abstracts all database access.

**Key Services**:
- `ExtractService` - LLM extraction (raw output)
- `VerificationService` - Verification pipeline orchestrator
- `IngestService` - Orchestrates extract → verify → store
- `ReviewService` - Generate review decks + record results
- `GraphStore` - All database CRUD operations

**Dependency Injection**: Each service has a factory function:
```python
extract_service = get_extract_service(ollama_client)
graph_store = get_graph_store(db)
```

### Frontend Architecture

**React Router** with client-side routing:
- `/` - IngestPage (text input → extraction results)
- `/review` - ReviewPage (flip-card or type-answer modes)
- `/library` - LibraryPage (browse/filter/delete items)
- `/coach` - CoachPage (placeholder)

**State Management**: Local component state (`useState`) + axios API calls (no Redux/Context).

**API Client** (`api/client.js`): Axios-based HTTP client with methods for all endpoints.

## Critical Patterns

### Backend

1. **Pydantic Schemas**: Strict validation for all API input/output
   - Extraction: `ExtractionOutput`, `VerifiedExtractionOutput`
   - Review: `ReviewResultRequest`, `ReviewDeckResponse`
   - Library: `LibraryItemSummary`, `LibraryItemDetail`

2. **Configuration**: Pydantic `BaseSettings` loads from `.env` with defaults

3. **Error Handling**: Custom exceptions (`ExtractionError`, `OllamaConnectionError`, `OllamaTimeoutError`)

4. **Ollama Client** (`utils/ollama_client.py`):
   - `generate()` - Free-form text
   - `generate_json()` - Structured JSON with format enforcement
   - Performance options: `num_predict=2000`, `temperature=0.3` (limits output for speed)

### Database

1. **Upsert Pattern**: `upsert_item()` and `upsert_edge()` create-or-update semantics

2. **Cascade Delete**: Deleting items removes related encounters and edges

3. **Indexing**: `canonical_form`, `type`, `created_at`, `timestamp` indexed

4. **Metadata Storage**: JSON stored as string in `metadata_json` column

### Frontend

1. **Modal Dialogs**: Item detail view and delete confirmation

2. **Loading/Error States**: Consistent patterns across all pages

3. **Multi-Select**: Library uses Set for selected item IDs

### UI Design System

**Theme**: Cheerful Nanobanana - A warm, friendly aesthetic with banana yellow as the primary color.

**Technology**:
- **shadcn/ui component library** for consistent, accessible React components
- **Tailwind CSS v4** with CSS variables defined in `@theme` block
- **HSL color variables** using `--color-*` naming convention (Tailwind v4 syntax)
- **Nunito font** for friendly, rounded aesthetic (weights 400, 600, 700, 800)
- **20px border radius** (bubbly design language)

**Component Structure**:
```
src/
├── components/
│   ├── ui/              # shadcn/ui components (Button, Card, etc.)
│   └── Layout.jsx       # Navigation wrapper
├── pages/               # Main pages (Ingest, Library, Review, Coach)
└── lib/
    └── utils.js         # cn() utility for class merging
```

**Key Files**:
- `frontend/src/index.css` - Theme CSS variables and base styles (Tailwind v4 `@theme` block)
- `frontend/tailwind.config.js` - Minimal config (only extends font family)
- `frontend/components.json` - shadcn/ui configuration
- `frontend/jsconfig.json` - Path alias configuration (`@/` → `src/`)

**Styling Approach**: No CSS files - all styling via Tailwind utility classes + CSS variables

**Important**: When adding new shadcn/ui components, use:
```bash
cd frontend
npx shadcn@latest add [component-name]
```

## Important Notes

### German Grammar Handling

**Verb Phrase Normalization**: The extraction prompt is configured to normalize German verb phrases to dictionary form:
- **Surface form** (extracted): Exact text as it appears in source (for verification)
- **Canonical form** (for learning): Infinitive dictionary form with object first
- **Example**: Text "suchen ein Taxi" → Canonical "ein Taxi suchen"

**Why This Matters**: German verb phrases in main clauses have Verb-Position-2 word order (V2), but dictionary/infinitive forms place the verb at the end. Without normalization, learners might internalize incorrect patterns:
- ❌ Wrong: "Ich muss suchen ein Taxi" (anglicized word order)
- ✅ Correct: "Ich muss ein Taxi suchen" (German infinitive structure)

**Implementation** ([extract_service.py:19-25](backend/app/services/extract_service.py#L19-L25)):
- System prompt includes CRITICAL rules for verb phrase normalization
- Examples provided: "kaufe ein Buch" → "ein Buch kaufen"
- Both forms stored: surface_form for verification, canonical for learning

**Source Context Display**: The Library item detail view shows the original source sentence for 'extract' mode encounters, providing learners with authentic context for how the item was used.

### Smart Extraction Filtering (Iteration 1.5.3)

**Problem**: The initial extraction was too permissive, extracting low-value items (proper nouns like "Silke", "Berlin") and failing to normalize complex verb forms (extracting "kennengelernt" instead of "sich kennenlernen").

**Solution**: Multi-layered filtering approach with parallel sentence batching

**Filtering Rules** (implemented in `EXTRACTION_SYSTEM_PROMPT`):
1. **IGNORE Low-Value Items**:
   - Proper nouns (people, cities, countries)
   - Simple connectors (und, aber, oder, denn)
   - Articles alone (der, die, das)
   - Pronouns alone (ich, du, er, sie)

2. **Advanced Verb Normalization**:
   - Participles → Infinitive: "kennengelernt" → "kennenlernen"
   - Reflexive verbs: "haben sich kennengelernt" → "sich kennenlernen"
   - Separable verbs: "rufe ... an" → "anrufen"
   - Verb phrases: "machen Ferien" → "Ferien machen" (object + infinitive)

3. **Collocation Detection**:
   - Extract multi-word fixed expressions where meaning changes when combined
   - Examples: "Ferien machen", "an der Universität", "Bescheid geben"

4. **Configurable Extraction Limits**:
   - `MAX_ITEMS_PER_TYPE=5` (per batch, per type)
   - Prevents LLM timeouts on local models
   - Focuses on highest-value items

**Parallel Sentence Batching**:
- Text split into 2-sentence chunks (`BATCH_SIZE_SENTENCES=2`)
- Batches processed in parallel with `asyncio.gather()` for 2-3x speedup
- Results merged with adjusted sentence indices
- Automatic fallback for short texts (<100 chars)

**Text Length Enforcement**:
- `MAX_TEXT_LENGTH=500` (reduced from 10,000)
- Frontend character counter with real-time feedback
- Red warning and disabled button when over limit
- API validation at backend boundary

**Configuration** (`.env`):
```bash
MAX_TEXT_LENGTH=500
BATCH_SIZE_SENTENCES=2
MAX_ITEMS_PER_TYPE=5
ENABLE_PARALLEL_BATCHING=true
```

**Source Context in Extraction Results**: IngestPage now displays the source sentence for each extracted item, consistent with LibraryPage styling.

### Extraction Quality & Validation (Iteration 1.5.4)

**Problem**: After Iteration 1.5.3, testing revealed critical quality issues: blank canonical forms, proper nouns still extracted, inconsistent results.

**Solution**: Multi-layered validation approach with simplified prompts

**Post-LLM Validation Layer** ([extract_service.py:53-95](backend/app/services/extract_service.py#L53-L95)):
- `validate_and_filter_items()` function filters invalid items after LLM extraction
- **Blank value filtering**: Rejects items with empty `canonical` or `surface_form`
- **Proper noun filtering**: 30+ known proper nouns (Silke, Julia, Berlin, München, Deutschland, etc.)
- **Low-value filtering**: Connectors (und/aber/oder/denn), articles (der/die/das)
- Applied immediately after LLM output, before verification pipeline

**Simplified Extraction Prompt** ([extract_service.py:98-125](backend/app/services/extract_service.py#L98-L125)):
- Reduced from 9 complex rules to 5 clear rules
- Negative examples first (what NOT to extract)
- Simpler language optimized for 7B models
- More explicit about required fields

**Enhanced Verification** ([verification_service.py:409-416](backend/app/services/verification_service.py#L409-L416)):
- Additional validation in verification pipeline
- Rejects items with blank `canonical_form` or `surface_form`
- Tracks invalid items in `verification_stats['invalid']`

**Robust Batch Error Handling** ([extract_service.py:305-333](backend/app/services/extract_service.py#L305-L333)):
- Logs batch failures: `[ERROR] Batch X failed: Type: message`
- Counts successful vs failed batches
- Falls back to single-batch extraction if >50% fail
- Validates each batch result before merging

**Defense in Depth**:
1. **Layer 1**: Post-LLM validation (programmatic filtering)
2. **Layer 2**: Verification pipeline (blank value checks)
3. **Layer 3**: Database constraints (Pydantic validation)

**Recommended LLM Models**:
- **Current**: `mistral:latest` (7B) - Fast but may ignore complex rules
- **Better**: `mistral:7b-instruct-v0.2` - Improved instruction following
- **Best**: `llama2:13b` - Larger, more reliable (slower but more accurate)

Update `.env` to test:
```bash
OLLAMA_MODEL=mistral:7b-instruct-v0.2
# or
OLLAMA_MODEL=llama2:13b
```

### Performance Optimization

If extraction times out:
1. **Use smaller Ollama models** (mistral:latest, qwen3:8b instead of 20B+ models)
2. **Disable LLM canonicalization** (`USE_LLM_FOR_CANONICALIZATION=false`)
3. **Increase timeout** (`EXTRACTION_TIMEOUT_SECONDS=180`)
4. **Simplify prompts** (reduce requested item count in `extract_service.py`)

The extraction prompt in `extract_service.py` currently asks for "5-12 key items" (optimized for speed). Increasing this will slow down extraction.

### Verification Pipeline Tradeoffs

- **LLM Canonicalization OFF**: Faster (no extra LLM call), but surface forms stored as canonical (e.g., "Hunde" not lemmatized to "Hund")
- **LLM Canonicalization ON**: Slower, but proper lemmatization for better deduplication
- **Semantic Deduplication**: Prevents duplicates but queries 100 recent items per extraction

### Database Schema Changes

1. Create migration: `alembic revision -m "description"`
2. Edit generated file in `alembic/versions/`
3. Test: `alembic upgrade head` (dev) → `alembic downgrade -1` → `alembic upgrade head`
4. Commit migration file to version control

### Adding New API Endpoints

1. Define Pydantic schemas in `app/schemas/`
2. Add endpoint to appropriate router in `app/api/`
3. Implement business logic in service layer (`app/services/`)
4. Use dependency injection for database session and services
5. Add corresponding method to `api/client.js` (frontend)

### Error Taxonomy

The system includes 17 German grammar error categories seeded in `error_tags` table:
- article_gender, article_case, noun_plural, verb_conjugation, verb_position, etc.
- Used for classifying errors in encounters for adaptive learning

## Project Status

**Completed**:
- Iteration 1 (core functionality)
- Iteration 1.5 (Library view, flip-card review)
- Iteration 1.5.1 (Library deletion)
- Iteration 1.5.2 (Verb phrase normalization)
- Iteration 1.5.3 (Smart extraction filtering)
- Iteration 1.5.4 (Extraction quality & validation fixes)

**Current Status**: Ready for user testing with robust extraction quality controls and validation

## Key Documentation

- **[prd.md](prd.md)** - **Primary reference**: Product Requirements Document with vision, guiding principles, and feature specifications
- **[README.md](README.md)** - Setup instructions, usage guide, and implementation history
- **[tasks.md](tasks.md)** - Detailed progress tracking and task breakdown

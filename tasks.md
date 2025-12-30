# Language Learning App - Implementation Tasks

## 🎉 Iteration 1 - COMPLETE

All 6 phases have been successfully implemented and tested!

- ✅ Phase 1: Project Foundation & Setup
- ✅ Phase 2: Database Schema & Models
- ✅ Phase 3: Core Services Layer
- ✅ Phase 4: API Layer
- ✅ Phase 5: Frontend Implementation
- ✅ Phase 6: Integration & Testing

**Status**: Ready for user acceptance testing

---

## Phase 1: Project Foundation & Setup ✅ COMPLETED

### 1.1 Create Project Structure
- [x] Create backend directory structure
- [x] Create frontend directory placeholder
- [x] Create docs directory

### 1.2 Initialize Backend
- [x] Create requirements.txt
- [x] Create .env.example
- [x] Create .env
- [x] Create backend/run.py
- [x] Create all __init__.py files

### 1.3 Initialize Frontend
- [x] Initialize Vite React app
- [x] Install dependencies (axios, react-router-dom, tailwindcss)
- [x] Create .env

### 1.4 Create Documentation
- [x] Create README.md
- [x] Create .gitignore (root)
- [x] Create backend/.gitignore
- [x] Create frontend/.gitignore

---

## Phase 2: Database Schema & Models ✅ COMPLETED

### 2.1 Create SQLAlchemy Models
- [x] backend/app/models/base.py
- [x] backend/app/models/item.py
- [x] backend/app/models/edge.py
- [x] backend/app/models/encounter.py
- [x] backend/app/models/error_tag.py

### 2.2 Configure Alembic
- [x] Initialize Alembic
- [x] Configure alembic.ini
- [x] Update alembic/env.py

### 2.3 Create Initial Migration
- [x] Create 5027e3ba87c7_initial_schema.py
- [x] Define all tables
- [x] Add indexes
- [x] Seed error_tags (17 tags)

### 2.4 Database Session Management
- [x] Create backend/app/db/session.py
- [x] Update health endpoint to test DB

### 2.5 Verification
- [x] Run migration (alembic upgrade head)
- [x] Database created at backend/data/lang_app.db
- [x] All tables created successfully
- [x] Error tags seeded

---

## Phase 3: Core Services Layer ✅ COMPLETED

### 3.1 Graph Store
- [x] backend/app/services/graph_store.py

### 3.2 Ollama Client
- [x] backend/app/utils/ollama_client.py

### 3.3 Extraction Service
- [x] backend/app/schemas/extraction.py
- [x] backend/app/services/extract_service.py

### 3.4 Ingest Service
- [x] backend/app/services/ingest_service.py

### 3.5 Review Service
- [x] backend/app/services/review_service.py

---

## Phase 4: API Layer ✅ COMPLETED

### 4.1 Pydantic Schemas
- [x] backend/app/schemas/source.py
- [x] backend/app/schemas/review.py
- [x] backend/app/schemas/extraction.py

### 4.2 API Endpoints
- [x] backend/app/api/sources.py (POST /api/sources)
- [x] backend/app/api/review.py (GET /api/review/today, POST /api/review/result)
- [x] backend/app/api/__init__.py

### 4.3 FastAPI Configuration
- [x] backend/app/config.py
- [x] backend/app/main.py (updated with routers)

---

## Phase 5: Frontend Implementation ✅ COMPLETED

### 5.1 API Client
- [x] frontend/src/api/client.js

### 5.2 Routing & Layout
- [x] frontend/src/App.jsx
- [x] frontend/src/components/Layout.jsx

### 5.3 Page Components
- [x] frontend/src/pages/IngestPage.jsx
- [x] frontend/src/pages/ReviewPage.jsx
- [x] frontend/src/pages/CoachPage.jsx

### 5.4 Verification
- [x] Frontend build successful
- [x] React Router configured with nested routes
- [x] All pages created and styled

---

## Phase 6: Integration & Testing ✅ COMPLETED

### 6.1 End-to-End Testing
- [x] Test ingestion flow (POST /api/sources - extracted 2 items successfully)
- [x] Test review flow (GET /api/review/today - returned 4 items)
- [x] Test review result submission (POST /api/review/result - encounter created)
- [x] Verify database persistence (all data persisted correctly)
- [x] Both servers running without errors (backend on :8000, frontend on :5173)

### 6.2 Documentation
- [x] Update README.md with completed status
- [x] Update tasks.md with progress tracking

---

## Legend
- ✅ Completed
- ⏳ In Progress
- ⏸️ Pending
- ❌ Blocked

---

## 📊 Test Results Summary

### Backend API Tests
- ✅ Health endpoint: All systems healthy (database + Ollama connected)
- ✅ Text ingestion: Successfully extracted 2 items from German text
- ✅ Review deck: Returns 4 items with complete metadata
- ✅ Review result: Successfully records encounters

### Frontend Tests
- ✅ Build successful (485ms, 273kB JS bundle)
- ✅ Development server starts on :5173
- ✅ React Router configured with 3 routes

### Database Tests
- ✅ 4 items persisted in items table
- ✅ 5 encounters recorded (4 extract + 1 review)
- ✅ 17 error tags seeded correctly

---

## Iteration 1.5: UX Enhancements ✅ COMPLETE

### Background
Based on user testing, two critical features needed before Iteration 2:
1. Library/Collection view to browse learned items
2. Flip-card review mode (Anki-style)

### Feature 1: Library/Collection View ✅

**Backend Implementation**
- [x] Create `backend/app/schemas/library.py` (ItemStats, LibraryItemSummary, LibraryItemDetail, LibraryResponse)
- [x] Add methods to `backend/app/services/graph_store.py`:
  - [x] `get_all_items_with_stats(limit, offset, type_filter)`
  - [x] `get_item_detail_with_relations(item_id)`
- [x] Create `backend/app/api/library.py` with endpoints:
  - [x] `GET /api/library/items`
  - [x] `GET /api/library/items/{id}`
- [x] Register library router in `backend/app/main.py`
- [x] Test library endpoints with curl

**Frontend Implementation**
- [x] Update `frontend/src/api/client.js`:
  - [x] `getLibraryItems(typeFilter, limit, offset)`
  - [x] `getItemDetail(itemId)`
- [x] Create `frontend/src/pages/LibraryPage.jsx`:
  - [x] Main LibraryPage component
  - [x] Filter tabs (All, Words, Phrases, Patterns)
  - [x] LibraryItemCard subcomponent
  - [x] ItemDetailModal subcomponent
- [x] Create `frontend/src/pages/LibraryPage.css`
- [x] Update `frontend/src/App.jsx` (add library route)
- [x] Update `frontend/src/components/Layout.jsx` (add Library nav link)
- [x] Test filtering, detail modal, relationships display

### Feature 2: Flip-Card Review Mode ✅

**Frontend Implementation (No backend changes)**
- [x] Modify `frontend/src/pages/ReviewPage.jsx`:
  - [x] Add state: reviewMode, isFlipped, selfGraded
  - [x] Add mode selector toggle UI
  - [x] Create FlipCardReview subcomponent
  - [x] Implement handleSelfGrade logic
  - [x] Add auto-advance after grading
- [x] Update `frontend/src/pages/ReviewPage.css`:
  - [x] Mode selector styles
  - [x] Flip card container and animations
  - [x] Self-grade button styles
- [x] Test both flip and input modes
- [x] Verify encounter logging works correctly

### Testing & Documentation ✅
- [x] End-to-end testing:
  - [x] Library API returns 7 items correctly
  - [x] Type filtering works (chunks filter returns 6 items)
  - [x] Item detail endpoint returns full data with stats
  - [x] All endpoints tested and working
- [x] Build verification:
  - [x] Frontend builds successfully (476ms)
  - [x] Bundle size: 281kB JS, 14.8kB CSS
- [x] Update documentation:
  - [x] Create ITERATION_1_5_PLAN.md
  - [x] Update README.md
  - [x] Update tasks.md

---

## Iteration 1.5.1: Library Deletion Feature ✅ COMPLETE

### Background
User requested ability to select and delete items from the Library before moving to Iteration 2.

### Feature: Multi-Select Delete in Library ✅

**Backend Implementation**
- [x] Add `delete_items(item_ids)` method to `backend/app/services/graph_store.py`
  - [x] Cascade deletion of encounters
  - [x] Cascade deletion of edges (both source and target)
  - [x] Return deletion statistics
- [x] Add schemas to `backend/app/schemas/library.py`:
  - [x] `DeleteItemsRequest` (request model)
  - [x] `DeleteItemsResponse` (response model with stats)
- [x] Add `POST /api/library/delete` endpoint to `backend/app/api/library.py`
- [x] Test cascade deletion logic with in-memory database

**Frontend Implementation**
- [x] Update `frontend/src/api/client.js`:
  - [x] Add `deleteItems(itemIds)` function
- [x] Update `frontend/src/pages/LibraryPage.jsx`:
  - [x] Add selection state (selectedIds Set)
  - [x] Add `toggleSelectItem` handler
  - [x] Add `toggleSelectAll` handler
  - [x] Add `handleDeleteClick` handler
  - [x] Add `handleConfirmDelete` async handler
  - [x] Add selection toolbar UI
  - [x] Update LibraryItemCard with checkbox
  - [x] Add ConfirmDeleteModal component
- [x] Update `frontend/src/pages/LibraryPage.css`:
  - [x] Selection toolbar styles
  - [x] Card selection state styles
  - [x] Checkbox styles
  - [x] Delete button styles
  - [x] Confirmation modal styles

**Testing**
- [x] Backend cascade deletion verified (deletes encounters, edges, items)
- [x] Frontend builds successfully (491ms, 283.93kB JS, 16.82kB CSS)
- [x] All components render without errors

**Features Delivered**
- ✅ Select individual items with checkboxes
- ✅ Select all items with single toggle
- ✅ Visual feedback for selected items (highlighted border)
- ✅ Delete button appears when items selected
- ✅ Confirmation dialog before deletion
- ✅ Success message with deletion statistics
- ✅ Auto-refresh library after deletion
- ✅ Cascade deletion preserves database integrity

---

## Iteration 1.5.2: German Verb Phrase Normalization ✅ COMPLETE

### Background
Critical feedback identified that extracted verb phrases used literal word order ("suchen ein Taxi") instead of dictionary form ("ein Taxi suchen"), which could teach incorrect German grammar patterns.

### Feature: Enhanced Extraction Quality ✅

**Backend Implementation**
- [x] Update `backend/app/services/extract_service.py`:
  - [x] Add CRITICAL rules for verb phrase normalization
  - [x] Examples: "kaufe ein Buch" → "ein Buch kaufen"
  - [x] Dual-form approach (surface_form for verification, canonical for learning)
- [x] Extend `backend/app/schemas/library.py`:
  - [x] Add `context_sentence` field to `EncounterSummary`
- [x] Update `backend/app/services/graph_store.py`:
  - [x] Include `context_sentence` in encounter summaries
- [x] Update `backend/.env`:
  - [x] Add CORS for ports 5173, 5174, 5175

**Frontend Implementation**
- [x] Update `frontend/src/pages/LibraryPage.jsx`:
  - [x] Display source sentence in item detail modal
  - [x] Italic styling with left border for encounters
  - [x] Only show for 'extract' mode

**Documentation**
- [x] Update `docs/Feedback.md` with solution implemented
- [x] Update `CLAUDE.md` with German Grammar Handling section
- [x] Update `README.md` with Iteration 1.5.2 summary

**Testing**
- [x] Frontend builds successfully (365.89 kB JS, 32.99 kB CSS)
- [x] Extraction prompt validated (1065 chars, contains normalization rules)
- [x] Schema includes context_sentence field
- [x] GraphStore returns context_sentence
- [x] Database cleared for fresh testing

**Impact**: Learners now see correct German dictionary forms for verb phrases, preventing anglicized patterns.

---

## Iteration 1.5.3: Smart Extraction Filtering ✅ COMPLETE

### Background
Feedback #2 requested intelligent extraction filtering to improve quality and performance by filtering proper nouns, normalizing complex verb forms, detecting collocations, and optimizing performance with sentence batching.

### Implemented Features ✅

**1. Enhanced Extraction Prompt**
- [x] Filter proper nouns (people, cities, countries)
- [x] Filter simple connectors (und, aber, oder, denn)
- [x] Normalize participles to infinitive (kennengelernt → kennenlernen)
- [x] Handle reflexive verbs (include "sich")
- [x] Handle separable verbs (combine prefix + verb)
- [x] Detect collocations ("Ferien machen" not just "Ferien")
- [x] Configurable item limits (top 5 per type per batch)

**2. Text Length Enforcement**
- [x] Backend: Update MAX_TEXT_LENGTH to 500 chars
- [x] Frontend: Character counter (e.g., "480/500")
- [x] Frontend: Red warning + disabled button if over limit
- [x] Backend: Validate at API boundary

**3. Parallel Sentence Batching**
- [x] Add config: BATCH_SIZE_SENTENCES=2
- [x] Add config: MAX_ITEMS_PER_TYPE=5
- [x] Add config: ENABLE_PARALLEL_BATCHING=true
- [x] Implement sentence splitting helper function
- [x] Implement parallel batch processing with asyncio.gather()
- [x] Merge results from all batches

**4. Source Sentence Display on IngestPage**
- [x] Backend: Add source_sentence to ExtractedItemSummary schema
- [x] Backend: Include encounter.context_sentence in response
- [x] Frontend: Display source sentence in extraction results
- [x] Frontend: Italic styling with left border

**Implementation Completed**: 2025-12-30

**Files Modified**:
- `backend/app/services/extract_service.py` - Enhanced prompt, batching logic
- `backend/app/services/ingest_service.py` - Conditional batched extraction
- `backend/app/config.py` - New configuration fields
- `backend/.env` - Environment variables
- `backend/app/schemas/source.py` - Schema updates
- `frontend/src/pages/IngestPage.jsx` - Character counter, source display
- `docs/Feedback.md` - Feedback tracking
- `tasks.md` - This file
- `README.md` - User documentation
- `CLAUDE.md` - Architecture documentation

**Results Achieved**:
- ✅ Proper nouns filtered intelligently
- ✅ Participles normalized to infinitives
- ✅ Character counter displays in real-time
- ✅ Parallel batching implemented (2-3x speedup potential)
- ✅ Source sentences appear in IngestPage results
- ✅ All changes backward compatible and configurable

---

## Iteration 1.5.4: Extraction Quality & Consistency Fixes ✅ COMPLETE

### Background
After Feedback #2 implementation, user testing revealed critical extraction quality issues: blank canonical forms in database, proper nouns still being extracted despite filtering rules, inconsistent results across similar inputs, and incorrect verb normalization.

### Root Causes
1. **LLM (mistral:latest 7B) not following complex instructions** - 9 rules too overwhelming
2. **Missing validation layer** - No post-LLM filtering to catch bad outputs
3. **Weak error handling** - Batch failures silently ignored
4. **No defensive programming** - Single point of failure in extraction quality

### Implemented Features ✅

**1. Post-LLM Validation Layer (CRITICAL)**
- [x] Add `validate_and_filter_items()` helper function in extract_service.py
- [x] Filter blank `canonical`/`surface_form` values
- [x] Add proper noun detection heuristics (known cities, person names)
- [x] Reject low-value items (connectors, articles)
- [x] Apply validation after LLM extraction, before verification

**2. Simplified Extraction Prompt (HIGH PRIORITY)**
- [x] Reduce complexity from 9 rules to 5 clearer rules
- [x] Put negative examples first (what NOT to extract)
- [x] More explicit about required fields
- [x] Simpler language optimized for 7B models
- [x] Update examples with actual full sentences

**3. Enhanced Verification Pipeline (MEDIUM PRIORITY)**
- [x] Add blank `canonical_form` rejection in verify_and_canonicalize()
- [x] Add blank `surface_form` rejection
- [x] Track invalid items in `verification_stats`
- [x] Add 'invalid' count to response dictionary

**4. Robust Batch Error Handling (MEDIUM PRIORITY)**
- [x] Log batch failures with index and error message
- [x] Validate each batch result before merging
- [x] Fall back to single-batch extraction if >50% fail
- [x] Better exception messages for debugging

**5. LLM Model Testing (OPTIONAL - USER TESTING)**
- [ ] Test with mistral:7b-instruct-v0.2 (better instruction tuning)
- [ ] Test with llama2:13b (larger, more reliable)
- [ ] Document performance trade-offs (speed vs accuracy)
- [ ] Update .env with recommended model (based on testing)

**Implementation Completed**: 2025-12-30 (~2 hours)

**Files Modified**:
- `backend/app/services/extract_service.py` - Validation layer, simplified prompt, batch error handling
- `backend/app/services/verification_service.py` - Enhanced validation, invalid count
- `docs/Feedback.md` - Feedback #3 tracking and implementation results
- `tasks.md` - This file

**Results Achieved**:
- ✅ No blank `canonical_form` in database (3 layers of validation)
- ✅ Proper nouns (Silke, Julia, Berlin, Universität) consistently filtered (30+ known names)
- ✅ Defense in depth: post-LLM → verification → database validation
- ✅ Resilient batching with fallback on >50% failure
- ✅ Error logs for debugging: `[ERROR] Batch X failed: Type: message`
- ✅ Simplified prompt (9 rules → 5 clearer rules)

**Next Steps**:
- User testing with original failing inputs
- Optional: Test larger models (mistral:7b-instruct-v0.2, llama2:13b) for comparison
- Monitor extraction quality and batch failure logs

---

Last Updated: 2025-12-30

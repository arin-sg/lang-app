# Iteration 2 Implementation Plan: Personalization & Error-Awareness

**Document Version**: 1.0
**Date**: 2025-12-31
**Status**: Planning Phase

---

## Executive Summary

This document provides a comprehensive gap analysis between the current implementation (Iteration 1.5.6) and the PRD requirements for Iteration 2 (Section 7.2). It identifies missing features, proposes an implementation roadmap, and provides detailed technical specifications for each component.

**Current State**: Iteration 1 MVP fully complete + 6 UX enhancement iterations (1.5.x)
**Target State**: Iteration 2 Personalization Engine fully operational
**Implementation Complexity**: Medium (infrastructure ready, new services needed)
**Estimated Scope**: ~5-7 implementation phases

---

## Table of Contents

1. [Current Implementation Status](#1-current-implementation-status)
2. [Iteration 2 Gap Analysis](#2-iteration-2-gap-analysis)
3. [Missing Core Components](#3-missing-core-components)
4. [Proposed Implementation Roadmap](#4-proposed-implementation-roadmap)
5. [Technical Specifications](#5-technical-specifications)
6. [Database Schema Extensions](#6-database-schema-extensions)
7. [API Contract Definitions](#7-api-contract-definitions)
8. [Frontend Requirements](#8-frontend-requirements)
9. [Testing Strategy](#9-testing-strategy)
10. [Risk Assessment](#10-risk-assessment)

---

## 1. Current Implementation Status

### 1.1 Iteration 1 Features (PRD 7.1) - ✅ COMPLETE

All 6 phases of Iteration 1 successfully implemented:

| Feature | Status | Evidence |
|---------|--------|----------|
| Repo & Stack Setup | ✅ Complete | FastAPI + React + Ollama working |
| Database & Schema | ✅ Complete | items, edges, encounters, error_tags tables |
| Ingest & Extract Pipeline | ✅ Complete | POST /sources with 3-layer validation |
| Basic Review Deck | ✅ Complete | GET /review/today (least-recently-seen) |
| Record Results | ✅ Complete | POST /review/result with encounters logging |
| Minimal UI | ✅ Complete | Ingest, Review, Library, Coach (placeholder) |

### 1.2 Iteration 1.5+ Enhancements - ✅ COMPLETE (Beyond MVP Scope)

Six additional enhancement iterations delivered:

- **1.5**: Library/Collection view + Flip-card review mode
- **1.5.1**: Multi-select deletion with cascade logic
- **1.5.2**: German verb phrase normalization (surface vs canonical forms)
- **1.5.3**: Smart extraction filtering + parallel batching + text length enforcement
- **1.5.4**: Post-LLM validation + simplified prompts + robust error handling
- **1.5.5**: Multi-provider LLM support (Ollama, LiteLLM, OpenAI, Gemini)
- **1.5.6**: Pattern extraction + UI terminology improvements

**Verdict**: Current implementation exceeds Iteration 1 requirements and provides a solid foundation for Iteration 2.

---

## 2. Iteration 2 Gap Analysis

### 2.1 PRD Section 7.2 Requirements vs Current State

| Requirement | PRD Section | Status | Priority |
|-------------|-------------|--------|----------|
| Implement Error Taxonomy | 7.2.1 | ⏳ Partial (DB ready, LLM not integrated) | P1 - CRITICAL |
| Activate Error Classification | 7.2.2 | ❌ Missing | P1 - CRITICAL |
| Implement Weakness Scoring | 7.2.3 | ❌ Missing | P1 - CRITICAL |
| Upgrade Deck Composition | 7.2.4 | ❌ Missing | P2 - HIGH |
| Introduce Adaptive Drills | 7.2.5 | ❌ Missing | P2 - HIGH |
| Simple Profile UI | 7.2.6 | ❌ Missing | P3 - MEDIUM |

### 2.2 MVP Feature Compliance (PRD Section 2.2)

| Feature | PRD Requirement | Current Status | Gap |
|---------|----------------|----------------|-----|
| Text Ingestion | Simple paste interface | ✅ Complete | None |
| LLM-Powered Extraction | Vocab/phrases/patterns | ✅ Complete | None |
| Local Storage | Graph-shaped SQLite | ✅ Complete | None |
| Personalized Review Deck | **Weakness-driven queue** | ⏳ Partial (simple prioritization only) | Weakness scoring missing |
| Targeted Drills | Cloze + collocation drills | ❌ Missing | No drill generation service |
| Constrained Chat Coach | Chat with corrections | ❌ Missing | No coach service |
| Error Telemetry | Systematic logging | ✅ Complete | None |

**MVP Compliance**: 5/7 complete, 1 partial, 1 missing

---

## 3. Missing Core Components

### 3.1 Error Classification Pipeline

**Current State**:
- ✅ Database: `error_tags` table seeded with 17 categories
- ✅ Schema: `encounters.error_type` column exists
- ❌ Service: No LLM integration for error classification
- ❌ API: No error classification in POST /review/result

**What's Missing**:
```python
# File: backend/app/services/error_classification_service.py (NEW)
class ErrorClassificationService:
    async def classify_error(
        self,
        incorrect_sentence: str,
        correct_sentence: str,
        context: str
    ) -> ErrorClassificationResult:
        """
        Calls LLM with Judge prompt (PRD 6.2) to classify user error.
        Returns: {
            "error_type": "gender",
            "error_subtype": "der_die",
            "confusion_target_id": None,
            "explanation": "The noun 'Entscheidung' is feminine..."
        }
        """
```

**Integration Point**: Update `POST /review/result` endpoint to:
1. Receive user's incorrect answer
2. Call ErrorClassificationService
3. Store error_type in encounters table
4. Return explanation to user

### 3.2 Weakness Scoring Algorithm

**Current State**:
- ✅ Database: Encounters table has all required telemetry fields
- ✅ Stats: `graph_store.get_item_stats()` returns basic stats (total_encounters, correct_count, success_rate)
- ❌ Formula: No implementation of weakness score calculation (PRD 5.2)
- ❌ Caching: No weakness score storage or updates

**What's Missing**:
```python
# File: backend/app/services/weakness_service.py (NEW)
class WeaknessService:
    def calculate_weakness_score(
        self,
        item_id: int,
        w_wrong: float = 2.0,
        w_confusable: float = 1.5,
        w_decay: float = 0.5,
        w_correct: float = 1.0
    ) -> float:
        """
        Implements PRD 5.2 formula:

        Weakness(Item) =
          (w_wrong × wrong_count_recent) +
          (w_confusable × confusable_penalty) +
          (w_decay × time_since_last_success) -
          (w_correct × correct_streak)

        Queries encounters table to calculate:
        - wrong_count_recent: Weighted count of recent incorrect encounters
        - confusable_penalty: Penalty if frequently confused with another item
        - time_since_last_success: Days since last correct answer
        - correct_streak: Consecutive correct answers
        """

    def calculate_all_weakness_scores(self) -> Dict[int, float]:
        """Batch calculate weakness scores for all items."""
```

**Database Extension**:
```python
# Add weakness_score column to items table for caching
class Item(Base):
    # ... existing columns ...
    weakness_score = Column(Float, default=0.0, index=True)
    last_weakness_update = Column(DateTime, default=None)
```

### 3.3 Adaptive Deck Composition

**Current State**:
- ✅ Endpoint: `GET /review/today` working
- ✅ Logic: Simple prioritization (least-recently-seen)
- ❌ Personalization: No 60/20/20 composition rule (PRD 5.3.1)

**Current Code** (review_service.py:24-36):
```python
def generate_deck(self, limit: int = 20) -> List[Dict[str, Any]]:
    """For Iteration 1: Simple prioritization (least recently seen items)."""
    return self.graph_store.get_items_for_review(limit=limit)
```

**What's Needed** (PRD 5.3.1):
```python
def generate_adaptive_deck(self, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Generate personalized deck with 60/20/20 composition:
    - 60% weakest items (by weakness score)
    - 20% known confusables (items with confusable relationships)
    - 20% patterns tied to user's top 3 error types
    """
    # Calculate bucket sizes
    weak_count = int(limit * 0.6)      # 12 items
    confusable_count = int(limit * 0.2) # 4 items
    pattern_count = int(limit * 0.2)    # 4 items

    # 1. Get top weak items by weakness_score DESC
    weak_items = self.graph_store.get_top_weak_items(weak_count)

    # 2. Get confusable items (items with confusable_with edges)
    confusable_items = self.graph_store.get_confusable_items(confusable_count)

    # 3. Get top 3 error types from user's encounter history
    top_error_types = self.graph_store.get_top_error_types(limit=3)

    # 4. Get patterns that match those error types
    pattern_items = self.graph_store.get_patterns_for_error_types(
        error_types=top_error_types,
        limit=pattern_count
    )

    # 5. Combine and shuffle
    deck = weak_items + confusable_items + pattern_items
    random.shuffle(deck)
    return deck
```

### 3.4 Drill Generation Service

**Current State**:
- ✅ Database: Encounters table supports `mode='drill'`
- ❌ Service: No drill generation service
- ❌ API: No drill endpoints
- ❌ Frontend: No drill components

**What's Missing**:
```python
# File: backend/app/services/drill_service.py (NEW)
class DrillService:
    async def generate_drills(
        self,
        item_id: int,
        item_type: str,
        error_profile: Dict[str, int],  # {"gender": 5, "word_order": 3}
        context_sentences: List[str],
        count: int = 3
    ) -> List[DrillItem]:
        """
        Generate drills based on user's error profile.
        Maps error types → drill types (PRD 5.3.2):

        - High CONFUSABLE → Minimal-pair MCQ
        - High WORD_ORDER → Sentence reordering
        - High GENDER → Article fill-in
        - High COLLOCATION → Verb selection

        Calls LLM with drill generation prompt (PRD 6.3).
        """
```

**API Endpoints Needed**:
```python
# File: backend/app/api/drills.py (NEW)
@router.get("/drills/today")
async def get_todays_drills():
    """Get personalized drills based on error profile."""

@router.post("/drills/result")
async def record_drill_result(request: DrillResultRequest):
    """Record drill attempt outcome."""
```

### 3.5 Coach Service

**Current State**:
- ✅ Frontend: CoachPage placeholder exists
- ❌ Service: No coach service implementation
- ❌ API: No coach endpoints
- ❌ LLM: No chat coach prompts

**What's Missing** (PRD 3.2, Section 2.2):
```python
# File: backend/app/services/coach_service.py (NEW)
class CoachService:
    def __init__(self, llm_provider: LLMProvider, graph_store: GraphStore):
        self.llm_provider = llm_provider
        self.graph_store = graph_store
        self.active_sessions: Dict[str, CoachSession] = {}

    async def start_session(
        self,
        user_id: str,
        target_items: List[int],
        duration_minutes: int = 5
    ) -> CoachSessionResponse:
        """
        Start a constrained chat session.
        - Selects target vocabulary/patterns to elicit
        - Sets conversation context
        - Returns initial coach prompt
        """

    async def send_message(
        self,
        user_id: str,
        message: str
    ) -> CoachMessageResponse:
        """
        Process user message and generate coach response.
        - Validates target item usage
        - Provides natural conversational feedback
        - Tracks errors for patch notes
        """

    async def end_session(self, user_id: str) -> PatchNotesResponse:
        """
        End session and generate "patch notes" summary:
        - Items used correctly
        - Errors made with classifications
        - Suggestions for practice
        """
```

**API Endpoints Needed**:
```python
# File: backend/app/api/coach.py (NEW)
@router.post("/coach/start")
async def start_coach_session()

@router.post("/coach/message")
async def send_coach_message()

@router.post("/coach/end")
async def end_coach_session()
```

### 3.6 Error Profile UI

**Current State**:
- ✅ LibraryPage shows item-level stats
- ❌ No user-level error profile display
- ❌ No weakness trends visualization

**What's Missing**:
```jsx
// File: frontend/src/pages/ProfilePage.jsx (NEW)
function ProfilePage() {
  // Display:
  // 1. Top 3 weak areas (error types with counts)
  // 2. Error fingerprint breakdown (all error types)
  // 3. Mastery trends over time (graph)
  // 4. Most confused items (confusable pairs)
  // 5. Recommended focus areas
}
```

**API Endpoint Needed**:
```python
# File: backend/app/api/profile.py (NEW)
@router.get("/profile/error-stats")
async def get_error_statistics():
    """
    Returns:
    - top_error_types: List[{"error_type": str, "count": int}]
    - total_encounters: int
    - overall_success_rate: float
    - error_trend_30_days: List[{"date": str, "error_count": int}]
    """

@router.get("/profile/confusables")
async def get_top_confusables():
    """Returns pairs of items frequently confused."""
```

---

## 4. Proposed Implementation Roadmap

### Phase 1: Error Classification Foundation (P1 - CRITICAL)

**Goal**: Enable error-aware learning by integrating LLM error classification

**Scope**:
1. Create `ErrorClassificationService` with Judge prompt (PRD 6.2)
2. Update `POST /review/result` to call error classification on incorrect answers
3. Store `error_type` in encounters table
4. Return error explanation to frontend
5. Update frontend to display error feedback

**Deliverables**:
- `backend/app/services/error_classification_service.py`
- Updated `backend/app/api/review.py`
- Updated `ReviewResultRequest` schema with error fields
- Updated `ReviewPage.jsx` to show error explanations

**Success Criteria**:
- When user answers incorrectly, error type is classified and stored
- User sees explanation: "The noun 'Entscheidung' is feminine, so it requires 'die', not 'der'."
- Encounters table populates with error_type values

**Estimated Effort**: 1-2 days

---

### Phase 2: Weakness Scoring Engine (P1 - CRITICAL)

**Goal**: Calculate personalized weakness scores for all items

**Scope**:
1. Create `WeaknessService` implementing PRD 5.2 formula
2. Add `weakness_score` column to items table (migration)
3. Implement batch calculation and caching
4. Add background task to recalculate scores periodically
5. Create GraphStore methods for weakness queries

**Deliverables**:
- `backend/app/services/weakness_service.py`
- Database migration adding `weakness_score` and `last_weakness_update` columns
- GraphStore methods: `get_top_weak_items()`, `update_weakness_scores()`
- Background task scheduler (optional: FastAPI BackgroundTasks or APScheduler)

**Success Criteria**:
- Every item has a calculated weakness_score
- Scores update after each encounter
- Query for top weak items returns correct prioritization

**Estimated Effort**: 2-3 days

---

### Phase 3: Adaptive Deck Composition (P2 - HIGH)

**Goal**: Personalize review deck with 60/20/20 composition rule

**Scope**:
1. Refactor `ReviewService.generate_deck()` to use weakness scores
2. Implement 60/20/20 composition logic
3. Add GraphStore methods for confusable and pattern queries
4. Add API parameter for deck composition strategy (for testing)

**Deliverables**:
- Updated `backend/app/services/review_service.py`
- GraphStore methods: `get_confusable_items()`, `get_patterns_for_error_types()`, `get_top_error_types()`
- Optional: `GET /review/today?strategy=adaptive` parameter

**Success Criteria**:
- Review deck contains 60% weakest items, 20% confusables, 20% patterns
- Deck composition adapts to user's error profile
- Users with different error profiles get different decks

**Estimated Effort**: 2-3 days

---

### Phase 4: Drill Generation Service (P2 - HIGH)

**Goal**: Generate targeted drills based on error profile

**Scope**:
1. Create `DrillService` with error-type → drill-type mapping
2. Implement LLM drill generation prompt (PRD 6.3)
3. Create drill API endpoints
4. Build frontend drill components (DrillPage.jsx)
5. Integrate drill results into encounters table

**Deliverables**:
- `backend/app/services/drill_service.py`
- `backend/app/api/drills.py` with GET /drills/today and POST /drills/result
- `backend/app/schemas/drill.py` for drill request/response models
- `frontend/src/pages/DrillPage.jsx` with drill UI components
- Updated navigation to include Drills page

**Drill Types to Implement**:
| Error Type | Drill Type | Frontend Component |
|-----------|-----------|-------------------|
| CONFUSABLE | Minimal-pair MCQ | MultipleChoiceDrill |
| WORD_ORDER | Sentence reordering | ReorderingDrill |
| GENDER | Article fill-in | ClozeDrill |
| COLLOCATION | Verb selection | VerbChoiceDrill |

**Success Criteria**:
- GET /drills/today returns 5-10 drills tailored to error profile
- Users with high GENDER errors get article drills
- Drill results are logged to encounters with mode='drill'
- Frontend displays drills with immediate feedback

**Estimated Effort**: 3-4 days

---

### Phase 5: Coach Chat Service (P3 - MEDIUM)

**Goal**: Enable conversational practice with targeted corrections

**Scope**:
1. Create `CoachService` with session management
2. Implement constrained chat prompt with target elicitation
3. Create coach API endpoints
4. Build frontend chat UI (update CoachPage.jsx)
5. Implement "patch notes" summary generation

**Deliverables**:
- `backend/app/services/coach_service.py`
- `backend/app/api/coach.py` with session endpoints
- `backend/app/schemas/coach.py` for request/response models
- `frontend/src/pages/CoachPage.jsx` with chat interface
- `frontend/src/components/ChatMessage.jsx` component
- `frontend/src/components/PatchNotes.jsx` component

**Success Criteria**:
- User can start 5-minute chat session
- Coach elicits use of target vocabulary/patterns
- Coach provides natural conversational corrections
- Session ends with "patch notes" summary of errors
- Errors logged to encounters with mode='chat'

**Estimated Effort**: 4-5 days

---

### Phase 6: Error Profile UI (P3 - MEDIUM)

**Goal**: Visualize user's error profile and learning progress

**Scope**:
1. Create ProfilePage with error statistics
2. Implement profile API endpoints
3. Add data visualization components (charts)
4. Display top weak items and confusables
5. Show mastery trends over time

**Deliverables**:
- `backend/app/api/profile.py` with statistics endpoints
- `frontend/src/pages/ProfilePage.jsx`
- `frontend/src/components/ErrorChart.jsx` (optional: use recharts library)
- Updated navigation to include Profile page

**Display Elements**:
1. **Top 3 Weak Areas**: Error types with counts (e.g., "Gender errors: 12")
2. **Error Fingerprint**: Breakdown of all error types
3. **Success Rate Trend**: 30-day chart of correct/incorrect
4. **Most Confused Items**: Pairs of confusable items with error counts
5. **Recommended Focus**: "Practice articles (12 gender errors this week)"

**Success Criteria**:
- Profile page displays real-time error statistics
- Charts update as user practices
- Recommendations are actionable

**Estimated Effort**: 2-3 days

---

### Phase 7: Integration & Polish (P4 - LOW)

**Goal**: Ensure all Iteration 2 features work together seamlessly

**Scope**:
1. End-to-end testing of complete personalization loop
2. Performance optimization (weakness score caching, query optimization)
3. UI polish and consistency
4. Documentation updates

**Deliverables**:
- Integration test suite
- Performance benchmarks
- Updated README.md and CLAUDE.md
- Updated tasks.md with Iteration 2 completion

**Success Criteria**:
- Complete user flow works: ingest → review (error classification) → drills (adaptive) → chat coach → profile
- System performs well with 1000+ items and encounters
- All documentation current

**Estimated Effort**: 2-3 days

---

## 5. Technical Specifications

### 5.1 Error Classification Service

**File**: `backend/app/services/error_classification_service.py`

```python
from typing import Dict, Optional
from app.providers.base import LLMProvider
from app.schemas.error import ErrorClassificationResult

class ErrorClassificationService:
    """
    Service for classifying user errors using LLM.
    Implements PRD Section 6.2 Judge prompt.
    """

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    async def classify_error(
        self,
        item_id: int,
        incorrect_answer: str,
        correct_answer: str,
        prompt: str,
        context_sentence: Optional[str] = None
    ) -> ErrorClassificationResult:
        """
        Classify a user's incorrect answer into error taxonomy.

        Args:
            item_id: The item being practiced
            incorrect_answer: User's submitted answer
            correct_answer: Expected correct answer
            prompt: The question/prompt shown to user
            context_sentence: Optional source sentence

        Returns:
            ErrorClassificationResult with:
            - error_type: str (gender, case, word_order, etc.)
            - error_subtype: str (der_die, nom_akk, etc.)
            - confusion_target_id: Optional[int]
            - explanation: str
        """
        system_prompt = self._build_judge_system_prompt()
        user_prompt = self._build_judge_user_prompt(
            incorrect_answer=incorrect_answer,
            correct_answer=correct_answer,
            prompt=prompt,
            context_sentence=context_sentence
        )

        result = await self.llm_provider.generate_json(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.3
        )

        return ErrorClassificationResult(
            error_type=result.get("error_type"),
            error_subtype=result.get("error_subtype"),
            confusion_target_id=result.get("confusion_target"),
            explanation=result.get("explanation")
        )

    def _build_judge_system_prompt(self) -> str:
        """
        System prompt for error classification (PRD 6.2).
        """
        return """You are an expert German language teacher analyzing student errors.

Your task is to classify errors into our taxonomy and provide a brief explanation.

ERROR TAXONOMY:
- GENDER: article errors (der_die, der_das, die_das)
- CASE: case errors (nom_akk, akk_dat, dat_gen)
- PREP_CASE: incorrect case after preposition
- WORD_ORDER: verb placement errors (verb_final, inversion)
- VERB_FORM: verb errors (conjugation, participle, auxiliary, tense)
- ADJECTIVE_ENDING: adjective declension errors
- COLLOCATION: unnatural word combinations
- CONFUSABLE: semantic confusion between similar words
- LEXICAL: other incorrect word choices

Output valid JSON:
{
  "error_type": "gender",
  "error_subtype": "der_die",
  "confusion_target": null,
  "explanation": "Brief explanation here"
}"""

    def _build_judge_user_prompt(
        self,
        incorrect_answer: str,
        correct_answer: str,
        prompt: str,
        context_sentence: Optional[str]
    ) -> str:
        """Build user-specific error classification prompt."""
        return f"""Classify this error:

Prompt shown to student: {prompt}
Student's answer: {incorrect_answer}
Correct answer: {correct_answer}
{f'Context: {context_sentence}' if context_sentence else ''}

Classify the error and explain briefly."""


def get_error_classification_service(
    llm_provider: LLMProvider
) -> ErrorClassificationService:
    """Factory function for dependency injection."""
    return ErrorClassificationService(llm_provider)
```

---

### 5.2 Weakness Scoring Service

**File**: `backend/app/services/weakness_service.py`

```python
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.item import Item
from app.models.encounter import Encounter
from app.models.edge import Edge

class WeaknessService:
    """
    Service for calculating personalized weakness scores.
    Implements PRD Section 5.2 formula.
    """

    # Default weights (configurable)
    DEFAULT_W_WRONG = 2.0
    DEFAULT_W_CONFUSABLE = 1.5
    DEFAULT_W_DECAY = 0.5
    DEFAULT_W_CORRECT = 1.0

    # Recency window for "recent" errors
    RECENT_DAYS = 7

    def __init__(self, db: Session):
        self.db = db

    def calculate_weakness_score(
        self,
        item_id: int,
        w_wrong: float = DEFAULT_W_WRONG,
        w_confusable: float = DEFAULT_W_CONFUSABLE,
        w_decay: float = DEFAULT_W_DECAY,
        w_correct: float = DEFAULT_W_CORRECT
    ) -> float:
        """
        Calculate weakness score for a single item.

        Formula (PRD 5.2):
        Weakness(Item) =
          (w_wrong × wrong_count_recent) +
          (w_confusable × confusable_penalty) +
          (w_decay × time_since_last_success) -
          (w_correct × correct_streak)
        """
        # 1. Calculate wrong_count_recent (weighted by recency)
        wrong_count_recent = self._calculate_recent_errors(item_id)

        # 2. Calculate confusable_penalty
        confusable_penalty = self._calculate_confusable_penalty(item_id)

        # 3. Calculate time_since_last_success (in days)
        time_since_last_success = self._calculate_time_since_success(item_id)

        # 4. Calculate correct_streak
        correct_streak = self._calculate_correct_streak(item_id)

        # Apply formula
        weakness_score = (
            (w_wrong * wrong_count_recent) +
            (w_confusable * confusable_penalty) +
            (w_decay * time_since_last_success) -
            (w_correct * correct_streak)
        )

        # Ensure non-negative
        return max(0.0, weakness_score)

    def _calculate_recent_errors(self, item_id: int) -> float:
        """
        Count recent errors with exponential decay.
        Most recent errors weighted higher.
        """
        cutoff_date = datetime.utcnow() - timedelta(days=self.RECENT_DAYS)

        recent_errors = (
            self.db.query(Encounter)
            .filter(
                Encounter.item_id == item_id,
                Encounter.correct == False,
                Encounter.timestamp >= cutoff_date
            )
            .order_by(Encounter.timestamp.desc())
            .all()
        )

        # Weight: 1.0 for today, 0.5 for 7 days ago
        weighted_count = 0.0
        for error in recent_errors:
            days_ago = (datetime.utcnow() - error.timestamp).days
            weight = 1.0 - (days_ago / self.RECENT_DAYS) * 0.5
            weighted_count += weight

        return weighted_count

    def _calculate_confusable_penalty(self, item_id: int) -> float:
        """
        Check if this item has confusable relationships.
        If user frequently confuses it with another item, add penalty.
        """
        # Check for confusable_with edges
        confusable_edges = (
            self.db.query(Edge)
            .filter(
                Edge.source_id == item_id,
                Edge.relation_type == 'confusable_with'
            )
            .all()
        )

        if not confusable_edges:
            return 0.0

        # Count how often user confused this item with the target
        penalty = 0.0
        for edge in confusable_edges:
            confusion_count = (
                self.db.query(Encounter)
                .filter(
                    Encounter.item_id == item_id,
                    Encounter.confusion_target_id == edge.target_id,
                    Encounter.correct == False
                )
                .count()
            )
            penalty += confusion_count * 0.5  # 0.5 per confusion

        return penalty

    def _calculate_time_since_success(self, item_id: int) -> float:
        """
        Calculate days since last correct answer.
        Returns 0 if never answered correctly.
        """
        last_success = (
            self.db.query(Encounter)
            .filter(
                Encounter.item_id == item_id,
                Encounter.correct == True
            )
            .order_by(Encounter.timestamp.desc())
            .first()
        )

        if not last_success:
            # Never answered correctly - check if seen at all
            first_seen = (
                self.db.query(Encounter)
                .filter(Encounter.item_id == item_id)
                .order_by(Encounter.timestamp.asc())
                .first()
            )
            if first_seen:
                days = (datetime.utcnow() - first_seen.timestamp).days
                return days  # High penalty for never-correct items
            return 0.0  # Never seen

        days = (datetime.utcnow() - last_success.timestamp).days
        return days

    def _calculate_correct_streak(self, item_id: int) -> int:
        """
        Count consecutive correct answers from most recent backwards.
        """
        recent_encounters = (
            self.db.query(Encounter)
            .filter(Encounter.item_id == item_id)
            .order_by(Encounter.timestamp.desc())
            .limit(10)  # Check last 10 encounters
            .all()
        )

        streak = 0
        for encounter in recent_encounters:
            if encounter.correct:
                streak += 1
            else:
                break  # Streak broken

        return streak

    def calculate_all_weakness_scores(self) -> Dict[int, float]:
        """
        Batch calculate weakness scores for all items.
        Returns dict of {item_id: weakness_score}.
        """
        items = self.db.query(Item).all()
        scores = {}

        for item in items:
            scores[item.id] = self.calculate_weakness_score(item.id)

        return scores

    def update_weakness_scores_in_db(self):
        """
        Update weakness_score column for all items.
        Should be called after encounters are recorded.
        """
        scores = self.calculate_all_weakness_scores()

        for item_id, score in scores.items():
            self.db.query(Item).filter(Item.id == item_id).update({
                "weakness_score": score,
                "last_weakness_update": datetime.utcnow()
            })

        self.db.commit()


def get_weakness_service(db: Session) -> WeaknessService:
    """Factory function for dependency injection."""
    return WeaknessService(db)
```

---

### 5.3 Adaptive Deck Composition Logic

**File**: `backend/app/services/review_service.py` (update existing)

```python
# Add this method to ReviewService class

def generate_adaptive_deck(self, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Generate personalized review deck with 60/20/20 composition (PRD 5.3.1).

    Composition:
    - 60% weakest items (by weakness_score DESC)
    - 20% known confusables (items with confusable_with edges)
    - 20% patterns tied to user's top 3 error types
    """
    import random

    # Calculate bucket sizes
    weak_count = int(limit * 0.6)       # 12 items for limit=20
    confusable_count = int(limit * 0.2)  # 4 items
    pattern_count = int(limit * 0.2)     # 4 items

    deck = []

    # BUCKET 1: Top weak items (60%)
    weak_items = self.graph_store.get_top_weak_items(limit=weak_count)
    deck.extend(weak_items)

    # BUCKET 2: Confusable items (20%)
    confusable_items = self.graph_store.get_confusable_items(
        limit=confusable_count,
        exclude_ids=[item['id'] for item in deck]
    )
    deck.extend(confusable_items)

    # BUCKET 3: Patterns for top error types (20%)
    top_error_types = self.graph_store.get_top_error_types(limit=3)
    if top_error_types:
        pattern_items = self.graph_store.get_patterns_for_error_types(
            error_types=top_error_types,
            limit=pattern_count,
            exclude_ids=[item['id'] for item in deck]
        )
        deck.extend(pattern_items)

    # Shuffle to avoid predictable order
    random.shuffle(deck)

    return deck[:limit]  # Ensure exact limit
```

**GraphStore methods to add**:

```python
# Add to backend/app/services/graph_store.py

def get_top_weak_items(self, limit: int = 12) -> List[Dict[str, Any]]:
    """Get items with highest weakness scores."""
    items = (
        self.db.query(Item)
        .order_by(Item.weakness_score.desc())
        .limit(limit)
        .all()
    )
    return [self._item_to_dict(item) for item in items]

def get_confusable_items(
    self,
    limit: int = 4,
    exclude_ids: List[int] = []
) -> List[Dict[str, Any]]:
    """Get items that have confusable_with relationships."""
    query = (
        self.db.query(Item)
        .join(Edge, Edge.source_id == Item.id)
        .filter(Edge.relation_type == 'confusable_with')
    )

    if exclude_ids:
        query = query.filter(Item.id.notin_(exclude_ids))

    items = query.distinct().limit(limit).all()
    return [self._item_to_dict(item) for item in items]

def get_top_error_types(self, limit: int = 3) -> List[str]:
    """Get user's most frequent error types."""
    from sqlalchemy import func

    results = (
        self.db.query(
            Encounter.error_type,
            func.count(Encounter.id).label('count')
        )
        .filter(Encounter.error_type.isnot(None))
        .group_by(Encounter.error_type)
        .order_by(func.count(Encounter.id).desc())
        .limit(limit)
        .all()
    )

    return [row.error_type for row in results]

def get_patterns_for_error_types(
    self,
    error_types: List[str],
    limit: int = 4,
    exclude_ids: List[int] = []
) -> List[Dict[str, Any]]:
    """
    Get pattern items that teach concepts related to error types.

    Mapping:
    - gender/case/prep_case → patterns tagged with case/article metadata
    - word_order → patterns with 'word order' in canonical_form
    - verb_form → patterns with verb-related templates
    """
    # Simple implementation: query patterns and filter by metadata
    patterns = (
        self.db.query(Item)
        .filter(Item.type == 'pattern')
    )

    if exclude_ids:
        patterns = patterns.filter(Item.id.notin_(exclude_ids))

    # TODO: Add metadata-based filtering for better matching
    # For now, return random patterns
    patterns = patterns.limit(limit).all()

    return [self._item_to_dict(item) for item in patterns]
```

---

## 6. Database Schema Extensions

### 6.1 Add Weakness Score Caching

**Migration**: `backend/alembic/versions/YYYYMMDD_add_weakness_score.py`

```python
"""Add weakness_score to items

Revision ID: abc123def456
Revises: <previous_migration_id>
Create Date: 2025-01-XX XX:XX:XX
"""

from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add weakness_score column with default 0.0
    op.add_column('items', sa.Column('weakness_score', sa.Float(), nullable=False, server_default='0.0'))

    # Add last_weakness_update timestamp
    op.add_column('items', sa.Column('last_weakness_update', sa.DateTime(), nullable=True))

    # Add index for fast sorting by weakness
    op.create_index('idx_items_weakness_score', 'items', ['weakness_score'], postgresql_ops={'weakness_score': 'DESC'})

def downgrade():
    op.drop_index('idx_items_weakness_score')
    op.drop_column('items', 'last_weakness_update')
    op.drop_column('items', 'weakness_score')
```

### 6.2 Database Schema Summary (After Iteration 2)

**items table**:
```sql
CREATE TABLE items (
    id INTEGER PRIMARY KEY,
    type TEXT NOT NULL,
    canonical_form TEXT NOT NULL,
    metadata_json TEXT,
    weakness_score REAL DEFAULT 0.0,  -- NEW
    last_weakness_update DATETIME,    -- NEW
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_items_canonical_form ON items(canonical_form);
CREATE INDEX idx_items_type ON items(type);
CREATE INDEX idx_items_weakness_score ON items(weakness_score DESC);  -- NEW
```

**No other table changes needed** - All other tables already support Iteration 2 features.

---

## 7. API Contract Definitions

### 7.1 Error Classification (Update Existing)

**Endpoint**: `POST /api/review/result` (update)

**Request** (updated):
```json
{
  "item_id": 123,
  "correct": false,
  "prompt": "Fill in: ___ Entscheidung treffen",
  "actual_answer": "der",
  "expected_answer": "die",
  "response_time_ms": 3500
}
```

**Response** (updated):
```json
{
  "status": "recorded",
  "encounter_id": 456,
  "error_classification": {  // NEW - only present if correct=false
    "error_type": "gender",
    "error_subtype": "der_die",
    "explanation": "The noun 'Entscheidung' is feminine, so it requires the article 'die', not 'der'."
  }
}
```

### 7.2 Drills API (New)

**Endpoint**: `GET /api/drills/today`

**Response**:
```json
{
  "drills": [
    {
      "drill_id": 1,
      "drill_type": "mcq",
      "item_id": 123,
      "prompt": "Ich wohne ___ zwei Jahren in Zürich.",
      "choices": ["seit", "für", "ab"],
      "answer": "seit",
      "explanation": "Use 'seit' for duration extending to present"
    },
    {
      "drill_id": 2,
      "drill_type": "cloze",
      "item_id": 124,
      "prompt": "Ich muss heute eine ____ treffen.",
      "answer": "Entscheidung",
      "choices": null
    }
  ]
}
```

**Endpoint**: `POST /api/drills/result`

**Request**:
```json
{
  "drill_id": 1,
  "item_id": 123,
  "correct": true,
  "user_answer": "seit",
  "response_time_ms": 2500
}
```

**Response**:
```json
{
  "status": "recorded",
  "encounter_id": 789,
  "feedback": "Correct! 'seit' is used for durations that extend to the present."
}
```

### 7.3 Coach API (New)

**Endpoint**: `POST /api/coach/start`

**Request**:
```json
{
  "duration_minutes": 5,
  "target_item_ids": [123, 124, 125]  // Optional: system selects if not provided
}
```

**Response**:
```json
{
  "session_id": "abc-123-def",
  "target_items": [
    {"id": 123, "canonical_form": "eine Entscheidung treffen"},
    {"id": 124, "canonical_form": "seit + Dativ"}
  ],
  "initial_message": "Hallo! Erzähl mir von einer wichtigen Entscheidung, die du kürzlich treffen musstest."
}
```

**Endpoint**: `POST /api/coach/message`

**Request**:
```json
{
  "session_id": "abc-123-def",
  "message": "Ich habe eine Entscheidung gemacht über mein Studium."
}
```

**Response**:
```json
{
  "session_id": "abc-123-def",
  "coach_message": "Interessant! Kannst du mehr darüber erzählen? (Übrigens: Wir sagen 'eine Entscheidung treffen', nicht 'machen'.)",
  "corrections": [
    {
      "original": "eine Entscheidung gemacht",
      "corrected": "eine Entscheidung getroffen",
      "error_type": "collocation"
    }
  ]
}
```

**Endpoint**: `POST /api/coach/end`

**Request**:
```json
{
  "session_id": "abc-123-def"
}
```

**Response**:
```json
{
  "session_id": "abc-123-def",
  "patch_notes": {
    "items_used_correctly": [
      {"id": 124, "canonical_form": "seit + Dativ", "examples": ["seit zwei Jahren"]}
    ],
    "errors_made": [
      {
        "item_id": 123,
        "error_type": "collocation",
        "correction": "eine Entscheidung treffen (not machen)",
        "explanation": "Fixed verb-noun collocation"
      }
    ],
    "recommendations": [
      "Practice collocation drills for 'Entscheidung treffen'"
    ]
  },
  "total_encounters_logged": 5
}
```

### 7.4 Profile API (New)

**Endpoint**: `GET /api/profile/error-stats`

**Response**:
```json
{
  "top_error_types": [
    {"error_type": "gender", "count": 12, "percentage": 35},
    {"error_type": "word_order", "count": 8, "percentage": 23},
    {"error_type": "collocation", "count": 6, "percentage": 17}
  ],
  "total_encounters": 100,
  "total_incorrect": 34,
  "overall_success_rate": 0.66,
  "error_trend_30_days": [
    {"date": "2025-01-01", "error_count": 2},
    {"date": "2025-01-02", "error_count": 1},
    // ... last 30 days
  ]
}
```

**Endpoint**: `GET /api/profile/confusables`

**Response**:
```json
{
  "confusable_pairs": [
    {
      "item_1": {"id": 123, "canonical_form": "seit"},
      "item_2": {"id": 124, "canonical_form": "für"},
      "confusion_count": 5,
      "last_confused": "2025-01-02T14:30:00Z"
    }
  ]
}
```

---

## 8. Frontend Requirements

### 8.1 Updated ReviewPage (Error Feedback)

**File**: `frontend/src/pages/ReviewPage.jsx` (update)

**New Features**:
- Display error explanation when answer is incorrect
- Show error type badge (e.g., "Gender Error")
- Link to related drill practice

**Mockup**:
```
┌─────────────────────────────────────┐
│ Review Card                         │
│                                     │
│ Fill in: ___ Entscheidung treffen  │
│                                     │
│ Your answer: der  ❌                │
│ Correct answer: die                 │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ 💡 Gender Error (der_die)       │ │
│ │                                 │ │
│ │ The noun 'Entscheidung' is      │ │
│ │ feminine, so it requires 'die', │ │
│ │ not 'der'.                      │ │
│ │                                 │ │
│ │ [Practice Gender Drills →]      │ │
│ └─────────────────────────────────┘ │
│                                     │
│ [Next Card]                         │
└─────────────────────────────────────┘
```

### 8.2 New DrillPage

**File**: `frontend/src/pages/DrillPage.jsx` (new)

**Components Needed**:
- `MultipleChoiceDrill` - MCQ with radio buttons
- `ClozeDrill` - Fill-in-the-blank input
- `ReorderingDrill` - Drag-and-drop sentence ordering
- `VerbChoiceDrill` - Choose correct verb for collocation

**Mockup**:
```
┌─────────────────────────────────────┐
│ Gender Practice Drills              │
│ Progress: ██████░░░░ 6/10           │
├─────────────────────────────────────┤
│                                     │
│ Fill in the correct article:       │
│                                     │
│   ___ Entscheidung treffen          │
│                                     │
│   ┌─────┐ ┌─────┐ ┌─────┐          │
│   │ der │ │ die │ │ das │          │
│   └─────┘ └─────┘ └─────┘          │
│                                     │
│ [Check Answer]                      │
│                                     │
│ Hint: Think about the gender of    │
│       'Entscheidung'                │
└─────────────────────────────────────┘
```

### 8.3 Updated CoachPage (Chat UI)

**File**: `frontend/src/pages/CoachPage.jsx` (update from placeholder)

**Components Needed**:
- `ChatMessage` - Individual message bubble
- `ChatInput` - Text input with send button
- `PatchNotes` - Summary card with corrections

**Mockup**:
```
┌─────────────────────────────────────┐
│ 💬 Chat Coach                       │
│ Session: 5:00 remaining             │
├─────────────────────────────────────┤
│                                     │
│ 🤖 Hallo! Erzähl mir von einer     │
│    wichtigen Entscheidung...        │
│                                     │
│         Ich habe eine Entscheidung  │
│         gemacht über mein Studium 👤│
│                                     │
│ 🤖 Interessant! Kannst du mehr     │
│    darüber erzählen?                │
│    💡 Tipp: 'treffen', nicht        │
│              'machen'               │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ Type your message...            │ │
│ │                            [📤] │ │
│ └─────────────────────────────────┘ │
│                                     │
│ [End Session & See Corrections]     │
└─────────────────────────────────────┘
```

### 8.4 New ProfilePage

**File**: `frontend/src/pages/ProfilePage.jsx` (new)

**Components Needed**:
- `ErrorStatsCard` - Top error types with counts
- `SuccessRateChart` - Line chart of performance over time
- `ConfusablesCard` - List of frequently confused items
- `RecommendationsCard` - Actionable next steps

**Mockup**:
```
┌─────────────────────────────────────┐
│ 📊 Your Learning Profile            │
├─────────────────────────────────────┤
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ Top Error Types                 │ │
│ │                                 │ │
│ │ 1. Gender (12 errors) ████████  │ │
│ │ 2. Word Order (8)     █████     │ │
│ │ 3. Collocation (6)    ████      │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ Success Rate (30 days)          │ │
│ │ [Line chart here]               │ │
│ │ Overall: 66% correct            │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ Most Confused Items             │ │
│ │                                 │ │
│ │ seit ↔ für (5 times)            │ │
│ │ der ↔ die (3 times)             │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ 💡 Recommendations              │ │
│ │                                 │ │
│ │ • Practice gender drills (12    │ │
│ │   errors this week)             │ │
│ │ • Review 'seit' vs 'für' rule   │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

---

## 9. Testing Strategy

### 9.1 Unit Tests

**Error Classification**:
```python
# tests/services/test_error_classification_service.py
async def test_classify_gender_error():
    result = await error_service.classify_error(
        item_id=1,
        incorrect_answer="der Entscheidung",
        correct_answer="die Entscheidung",
        prompt="Fill in: ___ Entscheidung"
    )
    assert result.error_type == "gender"
    assert result.error_subtype == "der_die"
```

**Weakness Scoring**:
```python
# tests/services/test_weakness_service.py
def test_weakness_score_calculation():
    # Setup: Item with 3 recent errors, no correct streak
    # Expected: High weakness score
    score = weakness_service.calculate_weakness_score(item_id=1)
    assert score > 5.0

def test_weakness_score_with_streak():
    # Setup: Item with 5 correct streak
    # Expected: Low/negative weakness score
    score = weakness_service.calculate_weakness_score(item_id=2)
    assert score < 2.0
```

**Deck Composition**:
```python
# tests/services/test_review_service.py
def test_adaptive_deck_composition():
    deck = review_service.generate_adaptive_deck(limit=20)

    # Check 60/20/20 composition
    weak_items = [item for item in deck if item['weakness_score'] > 5.0]
    assert len(weak_items) >= 10  # At least 50% should be weak

    # Check for confusables
    confusable_items = [item for item in deck if item.get('has_confusables')]
    assert len(confusable_items) >= 3  # At least 15%
```

### 9.2 Integration Tests

**End-to-End Error Classification Flow**:
```python
# tests/integration/test_error_classification_flow.py
async def test_review_with_error_classification():
    # 1. Submit incorrect answer
    response = await client.post("/api/review/result", json={
        "item_id": 1,
        "correct": False,
        "actual_answer": "der",
        "expected_answer": "die",
        "prompt": "___ Entscheidung"
    })

    # 2. Verify error classification in response
    assert response.json()["error_classification"]["error_type"] == "gender"

    # 3. Verify encounter logged with error_type
    encounter = db.query(Encounter).order_by(Encounter.id.desc()).first()
    assert encounter.error_type == "gender"
```

**Adaptive Deck Generation**:
```python
# tests/integration/test_adaptive_deck.py
def test_deck_adapts_to_errors():
    # 1. Create 10 items with varying weakness scores
    # 2. Generate adaptive deck
    deck = client.get("/api/review/today?strategy=adaptive").json()

    # 3. Verify weakest items are prioritized
    item_ids = [item['id'] for item in deck['items']]
    assert 1 in item_ids  # Item 1 has highest weakness
    assert 2 in item_ids  # Item 2 has second highest
```

### 9.3 Manual Testing Checklist

**Phase 1: Error Classification**
- [ ] Submit incorrect answer → Error explanation displayed
- [ ] Check encounters table → error_type populated
- [ ] Different error types classified correctly (gender, case, word order)

**Phase 2: Weakness Scoring**
- [ ] Run batch calculation → All items have weakness_score
- [ ] Make errors on item → Weakness score increases
- [ ] Correct streak on item → Weakness score decreases

**Phase 3: Adaptive Deck**
- [ ] User with high gender errors → Deck contains gender-related items
- [ ] User with high word order errors → Deck contains patterns
- [ ] User with confusable errors → Deck contains confusable pairs

**Phase 4: Drills**
- [ ] High gender errors → Article drills generated
- [ ] High confusable errors → Minimal-pair MCQ generated
- [ ] Complete drill → Result logged to encounters

**Phase 5: Coach**
- [ ] Start session → Receive initial prompt
- [ ] Make error → Coach provides correction
- [ ] End session → Patch notes show errors and corrections

**Phase 6: Profile**
- [ ] View profile → Top error types displayed
- [ ] Make more errors → Error stats update
- [ ] View confusables → Frequently confused items shown

---

## 10. Risk Assessment

### 10.1 Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| LLM error classification is inaccurate | Medium | High | Use temperature=0.3, add validation, human review of edge cases |
| Weakness scoring doesn't prioritize correctly | Medium | High | Configurable weights, A/B testing with users |
| Deck composition feels repetitive | Low | Medium | Add randomization, track "recently seen" separately |
| Drill generation is too slow | Medium | Medium | Cache drills, generate async in background |
| Coach chat is unnatural | High | Medium | Extensive prompt engineering, user feedback iteration |

### 10.2 Architectural Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Weakness score calculation is slow | Low | Medium | Cache scores, update incrementally, use indexes |
| Database queries become slow at scale | Low | High | Add indexes (weakness_score, error_type), pagination |
| LLM calls timeout on large text | Low | Medium | Already mitigated with batching and limits |

### 10.3 Product Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Users don't trust error classifications | Medium | High | Show explanations, allow manual override |
| Personalization feels opaque | Medium | Medium | Show weakness scores, explain deck composition |
| Users avoid chat coach (intimidating) | High | Medium | Make optional, start with simple scenarios |
| Drill types are too repetitive | Medium | Medium | Implement 4+ drill types, vary presentation |

---

## Appendices

### Appendix A: PRD Cross-Reference

| This Document Section | PRD Section | Status |
|----------------------|-------------|--------|
| 3.1 Error Classification | 6.2, 7.2.2 | Not Implemented |
| 3.2 Weakness Scoring | 5.2, 7.2.3 | Not Implemented |
| 3.3 Adaptive Deck | 5.3.1, 7.2.4 | Not Implemented |
| 3.4 Drill Generation | 5.3.2, 6.3, 7.2.5 | Not Implemented |
| 3.5 Coach Service | 3.2, 2.2, 7.2 | Not Implemented |
| 3.6 Error Profile UI | 7.2.6 | Not Implemented |

### Appendix B: File Creation Checklist

**New Backend Files**:
- [ ] `backend/app/services/error_classification_service.py`
- [ ] `backend/app/services/weakness_service.py`
- [ ] `backend/app/services/drill_service.py`
- [ ] `backend/app/services/coach_service.py`
- [ ] `backend/app/api/drills.py`
- [ ] `backend/app/api/coach.py`
- [ ] `backend/app/api/profile.py`
- [ ] `backend/app/schemas/error.py`
- [ ] `backend/app/schemas/drill.py`
- [ ] `backend/app/schemas/coach.py`
- [ ] `backend/alembic/versions/YYYYMMDD_add_weakness_score.py`

**New Frontend Files**:
- [ ] `frontend/src/pages/DrillPage.jsx`
- [ ] `frontend/src/pages/ProfilePage.jsx`
- [ ] `frontend/src/components/drills/MultipleChoiceDrill.jsx`
- [ ] `frontend/src/components/drills/ClozeDrill.jsx`
- [ ] `frontend/src/components/drills/ReorderingDrill.jsx`
- [ ] `frontend/src/components/drills/VerbChoiceDrill.jsx`
- [ ] `frontend/src/components/coach/ChatMessage.jsx`
- [ ] `frontend/src/components/coach/ChatInput.jsx`
- [ ] `frontend/src/components/coach/PatchNotes.jsx`
- [ ] `frontend/src/components/profile/ErrorStatsCard.jsx`
- [ ] `frontend/src/components/profile/SuccessRateChart.jsx`
- [ ] `frontend/src/components/profile/ConfusablesCard.jsx`

**Files to Update**:
- [ ] `backend/app/services/review_service.py` - Add generate_adaptive_deck()
- [ ] `backend/app/services/graph_store.py` - Add weakness/confusable/pattern queries
- [ ] `backend/app/api/review.py` - Add error classification to POST /review/result
- [ ] `backend/app/schemas/review.py` - Add error fields to ReviewResultResponse
- [ ] `backend/app/main.py` - Register new routers (drills, coach, profile)
- [ ] `frontend/src/pages/ReviewPage.jsx` - Display error explanations
- [ ] `frontend/src/pages/CoachPage.jsx` - Implement chat UI
- [ ] `frontend/src/App.jsx` - Add routes for Drills and Profile pages
- [ ] `frontend/src/components/Layout.jsx` - Add nav links for Drills and Profile

### Appendix C: Estimated Timeline

**Optimistic** (full-time, single developer):
- Phase 1 (Error Classification): 1-2 days
- Phase 2 (Weakness Scoring): 2-3 days
- Phase 3 (Adaptive Deck): 2-3 days
- Phase 4 (Drill Generation): 3-4 days
- Phase 5 (Coach Service): 4-5 days
- Phase 6 (Profile UI): 2-3 days
- Phase 7 (Integration): 2-3 days

**Total**: 16-23 days (~3-5 weeks)

**Realistic** (part-time, with iteration):
- Add 50% buffer for testing, debugging, iteration
- **Total**: 24-35 days (~5-7 weeks)

### Appendix D: Success Metrics

**Iteration 2 Complete When**:
1. ✅ Error classification integrated (100% of incorrect answers classified)
2. ✅ Weakness scores calculated for all items
3. ✅ Review deck uses 60/20/20 composition
4. ✅ At least 4 drill types implemented and working
5. ✅ Chat coach delivers 5-minute sessions with corrections
6. ✅ Profile page displays error stats and recommendations
7. ✅ All features tested end-to-end
8. ✅ Documentation updated

**Key Performance Indicators**:
- Error classification accuracy > 80%
- Weakness score correlation with actual user difficulty > 0.7
- Deck composition follows 60/20/20 rule ± 5%
- Drill completion rate > 70%
- Chat coach session completion rate > 50%

---

## Conclusion

This document provides a comprehensive roadmap for implementing Iteration 2 personalization features. The foundation from Iteration 1 is solid, and all infrastructure is in place. The next phase focuses on activating the adaptive learning engine through error classification, weakness scoring, and targeted practice.

**Recommended Next Step**: Review this plan with stakeholders, prioritize phases based on user feedback, and begin with Phase 1 (Error Classification) as it unlocks all subsequent personalization features.

**Document Owner**: Development Team
**Last Updated**: 2025-12-31
**Next Review**: After Phase 1 completion

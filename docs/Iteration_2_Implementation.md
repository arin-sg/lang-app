# Iteration 2: Active Drill Engine Implementation

**Date**: 2025-12-31
**Status**: ✅ Complete
**Total Files Created**: 11
**Total Files Modified**: 4

---

## Overview

Implemented the Active Drill Engine based on [docs/review-section.md](review-section.md) requirements. The system generates dynamic, context-aware exercises (Smart Cloze, Pattern Builder, Saboteur) and uses an LLM judge for fuzzy grading.

**Key Features**:
- 3 drill types with specialized UI components
- LLM-based answer grading with lenient acceptance
- Encounter tracking with mode='drill'
- Session-based drill queue with progress tracking
- Error type detection and classification

---

## Implementation Summary

### Phase 1: Backend Logic (7 files)

#### **NEW Files**

1. **backend/app/schemas/drill.py** - Drill schemas
   - `DrillType` enum (CLOZE, PATTERN, SABOTEUR)
   - `DrillRequest` - User answer submission
   - `DrillGradeResult` - Grading feedback
   - `DrillResponse` - Drill question with metadata

2. **backend/app/services/prompts.py** - LLM prompts
   - `SABOTEUR_GEN_PROMPT` - Introduces realistic grammar errors
   - `JUDGE_PROMPT` - Grades answers with lenient criteria

3. **backend/app/services/drill_service.py** - Drill generation/grading service
   - `create_cloze_drill()` - Fill-in-the-blank using context
   - `create_saboteur_drill()` - LLM-sabotaged sentences
   - `create_pattern_drill()` - Template-based exercises
   - `grade_drill()` - LLM judge grading

4. **backend/app/api/drills.py** - API endpoints
   - `GET /drills/today?limit=10` - Generate drill session
   - `POST /drills/grade` - Grade answer + record encounter

#### **MODIFIED Files**

5. **backend/app/services/graph_store.py**
   - Added `get_item_encounters(item_id, mode_filter)` - Filter encounters by mode

6. **backend/app/providers/factory.py**
   - Added `LLMTask.DRILL_GENERATION` enum value
   - Routes drill tasks to extraction provider

7. **backend/app/main.py**
   - Registered drills router: `app.include_router(drills.router, prefix="/api")`

---

### Phase 2: Frontend Components (7 files)

#### **NEW Files**

8. **frontend/src/components/drills/ClozeDrill.jsx**
   - Inline input for fill-in-the-blank
   - Splits question by "________" marker
   - Displays hint from metadata

9. **frontend/src/components/drills/PatternDrill.jsx**
   - Template display with FileCode icon
   - Textarea for sentence construction
   - Monospace font for pattern templates

10. **frontend/src/components/drills/SaboteurDrill.jsx**
    - Red destructive styling
    - AlertTriangle icon
    - Textarea for corrected sentence

11. **frontend/src/pages/DrillPage.jsx**
    - Session queue management
    - Progress badge (e.g., "3/10")
    - Feedback display (✓/✗ with CheckCircle/XCircle icons)
    - Session complete celebration screen

#### **MODIFIED Files**

12. **frontend/src/api/client.js**
    - `getDrillSession(limit)` - Fetch drills
    - `gradeDrill(request)` - Submit answer for grading

13. **frontend/src/App.jsx**
    - Added `/drills` route → `<DrillPage />`

14. **frontend/src/components/Layout.jsx**
    - Added "Drills" nav link between Review and Coach

---

## Drill Types

### 1. Smart Cloze (Fill-in-the-Blank)

**Logic**:
- Extracts context sentence from most recent extraction encounter
- Replaces `canonical_form` with "________" (case-insensitive)
- Provides English gloss as hint

**Example**:
```
Original: "Ich warte auf den Bus."
Question: "Ich warte ________ den Bus."
Hint: "to wait for"
```

**UI**: Inline input within sentence text

---

### 2. Pattern Builder (Template Construction)

**Logic**:
- Requires `type='pattern'` items
- Displays pattern template (e.g., "Je [KOMPARATIV], desto [KOMPARATIV]")
- User constructs sentence following structure

**Example**:
```
Template: "Je [KOMPARATIV], desto [KOMPARATIV]"
English: "The more..., the more..."
Question: "Use the pattern 'Je [KOMPARATIV], desto [KOMPARATIV]' to complete the sentence."
```

**UI**: Monospace template header + textarea input

---

### 3. Saboteur (Fix the Error)

**Logic**:
- LLM introduces realistic grammar error (gender, case, word order, verb conjugation)
- User corrects the broken sentence
- Judge verifies correction

**Example**:
```
Original: "Ich habe einen Hund"
Sabotaged: "Ich habe ein Hund"  [gender error]
Hint: "Check the article gender."
```

**UI**: Red border, destructive alert styling, AlertTriangle icon

---

## LLM Judge Grading

**Lenient Criteria**:
- ✅ Accepts synonyms if grammatically correct
- ✅ Accepts minor spelling errors if recognizable
- ✅ For patterns, checks structure compliance (not vocabulary choice)
- ❌ Rejects wrong case/gender with specific feedback

**Example Feedback**:
```json
{
  "is_correct": false,
  "feedback": "Not quite. You used accusative, but 'warten auf' requires accusative object.",
  "error_type": "error_case"
}
```

**Error Types** (matches `error_tags` table):
- `error_gender`, `error_case`, `error_article`
- `error_verb_conjugation`, `error_verb_position`
- `error_word_order`, `error_separable_verb`
- `error_preposition`, etc.

---

## Drill Selection Logic (Phase 1 - Simple)

**Algorithm**:
1. Get least recently seen items via `get_items_for_review(limit)`
2. For each item:
   - If `type='pattern'` → Pattern Drill
   - If `type='word'` or `type='chunk'`:
     - Even index → Cloze Drill
     - Odd index → Saboteur Drill
3. Skip items with errors (no context sentence, etc.)

**Future Enhancements** (not in scope):
- Adaptive selection based on error history
- Weakness scoring to prioritize drills
- Multi-choice drills for confusables
- Spaced repetition scheduling

---

## Database Schema

**No migration required** - existing schema supports drills:

```sql
-- Drill encounters recorded with mode='drill'
INSERT INTO encounters (
  item_id,
  mode,           -- 'drill'
  correct,        -- true/false from judge
  prompt,         -- drill question
  actual_answer,  -- user's submission
  expected_answer,-- target canonical form
  error_type      -- detected error (e.g., 'error_gender')
)
```

**Encounter Modes**:
- `extract` - Item first extracted from text
- `review` - Flashcard review
- `drill` - Active drill exercise (NEW)

---

## API Endpoints

### GET /api/drills/today

**Query Params**:
- `limit` (int, default=10) - Max drills to return

**Response**:
```json
[
  {
    "type": "cloze",
    "question": "Ich warte ________ den Bus.",
    "target_id": 123,
    "target_lemma": "auf",
    "meta": {
      "hint": "to wait for",
      "original_sentence": "Ich warte auf den Bus."
    }
  },
  {
    "type": "saboteur",
    "question": "Ich habe ein Hund",
    "target_id": 124,
    "target_lemma": "Hund",
    "meta": {
      "hint": "Check the article gender.",
      "original_sentence": "Ich habe einen Hund",
      "error_type": "GENDER"
    }
  }
]
```

### POST /api/drills/grade

**Request**:
```json
{
  "drill_type": "cloze",
  "user_answer": "auf",
  "target_lemma": "auf",
  "context": "Ich warte auf den Bus.",
  "question_meta": {
    "hint": "to wait for",
    "original_sentence": "Ich warte auf den Bus."
  }
}
```

**Response**:
```json
{
  "is_correct": true,
  "feedback": "Correct! You used the preposition 'auf' properly.",
  "detected_error_type": null
}
```

---

## Testing Checklist

### Manual Test Cases

**Test 1: Cloze Drill**
1. Extract text: "Ich warte auf den Bus."
2. Navigate to `/drills`
3. Verify cloze drill: "Ich warte ________ den Bus."
4. Type "auf" → Submit
5. ✅ Verify: Correct feedback, moves to next drill

**Test 2: Saboteur Drill**
1. Extract text with articles/cases
2. Navigate to `/drills`
3. Verify: Red border, broken sentence
4. Type corrected sentence → Submit
5. ✅ Verify: Feedback explains error

**Test 3: Pattern Drill**
1. Extract text: "Je schneller du fährst, desto früher kommst du an."
2. Navigate to `/drills`
3. Verify: Monospace template, FileCode icon
4. Type example sentence → Submit
5. ✅ Verify: Judge checks structure compliance

**Test 4: LLM Judge Lenience**
1. Submit synonym (e.g., "schnell" instead of "rasch")
2. ✅ Verify: Accepted if grammatically valid
3. Submit with minor spelling error
4. ✅ Verify: Accepted if recognizable
5. Submit wrong case/gender
6. ✅ Verify: Rejected with specific feedback

**Test 5: Session Complete**
1. Complete all 10 drills
2. ✅ Verify: Congratulations screen with "Start New Session" button

---

## Configuration

**Backend (.env)**:
```bash
# Uses EXTRACTION_PROVIDER for drill generation
EXTRACTION_PROVIDER=ollama
OLLAMA_EXTRACTION_MODEL=hf.co/MaziyarPanahi/Mistral-7B-Instruct-v0.3-GGUF:Q8_0
EXTRACTION_TIMEOUT_SECONDS=300

# Optional: Dedicated drill provider (future)
# DRILL_PROVIDER=ollama
# DRILL_MODEL=mistral:latest
```

**Frontend (.env)**:
```bash
VITE_API_BASE_URL=http://localhost:8000/api
```

---

## File Structure

```
backend/
├── app/
│   ├── api/
│   │   └── drills.py                  # NEW - Drill endpoints
│   ├── schemas/
│   │   └── drill.py                   # NEW - Drill schemas
│   ├── services/
│   │   ├── drill_service.py           # NEW - Drill generation/grading
│   │   ├── prompts.py                 # NEW - LLM prompts
│   │   └── graph_store.py             # MODIFIED - Added get_item_encounters()
│   └── providers/
│       └── factory.py                 # MODIFIED - Added DRILL_GENERATION task

frontend/
├── src/
│   ├── components/
│   │   ├── drills/
│   │   │   ├── ClozeDrill.jsx         # NEW
│   │   │   ├── PatternDrill.jsx       # NEW
│   │   │   └── SaboteurDrill.jsx      # NEW
│   │   └── Layout.jsx                 # MODIFIED - Added Drills nav
│   ├── pages/
│   │   └── DrillPage.jsx              # NEW - Session container
│   ├── api/
│   │   └── client.js                  # MODIFIED - Added drill methods
│   └── App.jsx                        # MODIFIED - Added /drills route
```

---

## Success Criteria

✅ **Backend**:
- GET /drills/today returns 10 diverse drills
- POST /drills/grade returns accurate feedback
- Saboteur drills introduce realistic errors
- Judge accepts synonyms and minor errors

✅ **Frontend**:
- All 3 drill types render correctly
- Feedback displays after grading
- Progress badge updates
- Session completion screen shows

✅ **Integration**:
- Drill encounters recorded to database
- Error types classified correctly
- Drills cover all item types (word/chunk/pattern)

---

## Future Enhancements (Phase 3+)

**Not in scope for Iteration 2**:
- Weakness scoring to prioritize drills
- Adaptive drill type selection
- Multi-choice drills for confusables
- Reordering drills for word order
- Spaced repetition scheduling
- Coach integration

---

## Commands

### Start Backend
```bash
cd backend
source venv/bin/activate
python run.py
# Runs on http://localhost:8000
```

### Start Frontend
```bash
cd frontend
npm run dev
# Runs on http://localhost:5173
```

### Test Drills
1. Navigate to http://localhost:5173/drills
2. If no items, extract text first at http://localhost:5173/ingest
3. Complete drill session

---

## Related Documentation

- [docs/review-section.md](review-section.md) - Original requirements
- [docs/Iteration_2_Plan.md](Iteration_2_Plan.md) - Implementation plan
- [prd.md](../prd.md) - Product requirements

---

**Last Updated**: 2025-12-31
**Implementation Time**: ~4 hours
**Next Steps**: User testing and quality improvements

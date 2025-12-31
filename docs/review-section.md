## Context

We are replacing the static "Flashcard" review system with an **Active Drill Engine**. Instead of simple recall, the system will generate dynamic, context-aware exercises based on the user's "Error Fingerprint" and the item type (Word vs. Pattern).

## Objectives

1. **Backend:** Implement a `DrillService` that generates three specific drill types:
* **Smart Cloze:** Fill-in-the-blank using original context.
* **Pattern Builder:** Construct sentences from abstract templates.
* **The Saboteur:** Correct intentionally broken grammar.


2. 
**Backend:** Create an **LLM Judge** endpoint to grade complex answers fuzzily.


3. **Frontend:** Build a `ReviewSession` container that dynamically renders the appropriate drill component.

---

## Phase 1: Backend Logic & Prompts

### 1. Define Drill Models

**File:** `backend/app/schemas.py`
**Task:** Define the schemas for the Drill API.

```python
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class DrillType(str, Enum):
    CLOZE = "cloze"
    PATTERN = "pattern"
    SABOTEUR = "saboteur"

class DrillRequest(BaseModel):
    # For grading
    drill_type: DrillType
    user_answer: str
    target_lemma: str
    context: Optional[str] = None
    question_meta: Dict[str, Any] = {}

class DrillResponse(BaseModel):
    # The generated question
    type: DrillType
    question: str
    target_id: int
    meta: Dict[str, Any] # hints, original sentence, specific error focus

```

### 2. Implement `DrillService` Logic

**File:** `backend/app/services/drill_service.py`
**Task:** Create functions to generate each drill type.

* **Logic 1: `create_cloze_drill(item)**`
* Take `item.context_snippet`.
* Replace `item.lemma` (case-insensitive) with `________`.
* Return `DrillResponse` with `type="cloze"` and `meta={"hint": item.meaning}`.


* **Logic 2: `create_saboteur_drill(item, error_profile)**`
* **Input:** Valid sentence (`item.context_snippet`) + User Weakness (e.g., "error_gender").
* 
**LLM Action:** Call `ollama` with the **Saboteur Prompt** (see below) to break the sentence.


* **Return:** `DrillResponse` with `type="saboteur"` and `question="[Broken Sentence]"`.


* **Logic 3: `grade_drill(request)**`
* **LLM Action:** Call `ollama` with the **Judge Prompt**.
* **Return:** JSON with `is_correct`, `feedback`, and `detected_error_type`.



### 3. LLM Prompts

**File:** `backend/app/services/prompts.py`
**Task:** Add these specific system prompts.

```python
SABOTEUR_GEN_PROMPT = """
You are a German Language Saboteur.
Task: Take this CORRECT sentence and introduce a SPECIFIC grammar error based on the target type.
Input: "{sentence}"
Target Error: "{error_type}" (e.g., GENDER, CASE, WORD_ORDER)

Rules:
1. Make the error realistic for a learner.
2. Do NOT change the meaning, only the grammar.

Output JSON:
{{
  "sabotaged_sentence": "Ich habe ein Hund",
  "hint": "Check the article gender."
}}
"""

JUDGE_PROMPT = """
You are a German Grammar Judge.
Drill Type: {drill_type}
Target: {target}
User Input: {user_input}
Context/Question: {context}

Task: Grade the user's answer.
1. For Cloze: Did they fill the blank correctly?
2. For Saboteur: Did they fix the grammar error?
3. For Pattern: Did they apply the structure '{target}' correctly?

Output JSON:
{{
  "is_correct": boolean,
  "feedback": "Short explanation",
  "error_type": "error_case" // Optional classification if wrong
}}
"""

```

### 4. API Endpoints

**File:** `backend/app/routers/review.py`
**Task:** Create endpoints to serve the session.

* 
`POST /review/session`: Returns a list of `DrillResponse` objects for the day (prioritizing weak items).


* `POST /review/grade`: Accepts `DrillRequest`, runs `DrillService.grade_drill`, logs result to DB, returns grading result.

---

## Phase 2: Frontend Components (React)

### 1. Drill Components

**Folder:** `frontend/src/components/drills/`
**Task:** Create three distinct components.

* **`ClozeDrill.tsx`**
* **UI:** Display the sentence with an `<input>` inline.
* **Props:** `question` (text with `________`), `onAnswer`.


* **`PatternDrill.tsx`**
* **UI:** Display the **Formula** (e.g., `Je [KOMPARATIV], desto ...`) at the top.
* **UI:** Display a scenario/prompt (e.g., "The bigger, the better").
* **Input:** Full text area for the user to construct the sentence.


* **`CorrectionDrill.tsx` (Saboteur)**
* **UI:** Display the **Incorrect Sentence** in a warning box (e.g., red border).
* **Input:** Full text area to rewrite the sentence.
* **Visuals:** Use an icon like `AlertTriangle` to indicate "Fix this!"



### 2. Session Container

**File:** `frontend/src/pages/ReviewSession.tsx`
**Task:** Manage the state of the review queue.

* **State:** `queue` (Array of drills), `currentIndex`, `isGrading` (loading state).
* **Logic:**
* On mount: Fetch drill queue from `/review/session`.
* Render `currentDrill = queue[currentIndex]`.
* Switch statement to render `<ClozeDrill>`, `<PatternDrill>`, or `<CorrectionDrill>` based on `currentDrill.type`.
* On Submit: Call `/review/grade`. Show Feedback (Success/Fail toast). Wait 1.5s. Increment index.



---

## Phase 3: Integration Steps

1. 
**Database Migration:** Ensure `encounters` table exists to log the results of `/review/grade` (Pass/Fail + Error Type).


2. **Service Integration:** Update `drill_service.py` to import `ollama` client.
3. **Frontend Route:** Add `/review` route in `App.tsx` pointing to `ReviewSession`.

---

## Verification Plan

* **Test Cloze:**
* Input: "Ich gehe ________ Hause" (Target: nach).
* User types "zu".
* Judge should return `is_correct: false`, `feedback: "Use 'nach' for direction home."`.


* **Test Saboteur:**
* System generates: "Ich helfe **den** Mann" (Error: Dative).
* User types: "Ich helfe **dem** Mann".
* Judge should return `is_correct: true`.


* **Test Pattern:**
* Target: `warten auf + [AKK]`.
* User types: "Ich warte auf dem Bus" (Dative error).
* Judge should return `is_correct: false`, `error_type: "error_case"`.
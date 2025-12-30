# Iteration 1.5 - UX Enhancements Plan

## Overview

Based on user testing of Iteration 1, two critical UX features are needed before moving to Iteration 2:

1. **Library/Collection View** - View and browse all learned items in a learner-friendly way
2. **Flip-Card Review Mode** - Anki-style flip card option in ReviewPage

**Status**: Iteration 1 complete and tested ✅ | Ready to implement 1.5

## User Requirements & Design Decisions

- **Library list view**: Rich preview (canonical form, translation, CEFR level, stats)
- **Review default mode**: Flip-card (with toggle to typing mode)
- **Relationships display**: Simple grouped list with human-friendly labels
- **Navigation**: Add Library link to main navigation bar

---

## Feature 1: Library/Collection View

### Strategic Goal

Transform the app from "black box" to "transparent learning companion." Users need to:
- Browse what they've learned
- See relationships between items
- Understand their learning progress

### Backend Implementation

**Estimated Time**: 4-5 hours

#### Files to Create/Modify:

1. **`backend/app/schemas/library.py`** (NEW)
   - `ItemStats`: Success rates, encounter counts
   - `LibraryItemSummary`: Card preview data
   - `RelatedItem`: Connected items via edges
   - `LibraryItemDetail`: Full item information
   - `LibraryResponse`: Paginated list response

2. **`backend/app/services/graph_store.py`** (MODIFY)
   - Add `get_all_items_with_stats(limit, offset, type_filter)` method
   - Add `get_item_detail_with_relations(item_id)` method
   - Map edge types to human-friendly labels

3. **`backend/app/api/library.py`** (NEW)
   - `GET /api/library/items` - Get filtered/paginated items list
   - `GET /api/library/items/{id}` - Get full item details with relationships

4. **`backend/app/main.py`** (MODIFY)
   - Register library router

#### Edge Relation Label Mapping:
```python
RELATION_LABELS = {
    "collocates_with": "Often used with",
    "confusable_with": "Don't confuse with",
    "near_synonym": "Similar meaning",
    "governs_case": "Grammar rule"
}
```

### Frontend Implementation

**Estimated Time**: 4-5 hours

#### Files to Create/Modify:

1. **`frontend/src/pages/LibraryPage.jsx`** (NEW)
   - Main LibraryPage component
   - Filter tabs (All, Words, Phrases, Patterns)
   - Items list with LibraryItemCard components
   - ItemDetailModal for full details

2. **`frontend/src/pages/LibraryPage.css`** (NEW)
   - Filter tabs styling
   - Item card styling
   - Modal overlay and content
   - Relationship chips

3. **`frontend/src/api/client.js`** (MODIFY)
   - Add `getLibraryItems(typeFilter, limit, offset)`
   - Add `getItemDetail(itemId)`

4. **`frontend/src/App.jsx`** (MODIFY)
   - Add route: `<Route path="library" element={<LibraryPage />} />`

5. **`frontend/src/components/Layout.jsx`** (MODIFY)
   - Add Library navigation link

#### Rich Preview Card Shows:
- Canonical form (large, prominent)
- English gloss
- Type badge (word/chunk/pattern)
- CEFR level (if available)
- Gender (for nouns)
- Stats: "👁 Seen X times • ✓ Y% success • Z ago"

#### Item Detail Modal Shows:
- Full metadata (gender, plural, POS, CEFR, "why worth learning")
- Performance statistics
- Related items grouped by relationship type
- Recent encounter history (optional)

---

## Feature 2: Flip-Card Review Mode

### Strategic Goal

Provide recognition-based learning (flip card) as default, while keeping production-based (typing) as option. Matches Anki UX that language learners are familiar with.

### Implementation

**Estimated Time**: 2-3 hours
**Note**: Frontend only - NO backend changes needed!

#### Files to Modify:

1. **`frontend/src/pages/ReviewPage.jsx`** (MODIFY)
   - Add state: `reviewMode` ('flip' | 'input'), `isFlipped`, `selfGraded`
   - Default to 'flip' mode
   - Add mode toggle UI at top
   - Create `FlipCardReview` subcomponent
   - Add `handleSelfGrade()` handler
   - Auto-advance after grading

2. **`frontend/src/pages/ReviewPage.css`** (MODIFY)
   - Mode selector buttons
   - Flip card container with perspective
   - Flip animation (0.6s transform)
   - Front/back card styling
   - Self-grade buttons (green for correct, red for incorrect)

#### UX Flow:

1. **Front of card**: Shows English gloss + "Show Answer" button
2. **Flip animation**: 0.6s CSS transform
3. **Back of card**: Shows German canonical form + self-grade buttons
4. **User self-grades**: Clicks "✓ I knew it" or "✗ I didn't know"
5. **Encounter logged**: Same API call as typing mode!
6. **Auto-advance**: 800ms delay, then next card

#### API Integration:

Uses existing `submitReviewResult()` API - no changes needed!
- `correct`: true/false from self-grading
- `actual_answer`: canonical_form if correct, empty if incorrect
- `expected_answer`: canonical_form
- `response_time_ms`: tracked from card show to self-grade

---

## Implementation Sequence

### Phase 1: Backend Foundation (Day 1, 4-5 hours)

1. Create `backend/app/schemas/library.py` with all response models
2. Add methods to `backend/app/services/graph_store.py`:
   - `get_all_items_with_stats()` - Join items + encounters, aggregate stats
   - `get_item_detail_with_relations()` - Get item + edges + related items
3. Create `backend/app/api/library.py` with 2 endpoints
4. Register router in `backend/app/main.py`
5. Test endpoints with curl/Postman

**Testing**:
```bash
# Test list endpoint
curl http://localhost:8000/api/library/items?type_filter=word&limit=10

# Test detail endpoint
curl http://localhost:8000/api/library/items/1
```

### Phase 2: Flip-Card Mode (Day 2, 2-3 hours)

1. Modify `frontend/src/pages/ReviewPage.jsx`:
   - Add state variables
   - Add mode selector toggle
   - Create FlipCardReview component
   - Implement handleSelfGrade logic
   - Add auto-advance
2. Update `frontend/src/pages/ReviewPage.css`:
   - Mode selector styles
   - Flip card animations
   - Self-grade button styles
3. Test both flip and input modes

**Testing**:
- Switch between modes
- Complete review in flip mode
- Verify encounter logged correctly
- Check response time tracking

### Phase 3: Library Frontend (Day 3, 4-5 hours)

1. Update `frontend/src/api/client.js` with library functions
2. Create `frontend/src/pages/LibraryPage.jsx`:
   - LibraryPage component with state management
   - LibraryItemCard subcomponent
   - ItemDetailModal subcomponent
   - Filter tabs logic
3. Create `frontend/src/pages/LibraryPage.css`
4. Update `frontend/src/App.jsx` to add library route
5. Update `frontend/src/components/Layout.jsx` to add nav link
6. Test filtering, pagination, detail modal

**Testing**:
- Ingest text → verify appears in library
- Filter by type (All, Words, Phrases, Patterns)
- Click item → view detail modal
- Check relationships display
- Verify stats accuracy

### Phase 4: Testing & Polish (Day 4, 2-3 hours)

1. **End-to-end testing**:
   - Ingest German text
   - Browse library, verify items shown
   - View item details, check relationships
   - Review in flip mode
   - Check encounter logged
   - Verify library stats updated

2. **Edge cases**:
   - Empty library (no items yet)
   - Items with no relationships
   - Items with no encounters yet
   - Very long canonical forms
   - Missing metadata fields

3. **Documentation**:
   - Update README.md with new features
   - Update tasks.md progress
   - Add screenshots (optional)

**Total Time: 12-16 hours (3-4 days)**

---

## Impact on Iteration 2

### Positive Impacts ✅

1. **Library view ready for error visualization**
   - ItemDetailModal has stats section that can be extended to show:
     - Error pattern analysis
     - Weakness scores
     - Recommended drills

2. **Flip-card encounters capture full telemetry**
   - Self-graded reviews still logged to encounters table
   - Response time tracked
   - Correct/incorrect recorded
   - Enables future error classification

3. **No schema changes**
   - Works with existing database structure
   - No migrations needed
   - Backward compatible

4. **Establishes patterns for Coach page**
   - Stats aggregation approach can be reused
   - Visualization components can be extended
   - Relationship display patterns established

### No Conflicts ❌

- Pure UX/presentation features
- Don't interfere with error taxonomy work planned for Iteration 2
- Don't change data capture or storage mechanisms
- Additive changes only - no breaking changes

### Extension Points for Iteration 2

When implementing error classification in Iteration 2, can easily add:

```jsx
// In ItemDetailModal component
<div className="error-analysis-section">
  <h3>Your Common Mistakes</h3>
  <p>Gender confusion: 60% of errors</p>
  <p>Case selection: 30% of errors</p>
  <button>Practice Gender Drill</button>
</div>
```

---

## Success Criteria

### Library View
- ✅ Library page accessible from main navigation
- ✅ Shows all learned items with filtering by type
- ✅ Item cards display rich preview (canonical, gloss, CEFR, stats)
- ✅ Click item opens detail modal
- ✅ Detail modal shows metadata + grouped relationships
- ✅ Relationships use human-friendly labels
- ✅ Stats display correctly (times seen, success rate, last seen)

### Flip-Card Mode
- ✅ Flip-card mode is default in ReviewPage
- ✅ Users can toggle between flip and input modes
- ✅ Front shows English gloss + "Show Answer" button
- ✅ Flip animation smooth (0.6s)
- ✅ Back shows German answer + self-grade buttons
- ✅ Self-grading creates proper encounter records
- ✅ Auto-advance to next card after grading
- ✅ Response time tracked accurately

### General
- ✅ All existing features continue to work
- ✅ No database migrations required
- ✅ No console errors
- ✅ Documentation updated

---

## Technical Notes

### Database Queries

**Library items with stats**:
```python
query = (
    db.query(Item)
    .outerjoin(Encounter, Item.id == Encounter.item_id)
    .group_by(Item.id)
    .with_entities(
        Item,
        func.count(Encounter.id).label('total_encounters'),
        func.sum(case((Encounter.correct == True, 1), else_=0)).label('correct_count'),
        func.max(Encounter.timestamp).label('last_seen')
    )
)
```

### Relationship Label Helpers

```python
def get_relation_label(relation_type: str) -> str:
    labels = {
        "collocates_with": "Often used with",
        "confusable_with": "Don't confuse with",
        "near_synonym": "Similar meaning",
        "governs_case": "Grammar rule",
        "minimal_pair": "Similar sounding"
    }
    return labels.get(relation_type, relation_type)
```

### Time Formatting

```javascript
function formatTimeAgo(timestamp) {
  const now = new Date();
  const then = new Date(timestamp);
  const diffMs = now - then;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffDays > 0) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  if (diffHours > 0) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
  if (diffMins > 0) return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`;
  return 'just now';
}
```

---

## Risk Assessment

### Low Risk ✅
- Backend changes are additive (new endpoints only)
- Frontend changes don't modify existing components
- No database schema changes
- Can be developed and tested incrementally

### Potential Issues & Mitigations

1. **Large library performance**
   - Mitigation: Pagination built in (limit 50 default)
   - Future: Add search/filter by CEFR or success rate

2. **Items with no encounters yet**
   - Mitigation: Handle null values gracefully
   - Show "Not reviewed yet" instead of stats

3. **Complex relationship graphs**
   - Mitigation: Limit to direct connections only (depth 1)
   - Group by type to prevent overwhelming display

4. **Browser compatibility (flip animation)**
   - Mitigation: Use standard CSS transforms
   - Tested in modern browsers (Chrome, Firefox, Safari)

---

## Files Summary

### Backend (4 files, ~200 LOC)
1. ✨ NEW: `backend/app/schemas/library.py`
2. ✨ NEW: `backend/app/api/library.py`
3. ✏️ MODIFY: `backend/app/services/graph_store.py`
4. ✏️ MODIFY: `backend/app/main.py`

### Frontend (5 files, ~400 LOC)
1. ✨ NEW: `frontend/src/pages/LibraryPage.jsx`
2. ✨ NEW: `frontend/src/pages/LibraryPage.css`
3. ✏️ MODIFY: `frontend/src/pages/ReviewPage.jsx`
4. ✏️ MODIFY: `frontend/src/pages/ReviewPage.css`
5. ✏️ MODIFY: `frontend/src/api/client.js`
6. ✏️ MODIFY: `frontend/src/App.jsx`
7. ✏️ MODIFY: `frontend/src/components/Layout.jsx`

**Total: 11 files, ~600 LOC**

---

## Next Steps After Iteration 1.5

Once these features are complete and tested:

1. **User feedback session**
   - Test library browsing flow
   - Test flip-card vs. typing preference
   - Gather insights on relationship display

2. **Plan Iteration 2**
   - Error classification implementation
   - Weakness scoring algorithm
   - Adaptive drill generation
   - Coach page with learning insights

3. **Optional enhancements** (if time permits)
   - Search functionality in library
   - Export learned items
   - Print flashcards
   - Audio pronunciation (future)

---

**Plan Created**: 2025-12-29
**Estimated Duration**: 3-4 days
**Status**: Ready to implement

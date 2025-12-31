# Pattern Extraction Test Cases

## Test Setup
1. Start backend: `cd backend && python run.py`
2. Start frontend: `cd frontend && npm run dev`
3. Navigate to Ingest page: http://localhost:5173

## Current Configuration
- Model: `Mistral-7B-Instruct-v0.3-GGUF:Q8_0` (instruct model - good!)
- Timeout: 300 seconds
- Max items per type: 5

## Test Cases

### Test 1: Verb-Preposition Pattern (PRIORITY)
**Input Text:**
```
Ich warte auf den Bus. Meine Schwester wartet auch auf den Bus.
```

**Expected Pattern:**
- Type: `pattern`
- Canonical: `warten auf + [AKK]`
- English: "to wait for (+ accusative object)"
- Structure Type: `verb_prep`

**How to Verify:**
1. Paste text in Ingest page
2. Click "Extract Items"
3. Look for pattern with FileCode icon (📄)
4. Should show `warten auf + [AKK]` in monospace font
5. Check Library → filter by "Patterns" → should appear there

---

### Test 2: Je...desto Connector (PRIORITY)
**Input Text:**
```
Je schneller du fährst, desto früher kommst du an. Je mehr du übst, desto besser wirst du.
```

**Expected Pattern:**
- Type: `pattern`
- Canonical: `Je [KOMPARATIV], desto [KOMPARATIV]`
- English: "The more..., the more..."
- Structure Type: `connector`

**How to Verify:**
1. Paste text in Ingest page
2. Click "Extract Items"
3. Look for pattern with placeholder syntax `[KOMPARATIV]`
4. Should abstract both examples into one template

---

### Test 3: Mixed Content (Realistic)
**Input Text:**
```
Ich muss heute nach Berlin fahren. Je schneller ich fahre, desto früher komme ich an. Ich warte auf den Zug.
```

**Expected Extraction:**
- Words: `Berlin`, `fahren`, `Zug`
- Phrases: `nach Berlin fahren`
- Patterns:
  - `Je [KOMPARATIV], desto [KOMPARATIV]`
  - `warten auf + [AKK]`

**How to Verify:**
1. Should extract all three types
2. Patterns should have FileCode icon
3. Check extracted items count (should have at least 2 patterns)

---

### Test 4: Modal Verb Pattern
**Input Text:**
```
Ich möchte ein Buch kaufen. Du möchtest Pizza essen. Sie möchte Deutsch lernen.
```

**Expected Pattern:**
- Type: `pattern`
- Canonical: `möchten + [VERB infinitive]` or `Ich möchte ... [verb]`
- English: "would like to..."
- Structure Type: `sentence_structure` or `idiom`

---

### Test 5: Es gibt Pattern
**Input Text:**
```
Es gibt hier einen Supermarkt. Es gibt viele Restaurants in Berlin.
```

**Expected Pattern:**
- Type: `pattern`
- Canonical: `Es gibt + [AKK]`
- English: "There is/are..."
- Structure Type: `idiom` or `sentence_structure`

---

## Success Criteria (Initial Phase - Focus on Extraction, Not Accuracy)

✅ **PASS if:**
1. At least 1 pattern is extracted from Test 1 or Test 2
2. Pattern appears with FileCode icon (📄) in results
3. Pattern appears in Library → Patterns filter
4. No validation errors in console
5. Extraction completes within 300s timeout

⚠️ **ACCEPTABLE for now:**
- Pattern canonical form not perfectly abstracted (e.g., missing placeholders)
- Structure type missing or incorrect
- Pattern not perfectly generalized
- Some patterns missed

❌ **FAIL if:**
- NO patterns extracted at all (type='pattern' never appears)
- Validation errors (missing fields)
- Timeout errors
- App crashes

---

## Debugging

### Check Backend Logs
```bash
# Look for extraction output
tail -f backend/logs/app.log  # if logging to file

# Or run backend in foreground to see console output
cd backend && python run.py
```

### Check Browser Console
1. Open DevTools (F12)
2. Look for extraction response in Network tab
3. Check for any JavaScript errors

### Check Database
```bash
sqlite3 backend/data/lang_app.db

# Count patterns
SELECT COUNT(*) FROM items WHERE type='pattern';

# View recent patterns
SELECT canonical_form, metadata_json FROM items WHERE type='pattern' ORDER BY created_at DESC LIMIT 5;
```

### Manual Prompt Test
If patterns still not extracting, test the prompt directly:

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "hf.co/MaziyarPanahi/Mistral-7B-Instruct-v0.3-GGUF:Q8_0",
  "prompt": "Extract patterns from: Ich warte auf den Bus. Return JSON with type=pattern, canonical=warten auf + [AKK]",
  "stream": false
}'
```

---

## Next Steps After Patterns Extract

Once patterns ARE being extracted (even if not perfect):

1. **Improve Abstraction Quality**: Fine-tune prompt to better abstract placeholders
2. **Add More Pattern Types**: Expand to cover more grammatical structures
3. **Pattern Metadata**: Consider adding structured pattern_meta later
4. **Frontend Enhancements**: Display grammar rules, slots, examples
5. **Pattern-Specific Review**: Create review cards optimized for patterns

---

**Last Updated**: 2025-12-31
**Current Goal**: Just get patterns to extract. Don't worry about quality yet.

"""
LLM prompts for drill generation and grading.
"""

SABOTEUR_GEN_PROMPT = """You are a German Language Saboteur.

Task: Take this CORRECT sentence and introduce a SPECIFIC grammar error based on the target type.

Input Sentence: "{sentence}"
Target Error Type: "{error_type}" (e.g., GENDER, CASE, WORD_ORDER, VERB_CONJUGATION)

Rules:
1. Make the error realistic for a learner (common mistakes only)
2. Do NOT change the meaning, only introduce a grammar mistake
3. The error should be noticeable but subtle
4. Return ONLY the sabotaged sentence and a brief hint

Output JSON (no markdown, no extra text):
{{
  "sabotaged_sentence": "Ich habe ein Hund",
  "hint": "Check the article gender."
}}"""

JUDGE_PROMPT = """You are a German Grammar Judge.

Drill Type: {drill_type}
Expected Target: {target}
User's Answer: {user_input}
Context/Original: {context}

Task: Grade the user's answer based on the drill type.

For CLOZE drills:
- Did they fill the blank correctly?
- Is the answer semantically and grammatically correct in context?

For SABOTEUR drills:
- Did they fix the grammar error?
- Is the corrected sentence now grammatically correct?

For PATTERN drills:
- Did they apply the structure '{target}' correctly?
- Is the word order and case usage correct?

Grading Guidelines:
- Be LENIENT with minor spelling errors if the word is recognizable
- Accept SYNONYMS if grammatically correct
- For patterns, check structure compliance, not vocabulary choice

Output JSON (no markdown, no extra text):
{{
  "is_correct": true,
  "feedback": "Correct! You used the dative case properly with 'mit'.",
  "error_type": null
}}

If incorrect, provide:
{{
  "is_correct": false,
  "feedback": "Not quite. You used accusative, but 'warten auf' requires accusative object.",
  "error_type": "error_case"
}}"""

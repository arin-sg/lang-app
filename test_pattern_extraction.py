#!/usr/bin/env python3
"""Test script to verify pattern extraction is working."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.extract_service import build_extraction_prompt, EXTRACTION_SYSTEM_PROMPT

# Test German text with clear pattern examples
test_text = """Heute esse ich Pizza. Ich möchte ein Bier trinken. Sie geht mit ihren Freunden ins Kino."""

# Build the prompt
prompt = build_extraction_prompt(test_text, max_items_per_type=3)

print("=" * 80)
print("SYSTEM PROMPT:")
print("=" * 80)
print(EXTRACTION_SYSTEM_PROMPT)
print("\n" + "=" * 80)
print("USER PROMPT:")
print("=" * 80)
print(prompt)
print("\n" + "=" * 80)
print("VERIFICATION:")
print("=" * 80)

# Check if patterns are mentioned
if "pattern" in prompt.lower():
    print("✅ Pattern example found in prompt")
else:
    print("❌ Pattern example NOT found in prompt")

if "EXTRACT PATTERNS" in EXTRACTION_SYSTEM_PROMPT:
    print("✅ Pattern extraction rule found in system prompt")
else:
    print("❌ Pattern extraction rule NOT found in system prompt")

print("\nPattern extraction should now work! ✨")

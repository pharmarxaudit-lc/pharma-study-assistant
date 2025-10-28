#!/usr/bin/env python3
"""
Test the preview generator with just 3 questions to verify it works.
"""

import json
import sqlite3
import os
import sys
import anthropic

# Add backend to path to import config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from config import Config

DB_PATH = '/Users/luiscotto/Code/pharma-study-assistant/backend/pharma_exam.db'

def test_ai_generation():
    """Test AI generation with 3 sample questions."""

    print("\n" + "="*80)
    print("TESTING AI DEFINITION GENERATION")
    print("Testing with 3 sample questions")
    print("="*80)

    # Get 3 questions with string array format
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, question_text, key_terms_json, explanation
        FROM questions
        WHERE key_terms_json NOT LIKE '%"term":%'
        AND LENGTH(key_terms_json) > 2
        ORDER BY id
        LIMIT 3
    """)

    questions = cursor.fetchall()
    conn.close()

    api_key = Config.ANTHROPIC_API_KEY or os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("\n❌ ANTHROPIC_API_KEY not found in config or environment")
        print("   Please set it in backend/.env or export ANTHROPIC_API_KEY='your-key-here'")
        return False

    client = anthropic.Anthropic(api_key=api_key)

    print(f"\n✅ Found {len(questions)} test questions")
    print(f"✅ API key loaded")

    for idx, (q_id, q_text, key_terms_json, explanation) in enumerate(questions, 1):
        print(f"\n{'='*80}")
        print(f"Test {idx}/3: Question {q_id}")
        print(f"{'='*80}")

        current_terms = json.loads(key_terms_json)

        print(f"\nQuestion: {q_text[:100]}...")
        print(f"\nCurrent terms (string array): {current_terms}")

        prompt = f"""Given this pharmacy law exam question and its explanation, provide concise, accurate definitions for each term.

Question: {q_text}

Explanation: {explanation}

Terms to define: {', '.join(current_terms)}

For each term, provide a brief (1-2 sentence) definition that:
1. Is specific to Puerto Rico pharmacy law context
2. Would help a student understand the concept
3. Is accurate based on the explanation provided

Return ONLY a valid JSON array with this exact format:
[
  {{"term": "term1", "definition": "Brief definition here"}},
  {{"term": "term2", "definition": "Brief definition here"}}
]

No additional text, just the JSON array."""

        print(f"\n🤖 Calling Claude API...")

        try:
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text.strip()
            definitions = json.loads(response_text)

            print(f"✅ Success! Generated {len(definitions)} definitions:")
            for term_obj in definitions:
                print(f"\n   • {term_obj['term']}")
                print(f"     → {term_obj['definition']}")

        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    print(f"\n{'='*80}")
    print("✅ TEST PASSED - AI generation is working correctly!")
    print(f"{'='*80}")
    print(f"\nYou can now run the full generator:")
    print(f"  python generate_keyterms_preview.py")
    print()

    return True

if __name__ == '__main__':
    try:
        success = test_ai_generation()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

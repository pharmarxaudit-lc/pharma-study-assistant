#!/usr/bin/env python3
"""
Generate preview of key_terms standardization using AI.
Creates a comparison file showing BEFORE and AFTER for review.
Does NOT modify the database - only generates preview.
"""

import json
import sqlite3
import os
import sys
import anthropic
from datetime import datetime

# Add backend to path to import config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from config import Config

DB_PATH = '/Users/luiscotto/Code/pharma-study-assistant/backend/pharma_exam.db'
OUTPUT_FILE = 'keyterms_standardization_preview.txt'
JSON_OUTPUT = 'keyterms_standardization_preview.json'

def get_questions_needing_conversion():
    """Get all questions with string array key_terms."""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, question_text, key_terms_json, explanation
        FROM questions
        WHERE key_terms_json NOT LIKE '%"term":%'
        AND LENGTH(key_terms_json) > 2
        ORDER BY id
    """)

    results = cursor.fetchall()
    conn.close()

    return results

def generate_definitions_with_ai(question_text, explanation, terms_list):
    """Use Claude API to generate term definitions based on question context."""

    api_key = Config.ANTHROPIC_API_KEY or os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("⚠️  Warning: ANTHROPIC_API_KEY not found. Using placeholder definitions.")
        return [{"term": term, "definition": f"[Definition needed for: {term}]"} for term in terms_list]

    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""Given this pharmacy law exam question and its explanation, provide concise, accurate definitions for each term.

Question: {question_text}

Explanation: {explanation}

Terms to define: {', '.join(terms_list)}

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

    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text.strip()

        # Parse the JSON response
        definitions = json.loads(response_text)

        return definitions

    except Exception as e:
        print(f"   ⚠️  Error with AI generation: {e}")
        return [{"term": term, "definition": f"[AI generation failed: {term}]"} for term in terms_list]

def generate_preview():
    """Generate preview file with before/after comparison."""

    print("\n" + "="*80)
    print("KEY TERMS STANDARDIZATION PREVIEW GENERATOR")
    print("="*80)

    questions = get_questions_needing_conversion()

    print(f"\n📊 Found {len(questions)} questions needing conversion")
    print(f"   Output: {OUTPUT_FILE}")
    print(f"   JSON Data: {JSON_OUTPUT}")

    print("\n🤖 Generating AI definitions... (this may take a few minutes)")

    preview_data = []
    conversions = []

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("KEY TERMS STANDARDIZATION PREVIEW\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Questions: {len(questions)}\n")
        f.write("="*80 + "\n\n")
        f.write("⚠️  IMPORTANT: This is a PREVIEW only. Review before applying changes.\n\n")
        f.write("="*80 + "\n\n")

        for idx, (q_id, q_text, key_terms_json, explanation) in enumerate(questions, 1):
            print(f"   Processing {idx}/{len(questions)}: Question {q_id}...", end='\r')

            # Parse current terms
            try:
                current_terms = json.loads(key_terms_json)
            except:
                current_terms = []

            if not current_terms:
                continue

            # Generate new format with AI
            new_terms = generate_definitions_with_ai(q_text, explanation or "", current_terms)

            # Store for JSON output
            conversions.append({
                'question_id': q_id,
                'question_text': q_text,
                'before': current_terms,
                'after': new_terms
            })

            # Write to preview file
            f.write(f"{'='*80}\n")
            f.write(f"Question {q_id}\n")
            f.write(f"{'='*80}\n\n")
            f.write(f"Text: {q_text[:100]}...\n\n")

            f.write("BEFORE (String Array):\n")
            f.write("-" * 40 + "\n")
            for term in current_terms:
                f.write(f"  • {term}\n")

            f.write("\nAFTER (Object Format):\n")
            f.write("-" * 40 + "\n")
            for term_obj in new_terms:
                term_name = term_obj.get('term', 'N/A')
                definition = term_obj.get('definition', 'N/A')
                f.write(f"  • {term_name}\n")
                f.write(f"    → {definition}\n")

            f.write("\n" + "="*80 + "\n\n")

    # Save JSON data for easy programmatic access
    preview_data = {
        'generated_at': datetime.now().isoformat(),
        'total_conversions': len(conversions),
        'conversions': conversions
    }

    with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(preview_data, f, indent=2, ensure_ascii=False)

    print(f"\n\n✅ Preview generated successfully!")
    print(f"\n📄 Files created:")
    print(f"   1. {OUTPUT_FILE} - Human-readable preview")
    print(f"   2. {JSON_OUTPUT} - Structured data for apply script")

    print(f"\n📋 Next Steps:")
    print(f"   1. Review {OUTPUT_FILE} to verify AI-generated definitions")
    print(f"   2. Check for accuracy, clarity, and correctness")
    print(f"   3. If approved, run: python apply_keyterms_standardization.py")
    print(f"   4. If changes needed, you can manually edit {JSON_OUTPUT}")

    print(f"\n💡 Tips for Review:")
    print(f"   - Ensure definitions are accurate to PR pharmacy law")
    print(f"   - Check that definitions match the question context")
    print(f"   - Verify terminology is consistent across questions")
    print(f"   - Look for any placeholder/error messages")

    print("\n" + "="*80)

    return True

if __name__ == '__main__':
    try:
        success = generate_preview()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Generation interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

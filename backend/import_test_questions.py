#!/usr/bin/env python3
"""
Import and process test questions from external PDFs.

This script:
1. Extracts text from test PDFs (Q&A format)
2. Uses Claude to parse and standardize questions to match existing format
3. Deduplicates against existing questions in database
4. Adds new questions to the database

Usage:
    python import_test_questions.py <pdf_path> [--dry-run] [--document-id <id>]
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional, Tuple

import anthropic
from config import Config
from database import get_database
from database_models import Document, Question
from pdf_extractor import PDFExtractor
from sqlalchemy import func

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class TestQuestionImporter:
    """Handles importing test questions from PDFs."""

    def __init__(self, pdf_path: str, document_id: Optional[int] = None):
        self.pdf_path = pdf_path
        self.document_id = document_id
        self.db = get_database(Config.DATABASE_PATH)
        self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)

    def extract_raw_text(self) -> str:
        """Extract raw text from PDF."""
        logger.info(f"Extracting text from: {self.pdf_path}")

        extractor = PDFExtractor(self.pdf_path)
        pages_data = extractor.extract_all()
        extractor.close()

        logger.info(f"Extracted {len(pages_data)} pages")

        # Combine all text
        full_text = []
        for page in pages_data:
            page_num = page.get('page', 0)
            full_text.append(f"\n--- Page {page_num} ---\n")

            # Add headers
            for header in page.get('headers', []):
                full_text.append(f"# {header}\n")

            # Add content
            for content_item in page.get('content', []):
                if isinstance(content_item, dict):
                    full_text.append(content_item.get('text', '') + '\n')
                else:
                    full_text.append(str(content_item) + '\n')

        return ''.join(full_text)

    def parse_questions_with_claude(self, raw_text: str) -> List[Dict]:
        """Use Claude to parse and standardize questions from raw text."""
        logger.info("Parsing questions with Claude API...")

        prompt = f"""You are tasked with extracting and standardizing pharmacy exam questions from a PDF document.

The text below contains questions and answers in various formats. Your job is to:

1. **Identify all questions** in the text
2. **Standardize each question** to match this exact JSON format:

{{
  "question_text": "The full question text in Spanish",
  "question_type": "single_answer" or "choose_all",
  "difficulty": "basic" or "intermediate" or "advanced",
  "options": {{
    "A": "Option A text",
    "B": "Option B text",
    "C": "Option C text",
    "D": "Option D text"
  }},
  "correct_answer": "A" (for single) or "A,B,C" (for multiple, comma-separated, sorted alphabetically),
  "explanation": "Detailed explanation in Spanish of why the answer is correct",
  "key_terms": ["term1", "term2", "term3"],
  "regulatory_context": "Relevant law/regulation reference (e.g., 'Ley 247 de 2004')",
  "topic_name": "The topic this question belongs to"
}}

**IMPORTANT RULES:**
- All text must be in Spanish
- For "choose_all" questions, the question text should include "Seleccione todas las correctas" or similar
- correct_answer for multiple choice should be comma-separated letters sorted alphabetically (e.g., "A,C,D")
- Infer difficulty based on complexity: basic (definition/recall), intermediate (application), advanced (analysis/synthesis)
- Extract regulatory references like "Ley 247 de 2004", "Ley 243 de 1938", etc.
- Topic names should match common pharmacy law topics
- If the question references a specific scenario, include that in question_text

**OUTPUT FORMAT:**
Return ONLY a valid JSON array of question objects. No markdown, no explanations, just the JSON array.

---

**RAW TEXT FROM PDF:**

{raw_text}

---

**OUTPUT (JSON array only):**"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=16000,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = response.content[0].text.strip()

            # Try to extract JSON if wrapped in markdown
            if response_text.startswith('```'):
                # Remove markdown code blocks
                lines = response_text.split('\n')
                response_text = '\n'.join(
                    line for line in lines
                    if not line.strip().startswith('```')
                )

            questions = json.loads(response_text)
            logger.info(f"Successfully parsed {len(questions)} questions from PDF")

            return questions

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response as JSON: {e}")
            logger.error(f"Response was: {response_text[:500]}...")
            return []
        except Exception as e:
            logger.error(f"Error calling Claude API: {e}", exc_info=True)
            return []

    def find_similar_questions(self, question_text: str, threshold: float = 0.85) -> List[Dict]:
        """Find similar questions in database using simple text similarity."""
        with self.db.session() as session:
            existing_questions = session.query(Question).all()

            similar = []
            question_text_clean = question_text.lower().strip()

            for q in existing_questions:
                existing_text_clean = q.question_text.lower().strip()

                # Simple similarity: check if texts are very similar
                # For more robust matching, could use difflib or fuzzy matching
                if question_text_clean == existing_text_clean:
                    similar.append({
                        'id': q.id,
                        'question_text': q.question_text,
                        'topic_name': q.topic_name
                    })
                elif len(question_text_clean) > 20:
                    # Check for substantial overlap (80%+ of words in common)
                    words_new = set(question_text_clean.split())
                    words_existing = set(existing_text_clean.split())

                    if len(words_new) > 0:
                        overlap = len(words_new & words_existing) / len(words_new)
                        if overlap >= threshold:
                            similar.append({
                                'id': q.id,
                                'question_text': q.question_text,
                                'topic_name': q.topic_name
                            })

            return similar

    def deduplicate_questions(self, parsed_questions: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """Separate new questions from duplicates."""
        logger.info("Deduplicating against existing questions...")

        new_questions = []
        duplicate_questions = []

        for q in parsed_questions:
            similar = self.find_similar_questions(q['question_text'])

            if similar:
                logger.info(f"  DUPLICATE: '{q['question_text'][:60]}...' matches existing ID {similar[0]['id']}")
                duplicate_questions.append({
                    'parsed': q,
                    'existing': similar[0]
                })
            else:
                logger.info(f"  NEW: '{q['question_text'][:60]}...'")
                new_questions.append(q)

        logger.info(f"\nResults: {len(new_questions)} new, {len(duplicate_questions)} duplicates")

        return new_questions, duplicate_questions

    def add_questions_to_database(self, questions: List[Dict], dry_run: bool = True) -> int:
        """Add new questions to database."""
        if not questions:
            logger.info("No questions to add")
            return 0

        if dry_run:
            logger.info(f"\n{'='*80}")
            logger.info("DRY RUN - Would add these questions:")
            logger.info(f"{'='*80}")
            for idx, q in enumerate(questions, 1):
                logger.info(f"\n{idx}. {q['question_text'][:80]}...")
                logger.info(f"   Type: {q['question_type']}, Difficulty: {q['difficulty']}")
                logger.info(f"   Topic: {q['topic_name']}")
                logger.info(f"   Correct: {q['correct_answer']}")
            logger.info(f"\n{'='*80}")
            logger.info("DRY RUN - No changes made. Use --execute to add questions.")
            return 0

        with self.db.session() as session:
            # Get or create document
            if self.document_id:
                document = session.query(Document).filter_by(id=self.document_id).first()
                if not document:
                    logger.error(f"Document ID {self.document_id} not found")
                    return 0
            else:
                # Use default document or create one
                document = session.query(Document).first()
                if not document:
                    logger.error("No document found in database. Please specify --document-id")
                    return 0

            logger.info(f"Adding questions to document: {document.file_id}")

            added_count = 0
            for q_data in questions:
                try:
                    question = Question(
                        document_id=document.id,
                        topic_id=0,  # Will be assigned based on topic_name
                        topic_name=q_data['topic_name'],
                        question_type=q_data['question_type'],
                        difficulty=q_data['difficulty'],
                        question_text=q_data['question_text'],
                        options_json=json.dumps(q_data['options']),
                        correct_answer=q_data['correct_answer'],
                        explanation=q_data.get('explanation', ''),
                        key_terms_json=json.dumps(q_data.get('key_terms', [])),
                        regulatory_context=q_data.get('regulatory_context', ''),
                        pages='',  # External questions don't have page references
                        times_seen=0,
                        times_correct=0
                    )
                    session.add(question)
                    added_count += 1

                except Exception as e:
                    logger.error(f"Error adding question: {e}")
                    logger.error(f"Question data: {q_data}")

            session.commit()
            logger.info(f"\n✅ Successfully added {added_count} questions to database")

            return added_count


def main():
    parser = argparse.ArgumentParser(
        description="Import test questions from PDF files"
    )
    parser.add_argument('pdf_path', help='Path to PDF file containing test questions')
    parser.add_argument('--document-id', type=int, help='Document ID to associate questions with')
    parser.add_argument('--execute', action='store_true', help='Actually add questions (default is dry-run)')
    parser.add_argument('--output', help='Save parsed questions to JSON file')

    args = parser.parse_args()

    if not os.path.exists(args.pdf_path):
        logger.error(f"PDF file not found: {args.pdf_path}")
        return 1

    if not Config.ANTHROPIC_API_KEY:
        logger.error("ANTHROPIC_API_KEY not configured")
        return 1

    dry_run = not args.execute

    logger.info("="*80)
    logger.info("TEST QUESTION IMPORTER")
    logger.info("="*80)
    logger.info(f"PDF: {args.pdf_path}")
    logger.info(f"Mode: {'EXECUTE' if not dry_run else 'DRY RUN'}")
    logger.info(f"Document ID: {args.document_id or 'Auto-detect'}")
    logger.info("="*80)

    try:
        importer = TestQuestionImporter(args.pdf_path, args.document_id)

        # Step 1: Extract text
        raw_text = importer.extract_raw_text()

        # Step 2: Parse with Claude
        parsed_questions = importer.parse_questions_with_claude(raw_text)

        if not parsed_questions:
            logger.error("No questions parsed from PDF")
            return 1

        # Save parsed questions if requested
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(parsed_questions, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved parsed questions to: {args.output}")

        # Step 3: Deduplicate
        new_questions, duplicates = importer.deduplicate_questions(parsed_questions)

        # Step 4: Add to database
        added = importer.add_questions_to_database(new_questions, dry_run=dry_run)

        logger.info("\n" + "="*80)
        logger.info("SUMMARY")
        logger.info("="*80)
        logger.info(f"Total questions parsed: {len(parsed_questions)}")
        logger.info(f"Duplicates found: {len(duplicates)}")
        logger.info(f"New questions: {len(new_questions)}")
        logger.info(f"Questions added: {added if not dry_run else 0}")
        logger.info("="*80)

        return 0

    except Exception as e:
        logger.error(f"Error during import: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())

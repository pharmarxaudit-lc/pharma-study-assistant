#!/usr/bin/env python3
"""
Analyze and review potential duplicate questions in the database.

This script provides multiple approaches to identify duplicates:
1. Exact text matches (case-insensitive)
2. High similarity matches (configurable threshold)
3. Similar topic + answer pattern
4. Semantic similarity (optional with fuzzy matching)

Usage:
    python analyze_duplicate_questions.py [--threshold 0.85] [--fuzzy] [--export duplicates.json]
"""

import argparse
import json
import logging
from collections import defaultdict
from typing import List, Dict, Tuple
from difflib import SequenceMatcher

from config import Config
from database import get_database
from database_models import Question

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class DuplicateAnalyzer:
    """Analyze questions for potential duplicates."""

    def __init__(self, threshold: float = 0.85, use_fuzzy: bool = False):
        self.threshold = threshold
        self.use_fuzzy = use_fuzzy
        self.db = get_database(Config.DATABASE_PATH)

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        if self.use_fuzzy:
            # Use SequenceMatcher for more sophisticated matching
            return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
        else:
            # Simple word overlap
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())

            if not words1 or not words2:
                return 0.0

            intersection = words1 & words2
            union = words1 | words2

            return len(intersection) / len(union)

    def find_exact_duplicates(self) -> Dict[str, List[Dict]]:
        """Find questions with identical text (case-insensitive)."""
        logger.info("Finding exact text duplicates...")

        with self.db.session() as session:
            all_questions = session.query(Question).all()

            # Group by normalized text
            text_groups = defaultdict(list)
            for q in all_questions:
                normalized = q.question_text.lower().strip()
                text_groups[normalized].append({
                    'id': q.id,
                    'question_text': q.question_text,
                    'correct_answer': q.correct_answer,
                    'topic_name': q.topic_name,
                    'difficulty': q.difficulty,
                    'times_seen': q.times_seen,
                    'times_correct': q.times_correct
                })

            # Filter to only duplicates
            duplicates = {text: questions for text, questions in text_groups.items() if len(questions) > 1}

            logger.info(f"Found {len(duplicates)} sets of exact duplicates")
            return duplicates

    def find_similar_questions(self) -> List[Dict]:
        """Find questions with high similarity but not exact matches."""
        logger.info(f"Finding similar questions (threshold: {self.threshold})...")

        with self.db.session() as session:
            all_questions = session.query(Question).all()

            similar_pairs = []
            checked_pairs = set()

            for i, q1 in enumerate(all_questions):
                for q2 in all_questions[i+1:]:
                    # Skip if already checked
                    pair_key = tuple(sorted([q1.id, q2.id]))
                    if pair_key in checked_pairs:
                        continue

                    checked_pairs.add(pair_key)

                    # Skip if texts are identical (already found by exact duplicates)
                    if q1.question_text.lower().strip() == q2.question_text.lower().strip():
                        continue

                    # Calculate similarity
                    similarity = self.calculate_similarity(q1.question_text, q2.question_text)

                    if similarity >= self.threshold:
                        similar_pairs.append({
                            'similarity': similarity,
                            'question1': {
                                'id': q1.id,
                                'text': q1.question_text,
                                'answer': q1.correct_answer,
                                'topic': q1.topic_name,
                                'difficulty': q1.difficulty
                            },
                            'question2': {
                                'id': q2.id,
                                'text': q2.question_text,
                                'answer': q2.correct_answer,
                                'topic': q2.topic_name,
                                'difficulty': q2.difficulty
                            }
                        })

            # Sort by similarity (highest first)
            similar_pairs.sort(key=lambda x: x['similarity'], reverse=True)

            logger.info(f"Found {len(similar_pairs)} pairs of similar questions")
            return similar_pairs

    def find_topic_answer_duplicates(self) -> Dict[str, List[Dict]]:
        """Find questions with same topic and correct answer pattern."""
        logger.info("Finding questions with same topic + answer pattern...")

        with self.db.session() as session:
            all_questions = session.query(Question).all()

            # Group by topic + answer
            topic_answer_groups = defaultdict(list)
            for q in all_questions:
                key = f"{q.topic_name}||{q.correct_answer}"
                topic_answer_groups[key].append({
                    'id': q.id,
                    'question_text': q.question_text,
                    'correct_answer': q.correct_answer,
                    'topic_name': q.topic_name,
                    'difficulty': q.difficulty
                })

            # Filter to groups with multiple questions
            duplicates = {key: questions for key, questions in topic_answer_groups.items() if len(questions) > 3}

            logger.info(f"Found {len(duplicates)} topic+answer groups with 4+ questions")
            return duplicates

    def analyze_all(self) -> Dict:
        """Run all duplicate analysis methods."""
        return {
            'exact_duplicates': self.find_exact_duplicates(),
            'similar_questions': self.find_similar_questions(),
            'topic_answer_groups': self.find_topic_answer_duplicates()
        }


def print_exact_duplicates(duplicates: Dict[str, List[Dict]]):
    """Print exact duplicate report."""
    if not duplicates:
        logger.info("✅ No exact duplicates found!")
        return

    logger.info("\n" + "="*80)
    logger.info("EXACT DUPLICATES REPORT")
    logger.info("="*80)

    total_duplicate_rows = sum(len(questions) - 1 for questions in duplicates.values())
    logger.info(f"Total: {len(duplicates)} unique questions with {total_duplicate_rows} duplicate rows\n")

    for idx, (text, questions) in enumerate(duplicates.items(), 1):
        logger.info(f"{idx}. Question Text: \"{text[:80]}...\"")
        logger.info(f"   Occurrences: {len(questions)}")
        for q in questions:
            logger.info(f"   - ID {q['id']}: Answer={q['correct_answer']}, Topic={q['topic_name']}, "
                       f"Seen={q['times_seen']}x, Correct={q['times_correct']}x")
        logger.info("")


def print_similar_questions(similar_pairs: List[Dict], limit: int = 20):
    """Print similar questions report."""
    if not similar_pairs:
        logger.info("✅ No similar questions found above threshold!")
        return

    logger.info("\n" + "="*80)
    logger.info(f"SIMILAR QUESTIONS REPORT (Top {min(limit, len(similar_pairs))})")
    logger.info("="*80)

    for idx, pair in enumerate(similar_pairs[:limit], 1):
        logger.info(f"\n{idx}. Similarity: {pair['similarity']:.2%}")
        logger.info(f"   Q1 [ID {pair['question1']['id']}]: {pair['question1']['text'][:80]}...")
        logger.info(f"      Answer: {pair['question1']['answer']}, Topic: {pair['question1']['topic']}")
        logger.info(f"   Q2 [ID {pair['question2']['id']}]: {pair['question2']['text'][:80]}...")
        logger.info(f"      Answer: {pair['question2']['answer']}, Topic: {pair['question2']['topic']}")


def print_topic_answer_groups(groups: Dict[str, List[Dict]], limit: int = 10):
    """Print topic+answer grouping report."""
    if not groups:
        logger.info("✅ No suspicious topic+answer groupings found!")
        return

    logger.info("\n" + "="*80)
    logger.info(f"TOPIC + ANSWER GROUPING REPORT (Groups with 4+ questions)")
    logger.info("="*80)

    # Sort by group size (largest first)
    sorted_groups = sorted(groups.items(), key=lambda x: len(x[1]), reverse=True)

    for idx, (key, questions) in enumerate(sorted_groups[:limit], 1):
        topic, answer = key.split('||')
        logger.info(f"\n{idx}. Topic: '{topic}' | Answer: '{answer}' | Count: {len(questions)}")
        for q in questions[:5]:  # Show first 5
            logger.info(f"   - ID {q['id']}: {q['question_text'][:60]}...")
        if len(questions) > 5:
            logger.info(f"   ... and {len(questions) - 5} more")


def export_results(results: Dict, output_file: str):
    """Export analysis results to JSON file."""
    logger.info(f"\nExporting results to: {output_file}")

    # Convert for JSON serialization
    export_data = {
        'exact_duplicates': {
            'count': len(results['exact_duplicates']),
            'groups': [
                {
                    'text': text,
                    'occurrences': questions
                }
                for text, questions in results['exact_duplicates'].items()
            ]
        },
        'similar_questions': {
            'count': len(results['similar_questions']),
            'pairs': results['similar_questions']
        },
        'topic_answer_groups': {
            'count': len(results['topic_answer_groups']),
            'groups': [
                {
                    'topic': key.split('||')[0],
                    'answer': key.split('||')[1],
                    'questions': questions
                }
                for key, questions in results['topic_answer_groups'].items()
            ]
        }
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)

    logger.info(f"✅ Export complete")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze questions for potential duplicates"
    )
    parser.add_argument('--threshold', type=float, default=0.85,
                       help='Similarity threshold for matching (0.0 to 1.0, default: 0.85)')
    parser.add_argument('--fuzzy', action='store_true',
                       help='Use fuzzy string matching (slower but more accurate)')
    parser.add_argument('--export', type=str,
                       help='Export results to JSON file')
    parser.add_argument('--limit', type=int, default=20,
                       help='Limit number of results to display (default: 20)')
    parser.add_argument('--exact-only', action='store_true',
                       help='Only check for exact duplicates (faster)')

    args = parser.parse_args()

    logger.info("="*80)
    logger.info("DUPLICATE QUESTION ANALYZER")
    logger.info("="*80)
    logger.info(f"Threshold: {args.threshold}")
    logger.info(f"Fuzzy matching: {'Enabled' if args.fuzzy else 'Disabled'}")
    logger.info(f"Database: {Config.DATABASE_PATH}")
    logger.info("="*80)

    analyzer = DuplicateAnalyzer(threshold=args.threshold, use_fuzzy=args.fuzzy)

    if args.exact_only:
        # Quick check for exact duplicates only
        exact_duplicates = analyzer.find_exact_duplicates()
        print_exact_duplicates(exact_duplicates)
    else:
        # Full analysis
        results = analyzer.analyze_all()

        print_exact_duplicates(results['exact_duplicates'])
        print_similar_questions(results['similar_questions'], limit=args.limit)
        print_topic_answer_groups(results['topic_answer_groups'], limit=args.limit)

        # Export if requested
        if args.export:
            export_results(results, args.export)

    logger.info("\n" + "="*80)
    logger.info("ANALYSIS COMPLETE")
    logger.info("="*80)


if __name__ == '__main__':
    main()

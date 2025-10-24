#!/usr/bin/env python3
"""
Analyze question coverage against the original 111-page study guide.

This script compares the current database questions against the topics
extracted from the original study guide to ensure complete coverage.
"""

import json
import logging
from collections import defaultdict
from typing import Dict, List, Set

from config import Config
from database import get_database
from database_models import Question

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


def load_original_study_guide_analysis(filepath: str) -> Dict:
    """Load the original study guide analysis JSON."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_database_topics() -> Dict[str, List[Dict]]:
    """Get all topics from current database questions."""
    db = get_database(Config.DATABASE_PATH)

    with db.session() as session:
        all_questions = session.query(Question).all()

        topics = defaultdict(list)
        for q in all_questions:
            topic_key = q.topic_name or "Unknown Topic"
            topics[topic_key].append({
                'id': q.id,
                'question_text': q.question_text[:100],  # Preview
                'difficulty': q.difficulty,
                'document_id': q.document_id,
                'pages': q.pages,
                'times_seen': q.times_seen
            })

    return dict(topics)


def normalize_topic_name(topic: str) -> str:
    """Normalize topic names for comparison."""
    # Remove special characters, lowercase, remove extra spaces
    normalized = topic.lower().strip()
    normalized = normalized.replace('á', 'a').replace('é', 'e').replace('í', 'i')
    normalized = normalized.replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')
    normalized = ' '.join(normalized.split())
    return normalized


def compare_coverage(original_analysis: Dict, db_topics: Dict[str, List[Dict]]) -> Dict:
    """Compare original study guide topics with database question topics."""

    # Extract topics from original guide
    original_topics = []
    for topic_data in original_analysis.get('topics', []):
        original_topics.append({
            'name': topic_data['main_topic'],
            'pages': topic_data.get('pages', ''),
            'difficulty': topic_data.get('difficulty_level', ''),
            'exam_focus': topic_data.get('exam_critical_points', []),
            'subtopics': topic_data.get('subtopics', [])
        })

    # Normalize database topics
    db_topics_normalized = {}
    for topic, questions in db_topics.items():
        normalized = normalize_topic_name(topic)
        db_topics_normalized[normalized] = {
            'original_name': topic,
            'questions': questions,
            'count': len(questions)
        }

    # Find matches and missing topics
    coverage_report = {
        'matched_topics': [],
        'unmatched_topics': [],
        'extra_db_topics': [],
        'statistics': {
            'original_topics_count': len(original_topics),
            'db_topics_count': len(db_topics),
            'matched_count': 0,
            'unmatched_count': 0
        }
    }

    # Match original topics with database
    matched_normalized = set()
    for orig_topic in original_topics:
        orig_normalized = normalize_topic_name(orig_topic['name'])

        # Try exact match
        if orig_normalized in db_topics_normalized:
            coverage_report['matched_topics'].append({
                'original_topic': orig_topic['name'],
                'db_topic': db_topics_normalized[orig_normalized]['original_name'],
                'pages': orig_topic['pages'],
                'question_count': db_topics_normalized[orig_normalized]['count'],
                'questions': db_topics_normalized[orig_normalized]['questions'][:5]  # First 5
            })
            matched_normalized.add(orig_normalized)
            coverage_report['statistics']['matched_count'] += 1
        else:
            # Try partial match
            found_partial = False
            for db_norm, db_data in db_topics_normalized.items():
                if orig_normalized in db_norm or db_norm in orig_normalized:
                    coverage_report['matched_topics'].append({
                        'original_topic': orig_topic['name'],
                        'db_topic': db_data['original_name'],
                        'pages': orig_topic['pages'],
                        'question_count': db_data['count'],
                        'match_type': 'partial',
                        'questions': db_data['questions'][:5]
                    })
                    matched_normalized.add(db_norm)
                    coverage_report['statistics']['matched_count'] += 1
                    found_partial = True
                    break

            if not found_partial:
                coverage_report['unmatched_topics'].append({
                    'original_topic': orig_topic['name'],
                    'pages': orig_topic['pages'],
                    'subtopics': orig_topic['subtopics']
                })
                coverage_report['statistics']['unmatched_count'] += 1

    # Find extra topics in database not in original
    for db_norm, db_data in db_topics_normalized.items():
        if db_norm not in matched_normalized:
            coverage_report['extra_db_topics'].append({
                'db_topic': db_data['original_name'],
                'question_count': db_data['count'],
                'questions': db_data['questions'][:3]
            })

    return coverage_report


def print_coverage_report(report: Dict):
    """Print formatted coverage report."""
    logger.info("="*80)
    logger.info("QUESTION COVERAGE ANALYSIS")
    logger.info("="*80)
    logger.info("")

    stats = report['statistics']
    logger.info(f"Original Study Guide Topics: {stats['original_topics_count']}")
    logger.info(f"Database Topics: {stats['db_topics_count']}")
    logger.info(f"Matched Topics: {stats['matched_count']}")
    logger.info(f"Unmatched Topics: {stats['unmatched_count']}")
    logger.info("")

    # Matched topics
    if report['matched_topics']:
        logger.info("="*80)
        logger.info("✅ MATCHED TOPICS (Original guide has database questions)")
        logger.info("="*80)
        for i, match in enumerate(report['matched_topics'], 1):
            match_type = match.get('match_type', 'exact')
            logger.info(f"\n{i}. Original: {match['original_topic']}")
            logger.info(f"   Database: {match['db_topic']} ({match_type} match)")
            logger.info(f"   Pages: {match['pages']}")
            logger.info(f"   Questions: {match['question_count']}")
            if match.get('questions'):
                logger.info(f"   Sample: {match['questions'][0]['question_text']}...")

    # Unmatched topics
    if report['unmatched_topics']:
        logger.info("\n" + "="*80)
        logger.info("⚠️  UNMATCHED TOPICS (Missing questions in database?)")
        logger.info("="*80)
        for i, topic in enumerate(report['unmatched_topics'], 1):
            logger.info(f"\n{i}. {topic['original_topic']}")
            logger.info(f"   Pages: {topic['pages']}")
            if topic['subtopics']:
                logger.info(f"   Subtopics: {', '.join(topic['subtopics'][:3])}")

    # Extra topics
    if report['extra_db_topics']:
        logger.info("\n" + "="*80)
        logger.info("📝 EXTRA TOPICS (In database but not in original guide)")
        logger.info("="*80)
        logger.info("These may be from the additional PDFs imported:")
        for i, topic in enumerate(report['extra_db_topics'], 1):
            logger.info(f"\n{i}. {topic['db_topic']}")
            logger.info(f"   Questions: {topic['question_count']}")
            if topic.get('questions'):
                logger.info(f"   Sample: {topic['questions'][0]['question_text'][:80]}...")

    logger.info("\n" + "="*80)
    logger.info("COVERAGE SUMMARY")
    logger.info("="*80)

    coverage_pct = (stats['matched_count'] / stats['original_topics_count'] * 100) if stats['original_topics_count'] > 0 else 0
    logger.info(f"Coverage: {coverage_pct:.1f}% of original topics have questions")

    if stats['unmatched_count'] == 0:
        logger.info("✅ All original study guide topics are covered!")
    else:
        logger.info(f"⚠️  {stats['unmatched_count']} original topics may need review")

    logger.info("")


def main():
    """Main execution."""
    original_guide_path = "/Users/luiscotto/Code/pharma-study-assistant/outputs/20251016_113156/20251016_113156_analysis.json"

    logger.info("Loading original study guide analysis...")
    original_analysis = load_original_study_guide_analysis(original_guide_path)

    logger.info("Loading database question topics...")
    db_topics = get_database_topics()

    logger.info("Comparing coverage...")
    coverage_report = compare_coverage(original_analysis, db_topics)

    print_coverage_report(coverage_report)

    # Export detailed report
    output_file = "question_coverage_report.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(coverage_report, f, indent=2, ensure_ascii=False)

    logger.info(f"✅ Detailed report exported to: {output_file}")


if __name__ == '__main__':
    main()

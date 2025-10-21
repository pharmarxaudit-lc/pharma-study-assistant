#!/usr/bin/env python3
"""
CLI script to generate questions from analyzed PDF content.

Usage:
    python generate_questions.py <file_id>              # Generate with defaults
    python generate_questions.py <file_id> --count 30   # Generate 30 per topic
    python generate_questions.py <file_id> --test       # Test with 1 topic only
"""
import argparse
import logging
import sys

from question_generator import QuestionGenerator


def setup_logging():
    """Configure logging for question generation."""
    # Create logs directory in project root
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(os.path.join(log_dir, 'question_generation.log'), mode='a', encoding='utf-8')
        ]
    )
    return logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='Generate exam questions from PDF analysis'
    )
    parser.add_argument(
        'file_id',
        help='File ID (timestamp) of the processed PDF'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=None,
        help='Number of questions per topic (default: 25)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test mode: generate for only the first topic'
    )

    args = parser.parse_args()

    # Setup logging
    logger = setup_logging()

    # Create generator
    generator = QuestionGenerator(logger)

    # Load analysis to check topic count
    try:
        analysis = generator.load_analysis(args.file_id)
        logger.info(f"\n📄 Document: {analysis.get('filename', 'Unknown')}")
        logger.info(f"📊 Topics found: {len(analysis['topics'])}")

        if args.test:
            logger.info(f"🧪 TEST MODE: Generating questions for FIRST topic only\n")
            # Temporarily modify topics list
            original_topics = analysis['topics']
            analysis['topics'] = [original_topics[0]]
    except Exception as e:
        logger.error(f"❌ Error loading analysis: {e}")
        return 1

    # Generate questions
    try:
        stats = generator.generate_all_questions(args.file_id, args.count)

        if stats.get('success'):
            logger.info(f"\n✅ SUCCESS! Generated {stats['total_questions_generated']} questions")
            return 0
        else:
            logger.error(f"\n❌ FAILED: {stats.get('error', 'Unknown error')}")
            return 1

    except KeyboardInterrupt:
        logger.warning(f"\n\n⚠️  Generation interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"\n❌ Error during generation: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())

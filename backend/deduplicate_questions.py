#!/usr/bin/env python3
"""
Script to identify and remove duplicate questions from the database.

This script:
1. Identifies questions with duplicate question_text
2. For each duplicate set, keeps the first occurrence (lowest ID)
3. Removes the duplicate entries
4. Updates any user_attempts that reference deleted questions
5. Creates a backup before making changes
"""

import json
import logging
import os
import shutil
import sys
import time
from collections import defaultdict

from config import Config
from database import get_database
from database_models import Question, UserAttempt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


def find_duplicates(session):
    """Find all duplicate questions grouped by question_text."""
    logger.info("Searching for duplicate questions...")

    all_questions = session.query(Question).order_by(Question.id).all()

    # Group questions by question_text
    question_groups = defaultdict(list)
    for q in all_questions:
        question_groups[q.question_text].append(q)

    # Filter to only duplicates
    duplicates = {text: questions for text, questions in question_groups.items() if len(questions) > 1}

    logger.info(f"Found {len(duplicates)} unique questions with duplicates")
    logger.info(f"Total duplicate rows: {sum(len(qs) - 1 for qs in duplicates.values())}")

    return duplicates


def analyze_duplicates(duplicates):
    """Analyze duplicates to understand differences."""
    logger.info("\n" + "="*80)
    logger.info("DUPLICATE ANALYSIS")
    logger.info("="*80)

    for idx, (question_text, questions) in enumerate(duplicates.items(), 1):
        logger.info(f"\n{idx}. Question: {question_text[:80]}...")
        logger.info(f"   Found {len(questions)} occurrences:")

        for q in questions:
            options = json.loads(q.options_json) if q.options_json else {}
            logger.info(f"   - ID {q.id}: {len(options)} options, "
                       f"correct={q.correct_answer}, "
                       f"times_seen={q.times_seen}, "
                       f"topic={q.topic_name}")

            # Show first option as sample
            if options:
                first_key = list(options.keys())[0] if isinstance(options, dict) else None
                if first_key:
                    sample = options[first_key][:60] if isinstance(options[first_key], str) else str(options[first_key])[:60]
                    logger.info(f"      Sample option: {sample}...")


def create_backup(db_path):
    """Create a backup of the database."""
    backup_path = f"{db_path}.backup_{int(time.time())}"
    logger.info(f"Creating backup: {backup_path}")
    shutil.copy2(db_path, backup_path)
    logger.info(f"✅ Backup created successfully")
    return backup_path


def remove_duplicates(session, duplicates, dry_run=True):
    """Remove duplicate questions, keeping the first occurrence (lowest ID)."""

    ids_to_keep = []
    ids_to_delete = []

    for question_text, questions in duplicates.items():
        # Sort by ID and keep the first one
        questions_sorted = sorted(questions, key=lambda q: q.id)
        keep = questions_sorted[0]
        delete = questions_sorted[1:]

        ids_to_keep.append(keep.id)
        ids_to_delete.extend([q.id for q in delete])

        if not dry_run:
            logger.info(f"Keeping ID {keep.id}, deleting IDs: {[q.id for q in delete]}")

    logger.info(f"\n{'DRY RUN - ' if dry_run else ''}Summary:")
    logger.info(f"  Questions to keep: {len(ids_to_keep)}")
    logger.info(f"  Questions to delete: {len(ids_to_delete)}")

    if dry_run:
        logger.info("\nThis was a DRY RUN. No changes made.")
        logger.info("Run with --execute to apply changes.")
        return ids_to_keep, ids_to_delete

    # Check for user attempts that reference deleted questions
    attempts_to_update = session.query(UserAttempt).filter(
        UserAttempt.question_id.in_(ids_to_delete)
    ).all()

    if attempts_to_update:
        logger.warning(f"\n⚠️  Found {len(attempts_to_update)} user attempts referencing questions to be deleted")
        logger.warning("These attempts will be deleted as well.")

    # Delete user attempts first (foreign key constraint)
    if attempts_to_update:
        session.query(UserAttempt).filter(
            UserAttempt.question_id.in_(ids_to_delete)
        ).delete(synchronize_session=False)
        logger.info(f"✅ Deleted {len(attempts_to_update)} user attempts")

    # Delete duplicate questions
    deleted_count = session.query(Question).filter(
        Question.id.in_(ids_to_delete)
    ).delete(synchronize_session=False)

    session.commit()

    logger.info(f"✅ Deleted {deleted_count} duplicate questions")

    return ids_to_keep, ids_to_delete


def verify_database(session):
    """Verify database state after deduplication."""
    logger.info("\n" + "="*80)
    logger.info("DATABASE VERIFICATION")
    logger.info("="*80)

    total_questions = session.query(Question).count()

    # Check for remaining duplicates
    all_questions = session.query(Question).all()
    question_texts = [q.question_text for q in all_questions]
    unique_texts = set(question_texts)

    logger.info(f"Total questions: {total_questions}")
    logger.info(f"Unique question texts: {len(unique_texts)}")

    if len(question_texts) == len(unique_texts):
        logger.info("✅ No duplicates found - database is clean!")
    else:
        logger.warning(f"⚠️  Still {len(question_texts) - len(unique_texts)} duplicates remaining")

    # Check for orphaned user attempts
    orphaned = session.execute("""
        SELECT COUNT(*)
        FROM user_attempts ua
        LEFT JOIN questions q ON ua.question_id = q.id
        WHERE q.id IS NULL
    """).scalar()

    if orphaned > 0:
        logger.warning(f"⚠️  Found {orphaned} orphaned user attempts (referencing deleted questions)")
    else:
        logger.info("✅ No orphaned user attempts")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Deduplicate questions in the database")
    parser.add_argument('--execute', action='store_true',
                       help='Actually perform the deduplication (default is dry-run)')
    parser.add_argument('--no-backup', action='store_true',
                       help='Skip creating a backup (not recommended)')
    args = parser.parse_args()

    dry_run = not args.execute

    logger.info("="*80)
    logger.info("QUESTION DEDUPLICATION SCRIPT")
    logger.info("="*80)
    logger.info(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    logger.info(f"Database: {Config.DATABASE_PATH}")
    logger.info("="*80)

    # Initialize database
    db = get_database(Config.DATABASE_PATH)

    try:
        with db.session() as session:
            # Find duplicates
            duplicates = find_duplicates(session)

            if not duplicates:
                logger.info("\n✅ No duplicates found! Database is clean.")
                return 0

            # Analyze duplicates
            analyze_duplicates(duplicates)

            # Create backup before making changes
            if not dry_run and not args.no_backup:
                create_backup(Config.DATABASE_PATH)

            # Remove duplicates
            logger.info("\n" + "="*80)
            logger.info(f"{'DRY RUN - ' if dry_run else ''}REMOVING DUPLICATES")
            logger.info("="*80)

            ids_to_keep, ids_to_delete = remove_duplicates(session, duplicates, dry_run=dry_run)

            if not dry_run:
                # Verify
                verify_database(session)

                logger.info("\n" + "="*80)
                logger.info("✅ DEDUPLICATION COMPLETE")
                logger.info("="*80)

            return 0

    except Exception as e:
        logger.error(f"❌ Error during deduplication: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())

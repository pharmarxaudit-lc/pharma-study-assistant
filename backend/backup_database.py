#!/usr/bin/env python3
"""
Database backup utility for Pharma Study Assistant.

This script creates comprehensive backups of the database including:
1. Complete SQLite database file copy
2. JSON export of all questions
3. Markdown report with statistics
4. Optional: SQL dump for version control

Usage:
    python backup_database.py [--output-dir backups] [--description "Before cleanup"]
"""

import argparse
import json
import logging
import os
import shutil
import sqlite3
from datetime import datetime
from typing import Dict, List

from config import Config
from database import get_database
from database_models import Question, Document, StudySession, UserAttempt

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseBackup:
    """Create comprehensive database backups."""

    def __init__(self, output_dir: str = "backups"):
        self.output_dir = output_dir
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_dir = os.path.join(output_dir, f"backup_{self.timestamp}")
        self.db = get_database(Config.DATABASE_PATH)

    def create_backup_directory(self):
        """Create backup directory structure."""
        os.makedirs(self.backup_dir, exist_ok=True)
        logger.info(f"Created backup directory: {self.backup_dir}")

    def backup_database_file(self) -> str:
        """Create a copy of the SQLite database file."""
        logger.info("Backing up database file...")

        backup_file = os.path.join(self.backup_dir, f"pharma_exam_{self.timestamp}.db")
        shutil.copy2(Config.DATABASE_PATH, backup_file)

        # Verify backup
        if os.path.exists(backup_file):
            size_mb = os.path.getsize(backup_file) / (1024 * 1024)
            logger.info(f"✅ Database file backed up: {backup_file} ({size_mb:.2f} MB)")
            return backup_file
        else:
            logger.error("❌ Failed to create database backup")
            return None

    def export_questions_json(self) -> str:
        """Export all questions to JSON format."""
        logger.info("Exporting questions to JSON...")

        with self.db.session() as session:
            all_questions = session.query(Question).order_by(Question.id).all()

            questions_data = []
            for q in all_questions:
                questions_data.append({
                    'id': q.id,
                    'document_id': q.document_id,
                    'topic_id': q.topic_id,
                    'topic_name': q.topic_name,
                    'question_type': q.question_type,
                    'difficulty': q.difficulty,
                    'question_text': q.question_text,
                    'options': json.loads(q.options_json) if q.options_json else {},
                    'correct_answer': q.correct_answer,
                    'explanation': q.explanation,
                    'key_terms': json.loads(q.key_terms_json) if q.key_terms_json else [],
                    'regulatory_context': q.regulatory_context,
                    'pages': q.pages,
                    'times_seen': q.times_seen,
                    'times_correct': q.times_correct,
                    'created_at': q.created_at if isinstance(q.created_at, str) else (q.created_at.isoformat() if q.created_at else None)
                })

        json_file = os.path.join(self.backup_dir, f"questions_{self.timestamp}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(questions_data, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ Exported {len(questions_data)} questions to: {json_file}")
        return json_file

    def create_statistics_report(self) -> str:
        """Create a markdown report with database statistics."""
        logger.info("Generating statistics report...")

        with self.db.session() as session:
            # Counts
            total_questions = session.query(Question).count()
            total_documents = session.query(Document).count()
            total_sessions = session.query(StudySession).count()
            total_attempts = session.query(UserAttempt).count()

            # Questions by difficulty
            basic_count = session.query(Question).filter_by(difficulty='basic').count()
            intermediate_count = session.query(Question).filter_by(difficulty='intermediate').count()
            advanced_count = session.query(Question).filter_by(difficulty='advanced').count()

            # Questions by type
            single_count = session.query(Question).filter_by(question_type='single_answer').count()
            multiple_count = session.query(Question).filter_by(question_type='choose_all').count()

            # Topics
            from sqlalchemy import func
            topic_counts = session.query(
                Question.topic_name,
                func.count(Question.id)
            ).group_by(Question.topic_name).order_by(func.count(Question.id).desc()).all()

            # Most seen questions - convert to dicts within session
            most_seen_query = session.query(Question).filter(
                Question.times_seen > 0
            ).order_by(Question.times_seen.desc()).limit(10).all()

            most_seen = []
            for q in most_seen_query:
                most_seen.append({
                    'id': q.id,
                    'question_text': q.question_text,
                    'times_seen': q.times_seen,
                    'times_correct': q.times_correct
                })

        # Create markdown report
        report = f"""# Database Backup Report

**Backup Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Backup ID:** {self.timestamp}
**Database:** {Config.DATABASE_PATH}

---

## Summary Statistics

- **Total Questions:** {total_questions}
- **Total Documents:** {total_documents}
- **Total Study Sessions:** {total_sessions}
- **Total User Attempts:** {total_attempts}

---

## Questions by Difficulty

| Difficulty | Count | Percentage |
|------------|-------|------------|
| Basic | {basic_count} | {(basic_count/total_questions*100):.1f}% |
| Intermediate | {intermediate_count} | {(intermediate_count/total_questions*100):.1f}% |
| Advanced | {advanced_count} | {(advanced_count/total_questions*100):.1f}% |
| **TOTAL** | **{total_questions}** | **100%** |

---

## Questions by Type

| Type | Count | Percentage |
|------|-------|------------|
| Single Answer | {single_count} | {(single_count/total_questions*100):.1f}% |
| Choose All (Multiple) | {multiple_count} | {(multiple_count/total_questions*100):.1f}% |
| **TOTAL** | **{total_questions}** | **100%** |

---

## Questions by Topic

| Topic | Count |
|-------|-------|
"""

        for topic, count in topic_counts[:20]:  # Top 20 topics
            report += f"| {topic or '(No Topic)'} | {count} |\n"

        if len(topic_counts) > 20:
            remaining = sum(count for _, count in topic_counts[20:])
            report += f"| *...and {len(topic_counts) - 20} more topics* | {remaining} |\n"

        report += f"\n---\n\n## Most Used Questions\n\n"

        if most_seen:
            report += "| ID | Question | Times Seen | Times Correct | Success Rate |\n"
            report += "|----|-----------|-----------:|---------------:|-------------:|\n"
            for q in most_seen:
                success_rate = (q['times_correct'] / q['times_seen'] * 100) if q['times_seen'] > 0 else 0
                question_preview = q['question_text'][:60] + "..." if len(q['question_text']) > 60 else q['question_text']
                report += f"| {q['id']} | {question_preview} | {q['times_seen']} | {q['times_correct']} | {success_rate:.1f}% |\n"
        else:
            report += "*No questions have been used in study sessions yet.*\n"

        report += f"\n---\n\n## Backup Files\n\n"
        report += f"- Database: `pharma_exam_{self.timestamp}.db`\n"
        report += f"- Questions JSON: `questions_{self.timestamp}.json`\n"
        report += f"- SQL Dump: `dump_{self.timestamp}.sql` (if created)\n"
        report += f"- This Report: `report_{self.timestamp}.md`\n"

        report += f"\n---\n\n## Restoration Instructions\n\n"
        report += f"### To restore this backup:\n\n"
        report += f"```bash\n"
        report += f"# Option 1: Restore database file\n"
        report += f"cp {self.backup_dir}/pharma_exam_{self.timestamp}.db {Config.DATABASE_PATH}\n\n"
        report += f"# Option 2: Restore from SQL dump\n"
        report += f"sqlite3 {Config.DATABASE_PATH} < {self.backup_dir}/dump_{self.timestamp}.sql\n"
        report += f"```\n"

        report_file = os.path.join(self.backup_dir, f"report_{self.timestamp}.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        logger.info(f"✅ Statistics report created: {report_file}")
        return report_file

    def create_sql_dump(self) -> str:
        """Create SQL dump for version control."""
        logger.info("Creating SQL dump...")

        dump_file = os.path.join(self.backup_dir, f"dump_{self.timestamp}.sql")

        try:
            # Connect to database
            conn = sqlite3.connect(Config.DATABASE_PATH)

            # Create dump
            with open(dump_file, 'w', encoding='utf-8') as f:
                for line in conn.iterdump():
                    f.write(f"{line}\n")

            conn.close()

            size_mb = os.path.getsize(dump_file) / (1024 * 1024)
            logger.info(f"✅ SQL dump created: {dump_file} ({size_mb:.2f} MB)")
            return dump_file

        except Exception as e:
            logger.error(f"❌ Failed to create SQL dump: {e}")
            return None

    def create_backup_info(self, description: str = ""):
        """Create backup metadata file."""
        info = {
            'timestamp': self.timestamp,
            'date': datetime.now().isoformat(),
            'description': description,
            'database_path': Config.DATABASE_PATH,
            'backup_directory': self.backup_dir,
            'files': {
                'database': f"pharma_exam_{self.timestamp}.db",
                'questions_json': f"questions_{self.timestamp}.json",
                'sql_dump': f"dump_{self.timestamp}.sql",
                'report': f"report_{self.timestamp}.md"
            }
        }

        info_file = os.path.join(self.backup_dir, 'backup_info.json')
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2)

        logger.info(f"✅ Backup info saved: {info_file}")

    def run_full_backup(self, description: str = "", include_sql: bool = True) -> str:
        """Run complete backup process."""
        logger.info("="*80)
        logger.info("STARTING FULL DATABASE BACKUP")
        logger.info("="*80)

        self.create_backup_directory()
        self.backup_database_file()
        self.export_questions_json()
        self.create_statistics_report()

        if include_sql:
            self.create_sql_dump()

        self.create_backup_info(description)

        logger.info("\n" + "="*80)
        logger.info("BACKUP COMPLETE")
        logger.info("="*80)
        logger.info(f"Backup location: {self.backup_dir}")

        return self.backup_dir


def list_backups(backup_dir: str = "backups"):
    """List all available backups."""
    if not os.path.exists(backup_dir):
        logger.info("No backups directory found")
        return

    backups = []
    for item in os.listdir(backup_dir):
        item_path = os.path.join(backup_dir, item)
        if os.path.isdir(item_path) and item.startswith('backup_'):
            info_file = os.path.join(item_path, 'backup_info.json')
            if os.path.exists(info_file):
                with open(info_file, 'r') as f:
                    info = json.load(f)
                    backups.append(info)

    if not backups:
        logger.info("No backups found")
        return

    logger.info("\n" + "="*80)
    logger.info("AVAILABLE BACKUPS")
    logger.info("="*80)

    backups.sort(key=lambda x: x['timestamp'], reverse=True)

    for backup in backups:
        logger.info(f"\nBackup: {backup['timestamp']}")
        logger.info(f"Date: {backup['date']}")
        logger.info(f"Description: {backup.get('description', 'N/A')}")
        logger.info(f"Location: {backup['backup_directory']}")


def restore_backup(backup_dir: str, target_db: str = None):
    """Restore database from backup."""
    if not os.path.exists(backup_dir):
        logger.error(f"Backup directory not found: {backup_dir}")
        return

    info_file = os.path.join(backup_dir, 'backup_info.json')
    if not os.path.exists(info_file):
        logger.error("No backup_info.json found in backup directory")
        return

    with open(info_file, 'r') as f:
        info = json.load(f)

    db_file = os.path.join(backup_dir, info['files']['database'])
    if not os.path.exists(db_file):
        logger.error(f"Database file not found in backup: {db_file}")
        return

    target = target_db or Config.DATABASE_PATH

    # Create backup of current database first
    if os.path.exists(target):
        current_backup = f"{target}.before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(target, current_backup)
        logger.info(f"Current database backed up to: {current_backup}")

    # Restore
    shutil.copy2(db_file, target)
    logger.info(f"✅ Database restored from: {backup_dir}")
    logger.info(f"✅ Restored to: {target}")


def main():
    parser = argparse.ArgumentParser(
        description="Backup or restore Pharma Study Assistant database"
    )
    parser.add_argument('--output-dir', default='backups',
                       help='Directory to store backups (default: backups)')
    parser.add_argument('--description', default='',
                       help='Description of this backup')
    parser.add_argument('--no-sql', action='store_true',
                       help='Skip SQL dump creation (faster)')
    parser.add_argument('--list', action='store_true',
                       help='List all available backups')
    parser.add_argument('--restore', type=str,
                       help='Restore from backup directory')

    args = parser.parse_args()

    if args.list:
        list_backups(args.output_dir)
        return

    if args.restore:
        restore_backup(args.restore)
        return

    # Create backup
    backup = DatabaseBackup(output_dir=args.output_dir)
    backup.run_full_backup(
        description=args.description,
        include_sql=not args.no_sql
    )


if __name__ == '__main__':
    main()

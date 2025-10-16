#!/usr/bin/env python3
"""
Initialize the pharmacy exam prep database.

Usage:
    python init_database.py              # Create tables if DB doesn't exist
    python init_database.py --reset      # Drop and recreate all tables (destroys data!)
    python init_database.py --test       # Create DB and add sample data
"""
import argparse
from datetime import date, datetime

from database import init_database
from database_models import Document, Question, SpacedRepetition, StudySession, UserAttempt


def add_sample_data(db):
    """Add sample data for testing."""
    print("\n📝 Adding sample data...")

    with db.session() as session:
        # Sample document
        doc = Document(
            file_id='20251016_113156',
            filename='repaso_ley_2025.pdf',
            total_topics=13,
            total_pages=111,
            analysis_path='outputs/20251016_113156/20251016_113156_analysis.json',
            formatted_path='outputs/20251016_113156/20251016_113156_formatted.md'
        )
        session.add(doc)
        session.flush()  # Get document ID

        # Sample question
        question = Question(
            document_id=doc.id,
            topic_id=1,
            topic_name='Requisitos para ejercer como Farmacéutico',
            question_type='single_answer',
            difficulty='intermediate',
            question_text='¿Cuántas horas de internado se requieren para obtener la licencia de farmacéutico en Puerto Rico?',
            options_json='["A. 1000 horas", "B. 1200 horas", "C. 1500 horas", "D. 2000 horas"]',
            correct_answer='C',
            explanation='Según la Ley 247 de 2004, se requieren un mínimo de 1500 horas de internado bajo supervisión de un farmacéutico preceptor autorizado por la Junta de Farmacia.',
            key_terms_json='[{"term": "Internado", "definition": "1500 horas bajo supervisión de farmacéutico preceptor"}]',
            regulatory_context='Ley 247 de 2004',
            pages='3-8',
            times_seen=5,
            times_correct=4
        )
        session.add(question)
        session.flush()  # Get question ID

        # Sample study session
        study_session = StudySession(
            document_id=doc.id,
            session_type='practice',
            topic_filter=None,
            difficulty_filter=None,
            total_questions=25,
            time_limit_minutes=60,
            start_time=datetime(2025, 10, 16, 14, 0, 0).isoformat(),
            end_time=datetime(2025, 10, 16, 14, 45, 0).isoformat(),
            correct_answers=20,
            incorrect_answers=5,
            score_percentage=80.0,
            status='completed'
        )
        session.add(study_session)
        session.flush()

        # Sample user attempt
        attempt = UserAttempt(
            question_id=question.id,
            session_id=study_session.id,
            selected_answer='C',
            is_correct=True,
            time_spent_seconds=15,
            attempt_date=datetime.now().isoformat()
        )
        session.add(attempt)

        # Sample spaced repetition entry
        sr = SpacedRepetition(
            question_id=question.id,
            ease_factor=2.6,
            interval_days=4,
            repetitions=2,
            next_review_date=date(2025, 10, 20),
            last_reviewed=datetime.now().isoformat(),
            total_reviews=3,
            correct_reviews=2
        )
        session.add(sr)

        session.commit()

        # Store values before session closes
        doc_filename = doc.filename
        question_text = question.question_text
        session_type = study_session.session_type
        session_score = study_session.score_percentage

    print("✅ Sample data added successfully")
    print(f"   - 1 Document: {doc_filename}")
    print(f"   - 1 Question: {question_text[:50]}...")
    print(f"   - 1 Study Session: {session_type} ({session_score}%)")
    print(f"   - 1 User Attempt")
    print(f"   - 1 Spaced Repetition entry")


def main():
    parser = argparse.ArgumentParser(description='Initialize pharmacy exam prep database')
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Drop and recreate all tables (WARNING: destroys all data!)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Add sample test data after initialization'
    )
    parser.add_argument(
        '--db',
        type=str,
        default='pharma_exam.db',
        help='Database file path (default: pharma_exam.db)'
    )

    args = parser.parse_args()

    print("="*60)
    print("Pharmacy Exam Prep - Database Initialization")
    print("="*60)

    if args.reset:
        response = input("\n⚠️  WARNING: This will DELETE ALL DATA! Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Initialization cancelled")
            return

    # Initialize database
    db = init_database(db_path=args.db, reset=args.reset)

    # Add sample data if requested
    if args.test:
        add_sample_data(db)

    print("\n✅ Database initialization complete!")
    print(f"📁 Database location: {args.db}")
    print("\n" + "="*60)


if __name__ == '__main__':
    main()

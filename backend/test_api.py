#!/usr/bin/env python3
"""
Test script for API endpoints.
Tests the new question and session endpoints.
"""
import json
import sys
from database import get_database
from database_models import Document, Question, StudySession
from config import Config

def test_database_connection():
    """Test database connectivity and content."""
    print("=" * 60)
    print("Testing Database Connection")
    print("=" * 60)

    db = get_database(Config.DATABASE_PATH)

    with db.session() as session:
        # Check documents
        doc_count = session.query(Document).count()
        print(f"✓ Documents in database: {doc_count}")

        if doc_count > 0:
            doc = session.query(Document).first()
            print(f"  - File ID: {doc.file_id}")
            print(f"  - Filename: {doc.filename}")
            print(f"  - Total topics: {doc.total_topics}")

        # Check questions
        q_count = session.query(Question).count()
        print(f"✓ Questions in database: {q_count}")

        if q_count > 0:
            # Get stats by difficulty
            from sqlalchemy import func
            by_diff = session.query(
                Question.difficulty,
                func.count(Question.id).label('count')
            ).group_by(Question.difficulty).all()

            print("  By difficulty:")
            for diff, count in by_diff:
                print(f"    - {diff}: {count}")

            # Get stats by type
            by_type = session.query(
                Question.question_type,
                func.count(Question.id).label('count')
            ).group_by(Question.question_type).all()

            print("  By type:")
            for qtype, count in by_type:
                print(f"    - {qtype}: {count}")

            # Get first question
            q = session.query(Question).first()
            print(f"\n  Sample question:")
            print(f"    - Topic: {q.topic_name}")
            print(f"    - Type: {q.question_type}")
            print(f"    - Difficulty: {q.difficulty}")
            print(f"    - Text: {q.question_text[:80]}...")

        # Check sessions
        s_count = session.query(StudySession).count()
        print(f"✓ Study sessions in database: {s_count}")

    print()
    return doc_count > 0 and q_count > 0

def test_question_queries():
    """Test question query logic (simulating API endpoints)."""
    print("=" * 60)
    print("Testing Question Queries")
    print("=" * 60)

    db = get_database(Config.DATABASE_PATH)

    with db.session() as session:
        # Get document
        doc = session.query(Document).filter_by(file_id='20251016_113156').first()
        if not doc:
            print("✗ Document not found")
            return False

        print(f"✓ Found document: {doc.filename}")

        # Test query with filtering
        query = session.query(Question).filter_by(document_id=doc.id)

        # Filter by difficulty
        basic_q = query.filter_by(difficulty='basic').count()
        inter_q = query.filter_by(difficulty='intermediate').count()
        adv_q = query.filter_by(difficulty='advanced').count()

        print(f"✓ Questions by difficulty:")
        print(f"  - Basic: {basic_q}")
        print(f"  - Intermediate: {inter_q}")
        print(f"  - Advanced: {adv_q}")

        # Test pagination
        page1 = query.limit(10).all()
        print(f"✓ Pagination works: fetched {len(page1)} questions")

        # Test single question retrieval
        q = session.query(Question).first()
        print(f"✓ Single question retrieval:")
        print(f"  - ID: {q.id}")
        print(f"  - Options count: {len(json.loads(q.options_json))}")
        print(f"  - Has explanation: {len(q.explanation) > 0}")

    print()
    return True

def test_session_logic():
    """Test session creation logic (simulating API endpoints)."""
    print("=" * 60)
    print("Testing Session Logic")
    print("=" * 60)

    db = get_database(Config.DATABASE_PATH)

    with db.session() as session:
        doc = session.query(Document).filter_by(file_id='20251016_113156').first()

        # Simulate session start
        from sqlalchemy import func
        from datetime import datetime

        # Random question selection
        questions = session.query(Question).filter_by(
            document_id=doc.id
        ).order_by(func.random()).limit(5).all()

        if not questions:
            print("✗ No questions found")
            return False

        print(f"✓ Selected {len(questions)} random questions for session")

        # Create test session
        test_session = StudySession(
            document_id=doc.id,
            session_type='study',
            start_time=datetime.now(),
            total_questions=len(questions),
            correct_answers=0,
            score_percentage=0.0
        )
        session.add(test_session)
        session.flush()

        print(f"✓ Created test session with ID: {test_session.id}")

        # Simulate answering questions
        from database_models import UserAttempt

        correct_count = 0
        for i, q in enumerate(questions):
            # Simulate correct answer for half
            is_correct = (i % 2 == 0)
            if is_correct:
                correct_count += 1

            attempt = UserAttempt(
                question_id=q.id,
                session_id=test_session.id,
                selected_answer=q.correct_answer if is_correct else 'WRONG',
                is_correct=is_correct,
                attempt_date=datetime.now(),
                time_spent_seconds=30
            )
            session.add(attempt)

            # Update question stats
            q.times_seen += 1
            if is_correct:
                q.times_correct += 1

        # Update session
        test_session.correct_answers = correct_count
        test_session.end_time = datetime.now()
        test_session.score_percentage = (correct_count / len(questions) * 100)

        session.commit()

        print(f"✓ Recorded {len(questions)} attempts")
        print(f"  - Correct: {correct_count}")
        print(f"  - Score: {test_session.score_percentage:.1f}%")

        # Verify retrieval
        saved_session = session.query(StudySession).filter_by(id=test_session.id).first()
        attempts = session.query(UserAttempt).filter_by(session_id=test_session.id).all()

        print(f"✓ Session retrieval works:")
        print(f"  - Session ID: {saved_session.id}")
        print(f"  - Attempts: {len(attempts)}")

    print()
    return True

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("API ENDPOINT TESTING")
    print("=" * 60 + "\n")

    success = True

    # Run tests
    success = test_database_connection() and success
    success = test_question_queries() and success
    success = test_session_logic() and success

    # Summary
    print("=" * 60)
    if success:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 60 + "\n")

    sys.exit(0 if success else 1)

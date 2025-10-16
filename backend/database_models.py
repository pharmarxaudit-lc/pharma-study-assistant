"""
SQLAlchemy database models for pharmacy exam prep application.

Tables:
- documents: Processed PDF documents
- questions: Generated exam questions
- user_attempts: Answer attempts for analytics
- study_sessions: Exam/study sessions
- spaced_repetition: SM-2 algorithm data
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Document(Base):
    """Processed PDF documents."""
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_id = Column(String(50), unique=True, nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    upload_date = Column(String(50), default=lambda: datetime.now().isoformat())
    total_topics = Column(Integer, nullable=False)
    total_pages = Column(Integer, nullable=False)
    analysis_path = Column(Text, nullable=False)
    formatted_path = Column(Text)
    created_at = Column(String(50), default=lambda: datetime.now().isoformat())

    # Relationships
    questions = relationship('Question', back_populates='document', cascade='all, delete-orphan')
    study_sessions = relationship('StudySession', back_populates='document', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, file_id='{self.file_id}', filename='{self.filename}')>"


class Question(Base):
    """Generated multiple-choice questions."""
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True)
    topic_id = Column(Integer, nullable=False, index=True)
    topic_name = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False, index=True)  # "single_answer" or "choose_all"
    difficulty = Column(String(50), nullable=False, index=True)  # "basic", "intermediate", "advanced"

    # Question content
    question_text = Column(Text, nullable=False)
    options_json = Column(Text, nullable=False)  # JSON array of options
    correct_answer = Column(String(50), nullable=False)  # "A" or "A,C,D"
    explanation = Column(Text, nullable=False)

    # Metadata
    key_terms_json = Column(Text)  # JSON array of key terms
    regulatory_context = Column(Text)
    pages = Column(String(50))

    # Tracking
    times_seen = Column(Integer, default=0)
    times_correct = Column(Integer, default=0)
    created_at = Column(String(50), default=lambda: datetime.now().isoformat())

    # Relationships
    document = relationship('Document', back_populates='questions')
    user_attempts = relationship('UserAttempt', back_populates='question', cascade='all, delete-orphan')
    spaced_repetition = relationship('SpacedRepetition', back_populates='question', uselist=False, cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f"<Question(id={self.id}, topic='{self.topic_name}', type='{self.question_type}')>"

    @property
    def accuracy_rate(self) -> float:
        """Calculate accuracy rate for this question."""
        if self.times_seen == 0:
            return 0.0
        return (self.times_correct / self.times_seen) * 100


class UserAttempt(Base):
    """Individual answer attempts."""
    __tablename__ = 'user_attempts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey('questions.id', ondelete='CASCADE'), nullable=False, index=True)
    session_id = Column(Integer, ForeignKey('study_sessions.id', ondelete='SET NULL'), index=True)

    # Answer details
    selected_answer = Column(String(50), nullable=False)
    is_correct = Column(Boolean, nullable=False, index=True)
    time_spent_seconds = Column(Integer)

    # Timestamp
    attempt_date = Column(String(50), default=lambda: datetime.now().isoformat(), index=True)

    # Relationships
    question = relationship('Question', back_populates='user_attempts')
    study_session = relationship('StudySession', back_populates='user_attempts')

    def __repr__(self) -> str:
        return f"<UserAttempt(id={self.id}, question_id={self.question_id}, correct={self.is_correct})>"


class StudySession(Base):
    """Exam and study sessions."""
    __tablename__ = 'study_sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True)

    # Session configuration
    session_type = Column(String(50), nullable=False, index=True)  # "study", "practice", "mock"
    topic_filter = Column(Text)  # NULL = all topics
    difficulty_filter = Column(String(50))  # NULL = all
    total_questions = Column(Integer, nullable=False)
    time_limit_minutes = Column(Integer)
    pass_threshold = Column(Integer, default=70)  # Pass threshold percentage (default 70%)

    # Session results
    start_time = Column(String(50), nullable=False, index=True)
    end_time = Column(String(50))
    correct_answers = Column(Integer, default=0)
    incorrect_answers = Column(Integer, default=0)
    score_percentage = Column(Float)

    # Status
    status = Column(String(50), default='in_progress', index=True)  # "in_progress", "completed", "abandoned"

    # Relationships
    document = relationship('Document', back_populates='study_sessions')
    user_attempts = relationship('UserAttempt', back_populates='study_session')

    def __repr__(self) -> str:
        return f"<StudySession(id={self.id}, type='{self.session_type}', score={self.score_percentage})>"

    def calculate_score(self) -> None:
        """Calculate and update score percentage."""
        if self.total_questions > 0:
            self.score_percentage = (self.correct_answers / self.total_questions) * 100

    @property
    def duration_minutes(self) -> Optional[int]:
        """Calculate session duration in minutes."""
        if not self.end_time:
            return None
        start = datetime.fromisoformat(self.start_time)
        end = datetime.fromisoformat(self.end_time)
        return int((end - start).total_seconds() / 60)


class SpacedRepetition(Base):
    """Spaced repetition data for SM-2 algorithm."""
    __tablename__ = 'spaced_repetition'

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey('questions.id', ondelete='CASCADE'), unique=True, nullable=False, index=True)

    # SM-2 Algorithm parameters
    ease_factor = Column(Float, default=2.5)  # Range: 1.3 - 2.5
    interval_days = Column(Integer, default=1)
    repetitions = Column(Integer, default=0)

    # Review tracking
    next_review_date = Column(Date, nullable=False, index=True)
    last_reviewed = Column(String(50))

    # Performance
    total_reviews = Column(Integer, default=0)
    correct_reviews = Column(Integer, default=0)

    # Relationship
    question = relationship('Question', back_populates='spaced_repetition')

    def __repr__(self) -> str:
        return f"<SpacedRepetition(question_id={self.question_id}, next_review={self.next_review_date})>"

    def update_after_review(self, quality: int) -> None:
        """
        Update spaced repetition parameters after a review using SM-2 algorithm.

        Args:
            quality: Quality of recall (0-5)
                0: Complete blackout
                1: Incorrect but familiar
                2: Incorrect but easy to recall correct answer
                3: Correct but difficult
                4: Correct with hesitation
                5: Perfect recall
        """
        self.total_reviews += 1
        self.last_reviewed = datetime.now().isoformat()

        if quality >= 3:
            # Correct answer
            self.correct_reviews += 1

            if self.repetitions == 0:
                self.interval_days = 1
            elif self.repetitions == 1:
                self.interval_days = 6
            else:
                self.interval_days = int(self.interval_days * self.ease_factor)

            self.repetitions += 1
        else:
            # Incorrect answer - reset
            self.repetitions = 0
            self.interval_days = 1

        # Update ease factor
        self.ease_factor = max(1.3, self.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))

        # Calculate next review date
        from datetime import date, timedelta
        self.next_review_date = date.today() + timedelta(days=self.interval_days)

    @property
    def accuracy_rate(self) -> float:
        """Calculate accuracy rate for this question's reviews."""
        if self.total_reviews == 0:
            return 0.0
        return (self.correct_reviews / self.total_reviews) * 100

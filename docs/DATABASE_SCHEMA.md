# Database Schema Design

**Created**: 2025-10-16
**Database**: SQLite
**Purpose**: Store questions, track user progress, manage study sessions

---

## Schema Overview

```
documents (1) ──┐
                ├──> questions (N)
                │         ├──> user_attempts (N)
                │         └──> spaced_repetition (1)
                └──> study_sessions (N) ──> user_attempts (N)
```

---

## Table Definitions

### 1. `documents`
Tracks processed PDF documents that have been analyzed.

```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id TEXT UNIQUE NOT NULL,           -- Timestamp-based ID (e.g., "20251016_113156")
    filename TEXT NOT NULL,                  -- Original filename
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_topics INTEGER NOT NULL,           -- Number of topics extracted
    total_pages INTEGER NOT NULL,            -- Total pages in PDF
    analysis_path TEXT NOT NULL,             -- Path to analysis.json
    formatted_path TEXT,                     -- Path to formatted.md
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_documents_file_id ON documents(file_id);
```

**Sample Data**:
```json
{
    "id": 1,
    "file_id": "20251016_113156",
    "filename": "repaso_ley_2025.pdf",
    "total_topics": 13,
    "total_pages": 111,
    "analysis_path": "outputs/20251016_113156/20251016_113156_analysis.json"
}
```

---

### 2. `questions`
Stores all generated multiple-choice questions.

```sql
CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,            -- FK to documents
    topic_id INTEGER NOT NULL,               -- Index in topics array (0-based)
    topic_name TEXT NOT NULL,                -- Main topic name for display
    question_type TEXT NOT NULL,             -- "single_answer" or "choose_all"
    difficulty TEXT NOT NULL,                -- "basic", "intermediate", "advanced"

    -- Question content
    question_text TEXT NOT NULL,             -- The question itself
    options_json TEXT NOT NULL,              -- JSON array of answer options
    correct_answer TEXT NOT NULL,            -- For single: "A"|"B"|"C"|"D", For multiple: "A,C,D"
    explanation TEXT NOT NULL,               -- Detailed explanation with regulatory context

    -- Metadata for question generation
    key_terms_json TEXT,                     -- JSON array of relevant key terms
    regulatory_context TEXT,                 -- Law/article citation
    pages TEXT,                              -- Page range (e.g., "3-8")

    -- Tracking
    times_seen INTEGER DEFAULT 0,            -- How many times shown to user
    times_correct INTEGER DEFAULT 0,         -- How many times answered correctly
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

CREATE INDEX idx_questions_document ON questions(document_id);
CREATE INDEX idx_questions_topic ON questions(document_id, topic_id);
CREATE INDEX idx_questions_difficulty ON questions(difficulty);
CREATE INDEX idx_questions_type ON questions(question_type);
```

**Sample Data**:
```json
{
    "id": 1,
    "document_id": 1,
    "topic_id": 1,
    "topic_name": "Requisitos para ejercer como Farmacéutico",
    "question_type": "single_answer",
    "difficulty": "intermediate",
    "question_text": "¿Cuántas horas de internado se requieren para obtener la licencia de farmacéutico en Puerto Rico?",
    "options_json": "[\"A. 1000 horas\", \"B. 1200 horas\", \"C. 1500 horas\", \"D. 2000 horas\"]",
    "correct_answer": "C",
    "explanation": "Según la Ley 247 de 2004, se requieren un mínimo de 1500 horas de internado bajo supervisión de un farmacéutico preceptor autorizado por la Junta de Farmacia.",
    "key_terms_json": "[{\"term\": \"Internado\", \"definition\": \"1500 horas bajo supervisión de farmacéutico preceptor\"}]",
    "regulatory_context": "Ley 247 de 2004",
    "pages": "3-8"
}
```

---

### 3. `user_attempts`
Records every answer attempt for analytics and spaced repetition.

```sql
CREATE TABLE user_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,            -- FK to questions
    session_id INTEGER,                      -- FK to study_sessions (NULL for standalone attempts)

    -- Answer details
    selected_answer TEXT NOT NULL,           -- User's answer (e.g., "A" or "A,C,D")
    is_correct BOOLEAN NOT NULL,             -- Whether answer was correct
    time_spent_seconds INTEGER,              -- Time spent on question

    -- Timestamps
    attempt_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES study_sessions(id) ON DELETE SET NULL
);

CREATE INDEX idx_attempts_question ON user_attempts(question_id);
CREATE INDEX idx_attempts_session ON user_attempts(session_id);
CREATE INDEX idx_attempts_date ON user_attempts(attempt_date);
CREATE INDEX idx_attempts_correct ON user_attempts(is_correct);
```

**Sample Data**:
```json
{
    "id": 1,
    "question_id": 1,
    "session_id": 1,
    "selected_answer": "C",
    "is_correct": true,
    "time_spent_seconds": 15,
    "attempt_date": "2025-10-16T14:30:00"
}
```

---

### 4. `study_sessions`
Tracks complete exam/study sessions.

```sql
CREATE TABLE study_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,            -- FK to documents

    -- Session configuration
    session_type TEXT NOT NULL,              -- "study", "practice", "mock"
    topic_filter TEXT,                       -- NULL = all topics, or topic name
    difficulty_filter TEXT,                  -- NULL = all, or "basic|intermediate|advanced"
    total_questions INTEGER NOT NULL,        -- Number of questions in session
    time_limit_minutes INTEGER,              -- NULL = no limit

    -- Session results
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,                      -- NULL if session incomplete
    correct_answers INTEGER DEFAULT 0,
    incorrect_answers INTEGER DEFAULT 0,
    score_percentage REAL,                   -- Calculated: (correct/total)*100

    -- Status
    status TEXT DEFAULT 'in_progress',       -- "in_progress", "completed", "abandoned"

    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

CREATE INDEX idx_sessions_document ON study_sessions(document_id);
CREATE INDEX idx_sessions_type ON study_sessions(session_type);
CREATE INDEX idx_sessions_start ON study_sessions(start_time);
CREATE INDEX idx_sessions_status ON study_sessions(status);
```

**Sample Data**:
```json
{
    "id": 1,
    "document_id": 1,
    "session_type": "practice",
    "topic_filter": null,
    "difficulty_filter": null,
    "total_questions": 25,
    "time_limit_minutes": 60,
    "start_time": "2025-10-16T14:00:00",
    "end_time": "2025-10-16T14:45:00",
    "correct_answers": 20,
    "incorrect_answers": 5,
    "score_percentage": 80.0,
    "status": "completed"
}
```

---

### 5. `spaced_repetition`
Implements SM-2 algorithm for optimal review scheduling.

```sql
CREATE TABLE spaced_repetition (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER UNIQUE NOT NULL,     -- One record per question

    -- SM-2 Algorithm parameters
    ease_factor REAL DEFAULT 2.5,            -- Difficulty factor (1.3-2.5)
    interval_days INTEGER DEFAULT 1,         -- Days until next review
    repetitions INTEGER DEFAULT 0,           -- Number of successful reviews

    -- Review tracking
    next_review_date DATE NOT NULL,          -- When to review again
    last_reviewed TIMESTAMP,                 -- Last review date

    -- Performance
    total_reviews INTEGER DEFAULT 0,         -- Total times reviewed
    correct_reviews INTEGER DEFAULT 0,       -- Correct review count

    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);

CREATE INDEX idx_spaced_next_review ON spaced_repetition(next_review_date);
CREATE INDEX idx_spaced_question ON spaced_repetition(question_id);
```

**Sample Data**:
```json
{
    "id": 1,
    "question_id": 1,
    "ease_factor": 2.6,
    "interval_days": 4,
    "repetitions": 2,
    "next_review_date": "2025-10-20",
    "last_reviewed": "2025-10-16T14:30:00",
    "total_reviews": 3,
    "correct_reviews": 2
}
```

---

## Relationships

1. **documents → questions** (1:N)
   - One document has many questions
   - CASCADE delete: Delete document removes all its questions

2. **questions → user_attempts** (1:N)
   - One question can be attempted multiple times
   - CASCADE delete: Delete question removes all attempts

3. **questions → spaced_repetition** (1:1)
   - Each question has one spaced repetition record
   - CASCADE delete: Delete question removes its spaced repetition data

4. **study_sessions → user_attempts** (1:N)
   - One session contains multiple attempts
   - SET NULL: Delete session keeps attempts but removes session_id

5. **documents → study_sessions** (1:N)
   - One document can have multiple study sessions
   - CASCADE delete: Delete document removes all sessions

---

## JSON Field Structures

### `questions.options_json`
```json
[
  "A. Primera opción",
  "B. Segunda opción",
  "C. Tercera opción",
  "D. Cuarta opción"
]
```

### `questions.key_terms_json`
```json
[
  {
    "term": "Internado",
    "definition": "1500 horas bajo supervisión de farmacéutico preceptor"
  }
]
```

---

## Key Design Decisions

1. **SQLite over PostgreSQL**: Simplicity for single-user app, easy deployment
2. **JSON fields**: Flexible storage for options and key terms
3. **Timestamps**: Track all temporal data for analytics
4. **Indexes**: Optimize common queries (by document, topic, date)
5. **Foreign keys with CASCADE**: Automatic cleanup on delete
6. **Spaced repetition**: Separate table for algorithm parameters
7. **Session tracking**: Complete history of all attempts

---

## Storage Estimates

- **13 topics** × **25 questions/topic** = **325 questions**
- **Average question size**: ~1KB
- **Total questions data**: ~325KB
- **Attempts (1000 attempts)**: ~50KB
- **Sessions (100 sessions)**: ~10KB
- **Total database size**: <1MB (very manageable)

---

## Next Steps

1. ✅ Schema designed
2. ⏳ Create `backend/database_models.py` with SQLAlchemy models
3. ⏳ Create `backend/database.py` for connection management
4. ⏳ Create initialization script to set up tables
5. ⏳ Test schema with sample data

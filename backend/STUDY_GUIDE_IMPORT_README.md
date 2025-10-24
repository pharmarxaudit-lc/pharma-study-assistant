# Study Guide Import Scripts - Documentation

## Overview

This directory contains scripts for importing and converting pharmacy law study guides from PDFs into standardized exam questions for the Pharma Study Assistant application.

**Created:** October 23, 2025
**Purpose:** Convert external study materials into database questions with automatic deduplication

---

## Scripts Inventory

### 1. `convert_study_guide.py`
**Purpose:** Convert first study guide (Repaso_Ley_D.pdf) to exam questions
**Source PDF:** `/Users/luiscotto/Library/CloudStorage/OneDrive-Personal/Personal/Repaso_Ley_D.pdf`
**Study Points:** 60
**Questions Generated:** 57
**Status:** Successfully processed

**Usage:**
```bash
python convert_study_guide.py --output /tmp/study_guide_questions.json --file-id repaso_ley_d [--execute]
```

**Features:**
- Hardcoded study guide text (60 points)
- Generates markdown files (raw and cleaned)
- Automatic deduplication against existing database
- Dry-run mode by default

**Output:**
- JSON file with generated questions
- `outputs/repaso_ley_d/study_guide_raw/study_guide_raw.md`
- `outputs/repaso_ley_d/study_guide_cleaned/study_guide_questions.md`

---

### 2. `convert_preguntas_examen.py`
**Purpose:** Initial attempt to convert second study guide (single batch)
**Source PDF:** `/Users/luiscotto/Library/CloudStorage/OneDrive-Personal/Personal/Preguntas_Examen_de_Leyes__Examen_de_Agosto_.docx.pdf`
**Study Points:** 117
**Status:** Deprecated (replaced by batched version)

**Issue:** Could only process 10 questions due to API token limits

---

### 3. `convert_preguntas_examen_batched.py` ✨ **RECOMMENDED**
**Purpose:** Convert second study guide using batch processing
**Source PDF:** `/Users/luiscotto/Library/CloudStorage/OneDrive-Personal/Personal/Preguntas_Examen_de_Leyes__Examen_de_Agosto_.docx.pdf`
**Study Points:** 117
**Questions Generated:** 117 (105 new, 12 duplicates)
**Status:** Successfully processed

**Usage:**
```bash
python convert_preguntas_examen_batched.py --output /tmp/preguntas_examen_all_questions.json --file-id preguntas_examen_leyes --delay 3 [--execute]
```

**Features:**
- **Batch processing:** Splits study guide into 6 manageable chunks
- **Rate limiting:** 3-second delay between API calls
- **Complete coverage:** Processes all 117 study points
- Generates markdown files
- Automatic deduplication
- Dry-run mode by default

**Batch Structure:**
1. Chunk 1: Questions 1-20 (20 questions)
2. Chunk 2: Questions 21-40 (19 questions)
3. Chunk 3: Questions 41-60 (20 questions)
4. Chunk 4: Additional Questions 1-20 (20 questions)
5. Chunk 5: Additional Questions 21-40 (20 questions)
6. Chunk 6: Additional Questions 41-57 (17 questions)

**Output:**
- JSON file with all generated questions
- `outputs/preguntas_examen_leyes/study_guide_raw/study_guide_raw.md`
- `outputs/preguntas_examen_leyes/study_guide_cleaned/study_guide_questions.md`

---

### 4. `import_test_questions.py`
**Purpose:** Core deduplication and import logic
**Status:** Shared utility used by all conversion scripts

**Key Components:**
- `TestQuestionImporter` class
- `find_similar_questions()`: Text similarity matching (85% threshold)
- `deduplicate_questions()`: Filters duplicates
- `add_questions_to_database()`: Bulk import with validation

**Modified:** Fixed SQLAlchemy session detachment issue (returns dicts instead of ORM objects)

---

### 5. `deduplicate_questions.py`
**Purpose:** Remove duplicate questions from existing database
**Status:** Utility script for database maintenance

**Usage:**
```bash
python deduplicate_questions.py [--execute] [--no-backup]
```

**Results from initial run:**
- Found 18 duplicate questions (36 total rows)
- Removed 18 duplicates
- Database cleaned from 255 → 237 questions

---

## Source PDFs

### PDF 1: Repaso_Ley_D.pdf
**Location:** `study_guides/Repaso_Ley_D.pdf` (copied into project)
**Original Location:** `/Users/luiscotto/Library/CloudStorage/OneDrive-Personal/Personal/Repaso_Ley_D.pdf`
**Pages:** 10
**Format:** Study guide with 60 numbered points
**Content:** Pharmacy law review covering:
- Junta de Farmacia
- Licensing requirements
- Continuing education
- Controlled substances
- Professional responsibilities

**Processing Script:** `convert_study_guide.py`
**Questions Generated:** 57 (0 duplicates found)
**Added to Database:** Yes (294 total questions after addition)

---

### PDF 2: Preguntas_Examen_de_Leyes__Examen_de_Agosto_.docx.pdf
**Location:** `study_guides/Preguntas_Examen_de_Leyes__Examen_de_Agosto_.docx.pdf` (copied into project)
**Original Location:** `/Users/luiscotto/Library/CloudStorage/OneDrive-Personal/Personal/Preguntas_Examen_de_Leyes__Examen_de_Agosto_.docx.pdf`
**Pages:** 9
**Format:** Two-section study guide with 117 points
**Content:** Pharmacy law exam questions covering:
- Section 1: Questions 1-60 (regulatory framework, licensing, facilities)
- Section 2: Additional Questions 1-57 (controlled substances, cannabis, bioequivalents)

**Processing Script:** `convert_preguntas_examen_batched.py`
**Questions Generated:** 117 (105 new, 12 duplicates)
**Added to Database:** Yes (399 total questions after addition)

---

## Database Summary

### Question Count History
1. **Initial state:** 255 questions (with 18 duplicates)
2. **After deduplication:** 237 unique questions
3. **After PDF 1 (Repaso_Ley_D):** 294 questions (+57)
4. **After PDF 2 (Preguntas_Examen_de_Leyes):** 399 questions (+105)

### Total New Questions from Study Guides
- **PDF 1:** 57 questions
- **PDF 2:** 105 questions
- **Total Added:** 162 questions
- **Total Duplicates Filtered:** 12

---

## Question Format

All generated questions follow this standardized format:

```json
{
  "question_text": "Question in Spanish",
  "question_type": "single_answer" | "choose_all",
  "difficulty": "basic" | "intermediate" | "advanced",
  "options": {
    "A": "Option text",
    "B": "Option text",
    "C": "Option text",
    "D": "Option text"
  },
  "correct_answer": "A" (single) or "A,B,C" (multiple, sorted),
  "explanation": "Detailed explanation in Spanish",
  "key_terms": ["term1", "term2", "term3"],
  "regulatory_context": "Ley 247 de 2004" | "Reglamento 156" | etc.,
  "topic_name": "Topic classification"
}
```

---

## Markdown Output Structure

Each processed study guide generates two markdown files:

### Raw Markdown
`outputs/{file_id}/study_guide_raw/study_guide_raw.md`
- Original study guide text
- Generation timestamp
- Study point count

### Cleaned Markdown
`outputs/{file_id}/study_guide_cleaned/study_guide_questions.md`
- Formatted questions with visual indicators
- Checkmarks (✓) for correct answers
- Complete metadata for each question
- Total question count

---

## API Configuration

**Model:** `claude-sonnet-4-20250514`
**Max Tokens:** 16,000
**Temperature:** 0.3
**Rate Limiting:** 3-second delay between batch calls
**API Key:** Configured in `config.py` as `ANTHROPIC_API_KEY`

---

## Deduplication Strategy

### Text Similarity Algorithm
1. **Exact Match:** Questions with identical text (case-insensitive)
2. **Word Overlap:** 85%+ word overlap for questions >20 characters
3. **Comparison Scope:** Checks against all existing questions in database

### Duplicate Handling
- Keeps first occurrence (lowest ID)
- Logs all duplicate matches with existing question IDs
- Provides detailed summary of duplicates found
- Dry-run mode shows what would be filtered

---

## Best Practices

### When Adding New Study Guides

1. **Analyze PDF structure** first to understand format
2. **Create dedicated script** if format differs significantly
3. **Use batch processing** for >50 study points
4. **Test with dry-run** before executing database changes
5. **Save markdown files** for documentation
6. **Specify file-id** for organized output storage

### Command Line Workflow

```bash
# 1. Dry run first to preview results
python convert_preguntas_examen_batched.py --output /tmp/questions.json --file-id my_study_guide

# 2. Review generated questions in /tmp/questions.json

# 3. Check markdown files in outputs/my_study_guide/

# 4. Execute if satisfied
python convert_preguntas_examen_batched.py --output /tmp/questions.json --file-id my_study_guide --execute
```

---

## Troubleshooting

### Issue: API Token Limit Exceeded
**Solution:** Use batched processing (see `convert_preguntas_examen_batched.py`)

### Issue: SQLAlchemy Detached Instance Error
**Solution:** Already fixed in `import_test_questions.py` - returns dicts instead of ORM objects

### Issue: Too Many API Rate Limit Errors
**Solution:** Increase `--delay` parameter (default is 3 seconds)

### Issue: JSON Parse Error from API
**Solution:** Reduce chunk size or study points per batch

---

## Future Enhancements

- [ ] Automated PDF text extraction (currently hardcoded)
- [ ] Support for additional document formats (Word, Excel)
- [ ] Configurable similarity threshold
- [ ] Question quality scoring
- [ ] Topic auto-classification using NLP
- [ ] Integration with main document processing pipeline

---

## Related Files

- `config.py`: API key and database configuration
- `database.py`: Database connection management
- `database_models.py`: Question and Document ORM models
- `pdf_extractor.py`: PDF text extraction utilities

---

## Maintenance

**Last Updated:** October 23, 2025
**Maintainer:** Development Team
**Scripts Location:** `/Users/luiscotto/Code/pharma-study-assistant/backend/`
**PDFs Location:** `/Users/luiscotto/Library/CloudStorage/OneDrive-Personal/Personal/`

---

## License

These scripts are part of the Pharma Study Assistant application.
All source PDFs remain property of their respective creators.

# Duplicate Question Detection Guide

## Overview

This guide explains how to review and detect potential duplicate questions in the database using multiple approaches, each designed to catch different types of duplicates.

---

## Detection Methods

### 1. **Exact Text Duplicates** (Highest Confidence)
Questions with identical text, ignoring case and whitespace.

**Characteristics:**
- 100% match in question text
- Most reliable indicator of duplication
- Should always be removed

**Example:**
```
Q1: "¿Cuál es el propósito de la Junta de Farmacia?"
Q2: "¿Cuál es el propósito de la Junta de Farmacia?"
```

---

### 2. **High Similarity Matches** (Medium Confidence)
Questions with very similar wording but not exactly identical.

**Characteristics:**
- 85%+ word overlap (configurable threshold)
- May be genuine duplicates with minor variations
- Requires manual review to confirm

**Example:**
```
Q1: "¿Cuántas horas de práctica debe completar un farmacéutico?"
Q2: "¿Cuántas horas de práctica supervisada debe completar un farmacéutico para obtener licencia?"
Similarity: 88%
```

**When to Keep Both:**
- Different difficulty levels testing the same concept
- One asks for specific detail, other asks general concept
- Different correct answers despite similar questions

**When to Remove One:**
- Same correct answer
- Same difficulty level
- No meaningful difference in what's being tested

---

### 3. **Topic + Answer Pattern** (Low Confidence)
Questions grouped by same topic and correct answer.

**Characteristics:**
- Same topic category
- Same correct answer choice (e.g., both answer "A")
- May indicate redundant coverage of same material

**Example:**
```
Topic: "Controlled Substances" | Answer: "B"
- Q1: "¿Quién puede revocar registro de controlados?"
- Q2: "¿Qué autoridad suspende licencias de controlados?"
- Q3: "¿Quién deniega permisos de sustancias controladas?"
```

**Analysis:**
- If 4+ questions in same topic with same answer → Review for redundancy
- Could be intentional (important concept tested multiple ways)
- Could be unintentional duplication

---

### 4. **Fuzzy String Matching** (Advanced)
Uses sequence-based algorithms to detect similar questions even with word reordering.

**Characteristics:**
- More sophisticated than word overlap
- Catches paraphrased duplicates
- Slower to compute

**When to Use:**
- After initial import of large question set
- When you suspect semantic duplicates
- For comprehensive database cleanup

---

## Using the Analyzer Script

### Quick Check (Exact Duplicates Only)
```bash
python analyze_duplicate_questions.py --exact-only
```

**Output:**
- List of questions with identical text
- IDs of all duplicates
- Usage statistics (times_seen, times_correct)

**Use Case:** Quick validation after import

---

### Standard Analysis
```bash
python analyze_duplicate_questions.py
```

**Output:**
- Exact duplicates report
- Top 20 similar question pairs (85%+ similarity)
- Topic+answer groupings with 4+ questions

**Use Case:** Regular database review

---

### Comprehensive Analysis
```bash
python analyze_duplicate_questions.py --fuzzy --threshold 0.80 --limit 50 --export duplicates.json
```

**Parameters:**
- `--fuzzy`: Enable advanced fuzzy matching
- `--threshold 0.80`: Lower threshold to catch more potential matches
- `--limit 50`: Show top 50 results
- `--export duplicates.json`: Save full report to file

**Use Case:** Deep analysis for database cleanup

---

## Interpretation Guide

### Exact Duplicates Report

```
1. Question Text: "¿Cuántas horas de internado debe completar un técnico de farmacia?"
   Occurrences: 2
   - ID 335: Answer=C, Topic=Técnicos de Farmacia, Seen=0x, Correct=0x
   - ID 368: Answer=C, Topic=Técnicos de Farmacia, Seen=0x, Correct=0x
```

**Decision:** Keep ID 335 (lower ID), delete ID 368

**Reasoning:** Both have 0 usage, identical content

---

### Similar Questions Report

```
1. Similarity: 92%
   Q1 [ID 44]: ¿Cuáles son los requisitos principales para ejercer como farmacéutico...
      Answer: A,B,C,D, Topic: Requisitos de Licencia
   Q2 [ID 329]: ¿Cuáles son los requisitos para ejercer como farmacéutico en PR?
      Answer: A,B,C,D, Topic: Requisitos de Licencia
```

**Decision Options:**

A) **Delete one if:**
   - Same difficulty level
   - Same correct answer
   - No meaningful difference

B) **Keep both if:**
   - Different difficulty levels
   - One is more specific
   - Testing different aspects

**Manual Review Required:** Compare full question text and options

---

### Topic+Answer Groups Report

```
1. Topic: 'Educación Continua' | Answer: 'A,B,C,D' | Count: 5
   - ID 333: ¿Cuáles son los requisitos de educación continua para farmacéuticos...
   - ID 388: ¿Cuáles son los requisitos de educación continua para farmacéuticos...
   - ID 407: ¿Cuál es el requisito mínimo de horas de educación continua...
   ... and 2 more
```

**Analysis Questions:**
1. Are all 5 questions testing the same knowledge?
2. Do they have different perspectives/focus areas?
3. Is this intentional comprehensive coverage?

**Decision:** Review individually, may keep all if testing different aspects

---

## Recommended Workflow

### Step 1: Initial Quick Check
```bash
python analyze_duplicate_questions.py --exact-only
```

**Action:** Remove all exact duplicates immediately

---

### Step 2: Export Full Analysis
```bash
python analyze_duplicate_questions.py --threshold 0.85 --export review.json
```

**Action:**
- Review exported JSON file
- Mark questions for deletion
- Note questions to keep

---

### Step 3: Manual Review of High-Similarity Pairs
For each pair with similarity > 90%:
1. Read full question text
2. Compare options
3. Check if answers are identical
4. Determine if truly duplicates or intentionally similar

---

### Step 4: Review Topic Clustering
For topics with 4+ questions with same answer:
1. Check if testing different aspects
2. Look for unintentional redundancy
3. Consider if comprehensive coverage is intentional

---

### Step 5: Execute Cleanup
Use `deduplicate_questions.py` for exact duplicates, or manually delete specific question IDs.

---

## Advanced Techniques

### 1. Compare Answer Options
Even if question text is similar, check if the answer options differ:
```python
# Add to analyzer script
if q1.options_json != q2.options_json:
    # Different options = probably intentional
    pass
```

### 2. Check Regulatory Context
Questions citing different laws may test similar concepts but from different angles:
```python
if q1.regulatory_context != q2.regulatory_context:
    # Different legal context = keep both
    pass
```

### 3. Difficulty Stratification
Same concept tested at different difficulty levels is often intentional:
```python
if q1.difficulty != q2.difficulty:
    # Different difficulty = likely intentional
    pass
```

---

## False Positives (Keep Both)

### Example 1: Different Specificity
```
Q1: "¿Cuántas horas de práctica se requieren?" (basic)
Q2: "¿Cuántas horas de práctica supervisada debe completar un farmacéutico bajo supervisión de preceptor?" (intermediate)
```
**Keep both:** Q2 is more specific and tests deeper knowledge

### Example 2: Different Perspectives
```
Q1: "¿Quién nombra los miembros de la Junta?" (Answer: Gobernador)
Q2: "¿Qué autoridad tiene el Gobernador respecto a la Junta?" (Answer: Nombra miembros)
```
**Keep both:** Different question perspectives on same fact

### Example 3: Multiple Choice vs. Select All
```
Q1: "¿Cuál es un requisito para ejercer?" (single_answer)
Q2: "¿Cuáles son los requisitos para ejercer?" (choose_all)
```
**Keep both:** Different question types test different skills

---

## Database Cleanup Strategy

### Conservative Approach (Recommended)
- **Remove:** Only exact duplicates
- **Review:** Similarity > 95%
- **Keep:** Everything else unless proven duplicate

**Pros:** Preserves question variety
**Cons:** May have some redundancy

---

### Aggressive Approach
- **Remove:** Exact duplicates + similarity > 90%
- **Review:** Similarity 80-90%
- **Consolidate:** Topic groups with 5+ same-answer questions

**Pros:** Leaner question database
**Cons:** May remove intentional variety

---

## Metrics to Track

After duplicate cleanup, monitor:

1. **Total Question Count**
   - Before: 399 questions
   - After: ??? questions
   - Reduction: ??? questions removed

2. **Questions Per Topic**
   - Ensure balanced coverage across topics
   - No topic should drop below minimum threshold

3. **Difficulty Distribution**
   - Maintain mix of basic/intermediate/advanced
   - Don't remove all questions of one difficulty level

4. **Usage Statistics**
   - Prioritize keeping questions with higher `times_seen`
   - Newer questions (times_seen=0) can be removed if duplicate

---

## Safety Measures

### Before Deletion:
1. **Always create database backup**
   ```bash
   cp pharma_exam.db pharma_exam_backup_$(date +%s).db
   ```

2. **Export questions to JSON**
   ```bash
   python analyze_duplicate_questions.py --export pre_cleanup_$(date +%s).json
   ```

3. **Use dry-run mode first**
   ```bash
   python deduplicate_questions.py  # Shows what would be deleted
   python deduplicate_questions.py --execute  # Actually deletes
   ```

---

## Next Steps

1. Run initial analysis:
   ```bash
   python analyze_duplicate_questions.py --export current_analysis.json
   ```

2. Review the exported JSON file

3. Decide on cleanup strategy (conservative vs. aggressive)

4. Execute cleanup with backups in place

5. Verify database integrity after cleanup

---

## Questions to Ask During Review

For each potential duplicate pair:
- [ ] Is the question text truly identical or just similar?
- [ ] Are the answer options the same?
- [ ] Is the correct answer the same?
- [ ] Are they testing the same knowledge?
- [ ] Do they have different difficulty levels?
- [ ] Do they reference different laws/regulations?
- [ ] Has either question been used in study sessions?
- [ ] Would removing one reduce educational value?

---

**Last Updated:** October 23, 2025
**Related Scripts:**
- `analyze_duplicate_questions.py`
- `deduplicate_questions.py`
- `import_test_questions.py`

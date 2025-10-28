# Key Terms Standardization Process

## Overview

This process converts key_terms from inconsistent formats to a single, standardized format using AI-generated definitions.

**Current State:**
- 232 questions: Object format `[{term: "...", definition: "..."}]` ✅
- 162 questions: String array `["term1", "term2"]` ❌

**Goal:**
- 394 questions: All use object format ✅

## Why Standardize?

1. **Simpler code** - No format detection logic needed
2. **Better UX** - All students get term definitions
3. **Easier maintenance** - One code path to maintain
4. **Prevents errors** - Consistent data structure

## Process (Safe & Reviewable)

### Step 1: Generate Preview (No Database Changes)

```bash
python generate_keyterms_preview.py
```

**What it does:**
- Finds all 162 questions with string array format
- Uses Claude AI to generate contextual definitions
- Creates two output files for review:
  - `keyterms_standardization_preview.txt` - Human-readable comparison
  - `keyterms_standardization_preview.json` - Structured data for application

**Output Example:**
```
================================================================================
Question 355
================================================================================

Text: ¿Cuándo se permite el intercambio por medicamentos bioequivalentes?...

BEFORE (String Array):
----------------------------------------
  • bioequivalentes
  • intercambio
  • No intercambie

AFTER (Object Format):
----------------------------------------
  • bioequivalentes
    → Medicamentos que contienen la misma cantidad de principio activo...
  • intercambio
    → Sustitución permitida de un medicamento por otro bioequivalente...
  • No intercambie
    → Indicación del prescriptor que prohíbe la sustitución...
```

**Time:** ~5-10 minutes (depends on AI API speed)

### Step 2: Review the Preview

1. Open `keyterms_standardization_preview.txt`
2. Review AI-generated definitions for:
   - ✅ Accuracy (correct for PR pharmacy law)
   - ✅ Clarity (helpful for students)
   - ✅ Consistency (matches question context)
   - ❌ Errors or placeholders

3. If you find issues:
   - Edit `keyterms_standardization_preview.json` directly
   - Fix the definitions in the JSON structure
   - Save and proceed to Step 3

### Step 3: Apply to Database (After Review Approval)

```bash
python apply_keyterms_standardization.py
```

**What it does:**
- Creates automatic backup: `pharma_exam_backup_keyterms_[timestamp].db`
- Reads approved data from `keyterms_standardization_preview.json`
- Updates all 162 questions in database
- Verifies conversion success

**Safety features:**
- Asks for confirmation before proceeding
- Creates backup automatically
- Shows progress and results
- Verifies all conversions worked

**Output:**
```
================================================================================
KEY TERMS STANDARDIZATION - APPLY TO DATABASE
================================================================================

⚠️  WARNING: This will modify the database!
   A backup will be created automatically.

❓ Continue with database update? (yes/no): yes

📦 Creating backup: pharma_exam_backup_keyterms_1234567890.db
   ✅ Backup created successfully

🔧 Applying 162 conversions to database...
   Processing 162/162: Question 462...

✅ Conversion complete!
   Success: 162
   Errors: 0

🔍 Verifying conversions...

📊 Database Status:
   Object format: 394
   String format: 0

   ✅ All questions now use object format!
```

## After Standardization

### Update the Code

Once database is standardized, simplify `QuestionDisplay.vue`:

**Remove this complexity:**
```vue
<template v-if="typeof term === 'string'">
  <strong>{{ term }}</strong>
</template>
<template v-else>
  <strong>{{ term.term }}:</strong> {{ term.definition }}
</template>
```

**Replace with simple version:**
```vue
<strong>{{ term.term }}:</strong> {{ term.definition }}
```

### Benefits Achieved

✅ All 394 questions have consistent format
✅ All students see term definitions
✅ Simpler, more maintainable code
✅ Prevents future format inconsistencies

## Rollback (If Needed)

If issues occur after applying:

```bash
# Stop the application
# Replace current database with backup
cp backend/pharma_exam_backup_keyterms_[timestamp].db backend/pharma_exam.db
# Restart application
```

## Files Created

1. **generate_keyterms_preview.py** - Preview generator (safe, no DB changes)
2. **apply_keyterms_standardization.py** - Database updater (requires approval)
3. **keyterms_standardization_preview.txt** - Human-readable comparison
4. **keyterms_standardization_preview.json** - Structured data for application
5. **KEYTERMS_STANDARDIZATION_README.md** - This file

## Questions?

- Preview looks good? → Run `apply_keyterms_standardization.py`
- Need to fix definitions? → Edit the JSON file and re-run apply script
- Something went wrong? → Restore from backup

---

**Status:** Ready to generate preview
**Next Step:** Run `python generate_keyterms_preview.py`

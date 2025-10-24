# Database Backup Guide

## Quick Reference

### Create Backup Before Any Changes
```bash
python backup_database.py --description "Before removing duplicates"
```

### List All Backups
```bash
python backup_database.py --list
```

### Restore from Backup
```bash
python backup_database.py --restore backups/backup_20251023_165000
```

---

## Complete Guide

### Why Backup?

Always create a backup before:
- ✅ Removing duplicate questions
- ✅ Importing new questions
- ✅ Modifying existing questions
- ✅ Database schema changes
- ✅ Testing new features

---

## Backup Methods

### Method 1: Full Automated Backup (Recommended)

**Use the backup script:**
```bash
cd /Users/luiscotto/Code/pharma-study-assistant/backend
python backup_database.py --description "Before duplicate cleanup"
```

**What it creates:**
- ✅ Complete SQLite database file copy
- ✅ JSON export of all questions
- ✅ Markdown report with statistics
- ✅ SQL dump for version control
- ✅ Backup metadata file

**Output location:**
```
backups/backup_20251023_165030/
├── pharma_exam_20251023_165030.db    # Database copy
├── questions_20251023_165030.json     # All questions
├── dump_20251023_165030.sql           # SQL dump
├── report_20251023_165030.md          # Statistics
└── backup_info.json                   # Metadata
```

---

### Method 2: Quick Database File Copy

**Simple file copy:**
```bash
cd /Users/luiscotto/Code/pharma-study-assistant/backend
cp pharma_exam.db "pharma_exam_backup_$(date +%Y%m%d_%H%M%S).db"
```

**Pros:** Fast, simple
**Cons:** No metadata, no JSON export

---

### Method 3: Fast Backup (Skip SQL Dump)

**Faster backup without SQL dump:**
```bash
python backup_database.py --description "Quick backup" --no-sql
```

**Use when:** You need a quick backup and don't need SQL dump

---

## Restoration

### Restore Full Database

**From automated backup:**
```bash
# List available backups first
python backup_database.py --list

# Restore specific backup
python backup_database.py --restore backups/backup_20251023_165030
```

**What happens:**
1. Current database is backed up (safety!)
2. Backup database replaces current database
3. Confirmation message shown

---

### Manual Restoration

**From database file:**
```bash
# Backup current database first
cp pharma_exam.db pharma_exam_current.db

# Restore from backup
cp backups/backup_20251023_165030/pharma_exam_20251023_165030.db pharma_exam.db
```

**From SQL dump:**
```bash
# Backup current database first
cp pharma_exam.db pharma_exam_current.db

# Restore from SQL dump
sqlite3 pharma_exam.db < backups/backup_20251023_165030/dump_20251023_165030.sql
```

---

## Backup Strategy

### Before Major Operations

**Before removing duplicates:**
```bash
python backup_database.py --description "Before removing 5 exact duplicates"
python deduplicate_questions.py --execute
```

**Before importing new questions:**
```bash
python backup_database.py --description "Before importing study guide X"
python convert_study_guide.py --execute
```

**Before database changes:**
```bash
python backup_database.py --description "Before schema migration"
# ... perform changes ...
```

---

### Regular Backups

**Daily backup (if actively developing):**
```bash
python backup_database.py --description "Daily backup $(date +%Y-%m-%d)"
```

**Before deploying:**
```bash
python backup_database.py --description "Pre-deployment backup"
```

---

## Backup Reports

Each backup includes a detailed markdown report with:

### Statistics Included:
- Total questions count
- Questions by difficulty (basic/intermediate/advanced)
- Questions by type (single/multiple choice)
- Questions by topic
- Most used questions
- Success rates

### Example Report Preview:
```markdown
# Database Backup Report

**Backup Date:** 2025-10-23 16:50:30
**Total Questions:** 399

## Questions by Difficulty
| Difficulty | Count | Percentage |
|------------|-------|------------|
| Basic      | 150   | 37.6%      |
| Intermediate | 180 | 45.1%      |
| Advanced   | 69    | 17.3%      |
```

---

## Storage Management

### Check Backup Size
```bash
du -sh backups/
du -sh backups/backup_*
```

### Clean Old Backups
```bash
# Keep only last 10 backups
cd backups
ls -dt backup_* | tail -n +11 | xargs rm -rf
```

### Archive Old Backups
```bash
# Compress old backups
tar -czf backups_archive_2025.tar.gz backups/backup_2025*
```

---

## Git Integration

### Add Backup to .gitignore

Add to `.gitignore`:
```
# Database backups
backups/
*.db
*.db-journal
pharma_exam_backup_*.db
```

### Track SQL Dumps in Git (Optional)

If you want version control:
```bash
# Add SQL dumps to git
git add backups/backup_*/dump_*.sql
git commit -m "Database backup: $(date +%Y-%m-%d)"
```

**Pros:** Version history
**Cons:** Large files in git

---

## Verification

### Verify Backup Integrity

**Check file exists:**
```bash
ls -lh backups/backup_20251023_165030/
```

**Verify database can be opened:**
```bash
sqlite3 backups/backup_20251023_165030/pharma_exam_20251023_165030.db "SELECT COUNT(*) FROM questions;"
```

**Compare with current:**
```bash
# Current database
sqlite3 pharma_exam.db "SELECT COUNT(*) FROM questions;"

# Backup database
sqlite3 backups/backup_*/pharma_exam_*.db "SELECT COUNT(*) FROM questions;"
```

---

## Troubleshooting

### Backup Failed

**Error: Permission denied**
```bash
# Fix permissions
chmod +w backups/
mkdir -p backups
```

**Error: Disk space**
```bash
# Check available space
df -h .

# Clean old backups
rm -rf backups/backup_2024*
```

---

### Restoration Failed

**Error: Database is locked**
```bash
# Stop the application first
# Then restore

# Or use SQL dump method instead
```

**Error: Corrupted backup**
```bash
# Use an older backup
python backup_database.py --list
python backup_database.py --restore backups/backup_PREVIOUS
```

---

## Best Practices

### ✅ DO:
- Create backup before ANY database changes
- Use descriptive descriptions
- Verify backup was created successfully
- Keep multiple backups (at least 3-5)
- Test restoration process periodically

### ❌ DON'T:
- Delete backups immediately after changes
- Skip verification
- Keep only one backup
- Forget to backup before imports
- Store backups on same disk only

---

## Automated Backup Script

Create a cron job for automated backups:

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /Users/luiscotto/Code/pharma-study-assistant/backend && python backup_database.py --description "Automated daily backup" --no-sql
```

---

## Recovery Scenarios

### Scenario 1: Deleted Wrong Questions

```bash
# 1. List backups
python backup_database.py --list

# 2. Restore from before deletion
python backup_database.py --restore backups/backup_20251023_165030

# 3. Verify restoration
sqlite3 pharma_exam.db "SELECT COUNT(*) FROM questions;"
```

---

### Scenario 2: Imported Bad Questions

```bash
# 1. Restore from before import
python backup_database.py --restore backups/backup_20251023_165030

# 2. Fix import script
# 3. Re-import with corrections
```

---

### Scenario 3: Database Corruption

```bash
# 1. Try SQL dump restoration
sqlite3 pharma_exam_new.db < backups/backup_*/dump_*.sql

# 2. Replace corrupted database
mv pharma_exam.db pharma_exam_corrupted.db
mv pharma_exam_new.db pharma_exam.db
```

---

## Current Backup Workflow

### Before Removing Duplicates:

```bash
# 1. Create backup
python backup_database.py --description "Before removing 5 exact duplicates - 399 questions"

# 2. Remove duplicates
python deduplicate_questions.py --execute

# 3. Verify
sqlite3 pharma_exam.db "SELECT COUNT(*) FROM questions;"

# 4. If satisfied, keep backup. If not, restore:
python backup_database.py --restore backups/backup_TIMESTAMP
```

---

## Examples

### Example 1: Complete Workflow

```bash
# Current state: 399 questions with 5 duplicates

# Step 1: Backup
python backup_database.py --description "Pre-cleanup: 399 questions, 5 duplicates identified"

# Output:
# ✅ Database file backed up: backups/backup_20251023_170000/pharma_exam_20251023_170000.db
# ✅ Exported 399 questions
# ✅ Statistics report created
# ✅ Backup complete

# Step 2: Remove duplicates
python deduplicate_questions.py --execute

# Step 3: Verify
sqlite3 pharma_exam.db "SELECT COUNT(*) FROM questions;"
# Expected: 394

# Step 4: If something went wrong, restore
python backup_database.py --restore backups/backup_20251023_170000
```

---

### Example 2: Compare Backups

```bash
# List all backups
python backup_database.py --list

# Output:
# Backup: 20251023_170000
# Date: 2025-10-23T17:00:00
# Description: Pre-cleanup: 399 questions
#
# Backup: 20251023_140000
# Date: 2025-10-23T14:00:00
# Description: After importing PDF 2

# Compare question counts
for backup in backups/backup_*/pharma_exam_*.db; do
  echo "$backup: $(sqlite3 $backup 'SELECT COUNT(*) FROM questions;') questions"
done
```

---

**Last Updated:** October 23, 2025
**Related Scripts:** `backup_database.py`, `deduplicate_questions.py`

# Deployment Guide

## Replit Deployment Steps

### First-Time Deployment with Alembic

If this is your **first deployment after adding Alembic**, follow these steps to preserve existing production data:

#### Step 1: Backup Production Database (Recommended)

Before making any changes, create a backup of your production database on Replit:

```bash
# In Replit Shell
cd backend
cp pharma_exam.db pharma_exam_backup_$(date +%Y%m%d).db
```

#### Step 2: Pull Latest Code

```bash
# In Replit Shell (from project root)
git pull origin main
```

**What this does:**
- ✅ Downloads Alembic configuration files
- ✅ Downloads migration scripts
- ✅ Updates `database.py` to use migrations
- ❌ Does NOT overwrite your existing `pharma_exam.db` (it's now in .gitignore)

#### Step 3: Install Alembic

```bash
# In Replit Shell
pip install alembic==1.13.1
```

Or let Replit auto-install from `requirements.txt` on next run.

#### Step 4: Stamp Existing Database

This tells Alembic "the database is already at this version, don't recreate tables":

```bash
cd backend
alembic stamp head
```

**What this does:**
- ✅ Creates `alembic_version` table in your database
- ✅ Records current schema version as `76089491c4fe`
- ✅ Preserves ALL existing data (questions, sessions, attempts, etc.)
- ✅ Prepares database for future migrations

#### Step 5: Verify Migration Status

```bash
alembic current
```

You should see:
```
76089491c4fe (head)
```

#### Step 6: Restart Application

Click the "Run" button in Replit or restart the server.

**✅ Done! Your production database is now under Alembic version control.**

---

## Future Deployments (After Schema Changes)

Once Alembic is set up, future deployments are much simpler:

### When You Add/Modify Database Schema

**Example: Adding a new field or table**

#### Step 1: Pull Latest Code

```bash
git pull origin main
```

This downloads new migration files like:
- `migrations/versions/abc123_add_user_notes.py`

#### Step 2: Apply Migrations

```bash
cd backend
alembic upgrade head
```

**What this does:**
- ✅ Detects new migrations
- ✅ Applies schema changes (ADD column, CREATE table, etc.)
- ✅ Preserves all existing data
- ✅ Updates `alembic_version` to latest

#### Step 3: Restart Application

Click "Run" or restart the server.

**✅ Done! Schema updated, data preserved.**

---

## Common Scenarios

### Scenario 1: Fresh Deployment (No Existing Database)

If deploying to a new environment with no database:

```bash
cd backend
# Copy baseline database (includes 325 pre-generated questions)
cp pharma_exam_baseline.db pharma_exam.db

# Verify questions loaded
sqlite3 pharma_exam.db "SELECT COUNT(*) FROM questions;"
# Should show: 325

# Database is already stamped with Alembic version, ready to use!
```

The baseline includes:
- ✅ 325 pharmacy exam questions (generated from PDF)
- ✅ 1 source document
- ✅ All tables created
- ✅ Alembic version tracking
- ❌ No user sessions or attempts (clean slate)

### Scenario 2: Check Migration Status

```bash
cd backend
alembic current        # Show current version
alembic history        # Show all migrations
```

### Scenario 3: Rollback a Migration (Emergency)

If a migration causes issues:

```bash
cd backend
alembic downgrade -1   # Go back one migration
```

Then investigate, fix, and re-run:

```bash
alembic upgrade head
```

### Scenario 4: Database Out of Sync

If you get "table already exists" errors:

```bash
# Option A: Stamp to current version (if schema matches code)
alembic stamp head

# Option B: Check what version database thinks it is
alembic current

# Option C: Manually fix by stamping to specific version
alembic stamp <revision_id>
```

---

## Verification Checklist

After any deployment, verify:

- [ ] Application starts without errors
- [ ] Can view existing exam sessions
- [ ] Can create new exam sessions
- [ ] Migration status shows correct version: `alembic current`
- [ ] No data loss (check question counts, session history)

---

## Troubleshooting

### Error: "alembic: command not found"

```bash
pip install alembic==1.13.1
```

### Error: "table already exists"

You need to stamp the database instead of upgrading:

```bash
cd backend
alembic stamp head
```

### Error: "Can't locate revision identified by 'head'"

The migrations folder wasn't pulled. Verify:

```bash
ls -la backend/migrations/versions/
```

Should show: `76089491c4fe_initial_schema_with_all_tables.py`

If missing, run `git pull` again.

### Database Performance Issues

After many migrations, you may want to vacuum the database:

```bash
sqlite3 backend/pharma_exam.db "VACUUM;"
```

---

## Database Backup Strategy

### Before Major Changes

Always backup before:
- Applying migrations in production
- Making manual database edits
- Upgrading Python/SQLAlchemy versions

```bash
cd backend
cp pharma_exam.db pharma_exam_backup_$(date +%Y%m%d_%H%M%S).db
```

### Regular Backups (Recommended)

Set up a cron job or scheduled task:

```bash
# Run daily at 2 AM
0 2 * * * cd /path/to/backend && cp pharma_exam.db backups/pharma_exam_$(date +\%Y\%m\%d).db
```

---

## Migration Development Workflow

For developers making schema changes:

### 1. Modify Model

```python
# backend/database_models.py
class StudySession(Base):
    # Add new field
    user_notes = Column(Text)
```

### 2. Generate Migration

```bash
cd backend
alembic revision --autogenerate -m "Add user notes to study sessions"
```

### 3. Review Generated Migration

Check `migrations/versions/XXX_add_user_notes.py`

### 4. Test Locally

```bash
# Apply migration
alembic upgrade head

# Test application
# ...

# If issues, rollback
alembic downgrade -1
```

### 5. Commit to Git

```bash
git add backend/migrations/versions/XXX_add_user_notes.py
git add backend/database_models.py
git commit -m "Add user notes feature"
git push
```

### 6. Deploy to Replit

See "Future Deployments" section above.

---

## Summary

**Key Points:**
- ✅ Database file (`pharma_exam.db`) is NOT in git
- ✅ Migration files (`migrations/versions/*.py`) ARE in git
- ✅ Each environment keeps its own data
- ✅ Schema changes are applied via `alembic upgrade head`
- ✅ User data is never lost during deployments

**Commands to Remember:**
```bash
alembic current          # Check current version
alembic history          # View all migrations
alembic upgrade head     # Apply new migrations
alembic stamp head       # Mark existing DB as current (one-time)
alembic downgrade -1     # Rollback last migration (emergency)
```

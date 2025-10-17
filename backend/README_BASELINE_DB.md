# Baseline Database Setup

## pharma_exam_baseline.db

This is a clean baseline database file that should be used for fresh deployments.

### What's included:
- ✅ All database tables (schema)
- ✅ Default timezone setting (America/Puerto_Rico - AST)
- ❌ No documents or questions (empty)
- ❌ No user sessions or attempts (empty)

### When to use:
1. **First-time deployment**: Copy this file to start with a clean database
2. **Reset database**: Replace your existing database to start fresh
3. **Development**: Use as a starting point for testing

### How to use:

#### Fresh Deployment:
```bash
cd backend
cp pharma_exam_baseline.db pharma_exam.db
```

#### Reset Existing Database:
```bash
cd backend
# Backup your current database first!
cp pharma_exam.db pharma_exam_backup_$(date +%Y%m%d).db
# Replace with baseline
cp pharma_exam_baseline.db pharma_exam.db
```

### After copying the baseline:
1. Start the backend server: `python backend/app.py`
2. Upload your PDF documents via the web interface
3. Process documents to generate questions
4. The database will be populated with your content

### Database Schema:
- **app_settings**: Application configuration (timezone, etc.)
- **documents**: Processed PDF documents metadata
- **questions**: Generated exam questions
- **user_attempts**: Student answer attempts
- **study_sessions**: Exam/study session tracking
- **spaced_repetition**: Spaced repetition algorithm data

### Default Settings:
- Timezone: `America/Puerto_Rico` (Atlantic Standard Time)
- Can be changed via Maintenance page in the UI

### Important Notes:
- The baseline database is tracked in git
- Your working database (`pharma_exam.db`) is NOT tracked in git
- Always backup your database before replacing it
- The baseline contains NO questions or user data

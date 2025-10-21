# Pharmacy Exam Prep - Phase 1

PDF to Structured Markdown conversion with AI-powered analysis for pharmacy law study materials.

## Quick Start

### Local Development

1. **Setup Environment**
```bash
# Copy .env.example to .env and add your API key
cp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

2. **Install Backend Dependencies**
```bash
pip install -r requirements.txt
```

3. **Initialize Database**
```bash
# Run database migrations to set up schema
cd backend
alembic upgrade head
cd ..
```

4. **Install Frontend Dependencies**
```bash
cd frontend
npm install
```

5. **Run Validation (Optional but Recommended)**
```bash
bash validate.sh
```
This runs linters and type checkers on both backend and frontend.

6. **Start Application**

Option A - Using the startup script (recommended):
```bash
bash start_app.sh
```

Option B - Manual development servers:

Terminal 1 (Backend):
```bash
cd backend
python app.py
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

7. **Access the Application**
- Startup script: http://localhost:5001
- Manual dev servers: http://localhost:3000

### Replit Deployment

1. **Get Anthropic API Key**
   - Visit: https://console.anthropic.com
   - Sign up → Get $5 free credit
   - Go to Settings → API Keys
   - Create key → Copy it (starts with `sk-ant-api03-...`)

2. **Create Replit Project**
   - Go to: https://replit.com
   - Click "+ Create Repl"
   - Choose Python template
   - Name: `pharmacy-exam-prep`

3. **Upload Files**
   - Upload all files from this project to Replit

4. **Configure API Key**
   - In Replit sidebar, click Secrets (lock icon)
   - Add: `ANTHROPIC_API_KEY` = your API key

5. **Deploy**
   - Click Run button
   - Wait for installation and build
   - Click "Open in new tab" when ready

## Features

- **Smart PDF Extraction**: Handles large files (40MB+, 100+ pages)
- **Incremental File Writing**: Files are written as they're processed, not at the end
  - Raw page extraction saved immediately
  - Cleaned pages saved after text processing
  - Each formatted topic appended to markdown as it completes
- **AI-Powered Analysis**: Claude analyzes content for:
  - Topic classification
  - Key term extraction
  - Exam-critical point identification
  - Question generation potential
  - Regulatory context
- **Rich Metadata**: YAML frontmatter + JSON for Phase 2
- **Clean Formatting**: Professional markdown with visual indicators
- **Real-time Progress**: Live updates during processing
- **Code Quality**: Comprehensive validation with ruff, mypy, and TypeScript checks

## Usage

1. Upload a PDF (up to 50MB)
2. Wait for processing (2-5 minutes depending on size)
3. Download formatted markdown file
4. Download analysis JSON file (for Phase 2)

## Output Files

All files are written incrementally during processing to `outputs/{file_id}/`:

### Page Extraction
- `pages/raw/page_001.md` - Raw text exactly as extracted by PyMuPDF
- `pages/cleaned/page_001.md` - After text cleaning and processing

### Markdown File
Clean, structured study materials with:
- YAML frontmatter with metadata
- Properly formatted headers and sections
- Bold key terms
- Visual indicators (⚠️ for critical points, 💊 for drugs, ⚖️ for laws)
- Topics appended incrementally as they're analyzed

### Analysis JSON
Rich metadata including:
- Content classification
- Key terms with definitions
- Exam-critical points
- Question generation potential
- Relationships between topics
- Written at completion with all topic metadata

## Cost Estimate

With Anthropic's $5 free credit:
- 100-page PDF: ~$0.50-$1.00
- Total: ~5-10 PDFs before needing payment

## Troubleshooting

### "API key not configured"
- Check `.env` file has `ANTHROPIC_API_KEY` set (local)
- Check Replit Secrets has `ANTHROPIC_API_KEY` set (Replit)

### "Upload fails"
- Check file is PDF format
- Check file size is under 50MB
- Verify PDF is not corrupted

### "Processing stalls"
- Check `/api/health` endpoint
- Verify API key is valid
- Check browser console for errors

### "Module not found" error
- Run: `pip install -r requirements.txt`

### "Frontend not loading"
```bash
cd frontend
npm run build
mkdir -p ../backend/static
cp -r dist/* ../backend/static/
```

## Database Migrations

This project uses **Alembic** for database schema version control, ensuring safe deployments without data loss.

### Initial Setup (First Time)
```bash
cd backend
alembic upgrade head
```

### Making Schema Changes

1. **Modify the model** in `backend/database_models.py`:
```python
# Example: Add a new column
class StudySession(Base):
    # ... existing columns ...
    user_notes = Column(Text)  # NEW COLUMN
```

2. **Generate migration** (Alembic auto-detects changes):
```bash
cd backend
alembic revision --autogenerate -m "Add user_notes to study sessions"
```

3. **Review the migration** in `backend/migrations/versions/`:
```python
# migrations/versions/XXX_add_user_notes.py
def upgrade():
    with op.batch_alter_table('study_sessions') as batch_op:
        batch_op.add_column(sa.Column('user_notes', sa.Text(), nullable=True))
```

4. **Apply migration**:
```bash
alembic upgrade head
```

### Deployment Workflow

When deploying updates to production:

```bash
cd backend
alembic upgrade head  # Apply any new migrations
cd ..
# Restart application
```

### Useful Commands

```bash
# Check current version
alembic current

# View migration history
alembic history

# Rollback one migration (if needed)
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision_id>

# Upgrade to latest
alembic upgrade head
```

### Migration Best Practices

- ✅ **Always review** auto-generated migrations before applying
- ✅ **Test migrations** on a copy of production data first
- ✅ **Make backups** before running migrations in production
- ✅ **Never edit** applied migrations - create new ones instead
- ✅ **Commit migrations** to version control along with model changes
- ⚠️ **SQLite limitations**: Some operations require batch mode (already configured)

## Project Structure

```
pharmacy-exam-prep/
├── backend/
│   ├── app.py                    # Flask API server
│   ├── database.py               # Database connection & session management
│   ├── database_models.py        # SQLAlchemy ORM models
│   ├── pdf_extractor.py          # PDF text extraction
│   ├── text_processor.py         # Text cleaning & structuring
│   ├── content_analyzer.py       # Claude-powered analysis
│   ├── llm_formatter.py          # Claude formatting
│   ├── config.py                 # Configuration
│   ├── alembic.ini               # Alembic migration config
│   ├── migrations/               # Database migrations
│   │   ├── env.py                # Migration environment
│   │   └── versions/             # Migration version files
│   └── pharma_exam.db            # SQLite database (tracked in git)
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── components/
│   │   │   ├── FileUpload.vue
│   │   │   ├── ProcessingStatus.vue
│   │   │   └── ResultViewer.vue
│   │   ├── main.ts
│   │   └── style.css
│   ├── package.json
│   ├── vite.config.ts
│   └── index.html
├── uploads/                      # Temp PDF storage
├── outputs/                      # Generated files
│   └── {file_id}/
│       ├── pages/
│       │   ├── raw/              # Raw extracted pages
│       │   └── cleaned/          # Cleaned pages
│       ├── formatted.md          # Final markdown output
│       └── analysis.json         # Analysis metadata
├── logs/                         # Application logs
├── validate.sh                   # Validation script (ruff, mypy, TypeScript)
├── start_app.sh                  # Startup script
├── stop_app.sh                   # Stop script
├── pyproject.toml                # Python tool configuration
├── .gitignore
└── README.md
```

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/upload` - Upload PDF file
- `POST /api/process/<file_id>` - Process PDF (SSE stream)
- `GET /api/download/<file_id>/<markdown|analysis>` - Download result

## Phase 2 Preview

The analysis JSON file is ready for Phase 2, which will include:
- Question generation from analyzed content
- Interactive quiz interface
- Progress tracking
- Spaced repetition algorithm

---

Made with Claude Code for pharmacy exam preparation

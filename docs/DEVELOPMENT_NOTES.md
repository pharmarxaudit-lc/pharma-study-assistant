# Development Notes

## Project Overview
Pharmacy exam prep application that converts PDF study materials into structured markdown using AI-powered analysis with Claude API.

## Recent Development Session Summary

### Key Features Implemented
1. **Incremental File Writing** - Files are written as they're processed, not waiting for completion
   - Raw pages saved immediately after extraction: `outputs/{file_id}/pages/raw/page_001.md`
   - Cleaned pages saved after text processing: `outputs/{file_id}/pages/cleaned/page_001.md`
   - Each formatted topic appended to markdown file as it completes
   - Final JSON written at end with all metadata

2. **Comprehensive Validation** - `validate.sh` script with error counting
   - Backend: ruff (linting), mypy (type checking), Python syntax checks
   - Frontend: TypeScript compiler checks
   - Per-tool error counts and detailed summary

3. **All Validation Errors Fixed**
   - Python: Fixed type annotations, added `# type: ignore` for Claude API responses
   - TypeScript: Fixed ref access patterns, removed unused variables
   - Current status: Zero errors across all tools

## Important Technical Decisions

### Python Version: 3.8
**Decision**: Use Python 3.8 instead of 3.13
**Reason**: PyMuPDF 1.23.8 has build issues with Python 3.13. Battle-tested compatibility with 3.8.
**Priority**: PDF parsing tool compatibility over newer Python features

### Topic Identification: LLM vs Rule-Based
**Decision**: Use Claude API for semantic topic identification instead of Python heuristics
**Reason**:
- Rule-based approach (headers, page counts) creates arbitrary topic boundaries
- LLM understands content semantics and natural topic transitions
- Results in meaningful topic names instead of "Section 11"
- Example: "Funciones del Farmacéutico y Administración de Medicamentos" vs "Pages 11-13"
**Implementation**:
- Process PDF in 10-page chunks
- Claude identifies topics semantically
- Context (summary + topics) passed between chunks for continuity
**See**: `docs/LLM_TOPIC_IDENTIFICATION.md` for complete details

### Language Preservation
**Decision**: Explicitly instruct Claude to preserve Spanish content
**Reason**: Puerto Rico pharmacy exam requires Spanish materials
**Implementation**: All prompts include "Keep all content in ORIGINAL LANGUAGE (Spanish)"
**Result**: No unwanted translation to English

### File Writing Strategy
**Decision**: Incremental writing instead of batch writing at completion
**Reason**:
- Large PDFs (92+ pages) take 15+ minutes to process
- Users need to see output as it's generated
- Prevents data loss if processing is interrupted
**Implementation**: Files written at each stage (raw → cleaned → formatted)

### Path Configuration
**Decision**: Use absolute paths in config.py
**Reason**: Prevents issues with relative paths when running from different directories
**Code**: `BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))`

### Memory Management
**Finding**: 111-page PDF only uses ~45-50MB total memory
**Approach**: In-memory pipeline with incremental disk writes is efficient

## Development Workflow

### Starting the Application
```bash
bash start_app.sh
```
- Builds frontend if needed
- Copies to backend/static/
- Starts Flask on port 5001
- Saves PID to .app.pid

### Stopping the Application
```bash
bash stop_app.sh
```

### Running Validation
```bash
bash validate.sh
```
Always run this before committing code. Should show "✅ All validation checks passed!"

### Development Servers (Alternative)
```bash
# Terminal 1 - Backend
cd backend && python app.py

# Terminal 2 - Frontend
cd frontend && npm run dev
```
Backend runs on port 5000, frontend on port 3000 (with proxy to backend).

## Code Quality Standards

### Python
- **Linter**: ruff with rules E,F,W,I,N,UP (ignoring E501 line length)
- **Type Checker**: mypy with `ignore_missing_imports`
- **Configuration**: pyproject.toml
- **Target**: Python 3.8

### TypeScript/Vue
- **Type Checker**: vue-tsc with --noEmit
- **Framework**: Vue 3 with Composition API and `<script setup>`
- **Build Tool**: Vite

## Key Files and Their Purpose

### Backend Core
- `app.py` - Flask API with SSE streaming for real-time progress
- `pdf_extractor.py` - PyMuPDF integration for text extraction
- `text_processor.py` - **LLM-based topic identification with context propagation**
- `content_analyzer.py` - Claude API for topic analysis (Spanish preservation)
- `llm_formatter.py` - Claude API for markdown formatting (Spanish preservation)
- `config.py` - Centralized configuration with absolute paths

### Frontend Components
- `FileUpload.vue` - Drag-drop PDF upload with file validation
- `ProcessingStatus.vue` - Real-time progress display using fetch streaming
- `ResultViewer.vue` - Download links for markdown and JSON

### Scripts and Tools
- `start_app.sh` - Production-like startup (builds frontend, starts backend)
- `stop_app.sh` - Graceful shutdown
- `validate.sh` - Comprehensive validation with error counting
- `pyproject.toml` - Python tooling configuration

## Recent Bug Fixes

### TypeScript Ref Access
**Problem**: `$refs.fileInput.click()` caused type errors
**Solution**: Use ref variable directly: `fileInput?.click()`
**Files**: FileUpload.vue:3, FileUpload.vue:18

### Unused EventSource Variable
**Problem**: `eventSource?.close()` referenced non-existent variable
**Solution**: Removed unused variable and `onUnmounted` import
**Reason**: Code switched to fetch streaming, EventSource not used
**File**: ProcessingStatus.vue:128

### Mypy Type Annotations
**Problem**: Mypy couldn't infer types for Counter and Claude API responses
**Solution**:
- Added explicit type: `text_frequency: Counter = Counter()`
- Added `# type: ignore` comments for Claude API response types
**Files**: text_processor.py:14, content_analyzer.py:48, llm_formatter.py:38

### Validation Script False Positives
**Problem**: `validate.sh` reported "all passed" when errors existed
**Solution**: Use `${PIPESTATUS[0]}` to check command exit code, not tee's exit code
**Pattern**: `command | tee file; if [ ${PIPESTATUS[0]} -eq 0 ]; then`

### Page Cleaning TypeError
**Problem**: Passing list to `clean_text()` which expects string
**Solution**: Loop through text_blocks and clean each string individually
**File**: app.py processing loop

## API Endpoints

- `GET /api/health` - Health check (returns status: "healthy")
- `POST /api/upload` - Upload PDF, returns file_id
- `POST /api/process/<file_id>` - Process PDF with SSE streaming
- `GET /api/download/<file_id>/<type>` - Download markdown or analysis JSON

## Output Structure

```
outputs/{file_id}/
├── pages/
│   ├── raw/
│   │   ├── page_001.md
│   │   ├── page_002.md
│   │   └── ...
│   └── cleaned/
│       ├── page_001.md
│       ├── page_002.md
│       └── ...
├── formatted.md          # Incrementally written
└── analysis.json         # Written at completion
```

## Processing Pipeline

1. **Upload** - PDF saved to `uploads/{file_id}.pdf`
2. **Extract** - PyMuPDF extracts text by page → saved to `pages/raw/`
3. **Clean** - Remove headers/footers/repeated elements → saved to `pages/cleaned/`
4. **LLM Topic Identification** (NEW) - Claude identifies topics in 10-page chunks
   - Chunk 1 (pages 1-10): Identify topics
   - Generate summary of last 2-3 pages
   - Chunk 2 (pages 11-20): Receive context + identify topics
   - Continue for all chunks...
   - Result: Semantically meaningful topics (e.g., 41 topics from 111 pages)
5. **Analyze** - Claude analyzes each identified topic → extracts key terms, critical points
6. **Format** - Claude formats each topic → appended to `formatted.md`
7. **Complete** - All metadata saved to `analysis.json`

## Future Improvements / Phase 2

- Question generation from analyzed content
- Interactive quiz interface
- Progress tracking
- Spaced repetition algorithm
- Potential: Use Ollama locally for extraction, Claude for question generation

## Cost Estimates

With Anthropic's $5 free credit:
- 100-page PDF: ~$0.50-$1.00
- Total: ~5-10 PDFs before needing payment
- Model: claude-3-5-sonnet-20241022

## GitHub Repository

- **URL**: https://github.com/pharmarxaudit-lc/pharma-study-assistant
- **Branch**: main
- **Visibility**: Public

## Environment Variables

Required in `.env` file:
```bash
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

The `.env` file is gitignored for security.

## Common Issues and Solutions

### "Processing stalls at X%"
- Check backend logs: `tail -f logs/backend.log`
- Verify API key is valid
- Check Anthropic API status

### "Module not found"
- Backend: `pip install -r backend/requirements.txt`
- Frontend: `cd frontend && npm install`

### "Port 5001 already in use"
- Run: `bash stop_app.sh`
- Or manually: `lsof -ti:5001 | xargs kill -9`

### Validation errors
- Run: `bash validate.sh` to see detailed error breakdown
- Backend fixes: `ruff check backend/ --fix` (auto-fix some issues)
- Check error counts by tool in validation summary

## Testing Checklist

Before committing:
1. ✅ Run `bash validate.sh` - should show zero errors
2. ✅ Test PDF upload and processing end-to-end
3. ✅ Verify raw pages, cleaned pages, and formatted output are all generated
4. ✅ Check logs for any errors or warnings
5. ✅ Test download functionality for both markdown and JSON

## Session History Context

This document was created at the end of a development session where:
- Fixed all TypeScript and Python validation errors (3 TS errors, 3 Python errors)
- Enhanced .gitignore with mypy/ruff caches and temp files
- Updated README with validation instructions and incremental writing details
- Created GitHub repository and pushed all code
- Copied entire project from `/Users/luiscotto/Code/supertest` to `/Users/luiscotto/Code/pharma-study-assistant`

All code is production-ready with zero validation errors.

---

Last updated: October 16, 2025
Generated during Claude Code development session

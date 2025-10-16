# Phase 1 Implementation Plan: PDF to Structured Markdown
## Pharmacy Exam Prep Application

### Overview
Extract and structure content from a 100-page, 40MB PowerPoint-as-PDF into clean, tagged markdown suitable for exam question generation.

---

## Architecture

### Tech Stack
- **Backend**: Python (Flask)
- **Frontend**: Vue 3 + TypeScript (Vite)
- **PDF Processing**: PyMuPDF (fitz)
- **LLM Integration**: Configurable (Ollama local / API-based for Replit)
- **Deployment**: Replit-ready single package

### File Structure
```
pharmacy-exam-prep/
├── backend/
│   ├── app.py                 # Flask server
│   ├── pdf_extractor.py       # PDF text extraction
│   ├── text_processor.py      # Cleaning & structuring
│   ├── llm_formatter.py       # LLM integration
│   ├── config.py              # LLM backend configuration
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── components/
│   │   │   ├── FileUpload.vue
│   │   │   ├── ProcessingStatus.vue
│   │   │   └── ResultViewer.vue
│   │   └── main.ts
│   ├── package.json
│   └── vite.config.ts
├── uploads/                   # Temporary PDF storage
├── outputs/                   # Generated markdown files
├── .replit                    # Replit configuration
└── README.md
```

---

## Implementation Phases

### Step 1: PDF Extraction (pdf_extractor.py)
**Goal**: Extract raw text from PDF page-by-page

**Key Functions**:
```python
def extract_text_from_pdf(pdf_path):
    """Extract text from all pages, return list of page texts"""
    
def extract_with_metadata(pdf_path):
    """Extract text + font info + positioning for structure detection"""
```

**Process**:
1. Open PDF with PyMuPDF
2. Iterate pages in batches (20 pages at a time)
3. Extract text blocks with font size metadata
4. Identify potential headers (larger font, ALL CAPS)
5. Return structured data: `[{page: 1, text: "...", headers: [...], body: [...]}]`

---

### Step 2: Text Processing (text_processor.py)
**Goal**: Clean and structure raw text

**Key Functions**:
```python
def clean_text(raw_text):
    """Remove junk, fix spacing, normalize"""
    
def detect_structure(page_data):
    """Identify headers, bullets, definitions"""
    
def group_by_topics(pages):
    """Combine related pages into topic sections"""
```

**Process**:
1. Remove repeated headers/footers
2. Fix PowerPoint artifacts (bullet chars, spacing)
3. Detect hierarchy: Title → Subtitles → Content
4. Group related pages by topic similarity
5. Return: `[{topic: "Controlled Substances", pages: [15-17], content: "..."}]`

---

### Step 3: LLM Formatting (llm_formatter.py)
**Goal**: Use LLM to enhance structure and extract metadata

**Configurable Backends**:
```python
# Option 1: Ollama (local dev)
def format_with_ollama(text_chunk):
    """Use local Llama/Mistral model"""

# Option 2: API-based (Replit deployment)
def format_with_api(text_chunk, provider="together"):
    """Use Together.ai, HuggingFace, or OpenAI"""
```

**LLM Prompt Template**:
```
You are formatting pharmacy law study materials.

Input text:
{raw_markdown}

Tasks:
1. Fix formatting: proper headers (# ##), bullet points
2. Identify key terms and bold them
3. Extract main topic and subtopics
4. Flag important exam concepts with ⚠️
5. Add metadata tags

Output as clean markdown with YAML frontmatter:
---
topic: [main topic]
subtopics: [list]
key_terms: [important terms]
pages: [page range]
---
[formatted content]
```

---

### Step 4: Flask API (app.py)
**Endpoints**:

```python
POST /api/upload
    - Accept PDF file
    - Save temporarily
    - Return file_id

POST /api/process
    - Process PDF (extraction → cleaning → LLM formatting)
    - Stream progress updates via SSE
    - Return structured markdown

GET /api/download/:file_id
    - Download final markdown file

GET /api/status/:file_id
    - Check processing status
```

---

### Step 5: Vue Frontend

**Components**:

1. **FileUpload.vue**
   - Drag-and-drop PDF upload
   - File size validation (40MB+)
   - Upload progress bar

2. **ProcessingStatus.vue**
   - Real-time status: "Extracting page 45/100..."
   - Progress percentage
   - Cancel button

3. **ResultViewer.vue**
   - Preview generated markdown
   - Syntax-highlighted code blocks
   - Download button
   - Topic summary table

**User Flow**:
```
1. Upload PDF → Shows file info
2. Click "Process" → Shows progress bar
3. Processing completes → Shows preview + download
4. Download markdown file → Ready for Phase 2
```

---

## LLM Backend Configuration

### For Local Development (Ollama)
```python
# config.py
LLM_BACKEND = "ollama"
OLLAMA_MODEL = "llama3.2:3b"  # Lightweight model
OLLAMA_URL = "http://localhost:11434"
```

### For Replit Deployment
```python
# config.py
LLM_BACKEND = "together"  # or "anthropic", "openai"
API_KEY = os.getenv("TOGETHER_API_KEY")
MODEL_NAME = "meta-llama/Llama-3.2-3B-Instruct-Turbo"
```

**Recommended for Replit**: Together.ai
- Free tier available
- Hosts open-source models
- Fast inference
- Simple REST API

---

## Replit Deployment Configuration

### .replit file
```toml
run = "cd backend && python app.py"
entrypoint = "backend/app.py"

[nix]
channel = "stable-23_11"

[deployment]
build = ["sh", "-c", "cd frontend && npm install && npm run build && cd ../backend && pip install -r requirements.txt"]
run = ["python", "backend/app.py"]
```

### Environment Variables (Replit Secrets)
```
TOGETHER_API_KEY=your_key_here
LLM_BACKEND=together
UPLOAD_FOLDER=/tmp/uploads
```

---

## Processing Pipeline Summary

```
PDF Upload
    ↓
[PyMuPDF] Extract text + metadata (20 pages/batch)
    ↓
[Text Processor] Clean & structure
    ↓
[Topic Grouper] Combine related pages
    ↓
[LLM Formatter] Enhance each topic section
    ↓
[Markdown Generator] Create final .md file
    ↓
Download or View in UI
```

---

## Output Format Example

```markdown
---
document: Pharmacy Law Review
topic: Controlled Substances Regulations
subtopics: [Schedule Classification, Prescription Requirements, Record Keeping]
key_terms: [DEA, Schedule II, Form 222, Refills]
pages: 23-27
exam_focus: high
---

# Controlled Substances Regulations

## Schedule II Drugs

**Definition**: Drugs with high potential for abuse but accepted medical use.

**Key Examples**:
- Morphine
- Oxycodone
- Fentanyl
- Amphetamines

**Prescription Requirements**: ⚠️ *EXAM CRITICAL*
- Must be written prescription (no phone-in except emergency)
- No refills permitted
- Must include DEA number
- Valid for 6 months from issue date

**Record Keeping**:
- DEA Form 222 required for ordering
- Separate inventory required
- Biennial inventory mandatory

---

## Key Exam Points
- ⚠️ Schedule II = NO REFILLS
- ⚠️ Emergency supply: 72-hour limit, written Rx within 7 days
- ⚠️ DEA registration renewal: every 3 years
```

---

## Success Metrics - Phase 1

✅ **Extraction**: All 100 pages processed without errors  
✅ **Quality**: >95% text accuracy (manually verify 5-10 pages)  
✅ **Structure**: Topics clearly identified with proper headers  
✅ **Metadata**: Key terms and exam focus areas tagged  
✅ **Output**: Clean markdown files ready for Phase 2 question generation  
✅ **Deployment**: One-click deploy on Replit, works smoothly  

---

## Timeline Estimate

- **PDF Extraction**: 2-3 hours
- **Text Processing**: 3-4 hours  
- **LLM Integration**: 2-3 hours
- **Flask API**: 2-3 hours
- **Vue Frontend**: 4-5 hours
- **Replit Setup & Testing**: 2 hours
- **Total**: ~15-20 hours

---

## Next Steps → Phase 2

Once Phase 1 is complete:
1. Add SQLite database (store topics, questions, user progress)
2. Question generation from structured markdown
3. Quiz interface with answer checking
4. Progress tracking and weak area identification
5. Spaced repetition algorithm

---

## Notes

- Keep it simple: MVP first, optimize later
- Process in batches to handle 40MB file
- Cache LLM results to avoid reprocessing
- Add error handling for malformed PDFs
- Log processing steps for debugging

Ready to implement! 🚀
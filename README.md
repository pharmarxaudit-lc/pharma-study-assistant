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
cd backend
pip install -r requirements.txt
```

3. **Install Frontend Dependencies**
```bash
cd frontend
npm install
```

4. **Run Development Servers**

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

5. **Access the Application**
- Open http://localhost:3000 in your browser

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
- **AI-Powered Analysis**: Claude analyzes content for:
  - Topic classification
  - Key term extraction
  - Exam-critical point identification
  - Question generation potential
  - Regulatory context
- **Rich Metadata**: YAML frontmatter + JSON for Phase 2
- **Clean Formatting**: Professional markdown with visual indicators
- **Real-time Progress**: Live updates during processing

## Usage

1. Upload a PDF (up to 50MB)
2. Wait for processing (2-5 minutes depending on size)
3. Download formatted markdown file
4. Download analysis JSON file (for Phase 2)

## Output Files

### Markdown File
Clean, structured study materials with:
- YAML frontmatter with metadata
- Properly formatted headers and sections
- Bold key terms
- Visual indicators (⚠️ for critical points, 💊 for drugs, ⚖️ for laws)

### Analysis JSON
Rich metadata including:
- Content classification
- Key terms with definitions
- Exam-critical points
- Question generation potential
- Relationships between topics

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
- Run: `cd backend && pip install -r requirements.txt`

### "Frontend not loading"
```bash
cd frontend
npm run build
mkdir -p ../backend/static
cp -r dist/* ../backend/static/
```

## Project Structure

```
pharmacy-exam-prep/
├── backend/
│   ├── app.py                    # Flask API server
│   ├── pdf_extractor.py          # PDF text extraction
│   ├── text_processor.py         # Text cleaning & structuring
│   ├── content_analyzer.py       # Claude-powered analysis
│   ├── llm_formatter.py          # Claude formatting
│   ├── config.py                 # Configuration
│   └── requirements.txt
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
├── .replit                       # Replit config
├── replit.nix                    # Nix dependencies
├── start.sh                      # Startup script
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

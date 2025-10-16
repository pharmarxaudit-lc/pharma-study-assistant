# Pharmacy Exam Prep - Phase 1 Implementation
## ONE-SHOT DEPLOYMENT GUIDE FOR REPLIT (< 2 HOURS)

---

## 🎯 PROJECT OVERVIEW

**Goal**: Convert 100-page pharmacy law PDF into structured markdown with AI analysis for exam prep.

**Tech Stack**:
- Backend: Python + Flask + PyMuPDF + Anthropic Claude API
- Frontend: Vue 3 + TypeScript + Vite
- Deployment: Replit (one-click)

**Timeline**: 
- Setup: 10 min
- Implementation: 60 min (automated)
- Testing: 15 min
- Deployment: 5 min

---

## 📁 COMPLETE FILE STRUCTURE

```
pharmacy-exam-prep/
├── backend/
│   ├── requirements.txt
│   ├── config.py
│   ├── app.py
│   ├── pdf_extractor.py
│   ├── text_processor.py
│   ├── content_analyzer.py
│   └── llm_formatter.py
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── index.html
│   └── src/
│       ├── main.ts
│       ├── style.css
│       ├── App.vue
│       └── components/
│           ├── FileUpload.vue
│           ├── ProcessingStatus.vue
│           └── ResultViewer.vue
├── .replit
├── replit.nix
├── start.sh
└── README.md
```

---

## 🔧 COMPLETE CODE - ALL FILES

### FILE: `backend/requirements.txt`

```txt
flask==3.0.0
flask-cors==4.0.0
PyMuPDF==1.23.8
anthropic==0.18.1
python-dotenv==1.0.0
```

---

### FILE: `backend/config.py`

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"
    UPLOAD_FOLDER = './uploads'
    OUTPUT_FOLDER = './outputs'
    MAX_FILE_SIZE = 50 * 1024 * 1024
    BATCH_SIZE = 20
```

---

### FILE: `backend/pdf_extractor.py`

```python
import fitz
from typing import List, Dict

class PDFExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.total_pages = len(self.doc)
    
    def extract_all(self) -> List[Dict]:
        pages_data = []
        for page_num in range(self.total_pages):
            page_data = self.extract_page(page_num)
            pages_data.append(page_data)
        return pages_data
    
    def extract_page(self, page_num: int) -> Dict:
        page = self.doc[page_num]
        blocks = page.get_text("dict")["blocks"]
        
        text_content = []
        headers = []
        
        for block in blocks:
            if block.get("type") == 0:
                for line in block.get("lines", []):
                    line_text = ""
                    max_size = 0
                    
                    for span in line.get("spans", []):
                        line_text += span.get("text", "")
                        max_size = max(max_size, span.get("size", 0))
                    
                    line_text = line_text.strip()
                    if line_text:
                        is_header = max_size > 14 or (line_text.isupper() and len(line_text) > 3)
                        if is_header:
                            headers.append(line_text)
                        text_content.append({
                            "text": line_text,
                            "size": max_size,
                            "is_header": is_header
                        })
        
        return {
            "page": page_num + 1,
            "content": text_content,
            "headers": headers,
            "full_text": page.get_text()
        }
    
    def close(self):
        self.doc.close()
```

---

### FILE: `backend/text_processor.py`

```python
import re
from typing import List, Dict
from collections import Counter

class TextProcessor:
    def clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = text.replace('', '•').replace('', '-')
        text = re.sub(r'\d+\s*$', '', text)
        return text.strip()
    
    def detect_repeated_elements(self, pages_data: List[Dict]) -> set:
        text_frequency = Counter()
        for page in pages_data:
            for item in page.get("content", []):
                text = item.get("text", "").strip()
                if len(text) > 5:
                    text_frequency[text] += 1
        threshold = len(pages_data) * 0.3
        return {text for text, count in text_frequency.items() if count > threshold}
    
    def remove_repeated_elements(self, pages_data: List[Dict], repeated: set) -> List[Dict]:
        cleaned_pages = []
        for page in pages_data:
            cleaned_content = [
                item for item in page.get("content", [])
                if item.get("text", "").strip() not in repeated
            ]
            page["content"] = cleaned_content
            cleaned_pages.append(page)
        return cleaned_pages
    
    def structure_page(self, page_data: Dict) -> Dict:
        structured = {
            "page": page_data["page"],
            "headers": [],
            "bullets": [],
            "body": []
        }
        
        for item in page_data.get("content", []):
            text = self.clean_text(item.get("text", ""))
            if not text:
                continue
            
            if item.get("is_header", False):
                structured["headers"].append(text)
            elif text.startswith(('•', '-', '*', '○')):
                structured["bullets"].append(text.lstrip('•-*○ '))
            else:
                structured["body"].append(text)
        
        return structured
    
    def group_by_topics(self, pages_data: List[Dict]) -> List[Dict]:
        topics = []
        current_topic = None
        
        for page in pages_data:
            structured = self.structure_page(page)
            
            if structured["headers"]:
                if current_topic and current_topic["content"]:
                    topics.append(current_topic)
                current_topic = {
                    "topic": structured["headers"][0],
                    "start_page": page["page"],
                    "end_page": page["page"],
                    "content": [structured]
                }
            elif current_topic:
                current_topic["end_page"] = page["page"]
                current_topic["content"].append(structured)
            else:
                current_topic = {
                    "topic": f"Section {page['page']}",
                    "start_page": page["page"],
                    "end_page": page["page"],
                    "content": [structured]
                }
        
        if current_topic and current_topic["content"]:
            topics.append(current_topic)
        
        return topics
    
    def process(self, pages_data: List[Dict]) -> List[Dict]:
        repeated = self.detect_repeated_elements(pages_data)
        cleaned_pages = self.remove_repeated_elements(pages_data, repeated)
        topics = self.group_by_topics(cleaned_pages)
        return topics
```

---

### FILE: `backend/content_analyzer.py`

```python
from typing import Dict
from anthropic import Anthropic
from config import Config
import json

class PharmacyContentAnalyzer:
    def __init__(self):
        self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.model = Config.ANTHROPIC_MODEL
    
    def analyze_topic(self, topic_data: Dict) -> Dict:
        content_text = self._prepare_content(topic_data)
        
        prompt = f"""Analyze this pharmacy law content and return ONLY valid JSON:

{content_text}

Return this exact structure:
{{
  "main_topic": "topic name",
  "subtopics": ["sub1", "sub2"],
  "content_type": "regulation",
  "key_terms": [{{"term": "name", "definition": "def", "importance": "high"}}],
  "exam_critical_points": [{{"point": "fact", "category": "requirement"}}],
  "question_potential": {{"multiple_choice": "high", "true_false": "medium", "scenario_based": "high", "calculation": "low"}},
  "difficulty_level": "intermediate",
  "regulatory_context": "DEA"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            analysis_text = response.content[0].text
            if "```json" in analysis_text:
                analysis_text = analysis_text.split("```json")[1].split("```")[0]
            
            analysis = json.loads(analysis_text.strip())
            analysis["pages"] = f"{topic_data['start_page']}-{topic_data['end_page']}"
            return analysis
            
        except Exception as e:
            print(f"Analysis error: {e}")
            return self._fallback_analysis(topic_data)
    
    def _prepare_content(self, topic_data: Dict) -> str:
        lines = [f"TOPIC: {topic_data['topic']}", ""]
        for page in topic_data['content']:
            if page['headers']:
                lines.append("## " + " / ".join(page['headers']))
            for bullet in page['bullets']:
                lines.append(f"• {bullet}")
            for body_text in page['body']:
                lines.append(body_text)
            lines.append("")
        return "\n".join(lines)[:3000]  # Limit for speed
    
    def _fallback_analysis(self, topic_data: Dict) -> Dict:
        return {
            "main_topic": topic_data['topic'],
            "subtopics": [],
            "content_type": "mixed",
            "key_terms": [],
            "exam_critical_points": [],
            "question_potential": {"multiple_choice": "medium", "true_false": "medium", "scenario_based": "low", "calculation": "low"},
            "difficulty_level": "intermediate",
            "regulatory_context": "Mixed",
            "pages": f"{topic_data['start_page']}-{topic_data['end_page']}"
        }
```

---

### FILE: `backend/llm_formatter.py`

```python
from typing import Dict
from anthropic import Anthropic
from config import Config

class ClaudeFormatter:
    def __init__(self):
        self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.model = Config.ANTHROPIC_MODEL
    
    def format_topic(self, topic_data: Dict, analysis: Dict) -> str:
        content_text = self._prepare_input(topic_data)
        
        prompt = f"""Format this pharmacy content as clean markdown with YAML frontmatter:

{content_text}

Use this structure:
---
topic: {analysis['main_topic']}
pages: {analysis['pages']}
difficulty: {analysis['difficulty_level']}
exam_focus: high
---

# {analysis['main_topic']}

[Format with proper headers, bold key terms, use ⚠️ for critical points, 💊 for drugs, ⚖️ for laws]"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        except Exception as e:
            print(f"Format error: {e}")
            return self._basic_format(topic_data, analysis)
    
    def _prepare_input(self, topic_data: Dict) -> str:
        lines = []
        for page in topic_data['content']:
            if page['headers']:
                lines.append("HEADERS: " + " | ".join(page['headers']))
            for bullet in page['bullets']:
                lines.append(f"  • {bullet}")
            for body in page['body']:
                lines.append(f"  {body}")
        return "\n".join(lines)[:2000]
    
    def _basic_format(self, topic_data: Dict, analysis: Dict) -> str:
        lines = ["---", f"topic: {analysis['main_topic']}", f"pages: {analysis['pages']}", "---", "", f"# {topic_data['topic']}", ""]
        for page in topic_data['content']:
            if page['headers']:
                for h in page['headers']:
                    lines.append(f"## {h}")
            for bullet in page['bullets']:
                lines.append(f"• {bullet}")
            for body in page['body']:
                lines.append(body)
            lines.append("")
        return "\n".join(lines)
```

---

### FILE: `backend/app.py`

```python
from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from pdf_extractor import PDFExtractor
from text_processor import TextProcessor
from content_analyzer import PharmacyContentAnalyzer
from llm_formatter import ClaudeFormatter
from config import Config

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)

processing_status = {}

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "claude_configured": bool(Config.ANTHROPIC_API_KEY),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '' or not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Invalid file"}), 400
    
    filename = secure_filename(file.filename)
    file_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(Config.UPLOAD_FOLDER, f"{file_id}_{filename}")
    file.save(filepath)
    
    try:
        extractor = PDFExtractor(filepath)
        total_pages = extractor.total_pages
        extractor.close()
    except Exception as e:
        return jsonify({"error": f"Invalid PDF: {str(e)}"}), 400
    
    return jsonify({
        "file_id": file_id,
        "filename": filename,
        "size": os.path.getsize(filepath),
        "total_pages": total_pages
    })

@app.route('/api/process/<file_id>', methods=['POST'])
def process_file(file_id):
    files = [f for f in os.listdir(Config.UPLOAD_FOLDER) if f.startswith(file_id)]
    if not files:
        return jsonify({"error": "File not found"}), 404
    
    filepath = os.path.join(Config.UPLOAD_FOLDER, files[0])
    
    def generate():
        try:
            yield f"data: {json.dumps({'progress': 10, 'message': 'Extracting PDF...'})}\n\n"
            
            extractor = PDFExtractor(filepath)
            pages_data = extractor.extract_all()
            extractor.close()
            
            yield f"data: {json.dumps({'progress': 30, 'message': 'Processing text...'})}\n\n"
            
            processor = TextProcessor()
            topics = processor.process(pages_data)
            
            yield f"data: {json.dumps({'progress': 50, 'message': f'Analyzing {len(topics)} topics...'})}\n\n"
            
            analyzer = PharmacyContentAnalyzer()
            formatter = ClaudeFormatter()
            
            formatted_sections = []
            analyses = []
            
            for idx, topic in enumerate(topics):
                progress = 50 + int((idx / len(topics)) * 45)
                yield f"data: {json.dumps({'progress': progress, 'message': f'Processing {idx+1}/{len(topics)}'})}\n\n"
                
                analysis = analyzer.analyze_topic(topic)
                formatted = formatter.format_topic(topic, analysis)
                
                formatted_sections.append(formatted)
                analyses.append(analysis)
            
            yield f"data: {json.dumps({'progress': 95, 'message': 'Saving files...'})}\n\n"
            
            md_file = f"{file_id}_formatted.md"
            json_file = f"{file_id}_analysis.json"
            
            with open(os.path.join(Config.OUTPUT_FOLDER, md_file), 'w', encoding='utf-8') as f:
                f.write(f"# Pharmacy Law Study Guide\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n")
                for section in formatted_sections:
                    f.write(section + "\n\n---\n\n")
            
            with open(os.path.join(Config.OUTPUT_FOLDER, json_file), 'w') as f:
                json.dump({"metadata": {"generated": datetime.now().isoformat(), "total_topics": len(analyses)}, "topics": analyses}, f, indent=2)
            
            processing_status[file_id] = {"status": "complete", "output_file": md_file, "analysis_file": json_file}
            
            yield f"data: {json.dumps({'progress': 100, 'message': 'Complete!', 'output_file': md_file})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/download/<file_id>/<file_type>', methods=['GET'])
def download_file(file_id, file_type):
    if file_id not in processing_status:
        return jsonify({"error": "File not found"}), 404
    
    status = processing_status[file_id]
    output_file = status.get("output_file" if file_type == "markdown" else "analysis_file")
    
    if not output_file:
        return jsonify({"error": "File not ready"}), 400
    
    filepath = os.path.join(Config.OUTPUT_FOLDER, output_file)
    return send_file(filepath, as_attachment=True, download_name=output_file)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
```

---

### FILE: `frontend/package.json`

```json
{
  "name": "pharmacy-exam-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "vue-tsc": "^1.8.0"
  }
}
```

---

### FILE: `frontend/vite.config.ts`

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: { port: 3000 },
  build: { outDir: 'dist' }
})
```

---

### FILE: `frontend/tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "lib": ["ES2020", "DOM"],
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "jsx": "preserve",
    "strict": true
  },
  "include": ["src/**/*.ts", "src/**/*.vue"]
}
```

---

### FILE: `frontend/index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Pharmacy Exam Prep</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.ts"></script>
</body>
</html>
```

---

### FILE: `frontend/src/main.ts`

```typescript
import { createApp } from 'vue'
import App from './App.vue'
import './style.css'

createApp(App).mount('#app')
```

---

### FILE: `frontend/src/style.css`

```css
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  padding: 20px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  border-radius: 16px;
  padding: 50px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

h1 { color: #333; font-size: 2.5em; margin-bottom: 10px; }
.subtitle { color: #666; font-size: 1.2em; margin-bottom: 40px; }

button {
  background: #667eea;
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

button:hover:not(:disabled) {
  background: #5568d3;
  transform: translateY(-2px);
}

button:disabled { background: #ccc; cursor: not-allowed; }

.progress-bar {
  width: 100%;
  height: 40px;
  background: #e8eaf6;
  border-radius: 20px;
  overflow: hidden;
  margin: 25px 0;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
}

.error {
  background: #ffebee;
  border: 2px solid #ef5350;
  border-radius: 8px;
  padding: 16px;
  color: #c62828;
  margin-top: 20px;
}

.drop-zone {
  border: 3px dashed #ccc;
  border-radius: 16px;
  padding: 80px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.drop-zone:hover { border-color: #667eea; background: #f8f9ff; }
.drop-zone.drag-over { border-color: #667eea; border-style: solid; }

.actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 25px;
}
```

---

### FILE: `frontend/src/App.vue`

```vue
<template>
  <div class="container">
    <h1>📚 Pharmacy Exam Prep</h1>
    <p class="subtitle">Phase 1: PDF to Structured Markdown</p>
    
    <FileUpload v-if="step === 'upload'" @uploaded="handleUpload" />
    <ProcessingStatus v-if="step === 'process'" :fileId="fileId" @complete="step = 'result'" />
    <ResultViewer v-if="step === 'result'" :fileId="fileId" @restart="step = 'upload'" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import FileUpload from './components/FileUpload.vue'
import ProcessingStatus from './components/ProcessingStatus.vue'
import ResultViewer from './components/ResultViewer.vue'

const step = ref<'upload' | 'process' | 'result'>('upload')
const fileId = ref('')

function handleUpload(id: string) {
  fileId.value = id
  step.value = 'process'
}
</script>
```

---

### FILE: `frontend/src/components/FileUpload.vue`

```vue
<template>
  <div>
    <div class="drop-zone" :class="{ 'drag-over': isDragging }" @drop.prevent="handleDrop" @dragover.prevent="isDragging = true" @dragleave="isDragging = false" @click="$refs.fileInput.click()">
      <input ref="fileInput" type="file" accept=".pdf" @change="handleSelect" style="display: none" />
      <div v-if="!file">
        <div style="font-size: 64px; margin-bottom: 20px;">📄</div>
        <h3>Drop PDF or click to browse</h3>
        <p>Max 50MB</p>
      </div>
      <div v-else>
        <div style="font-size: 48px;">✓</div>
        <h3>{{ file.name }}</h3>
        <p>{{ formatSize(file.size) }}</p>
      </div>
    </div>
    
    <div class="actions">
      <button v-if="!file" @click="$refs.fileInput.click()">Choose File</button>
      <template v-else>
        <button @click="clear" style="background: #999;">Clear</button>
        <button @click="upload" :disabled="uploading">{{ uploading ? 'Uploading...' : 'Process' }}</button>
      </template>
    </div>
    
    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'

const emit = defineEmits<{ (e: 'uploaded', id: string): void }>()

const fileInput = ref<HTMLInputElement>()
const file = ref<File | null>(null)
const isDragging = ref(false)
const uploading = ref(false)
const error = ref('')

function handleSelect(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files?.[0]) file.value = target.files[0]
}

function handleDrop(e: DragEvent) {
  isDragging.value = false
  if (e.dataTransfer?.files?.[0]?.type === 'application/pdf') {
    file.value = e.dataTransfer.files[0]
  }
}

function clear() { file.value = null }

async function upload() {
  if (!file.value) return
  uploading.value = true
  error.value = ''
  
  const formData = new FormData()
  formData.append('file', file.value)
  
  try {
    const res = await axios.post('/api/upload', formData)
    emit('uploaded', res.data.file_id)
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Upload failed'
  } finally {
    uploading.value = false
  }
}

function formatSize(bytes: number) {
  const k = 1024
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ['B', 'KB', 'MB'][i]
}
</script>
```

---

### FILE: `frontend/src/components/ProcessingStatus.vue`

```vue
<template>
  <div style="text-align: center; padding: 40px;">
    <div style="font-size: 64px; animation: spin 2s linear infinite;">⚙️</div>
    <h2>Processing...</h2>
    
    <div class="progress-bar">
      <div class="progress-fill" :style="{ width: progress + '%' }">{{ progress }}%</div>
    </div>
    
    <p style="color: #666; font-size: 1.1em; margin-top: 20px;">{{ message }}</p>
    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps<{ fileId: string }>()
const emit = defineEmits<{ (e: 'complete'): void }>()

const progress = ref(0)
const message = ref('Starting...')
const error = ref('')
let eventSource: EventSource | null = null

onMounted(() => {
  eventSource = new EventSource(`/api/process/${props.fileId}`)
  eventSource.onmessage = (e) => {
    const data = JSON.parse(e.data)
    if (data.error) {
      error.value = data.error
      eventSource?.close()
    } else {
      progress.value = data.progress || 0
      message.value = data.message || ''
      if (data.progress === 100) {
        setTimeout(() => { emit('complete'); eventSource?.close() }, 500)
      }
    }
  }
})

onUnmounted(() => eventSource?.close())
</script>

<style scoped>
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
</style>
```

---

### FILE: `frontend/src/components/ResultViewer.vue`

```vue
<template>
  <div style="text-align: center; padding: 40px;">
    <div style="font-size: 64px;">✅</div>
    <h2 style="color: #27ae60; margin: 20px 0;">Complete!</h2>
    
    <div style="background: #d4edda; border: 2px solid #28a745; border-radius: 12px; padding: 30px; margin: 30px 0;">
      <p><strong>Your files are ready!</strong></p>
      <p>Markdown + Analysis JSON generated</p>
    </div>
    
    <div class="actions">
      <button @click="download('markdown')" style="background: #27ae60;">Download Markdown</button>
      <button @click="download('analysis')" style="background: #3498db;">Download JSON</button>
    </div>
    
    <div class="actions" style="margin-top: 30px;">
      <button @click="emit('restart')" style="background: #999;">Process Another</button>
    </div>
    
    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'

const props = defineProps<{ fileId: string }>()
const emit = defineEmits<{ (e: 'restart'): void }>()

const error = ref('')

async function download(type: string) {
  try {
    const res = await axios.get(`/api/download/${props.fileId}/${type}`, { responseType: 'blob' })
    const url = URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = `pharmacy_${props.fileId}.${type === 'markdown' ? 'md' : 'json'}`
    link.click()
    URL.revokeObjectURL(url)
  } catch (err: any) {
    error.value = 'Download failed'
  }
}
</script>
```

---

### FILE: `.replit`

```toml
run = "bash start.sh"
entrypoint = "backend/app.py"

[nix]
channel = "stable-23_11"

[deployment]
run = ["bash", "start.sh"]
```

---

### FILE: `replit.nix`

```nix
{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.nodejs_20
    pkgs.mupdf
  ];
}
```

---

### FILE: `start.sh`

```bash
#!/bin/bash
set -e

echo "Installing Python dependencies..."
cd backend
pip install -r requirements.txt

echo "Installing Node dependencies..."
cd ../frontend
npm install

echo "Building frontend..."
npm run build

echo "Copying frontend build..."
mkdir -p ../backend/static
cp -r dist/* ../backend/static/

echo "Starting server..."
cd ../backend
python app.py
```

---

### FILE: `README.md`

```markdown
# Pharmacy Exam Prep - Phase 1

## Quick Start

1. Get API key: https://console.anthropic.com
2. Add to Replit Secrets: `ANTHROPIC_API_KEY`
3. Click Run

## Testing

1. Upload a PDF
2. Wait for processing (2-5 min)
3. Download markdown + JSON files

## Troubleshooting

- **API Error**: Check ANTHROPIC_API_KEY in Secrets
- **Upload Fails**: Check file is PDF < 50MB
- **Build Error**: Click "Shell" and run `bash start.sh`
```

---

## 🚀 DEPLOYMENT STEPS (15 MINUTES)

### Step 1: Get Anthropic API Key (3 min)

1. Visit: https://console.anthropic.com
2. Sign up → Get $5 free credit
3. Go to: **Settings → API Keys**
4. Create key → Copy it (starts with `sk-ant-api03-...`)

### Step 2: Create Replit Project (2 min)

1. Go to: https://replit.com
2. Click **"+ Create Repl"**
3. Choose **Python** template
4. Name: `pharmacy-exam-prep`
5. Click **Create Repl**

### Step 3: Add Files (5 min)

**Option A: Manual Copy (Recommended)**
1. In Replit, click **"+ Add file"** or **"+ Add folder"**
2. Create the folder structure shown above
3. Copy each file's content from this document into Replit
4. Make sure `start.sh` is executable (it usually is by default)

**Option B: Git Clone (If you have the repo)**
1. In Replit Shell: `git clone <your-repo-url> .`

### Step 4: Configure API Key (1 min)

1. In Replit sidebar, click **🔒 Secrets** (lock icon)
2. Click **"+ New Secret"**
3. Key: `ANTHROPIC_API_KEY`
4. Value: Paste your API key from Step 1
5. Click **Add secret**

### Step 5: Deploy (2 min)

1. Click **▶️ Run** button
2. Wait for:
   - Python packages install (~1 min)
   - Node packages install (~30 sec)
   - Frontend build (~30 sec)
   - Server start
3. Click **"Open in new tab"** when ready

### Step 6: Test (2 min)

1. Upload a test PDF (even a small one)
2. Watch processing status
3. Download markdown file
4. Verify content looks good

---

## ✅ SUCCESS CRITERIA

You know it's working when:

- [ ] Health check shows: `{"status": "healthy", "claude_configured": true}`
- [ ] Upload accepts PDF files
- [ ] Processing shows real-time progress
- [ ] Markdown file downloads with formatted content
- [ ] JSON file downloads with analysis data

---

## ⚡ TROUBLESHOOTING

### "Module not found" error
**Fix**: Run in Shell: `cd backend && pip install -r requirements.txt`

### "API key not configured"
**Fix**: Check Secrets tab has `ANTHROPIC_API_KEY` (exact spelling)

### "Frontend not loading"
**Fix**: 
```bash
cd frontend
npm run build
mkdir -p ../backend/static
cp -r dist/* ../backend/static/
```

### "Port already in use"
**Fix**: Stop and restart the Repl

### Processing hangs
**Fix**: Check browser console (F12) for errors. Usually network issue.

---

## 📊 EXPECTED PROCESSING TIME

- 10-page PDF: ~30 seconds
- 50-page PDF: ~2 minutes
- 100-page PDF: ~4 minutes

---

## 💰 COST ESTIMATE

With $5 free credit:
- 100-page PDF: ~$1
- **Total: 5 PDFs before needing to add payment**

---

## 🎯 PHASE 2 PREVIEW

After Phase 1 is complete, the JSON file will have everything needed for:
- Question generation
- Quiz interface
- Progress tracking
- Spaced repetition

---

**Ready to deploy? Copy this entire file and start implementing!** 🚀
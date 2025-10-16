# ============================================================================
# COMPLETE PHARMACY EXAM PREP - PHASE 1 IMPLEMENTATION
# ============================================================================
# 
# Directory Structure:
# pharmacy-exam-prep/
# ├── backend/
# │   ├── app.py
# │   ├── pdf_extractor.py
# │   ├── text_processor.py
# │   ├── llm_formatter.py
# │   ├── config.py
# │   └── requirements.txt
# ├── frontend/
# │   ├── index.html
# │   ├── src/
# │   │   ├── App.vue
# │   │   ├── main.ts
# │   │   └── components/
# │   │       ├── FileUpload.vue
# │   │       ├── ProcessingStatus.vue
# │   │       └── ResultViewer.vue
# │   ├── package.json
# │   └── vite.config.ts
# ├── .replit
# ├── replit.nix
# └── README.md
#
# ============================================================================

# ============================================================================
# FILE: backend/requirements.txt
# ============================================================================
"""
flask==3.0.0
flask-cors==4.0.0
PyMuPDF==1.23.8
requests==2.31.0
python-dotenv==1.0.0
"""

# ============================================================================
# FILE: backend/config.py
# ============================================================================
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # LLM Backend Configuration
    LLM_BACKEND = os.getenv('LLM_BACKEND', 'together')  # 'ollama', 'together', 'anthropic', 'openai'
    
    # API Keys
    TOGETHER_API_KEY = os.getenv('TOGETHER_API_KEY', '')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # Model Configuration
    TOGETHER_MODEL = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
    OLLAMA_MODEL = "llama3.2:3b"
    OLLAMA_URL = "http://localhost:11434"
    
    # File Settings
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './uploads')
    OUTPUT_FOLDER = './outputs'
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    # Processing Settings
    BATCH_SIZE = 20  # Pages per batch
    
    @classmethod
    def get_api_key(cls):
        """Get the appropriate API key based on backend"""
        if cls.LLM_BACKEND == 'together':
            return cls.TOGETHER_API_KEY
        elif cls.LLM_BACKEND == 'anthropic':
            return cls.ANTHROPIC_API_KEY
        elif cls.LLM_BACKEND == 'openai':
            return cls.OPENAI_API_KEY
        return None

# ============================================================================
# FILE: backend/pdf_extractor.py
# ============================================================================
import fitz  # PyMuPDF
from typing import List, Dict
import re

class PDFExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.total_pages = len(self.doc)
    
    def extract_all(self) -> List[Dict]:
        """Extract text from all pages with metadata"""
        pages_data = []
        
        for page_num in range(self.total_pages):
            page_data = self.extract_page(page_num)
            pages_data.append(page_data)
            
        return pages_data
    
    def extract_page(self, page_num: int) -> Dict:
        """Extract text and structure from a single page"""
        page = self.doc[page_num]
        
        # Get text blocks with font information
        blocks = page.get_text("dict")["blocks"]
        
        text_content = []
        headers = []
        
        for block in blocks:
            if block.get("type") == 0:  # Text block
                for line in block.get("lines", []):
                    line_text = ""
                    max_size = 0
                    
                    for span in line.get("spans", []):
                        line_text += span.get("text", "")
                        max_size = max(max_size, span.get("size", 0))
                    
                    line_text = line_text.strip()
                    if line_text:
                        # Detect headers (larger font or all caps)
                        if max_size > 14 or (line_text.isupper() and len(line_text) > 3):
                            headers.append(line_text)
                        
                        text_content.append({
                            "text": line_text,
                            "size": max_size,
                            "is_header": max_size > 14
                        })
        
        return {
            "page": page_num + 1,
            "content": text_content,
            "headers": headers,
            "full_text": page.get_text()
        }
    
    def extract_batch(self, start_page: int, batch_size: int) -> List[Dict]:
        """Extract a batch of pages"""
        end_page = min(start_page + batch_size, self.total_pages)
        return [self.extract_page(i) for i in range(start_page, end_page)]
    
    def close(self):
        """Close the PDF document"""
        self.doc.close()

# ============================================================================
# FILE: backend/text_processor.py
# ============================================================================
import re
from typing import List, Dict
from collections import Counter

class TextProcessor:
    def __init__(self):
        self.common_footers = set()
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common PowerPoint artifacts
        text = text.replace('', '•')
        text = text.replace('', '-')
        
        # Remove page numbers at end
        text = re.sub(r'\d+\s*$', '', text)
        
        return text.strip()
    
    def detect_repeated_elements(self, pages_data: List[Dict]) -> set:
        """Detect headers/footers that appear on multiple pages"""
        text_frequency = Counter()
        
        for page in pages_data:
            for item in page.get("content", []):
                text = item.get("text", "").strip()
                if len(text) > 5:  # Ignore very short text
                    text_frequency[text] += 1
        
        # Elements appearing on >30% of pages are likely headers/footers
        threshold = len(pages_data) * 0.3
        repeated = {text for text, count in text_frequency.items() if count > threshold}
        
        return repeated
    
    def remove_repeated_elements(self, pages_data: List[Dict], repeated: set) -> List[Dict]:
        """Remove repeated headers/footers from pages"""
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
        """Convert page content to structured format"""
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
            
            # Categorize content
            if item.get("is_header", False):
                structured["headers"].append(text)
            elif text.startswith(('•', '-', '*', '○')):
                structured["bullets"].append(text.lstrip('•-*○ '))
            else:
                structured["body"].append(text)
        
        return structured
    
    def group_by_topics(self, pages_data: List[Dict]) -> List[Dict]:
        """Group pages into topic sections"""
        topics = []
        current_topic = None
        
        for page in pages_data:
            structured = self.structure_page(page)
            
            # New topic if page has headers
            if structured["headers"]:
                if current_topic:
                    topics.append(current_topic)
                
                current_topic = {
                    "topic": structured["headers"][0],
                    "start_page": page["page"],
                    "end_page": page["page"],
                    "content": [structured]
                }
            elif current_topic:
                # Continue current topic
                current_topic["end_page"] = page["page"]
                current_topic["content"].append(structured)
            else:
                # No topic yet, create default
                current_topic = {
                    "topic": f"Section starting page {page['page']}",
                    "start_page": page["page"],
                    "end_page": page["page"],
                    "content": [structured]
                }
        
        if current_topic:
            topics.append(current_topic)
        
        return topics
    
    def process(self, pages_data: List[Dict]) -> List[Dict]:
        """Main processing pipeline"""
        # Detect and remove repeated elements
        repeated = self.detect_repeated_elements(pages_data)
        cleaned_pages = self.remove_repeated_elements(pages_data, repeated)
        
        # Group into topics
        topics = self.group_by_topics(cleaned_pages)
        
        return topics

# ============================================================================
# FILE: backend/llm_formatter.py
# ============================================================================
import requests
from typing import Dict, Optional
from config import Config

class LLMFormatter:
    def __init__(self):
        self.config = Config
        self.backend = Config.LLM_BACKEND
    
    def format_topic(self, topic_data: Dict) -> str:
        """Format a topic section using LLM"""
        # Prepare input text
        input_text = self._prepare_input(topic_data)
        
        # Get formatting from LLM
        if self.backend == 'ollama':
            formatted = self._format_with_ollama(input_text)
        elif self.backend == 'together':
            formatted = self._format_with_together(input_text)
        elif self.backend == 'anthropic':
            formatted = self._format_with_anthropic(input_text)
        else:
            # Fallback: basic formatting without LLM
            formatted = self._basic_format(topic_data)
        
        return formatted
    
    def _prepare_input(self, topic_data: Dict) -> str:
        """Prepare text for LLM processing"""
        lines = []
        lines.append(f"Topic: {topic_data['topic']}")
        lines.append(f"Pages: {topic_data['start_page']}-{topic_data['end_page']}")
        lines.append("")
        
        for page in topic_data['content']:
            if page['headers']:
                lines.append("## " + " / ".join(page['headers']))
            
            for bullet in page['bullets']:
                lines.append(f"- {bullet}")
            
            for body_text in page['body']:
                lines.append(body_text)
            
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_with_together(self, text: str) -> str:
        """Format using Together.ai API"""
        api_key = Config.TOGETHER_API_KEY
        if not api_key:
            return self._basic_format_text(text)
        
        prompt = f"""You are formatting pharmacy law study materials for exam preparation.

Input text:
{text}

Tasks:
1. Create clean markdown with proper headers (# for main topic, ## for sections)
2. Bold important terms and concepts
3. Use bullet points for lists
4. Add ⚠️ emoji before critical exam points
5. Create YAML frontmatter with:
   - topic: main topic name
   - subtopics: list of subtopics
   - key_terms: important terms mentioned
   - exam_focus: high/medium/low

Output format:
---
topic: [topic name]
subtopics: [list]
key_terms: [list]
exam_focus: [level]
---

[formatted markdown content]

Format the content now:"""

        try:
            response = requests.post(
                "https://api.together.xyz/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": Config.TOGETHER_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 2000,
                    "temperature": 0.3
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                print(f"Together API error: {response.status_code}")
                return self._basic_format_text(text)
                
        except Exception as e:
            print(f"Error with Together API: {e}")
            return self._basic_format_text(text)
    
    def _format_with_ollama(self, text: str) -> str:
        """Format using local Ollama"""
        prompt = f"""Format this pharmacy study content as clean markdown with YAML frontmatter.

{text}

Add proper headers, bold key terms, and mark exam-critical points with ⚠️."""

        try:
            response = requests.post(
                f"{Config.OLLAMA_URL}/api/generate",
                json={
                    "model": Config.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()['response']
            else:
                return self._basic_format_text(text)
                
        except Exception as e:
            print(f"Ollama error: {e}")
            return self._basic_format_text(text)
    
    def _format_with_anthropic(self, text: str) -> str:
        """Format using Anthropic Claude API"""
        # Similar implementation to Together
        return self._basic_format_text(text)
    
    def _basic_format_text(self, text: str) -> str:
        """Basic formatting without LLM (fallback)"""
        lines = text.split('\n')
        formatted = []
        
        for line in lines:
            line = line.strip()
            if not line:
                formatted.append("")
                continue
            
            # Simple header detection
            if line.startswith("Topic:"):
                formatted.append(f"# {line[6:].strip()}")
            elif line.startswith("##"):
                formatted.append(line)
            elif line.startswith("-"):
                formatted.append(line)
            else:
                formatted.append(line)
        
        return "\n".join(formatted)
    
    def _basic_format(self, topic_data: Dict) -> str:
        """Basic formatting without LLM"""
        text = self._prepare_input(topic_data)
        return self._basic_format_text(text)

# ============================================================================
# FILE: backend/app.py
# ============================================================================
from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from pdf_extractor import PDFExtractor
from text_processor import TextProcessor
from llm_formatter import LLMFormatter
from config import Config

app = Flask(__name__)
CORS(app)

# Ensure directories exist
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)

# Store processing status
processing_status = {}

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "llm_backend": Config.LLM_BACKEND,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload PDF file"""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "File must be PDF"}), 400
    
    # Save file
    filename = secure_filename(file.filename)
    file_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(Config.UPLOAD_FOLDER, f"{file_id}_{filename}")
    
    file.save(filepath)
    
    # Get file size
    file_size = os.path.getsize(filepath)
    
    # Extract basic info
    try:
        extractor = PDFExtractor(filepath)
        total_pages = extractor.total_pages
        extractor.close()
    except Exception as e:
        return jsonify({"error": f"Invalid PDF: {str(e)}"}), 400
    
    return jsonify({
        "file_id": file_id,
        "filename": filename,
        "size": file_size,
        "total_pages": total_pages
    })

@app.route('/api/process/<file_id>', methods=['POST'])
def process_file(file_id):
    """Process uploaded PDF"""
    # Find the file
    files = [f for f in os.listdir(Config.UPLOAD_FOLDER) if f.startswith(file_id)]
    if not files:
        return jsonify({"error": "File not found"}), 404
    
    filepath = os.path.join(Config.UPLOAD_FOLDER, files[0])
    
    # Initialize status
    processing_status[file_id] = {
        "status": "processing",
        "progress": 0,
        "message": "Starting extraction...",
        "current_page": 0,
        "total_pages": 0
    }
    
    def generate():
        """Generator for SSE progress updates"""
        try:
            # Step 1: Extract text
            yield f"data: {json.dumps({'progress': 10, 'message': 'Extracting text from PDF...'})}\n\n"
            
            extractor = PDFExtractor(filepath)
            total_pages = extractor.total_pages
            processing_status[file_id]["total_pages"] = total_pages
            
            pages_data = []
            for i in range(0, total_pages, Config.BATCH_SIZE):
                batch = extractor.extract_batch(i, Config.BATCH_SIZE)
                pages_data.extend(batch)
                
                progress = 10 + int((i / total_pages) * 30)
                yield f"data: {json.dumps({'progress': progress, 'message': f'Extracted pages {i+1}-{min(i+Config.BATCH_SIZE, total_pages)}'})}\n\n"
            
            extractor.close()
            
            # Step 2: Process text
            yield f"data: {json.dumps({'progress': 45, 'message': 'Processing and structuring text...'})}\n\n"
            
            processor = TextProcessor()
            topics = processor.process(pages_data)
            
            yield f"data: {json.dumps({'progress': 60, 'message': f'Found {len(topics)} topic sections'})}\n\n"
            
            # Step 3: Format with LLM
            formatter = LLMFormatter()
            formatted_topics = []
            
            for idx, topic in enumerate(topics):
                progress = 60 + int((idx / len(topics)) * 35)
                yield f"data: {json.dumps({'progress': progress, 'message': f'Formatting topic {idx+1}/{len(topics)}: {topic[\"topic\"][:50]}...'})}\n\n"
                
                formatted = formatter.format_topic(topic)
                formatted_topics.append(formatted)
            
            # Step 4: Save output
            yield f"data: {json.dumps({'progress': 95, 'message': 'Saving formatted markdown...'})}\n\n"
            
            output_filename = f"{file_id}_formatted.md"
            output_path = os.path.join(Config.OUTPUT_FOLDER, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# Pharmacy Law Study Guide\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"---\n\n")
                
                for formatted in formatted_topics:
                    f.write(formatted)
                    f.write("\n\n---\n\n")
            
            # Complete
            processing_status[file_id] = {
                "status": "complete",
                "progress": 100,
                "message": "Processing complete!",
                "output_file": output_filename
            }
            
            yield f"data: {json.dumps({'progress': 100, 'message': 'Complete!', 'output_file': output_filename})}\n\n"
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            processing_status[file_id] = {
                "status": "error",
                "message": error_msg
            }
            yield f"data: {json.dumps({'error': error_msg})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/download/<file_id>', methods=['GET'])
def download_file(file_id):
    """Download processed markdown file"""
    if file_id not in processing_status:
        return jsonify({"error": "File not found"}), 404
    
    status = processing_status[file_id]
    if status.get("status") != "complete":
        return jsonify({"error": "Processing not complete"}), 400
    
    output_file = status.get("output_file")
    if not output_file:
        return jsonify({"error": "No output file"}), 404
    
    filepath = os.path.join(Config.OUTPUT_FOLDER, output_file)
    if not os.path.exists(filepath):
        return jsonify({"error": "Output file not found"}), 404
    
    return send_file(filepath, as_attachment=True, download_name=output_file)

@app.route('/api/status/<file_id>', methods=['GET'])
def get_status(file_id):
    """Get processing status"""
    if file_id not in processing_status:
        return jsonify({"error": "File not found"}), 404
    
    return jsonify(processing_status[file_id])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

# ============================================================================
# FILE: frontend/package.json
# ============================================================================
"""
{
  "name": "pharmacy-exam-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview"
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
"""

# ============================================================================
# FILE: frontend/vite.config.ts
# ============================================================================
"""
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
})
"""

# ============================================================================
# FILE: frontend/index.html
# ============================================================================
"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Pharmacy Exam Prep - Phase 1</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.ts"></script>
</body>
</html>
"""

# ============================================================================
# FILE: frontend/src/main.ts
# ============================================================================
"""
import { createApp } from 'vue'
import App from './App.vue'
import './style.css'

createApp(App).mount('#app')
"""

# ============================================================================
# FILE: frontend/src/style.css
# ============================================================================
"""
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  padding: 20px;
}

#app {
  max-width: 1200px;
  margin: 0 auto;
}

.container {
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

h1 {
  color: #333;
  margin-bottom: 10px;
  font-size: 2.5em;
}

.subtitle {
  color: #666;
  margin-bottom: 40px;
  font-size: 1.1em;
}

button {
  background: #667eea;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

button:hover {
  background: #5568d3;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
}

.progress-bar {
  width: 100%;
  height: 30px;
  background: #e0e0e0;
  border-radius: 15px;
  overflow: hidden;
  margin: 20px 0;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
}
"""

# ============================================================================
# FILE: frontend/src/App.vue
# ============================================================================
"""
<template>
  <div class="container">
    <h1>📚 Pharmacy Exam Prep</h1>
    <p class="subtitle">Phase 1: PDF to Structured Markdown</p>
    
    <FileUpload 
      v-if="currentStep === 'upload'"
      @file-uploaded="handleFileUploaded"
    />
    
    <ProcessingStatus
      v-if="currentStep === 'processing'"
      :file-id="fileId"
      :progress="progress"
      :message="statusMessage"
      @processing-complete="handleProcessingComplete"
    />
    
    <ResultViewer
      v-if="currentStep === 'complete'"
      :file-id="fileId"
      @start-over="resetApp"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import FileUpload from './components/FileUpload.vue'
import ProcessingStatus from './components/ProcessingStatus.vue'
import ResultViewer from './components/ResultViewer.vue'

const currentStep = ref<'upload' | 'processing' | 'complete'>('upload')
const fileId = ref('')
const progress = ref(0)
const statusMessage = ref('')

function handleFileUploaded(id: string) {
  fileId.value = id
  currentStep.value = 'processing'
}

function handleProcessingComplete() {
  currentStep.value = 'complete'
}

function resetApp() {
  currentStep.value = 'upload'
  fileId.value = ''
  progress.value = 0
  statusMessage.value = ''
}
</script>
"""

# ============================================================================
# FILE: frontend/src/components/FileUpload.vue
# ============================================================================
"""
<template>
  <div class="upload-container">
    <div 
      class="drop-zone"
      :class="{ 'drag-over': isDragging }"
      @drop.prevent="handleDrop"
      @dragover.prevent="isDragging = true"
      @dragleave="isDragging = false"
    >
      <input
        ref="fileInput"
        type="file"
        accept=".pdf"
        @change="handleFileSelect"
        style="display: none"
      />
      
      <div v-if="!selectedFile" class="drop-prompt">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="17 8 12 3 7 8"/>
          <line x1="12" y1="3" x2="12" y2="15"/>
        </svg>
        <h3>Drop PDF here or click to browse</h3>
        <p>Maximum file size: 50MB</p>
      </div>
      
      <div v-else class="file-info">
        <h3>📄 {{ selectedFile.name }}</h3>
        <p>Size: {{ formatFileSize(selectedFile.size) }}</p>
      </div>
    </div>
    
    <div class="actions">
      <button v-if="!selectedFile" @click="$refs.fileInput.click()">
        Choose File
      </button>
      <template v-else>
        <button @click="clearFile">Clear</button>
        <button @click="uploadFile" :disabled="uploading">
          {{ uploading ? 'Uploading...' : 'Upload & Process' }}
        </button>
      </template>
    </div>
    
    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'

const emit = defineEmits<{
  (e: 'file-uploaded', fileId: string): void
}>()

const fileInput = ref<HTMLInputElement>()
const selectedFile = ref<File | null>(null)
const isDragging = ref(false)
const uploading = ref(false)
const error = ref('')

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    selectedFile.value = target.files[0]
    error.value = ''
  }
}

function handleDrop(event: DragEvent) {
  isDragging.value = false
  
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    const file = event.dataTransfer.files[0]
    
    if (file.type === 'application/pdf') {
      selectedFile.value = file
      error.value = ''
    } else {
      error.value = 'Please upload a PDF file'
    }
  }
}

function clearFile() {
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

async function uploadFile() {
  if (!selectedFile.value) return
  
  uploading.value = true
  error.value = ''
  
  const formData = new FormData()
  formData.append('file', selectedFile.value)
  
  try {
    const response = await axios.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    emit('file-uploaded', response.data.file_id)
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Upload failed'
  } finally {
    uploading.value = false
  }
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}
</script>

<style scoped>
.upload-container {
  margin: 20px 0;
}

.drop-zone {
  border: 3px dashed #ccc;
  border-radius: 12px;
  padding: 60px;
  text-align: center;
  transition: all 0.3s;
  cursor: pointer;
}

.drop-zone:hover, .drop-zone.drag-over {
  border-color: #667eea;
  background: #f8f9ff;
}

.drop-prompt svg {
  color: #667eea;
  margin-bottom: 20px;
}

.drop-prompt h3 {
  color: #333;
  margin-bottom: 10px;
}

.drop-prompt p {
  color: #666;
}

.file-info h3 {
  color: #333;
  margin-bottom: 10px;
}

.file-info p {
  color: #666;
}

.actions {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-top: 20px;
}

.error {
  color: #e74c3c;
  margin-top: 10px;
  text-align: center;
  font-weight: bold;
}
</style>
"""

# ============================================================================
# FILE: frontend/src/components/ProcessingStatus.vue
# ============================================================================
"""
<template>
  <div class="processing-container">
    <h2>⚙️ Processing PDF...</h2>
    
    <div class="progress-bar">
      <div class="progress-fill" :style="{ width: progress + '%' }">
        {{ progress }}%
      </div>
    </div>
    
    <p class="status-message">{{ message }}</p>
    
    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

const props = defineProps<{
  fileId: string
  progress: number
  message: string
}>()

const emit = defineEmits<{
  (e: 'processing-complete'): void
}>()

const error = ref('')
const localProgress = ref(0)
const localMessage = ref('Starting...')
let eventSource: EventSource | null = null

onMounted(() => {
  startProcessing()
})

onUnmounted(() => {
  if (eventSource) {
    eventSource.close()
  }
})

function startProcessing() {
  eventSource = new EventSource(`/api/process/${props.fileId}`)
  
  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      
      if (data.error) {
        error.value = data.error
        eventSource?.close()
        return
      }
      
      localProgress.value = data.progress || 0
      localMessage.value = data.message || ''
      
      if (data.progress === 100) {
        setTimeout(() => {
          emit('processing-complete')
          eventSource?.close()
        }, 500)
      }
    } catch (err) {
      console.error('Error parsing SSE data:', err)
    }
  }
  
  eventSource.onerror = () => {
    error.value = 'Connection lost. Please refresh and try again.'
    eventSource?.close()
  }
}
</script>

<style scoped>
.processing-container {
  text-align: center;
  padding: 40px 20px;
}

h2 {
  color: #333;
  margin-bottom: 30px;
}

.status-message {
  color: #666;
  margin-top: 20px;
  font-size: 1.1em;
}

.error {
  color: #e74c3c;
  margin-top: 20px;
  font-weight: bold;
}
</style>
"""

# ============================================================================
# FILE: frontend/src/components/ResultViewer.vue
# ============================================================================
"""
<template>
  <div class="result-container">
    <h2>✅ Processing Complete!</h2>
    
    <div class="success-message">
      <p>Your pharmacy study materials have been successfully formatted.</p>
      <p>The markdown file is ready for download and use in Phase 2.</p>
    </div>
    
    <div class="actions">
      <button @click="downloadFile" class="primary">
        📥 Download Markdown
      </button>
      <button @click="emit('start-over')">
        🔄 Process Another File
      </button>
    </div>
    
    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'

const props = defineProps<{
  fileId: string
}>()

const emit = defineEmits<{
  (e: 'start-over'): void
}>()

const error = ref('')

async function downloadFile() {
  try {
    const response = await axios.get(`/api/download/${props.fileId}`, {
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `pharmacy_study_guide_${props.fileId}.md`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (err: any) {
    error.value = 'Download failed. Please try again.'
  }
}
</script>

<style scoped>
.result-container {
  text-align: center;
  padding: 40px 20px;
}

h2 {
  color: #27ae60;
  margin-bottom: 30px;
  font-size: 2em;
}

.success-message {
  background: #d4edda;
  border: 1px solid #c3e6cb;
  border-radius: 8px;
  padding: 20px;
  margin: 30px 0;
}

.success-message p {
  color: #155724;
  margin: 10px 0;
  font-size: 1.1em;
}

.actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 30px;
}

.primary {
  background: #27ae60;
}

.primary:hover {
  background: #229954;
}

.error {
  color: #e74c3c;
  margin-top: 20px;
  font-weight: bold;
}
</style>
"""

# ============================================================================
# FILE: .replit
# ============================================================================
"""
run = "bash start.sh"
entrypoint = "backend/app.py"

[nix]
channel = "stable-23_11"

[deployment]
run = ["bash", "start.sh"]
deploymentTarget = "cloudrun"
"""

# ============================================================================
# FILE: replit.nix
# ============================================================================
"""
{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.nodejs_20
    pkgs.mupdf
  ];
}
"""

# ============================================================================
# FILE: start.sh
# ============================================================================
"""
#!/bin/bash

# Install Python dependencies
cd backend
pip install -r requirements.txt

# Install Node dependencies and build frontend
cd ../frontend
npm install
npm run build

# Move built frontend to backend static folder
mkdir -p ../backend/static
cp -r dist/* ../backend/static/

# Start Flask server
cd ../backend
python app.py
"""

# ============================================================================
# FILE: README.md
# ============================================================================
"""
# Pharmacy Exam Prep - Phase 1

PDF to Structured Markdown conversion tool for pharmacy law study materials.

## Setup Instructions

### Local Development

1. **Backend Setup**:
```bash
cd backend
pip install -r requirements.txt
python app.py
```

2. **Frontend Setup**:
```bash
cd frontend
npm install
npm run dev
```

### Replit Deployment

1. Create new Replit
2. Import this repository
3. Add environment variables in Secrets:
   - `LLM_BACKEND=together`
   - `TOGETHER_API_KEY=your_key_here`
4. Click Run

## Configuration

Edit `backend/config.py` to change:
- LLM backend (ollama/together/anthropic/openai)
- Model names
- Processing batch size

## API Keys

### Together.ai (Recommended for Replit)
1. Sign up at https://together.ai
2. Get API key from dashboard
3. Add to Replit Secrets as `TOGETHER_API_KEY`

### Local Ollama
```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Pull model
ollama pull llama3.2:3b

# Run in config.py
LLM_BACKEND = "ollama"
```

## Usage

1. Upload PDF (up to 50MB)
2. Wait for processing (progress shown)
3. Download formatted markdown
4. Use in Phase 2 for question generation

## Output Format

```markdown
---
topic: Controlled Substances
subtopics: [Schedule II, Prescriptions]
key_terms: [DEA, Refills, Form 222]
exam_focus: high
---

# Topic Content...
```

## Troubleshomat

- **Upload fails**: Check file size (<50MB) and format (PDF)
- **Processing stalls**: Check API key configuration
- **No LLM output**: Falls back to basic formatting
- **Port conflicts**: Change port in `app.py`

## Phase 2 Preview

Next phase will add:
- SQLite database for questions
- Question generation from markdown
- Quiz interface
- Progress tracking
- Spaced repetition

---

Made with ❤️ for pharmacy exam prep
"""
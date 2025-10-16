# ============================================================================
# PHARMACY EXAM PREP - PHASE 1 (ENHANCED WITH CLAUDE API)
# ============================================================================
# Optimized for Anthropic Claude with pharmacy-specific analysis
# ============================================================================

# ============================================================================
# FILE: backend/requirements.txt
# ============================================================================
"""
flask==3.0.0
flask-cors==4.0.0
PyMuPDF==1.23.8
anthropic==0.18.1
python-dotenv==1.0.0
"""

# ============================================================================
# FILE: backend/config.py
# ============================================================================
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Anthropic Configuration
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"
    
    # File Settings
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './uploads')
    OUTPUT_FOLDER = './outputs'
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    # Processing Settings
    BATCH_SIZE = 20  # Pages per batch
    ANALYSIS_BATCH_SIZE = 10  # Pages per LLM analysis call

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
        font_sizes = []
        
        for block in blocks:
            if block.get("type") == 0:  # Text block
                for line in block.get("lines", []):
                    line_text = ""
                    max_size = 0
                    
                    for span in line.get("spans", []):
                        line_text += span.get("text", "")
                        font_size = span.get("size", 0)
                        max_size = max(max_size, font_size)
                        font_sizes.append(font_size)
                    
                    line_text = line_text.strip()
                    if line_text:
                        # Detect headers (larger font or all caps)
                        is_header = max_size > 14 or (line_text.isupper() and len(line_text) > 3)
                        
                        if is_header:
                            headers.append(line_text)
                        
                        text_content.append({
                            "text": line_text,
                            "size": max_size,
                            "is_header": is_header,
                            "is_bold": max_size > 12
                        })
        
        # Calculate average font size for reference
        avg_font = sum(font_sizes) / len(font_sizes) if font_sizes else 11
        
        return {
            "page": page_num + 1,
            "content": text_content,
            "headers": headers,
            "full_text": page.get_text(),
            "avg_font_size": avg_font
        }
    
    def extract_batch(self, start_page: int, batch_size: int) -> List[Dict]:
        """Extract a batch of pages"""
        end_page = min(start_page + batch_size, self.total_pages)
        return [self.extract_page(i) for i in range(start_page, end_page)]
    
    def get_basic_info(self) -> Dict:
        """Get PDF metadata"""
        return {
            "total_pages": self.total_pages,
            "title": self.doc.metadata.get("title", "Unknown"),
            "author": self.doc.metadata.get("author", "Unknown")
        }
    
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
        text = text.replace('', "'")
        
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
            "body": [],
            "emphasis": []  # Bold or important text
        }
        
        for item in page_data.get("content", []):
            text = self.clean_text(item.get("text", ""))
            
            if not text:
                continue
            
            # Categorize content
            if item.get("is_header", False):
                structured["headers"].append(text)
            elif text.startswith(('•', '-', '*', '○', '▪')):
                structured["bullets"].append(text.lstrip('•-*○▪ '))
            elif item.get("is_bold", False):
                structured["emphasis"].append(text)
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
                if current_topic and current_topic["content"]:
                    topics.append(current_topic)
                
                current_topic = {
                    "topic": structured["headers"][0],
                    "start_page": page["page"],
                    "end_page": page["page"],
                    "content": [structured],
                    "all_headers": structured["headers"]
                }
            elif current_topic:
                # Continue current topic
                current_topic["end_page"] = page["page"]
                current_topic["content"].append(structured)
                # Accumulate headers from continuation pages
                if structured["headers"]:
                    current_topic["all_headers"].extend(structured["headers"])
            else:
                # No topic yet, create default
                current_topic = {
                    "topic": f"Introduction (Page {page['page']})",
                    "start_page": page["page"],
                    "end_page": page["page"],
                    "content": [structured],
                    "all_headers": structured["headers"]
                }
        
        if current_topic and current_topic["content"]:
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
# FILE: backend/content_analyzer.py
# ============================================================================
from typing import Dict, List
from anthropic import Anthropic
from config import Config
import json

class PharmacyContentAnalyzer:
    """
    Analyzes pharmacy law content using Claude to extract metadata
    and prepare content for Phase 2 question generation
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.model = Config.ANTHROPIC_MODEL
    
    def analyze_topic(self, topic_data: Dict) -> Dict:
        """
        Analyze a topic section and extract rich metadata
        """
        content_text = self._prepare_content_for_analysis(topic_data)
        
        analysis_prompt = f"""You are analyzing pharmacy law study materials to prepare them for exam question generation.

Analyze this content and provide detailed metadata in JSON format.

Content to analyze:
{content_text}

Provide your analysis in this exact JSON structure:
{{
  "main_topic": "Brief main topic name",
  "subtopics": ["list", "of", "subtopics"],
  "content_type": "regulation|definition|procedure|case_study|calculation|mixed",
  "key_terms": [
    {{"term": "term name", "definition": "brief definition", "importance": "high|medium|low"}}
  ],
  "exam_critical_points": [
    {{"point": "critical fact", "category": "penalty|exception|requirement|time_limit|dosage"}}
  ],
  "relationships": [
    {{"subject": "drug/law", "relationship": "affects|requires|prohibits", "object": "another drug/law"}}
  ],
  "question_potential": {{
    "multiple_choice": "high|medium|low",
    "true_false": "high|medium|low", 
    "scenario_based": "high|medium|low",
    "calculation": "high|medium|low"
  }},
  "difficulty_level": "basic|intermediate|advanced",
  "regulatory_context": "DEA|FDA|State|Federal|Mixed",
  "numerical_data": [
    {{"type": "time_limit|dosage|penalty|count", "value": "the number", "context": "what it relates to"}}
  ]
}}

Only return valid JSON, no other text."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.1,
                messages=[
                    {"role": "user", "content": analysis_prompt}
                ]
            )
            
            analysis_text = response.content[0].text
            
            # Parse JSON from response
            # Handle cases where Claude might add markdown formatting
            if "```json" in analysis_text:
                analysis_text = analysis_text.split("```json")[1].split("```")[0]
            elif "```" in analysis_text:
                analysis_text = analysis_text.split("```")[1].split("```")[0]
            
            analysis = json.loads(analysis_text.strip())
            
            # Add page range
            analysis["pages"] = f"{topic_data['start_page']}-{topic_data['end_page']}"
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing topic: {e}")
            # Return basic fallback analysis
            return self._fallback_analysis(topic_data)
    
    def _prepare_content_for_analysis(self, topic_data: Dict) -> str:
        """Convert topic data into readable text for analysis"""
        lines = []
        lines.append(f"TOPIC: {topic_data['topic']}")
        lines.append(f"PAGES: {topic_data['start_page']}-{topic_data['end_page']}")
        lines.append("")
        
        for page in topic_data['content']:
            if page['headers']:
                lines.append("## " + " / ".join(page['headers']))
            
            if page['emphasis']:
                lines.append("**Key Points:**")
                for emp in page['emphasis']:
                    lines.append(f"  • {emp}")
            
            if page['bullets']:
                for bullet in page['bullets']:
                    lines.append(f"• {bullet}")
            
            for body_text in page['body']:
                lines.append(body_text)
            
            lines.append("")
        
        return "\n".join(lines)
    
    def _fallback_analysis(self, topic_data: Dict) -> Dict:
        """Basic analysis when API fails"""
        return {
            "main_topic": topic_data['topic'],
            "subtopics": topic_data.get('all_headers', [])[:5],
            "content_type": "mixed",
            "key_terms": [],
            "exam_critical_points": [],
            "relationships": [],
            "question_potential": {
                "multiple_choice": "medium",
                "true_false": "medium",
                "scenario_based": "low",
                "calculation": "low"
            },
            "difficulty_level": "intermediate",
            "regulatory_context": "Mixed",
            "numerical_data": [],
            "pages": f"{topic_data['start_page']}-{topic_data['end_page']}"
        }

# ============================================================================
# FILE: backend/llm_formatter.py
# ============================================================================
from typing import Dict
from anthropic import Anthropic
from config import Config

class ClaudeFormatter:
    """
    Uses Claude to format pharmacy content into clean, structured markdown
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.model = Config.ANTHROPIC_MODEL
    
    def format_topic(self, topic_data: Dict, analysis: Dict) -> str:
        """Format a topic section using Claude with analysis context"""
        
        content_text = self._prepare_input(topic_data)
        
        format_prompt = f"""You are formatting pharmacy law study materials into clean, well-structured markdown for exam preparation.

CONTENT TO FORMAT:
{content_text}

ANALYSIS CONTEXT:
- Main Topic: {analysis['main_topic']}
- Content Type: {analysis['content_type']}
- Difficulty: {analysis['difficulty_level']}
- Regulatory Context: {analysis['regulatory_context']}

FORMATTING INSTRUCTIONS:
1. Create YAML frontmatter with this exact structure:
---
topic: {analysis['main_topic']}
subtopics: {analysis['subtopics']}
content_type: {analysis['content_type']}
difficulty: {analysis['difficulty_level']}
regulatory_context: {analysis['regulatory_context']}
pages: {analysis['pages']}
exam_focus: {self._get_exam_focus(analysis)}
---

2. Format the body content with:
   - # for main topic heading
   - ## for major sections
   - ### for subsections
   - **Bold** for key terms and important concepts
   - Use bullet points (•) for lists
   - Add ⚠️ before critical exam points
   - Add 📋 before definitions
   - Add ⚖️ before legal requirements/regulations
   - Add 💊 before drug-specific information
   - Add 🔢 before numerical requirements (time limits, dosages, penalties)

3. Structure content logically:
   - Start with overview/definition
   - Main requirements/rules
   - Exceptions and special cases
   - Examples if present
   - Key takeaways for exam

4. Make it exam-focused - emphasize testable content

Generate clean, professional markdown now:"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": format_prompt}
                ]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            print(f"Error formatting with Claude: {e}")
            return self._basic_format(topic_data, analysis)
    
    def _prepare_input(self, topic_data: Dict) -> str:
        """Prepare text for formatting"""
        lines = []
        
        for page in topic_data['content']:
            if page['headers']:
                lines.append("HEADERS: " + " | ".join(page['headers']))
            
            if page['emphasis']:
                lines.append("IMPORTANT:")
                for emp in page['emphasis']:
                    lines.append(f"  {emp}")
            
            if page['bullets']:
                lines.append("BULLET POINTS:")
                for bullet in page['bullets']:
                    lines.append(f"  • {bullet}")
            
            if page['body']:
                lines.append("CONTENT:")
                for body_text in page['body']:
                    lines.append(f"  {body_text}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def _get_exam_focus(self, analysis: Dict) -> str:
        """Determine exam focus level from analysis"""
        critical_points = len(analysis.get('exam_critical_points', []))
        question_potential = analysis.get('question_potential', {})
        
        high_potential = sum(1 for v in question_potential.values() if v == 'high')
        
        if critical_points >= 3 or high_potential >= 2:
            return "high"
        elif critical_points >= 1 or high_potential >= 1:
            return "medium"
        else:
            return "low"
    
    def _basic_format(self, topic_data: Dict, analysis: Dict) -> str:
        """Fallback formatting without API"""
        lines = []
        
        # YAML frontmatter
        lines.append("---")
        lines.append(f"topic: {analysis['main_topic']}")
        lines.append(f"pages: {analysis['pages']}")
        lines.append(f"difficulty: {analysis['difficulty_level']}")
        lines.append("---")
        lines.append("")
        
        # Content
        lines.append(f"# {topic_data['topic']}")
        lines.append("")
        
        for page in topic_data['content']:
            if page['headers']:
                for header in page['headers']:
                    lines.append(f"## {header}")
                    lines.append("")
            
            if page['bullets']:
                for bullet in page['bullets']:
                    lines.append(f"• {bullet}")
                lines.append("")
            
            for body in page['body']:
                lines.append(body)
                lines.append("")
        
        return "\n".join(lines)

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
from content_analyzer import PharmacyContentAnalyzer
from llm_formatter import ClaudeFormatter
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
    has_api_key = bool(Config.ANTHROPIC_API_KEY)
    return jsonify({
        "status": "healthy",
        "claude_configured": has_api_key,
        "model": Config.ANTHROPIC_MODEL if has_api_key else "Not configured",
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
    """Process uploaded PDF with enhanced analysis"""
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
            yield f"data: {json.dumps({'progress': 5, 'message': 'Extracting text from PDF...'})}\n\n"
            
            extractor = PDFExtractor(filepath)
            total_pages = extractor.total_pages
            processing_status[file_id]["total_pages"] = total_pages
            
            pages_data = []
            for i in range(0, total_pages, Config.BATCH_SIZE):
                batch = extractor.extract_batch(i, Config.BATCH_SIZE)
                pages_data.extend(batch)
                
                progress = 5 + int((i / total_pages) * 20)
                yield f"data: {json.dumps({'progress': progress, 'message': f'Extracted pages {i+1}-{min(i+Config.BATCH_SIZE, total_pages)}/{total_pages}'})}\n\n"
            
            extractor.close()
            
            # Step 2: Process and structure text
            yield f"data: {json.dumps({'progress': 30, 'message': 'Processing and structuring content...'})}\n\n"
            
            processor = TextProcessor()
            topics = processor.process(pages_data)
            
            yield f"data: {json.dumps({'progress': 35, 'message': f'Identified {len(topics)} topic sections'})}\n\n"
            
            # Step 3: Analyze content with Claude
            yield f"data: {json.dumps({'progress': 40, 'message': 'Analyzing content with Claude AI...'})}\n\n"
            
            analyzer = PharmacyContentAnalyzer()
            analyzed_topics = []
            
            for idx, topic in enumerate(topics):
                progress = 40 + int((idx / len(topics)) * 25)
                yield f"data: {json.dumps({'progress': progress, 'message': f'Analyzing topic {idx+1}/{len(topics)}: {topic[\"topic\"][:40]}...'})}\n\n"
                
                analysis = analyzer.analyze_topic(topic)
                analyzed_topics.append({
                    'topic_data': topic,
                    'analysis': analysis
                })
            
            # Step 4: Format with Claude
            yield f"data: {json.dumps({'progress': 70, 'message': 'Formatting with Claude...'})}\n\n"
            
            formatter = ClaudeFormatter()
            formatted_sections = []
            analyses_for_json = []
            
            for idx, item in enumerate(analyzed_topics):
                progress = 70 + int((idx / len(analyzed_topics)) * 25)
                yield f"data: {json.dumps({'progress': progress, 'message': f'Formatting section {idx+1}/{len(analyzed_topics)}'})}\n\n"
                
                formatted = formatter.format_topic(item['topic_data'], item['analysis'])
                formatted_sections.append(formatted)
                analyses_for_json.append(item['analysis'])
            
            # Step 5: Save outputs
            yield f"data: {json.dumps({'progress': 95, 'message': 'Saving formatted content...'})}\n\n"
            
            output_filename = f"{file_id}_formatted.md"
            output_path = os.path.join(Config.OUTPUT_FOLDER, output_filename)
            
            analysis_filename = f"{file_id}_analysis.json"
            analysis_path = os.path.join(Config.OUTPUT_FOLDER, analysis_filename)
            
            # Save markdown
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# Pharmacy Law Study Guide\n\n")
                f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"**Source:** {files[0]}\n\n")
                f.write(f"**Total Pages:** {total_pages}\n\n")
                f.write(f"**Topics Analyzed:** {len(analyzed_topics)}\n\n")
                f.write(f"---\n\n")
                
                for formatted in formatted_sections:
                    f.write(formatted)
                    f.write("\n\n---\n\n")
            
            # Save analysis JSON for Phase 2
            with open(analysis_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "metadata": {
                        "generated": datetime.now().isoformat(),
                        "source_file": files[0],
                        "total_pages": total_pages,
                        "total_topics": len(analyzed_topics)
                    },
                    "topics": analyses_for_json
                }, f, indent=2)
            
            # Complete
            processing_status[file_id] = {
                "status": "complete",
                "progress": 100,
                "message": "Processing complete!",
                "output_file": output_filename,
                "analysis_file": analysis_filename
            }
            
            yield f"data: {json.dumps({'progress': 100, 'message': 'Complete! Ready for download.', 'output_file': output_filename, 'analysis_file': analysis_filename})}\n\n"
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"Processing error: {e}")
            import traceback
            traceback.print_exc()
            
            processing_status[file_id] = {
                "status": "error",
                "message": error_msg
            }
            yield f"data: {json.dumps({'error': error_msg})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/download/<file_id>/<file_type>', methods=['GET'])
def download_file(file_id, file_type):
    """Download processed file (markdown or analysis json)"""
    if file_id not in processing_status:
        return jsonify({"error": "File not found"}), 404
    
    status = processing_status[file_id]
    if status.get("status") != "complete":
        return jsonify({"error": "Processing not complete"}), 400
    
    if file_type == 'markdown':
        output_file = status.get("output_file")
    elif file_type == 'analysis':
        output_file = status.get("analysis_file")
    else:
        return jsonify({"error": "Invalid file type"}), 400
    
    if not output_file:
        return jsonify({"error": "File not found"}), 404
    
    filepath = os.path.join(Config.OUTPUT_FOLDER, output_file)
    if not os.path.exists(filepath):
        return jsonify({"error": "Output file not found on server"}), 404
    
    return send_file(filepath, as_attachment=True, download_name=output_file)

@app.route('/api/status/<file_id>', methods=['GET'])
def get_status(file_id):
    """Get processing status"""
    if file_id not in processing_status:
        return jsonify({"error": "File not found"}), 404
    
    return jsonify(processing_status[file_id])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# ============================================================================
# FILE: .env.example
# ============================================================================
"""
# Copy this to .env and fill in your API key
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
UPLOAD_FOLDER=./uploads
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

[env]
PYTHONUNBUFFERED = "1"
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
# 🎓 Pharmacy Exam Prep - Phase 1 (Enhanced with Claude)

Intelligent PDF to Structured Markdown conversion with AI-powered analysis for pharmacy law study materials.

## ✨ Features

- **Smart PDF Extraction**: Handles large files (40MB+, 100+ pages)
- **Intelligent Analysis**: Claude AI analyzes content for:
  - Topic classification
  - Key term extraction
  - Exam-critical point identification
  - Question generation potential
  - Regulatory context
- **Rich Metadata**: YAML frontmatter + JSON sidecar for Phase 2
- **Clean Formatting**: Professional markdown with emojis for visual clarity
- **Real-time Progress**: Live updates during processing

## 🚀 Quick Start (Replit)

### 1. Get Anthropic API Key

1. Go to: https://console.anthropic.com
2. Sign up (get $5 free credit - enough for several 100-page PDFs!)
3. Navigate to: Settings → API Keys
4. Create a new key
5. Copy the key (starts with `sk-ant-api03-...`)

### 2. Deploy on Replit

1. **Create new Repl** (Python template)
2. **Upload all files** from this project
3. **Add Secret** (in Replit sidebar):
   - Key: `ANTHROPIC_API_KEY`
   - Value: Your API key from step 1
4. **Click Run** ▶️

That's it! The app will:
- Install dependencies
- Build frontend
- Start server
- Open in a new tab

## 📁 Project Structure

```
pharmacy-exam-prep/
├── backend/
│   ├── app.py                    # Flask API server
│   ├── pdf_extractor.py          # PDF text extraction
│   ├── text_processor.py         # Text cleaning & structuring
│   ├── content_analyzer.py       # 🆕 Claude-powered analysis
│   ├── llm_formatter.py          # 🆕 Claude formatting
│   ├── config.py                 # Configuration
│   └── requirements.txt
├── frontend/                     # Vue 3 + TypeScript UI
├── uploads/                      # Temp PDF storage
├── outputs/                      # Generated files
│   ├── *_formatted.md           # Formatted markdown
│   └── *_analysis.json          # 🆕 Metadata for Phase 2
└── README.md
```

## 🔬 What Gets Analyzed

For each topic section, Claude extracts:

### Content Classification
- **Type**: Regulation, definition, procedure, case study, calculation
- **Difficulty**: Basic, intermediate, advanced
- **Regulatory Context**: DEA, FDA, State, Federal

### Exam Intelligence
- **Key Terms**: With definitions and importance level
- **Critical Points**: Categorized (penalty, exception, requirement, etc.)
- **Relationships**: How laws/drugs affect each other
- **Numerical Data**: Time limits, dosages, penalties

### Question Potential
Scores for each question type:
- Multiple choice
- True/False
- Scenario-based
- Calculation problems

## 📄 Output Format

### Markdown File
```markdown
---
topic: Controlled Substances - Schedule II
subtopics: [Prescriptions, Record Keeping, Ordering]
content_type: regulation
difficulty: intermediate
regulatory_context: DEA
pages: 23-27
exam_focus: high
---

# Controlled Substances - Schedule II

## Overview
📋 **Definition**: Schedule II drugs have high potential for abuse...

## Prescription Requirements
⚠️ **CRITICAL FOR EXAM**: No refills permitted for Schedule II drugs

💊 **Examples**:
• Morphine
• Oxycodone
• Fentanyl

⚖️ **Legal Requirements**:
• Written prescription required (with limited exceptions)
• Must include DEA number
• Valid for 6 months from issue date

🔢 **Emergency Supply**: 72-hour maximum, written Rx within 7 days

...
```

### Analysis JSON (Phase 2 Ready)
```json
{
  "metadata": {
    "generated": "2024-...",
    "total_pages": 100,
    "total_topics": 15
  },
  "topics": [
    {
      "main_topic": "Controlled Substances",
      "exam_critical_points": [
        {
          "point": "No refills for Schedule II",
          "category": "requirement"
        }
      ],
      "question_potential": {
        "multiple_choice": "high",
        "scenario_based": "high"
      },
      ...
    }
  ]
}
```

## 💰 Cost Estimate

**For a 100-page PDF:**
- Input tokens: ~150,000
- Output tokens: ~50,000
- **Cost: $0.50 - $1.00**
- Free tier credit ($5): **~5-10 PDFs**

## 🔧 Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
python app.py

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Set `ANTHROPIC_API_KEY` in `.env` file.

## 📊 Processing Pipeline

```
PDF Upload
    ↓
[PyMuPDF] Extract with structure detection
    ↓
[Text Processor] Clean & group by topics
    ↓
[Claude Analyzer] 🆕 Deep content analysis
    ↓
[Claude Formatter] 🆕 Create structured markdown
    ↓
Save: markdown.md + analysis.json
    ↓
Download both files
```

## 🎯 Phase 2 Preview

The `analysis.json` file is **ready for Phase 2**, which will:
- Generate quiz questions from analyzed content
- Use metadata to create appropriate question types
- Focus on exam-critical points
- Build SQLite database with questions
- Create interactive quiz interface
- Track progress and weak areas

## ⚠️ Troubleshooting

### "API key not configured"
- Check Replit Secrets has `ANTHROPIC_API_KEY` set
- Verify key starts with `sk-ant-api03-`

### "Processing stalled"
- Check `/api/health` endpoint
- Verify API key is valid
- Check browser console for errors

### "Upload fails"
- Max file size: 50MB (configurable in `config.py`)
- Ensure file is actual PDF (not image)

### "Out of API credits"
- Check usage: https://console.anthropic.com/settings/billing
- Add payment method or wait for free tier reset

## 📞 Support

For issues with:
- **Anthropic API**: https://support.anthropic.com
- **This code**: Check browser/server console logs

---

**Ready for Phase 2**: Once you've processed your PDF and downloaded both files, you're ready to build the exam question generator! 🎉
"""
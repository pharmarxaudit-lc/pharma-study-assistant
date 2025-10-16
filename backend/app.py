import json
import logging
import os
from datetime import datetime

from config import Config
from content_analyzer import PharmacyContentAnalyzer
from flask import Flask, Response, jsonify, request, send_file
from flask_cors import CORS
from llm_formatter import ClaudeFormatter
from pdf_extractor import PDFExtractor
from text_processor import TextProcessor
from werkzeug.utils import secure_filename

# Create necessary directories first
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('logs/backend.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)

processing_status = {}

def create_session_logger(file_id: str) -> logging.Logger:
    """Create a file-specific logger for tracing individual processing sessions."""
    # Create logger with unique name
    session_logger = logging.getLogger(f'session_{file_id}')
    session_logger.setLevel(logging.DEBUG)

    # Prevent propagation to root logger to avoid duplicate logs
    session_logger.propagate = False

    # Remove any existing handlers to avoid duplicates
    session_logger.handlers.clear()

    # Create file handler for this session
    log_file = os.path.join('logs', f'{file_id}.log')
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))

    # Also add console handler for visibility
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))

    session_logger.addHandler(file_handler)
    session_logger.addHandler(console_handler)

    return session_logger

logger.info("="*80)
logger.info("Pharmacy Exam Prep Application Starting")
logger.info(f"Upload folder: {Config.UPLOAD_FOLDER}")
logger.info(f"Output folder: {Config.OUTPUT_FOLDER}")
logger.info(f"Anthropic API Key configured: {bool(Config.ANTHROPIC_API_KEY)}")
logger.info("="*80)

@app.route('/')
def index():
    logger.debug("Serving index.html")
    return app.send_static_file('index.html')

@app.route('/api/health', methods=['GET'])
def health():
    logger.debug("Health check requested")
    health_data = {
        "status": "healthy",
        "claude_configured": bool(Config.ANTHROPIC_API_KEY),
        "timestamp": datetime.now().isoformat()
    }
    logger.info(f"Health check: {health_data}")
    return jsonify(health_data)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    logger.info("="*80)
    logger.info("File upload request received")

    if 'file' not in request.files:
        logger.error("No file in request")
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    logger.info(f"File received: {file.filename}")

    if file.filename == '' or not file.filename.lower().endswith('.pdf'):
        logger.error(f"Invalid file: {file.filename}")
        return jsonify({"error": "Invalid file"}), 400

    filename = secure_filename(file.filename)
    file_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(Config.UPLOAD_FOLDER, f"{file_id}_{filename}")

    logger.info(f"Saving file to: {filepath}")
    file.save(filepath)
    file_size = os.path.getsize(filepath)
    logger.info(f"File saved successfully. Size: {file_size} bytes")

    try:
        logger.info("Extracting PDF metadata...")
        extractor = PDFExtractor(filepath)
        total_pages = extractor.total_pages
        extractor.close()
        logger.info(f"PDF has {total_pages} pages")
    except Exception as e:
        logger.error(f"Failed to read PDF: {str(e)}", exc_info=True)
        return jsonify({"error": f"Invalid PDF: {str(e)}"}), 400

    response_data = {
        "file_id": file_id,
        "filename": filename,
        "size": file_size,
        "total_pages": total_pages
    }
    logger.info(f"Upload successful: {response_data}")
    logger.info("="*80)
    return jsonify(response_data)

@app.route('/api/process/<file_id>', methods=['POST'])
def process_file(file_id):
    logger.info("="*80)
    logger.info(f"Processing request for file_id: {file_id}")

    files = [f for f in os.listdir(Config.UPLOAD_FOLDER) if f.startswith(file_id)]
    if not files:
        logger.error(f"File not found for file_id: {file_id}")
        return jsonify({"error": "File not found"}), 404

    filepath = os.path.join(Config.UPLOAD_FOLDER, files[0])
    logger.info(f"Processing file: {filepath}")

    def generate():
        # Create session-specific logger
        session_logger = create_session_logger(file_id)
        session_logger.info("="*80)
        session_logger.info(f"Starting processing session for file_id: {file_id}")
        session_logger.info(f"File path: {filepath}")
        session_logger.info("="*80)

        try:
            # Create output directory structure
            output_dir = os.path.join(Config.OUTPUT_FOLDER, file_id)
            pages_raw_dir = os.path.join(output_dir, 'pages', 'raw')
            pages_cleaned_dir = os.path.join(output_dir, 'pages', 'cleaned')
            os.makedirs(pages_raw_dir, exist_ok=True)
            os.makedirs(pages_cleaned_dir, exist_ok=True)

            session_logger.info("Starting PDF extraction...")
            yield f"data: {json.dumps({'progress': 10, 'message': 'Extracting PDF...'})}\n\n"

            extractor = PDFExtractor(filepath)
            total_pages = extractor.total_pages
            session_logger.info(f"Extracting {total_pages} pages...")
            pages_data = extractor.extract_all()
            extractor.close()
            session_logger.info(f"Extracted {len(pages_data)} pages successfully")

            # Save raw pages immediately
            session_logger.info("Saving raw pages...")
            for page in pages_data:
                page_num = page.get('page', 1)  # Fixed: use 'page' key instead of 'page_num'
                page_file = os.path.join(pages_raw_dir, f"page_{page_num:03d}.md")
                with open(page_file, 'w', encoding='utf-8') as f:
                    f.write(f"# Page {page_num}\n\n")
                    for header in page.get('headers', []):
                        f.write(f"### {header}\n\n")
                    # Use the content structure from PDFExtractor
                    for content_item in page.get('content', []):
                        if isinstance(content_item, dict):
                            f.write(f"{content_item.get('text', '')}\n\n")
                        else:
                            f.write(f"{content_item}\n\n")

            yield f"data: {json.dumps({'progress': 30, 'message': 'Processing text...'})}\n\n"
            session_logger.info("Processing text...")

            processor = TextProcessor(logger=session_logger)
            topics = processor.process(pages_data)
            session_logger.info(f"Identified {len(topics)} topics")

            # Save cleaned pages immediately
            session_logger.info("Saving cleaned pages...")
            for page in pages_data:
                page_num = page.get('page', 1)  # Fixed: use 'page' key instead of 'page_num'
                page_file = os.path.join(pages_cleaned_dir, f"page_{page_num:03d}.md")
                with open(page_file, 'w', encoding='utf-8') as f:
                    f.write(f"# Page {page_num}\n\n")
                    for header in page.get('headers', []):
                        f.write(f"### {header}\n\n")
                    # Apply text cleaning to each content item
                    for content_item in page.get('content', []):
                        if isinstance(content_item, dict):
                            text = content_item.get('text', '')
                            if text:
                                cleaned_text = processor.clean_text(text)
                                f.write(f"{cleaned_text}\n\n")

            yield f"data: {json.dumps({'progress': 50, 'message': f'Analyzing {len(topics)} topics...'})}\n\n"

            # Initialize output files for incremental writing
            md_file = f"{file_id}_formatted.md"
            json_file = f"{file_id}_analysis.json"
            md_path = os.path.join(output_dir, md_file)
            json_path = os.path.join(output_dir, json_file)

            # Write markdown header
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write("# Pharmacy Law Study Guide\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n")

            analyzer = PharmacyContentAnalyzer(logger=session_logger)
            formatter = ClaudeFormatter(logger=session_logger)

            analyses = []

            for idx, topic in enumerate(topics):
                progress = 50 + int((idx / len(topics)) * 45)
                topic_name = topic.get('topic', 'Unknown')
                session_logger.info(f"Processing topic {idx+1}/{len(topics)}: {topic_name}")
                yield f"data: {json.dumps({'progress': progress, 'message': f'Processing {idx+1}/{len(topics)}: {topic_name[:30]}...'})}\n\n"

                session_logger.debug(f"Analyzing topic: {topic_name}")
                analysis = analyzer.analyze_topic(topic)
                session_logger.debug(f"Analysis complete for: {topic_name}")

                session_logger.debug(f"Formatting topic: {topic_name}")
                formatted = formatter.format_topic(topic, analysis)
                session_logger.debug(f"Formatting complete for: {topic_name}")

                # Write this topic immediately to markdown file
                with open(md_path, 'a', encoding='utf-8') as f:
                    f.write(formatted + "\n\n---\n\n")
                session_logger.info(f"Topic {idx+1} written to {md_path}")

                analyses.append(analysis)

            yield f"data: {json.dumps({'progress': 95, 'message': 'Finalizing files...'})}\n\n"
            session_logger.info("Writing final analysis JSON...")

            # Write final JSON analysis
            with open(json_path, 'w') as f:
                json.dump({
                    "metadata": {
                        "generated": datetime.now().isoformat(),
                        "total_topics": len(analyses),
                        "file_id": file_id
                    },
                    "topics": analyses
                }, f, indent=2)

            processing_status[file_id] = {
                "status": "complete",
                "output_file": md_file,
                "analysis_file": json_file
            }

            session_logger.info(f"Processing complete for file_id: {file_id}")
            session_logger.info("="*80)
            yield f"data: {json.dumps({'progress': 100, 'message': 'Complete!', 'output_file': md_file})}\n\n"

        except Exception as e:
            session_logger.error(f"Error during processing: {str(e)}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/download/<file_id>/<file_type>', methods=['GET'])
def download_file(file_id, file_type):
    logger.info(f"Download request: file_id={file_id}, type={file_type}")

    if file_id not in processing_status:
        logger.error(f"File not found in processing status: {file_id}")
        return jsonify({"error": "File not found"}), 404

    status = processing_status[file_id]
    output_file = status.get("output_file" if file_type == "markdown" else "analysis_file")

    if not output_file:
        logger.error(f"Output file not ready for {file_id}")
        return jsonify({"error": "File not ready"}), 400

    filepath = os.path.join(Config.OUTPUT_FOLDER, output_file)
    logger.info(f"Sending file: {filepath}")

    if not os.path.exists(filepath):
        logger.error(f"File does not exist: {filepath}")
        return jsonify({"error": "File not found on disk"}), 404

    return send_file(filepath, as_attachment=True, download_name=output_file)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'
    logger.info(f"Starting Flask server on port {port} (debug={debug_mode})")
    app.run(host='0.0.0.0', port=port, debug=debug_mode, use_reloader=debug_mode)

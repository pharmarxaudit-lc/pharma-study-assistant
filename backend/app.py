from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
import logging
from datetime import datetime
from pdf_extractor import PDFExtractor
from text_processor import TextProcessor
from content_analyzer import PharmacyContentAnalyzer
from llm_formatter import ClaudeFormatter
from config import Config

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
        try:
            logger.info("Starting PDF extraction...")
            yield f"data: {json.dumps({'progress': 10, 'message': 'Extracting PDF...'})}\n\n"

            extractor = PDFExtractor(filepath)
            total_pages = extractor.total_pages
            logger.info(f"Extracting {total_pages} pages...")
            pages_data = extractor.extract_all()
            extractor.close()
            logger.info(f"Extracted {len(pages_data)} pages successfully")

            yield f"data: {json.dumps({'progress': 30, 'message': 'Processing text...'})}\n\n"
            logger.info("Processing text...")

            processor = TextProcessor()
            topics = processor.process(pages_data)
            logger.info(f"Identified {len(topics)} topics")

            yield f"data: {json.dumps({'progress': 50, 'message': f'Analyzing {len(topics)} topics...'})}\n\n"

            analyzer = PharmacyContentAnalyzer()
            formatter = ClaudeFormatter()

            formatted_sections = []
            analyses = []

            for idx, topic in enumerate(topics):
                progress = 50 + int((idx / len(topics)) * 45)
                topic_name = topic.get('topic', 'Unknown')
                logger.info(f"Processing topic {idx+1}/{len(topics)}: {topic_name}")
                yield f"data: {json.dumps({'progress': progress, 'message': f'Processing {idx+1}/{len(topics)}: {topic_name[:30]}...'})}\n\n"

                logger.debug(f"Analyzing topic: {topic_name}")
                analysis = analyzer.analyze_topic(topic)
                logger.debug(f"Analysis complete for: {topic_name}")

                logger.debug(f"Formatting topic: {topic_name}")
                formatted = formatter.format_topic(topic, analysis)
                logger.debug(f"Formatting complete for: {topic_name}")

                formatted_sections.append(formatted)
                analyses.append(analysis)

            yield f"data: {json.dumps({'progress': 95, 'message': 'Saving files...'})}\n\n"
            logger.info("Saving output files...")

            md_file = f"{file_id}_formatted.md"
            json_file = f"{file_id}_analysis.json"

            md_path = os.path.join(Config.OUTPUT_FOLDER, md_file)
            json_path = os.path.join(Config.OUTPUT_FOLDER, json_file)

            logger.info(f"Writing markdown to: {md_path}")
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(f"# Pharmacy Law Study Guide\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n")
                for section in formatted_sections:
                    f.write(section + "\n\n---\n\n")

            logger.info(f"Writing analysis JSON to: {json_path}")
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

            logger.info(f"Processing complete for file_id: {file_id}")
            logger.info("="*80)
            yield f"data: {json.dumps({'progress': 100, 'message': 'Complete!', 'output_file': md_file})}\n\n"

        except Exception as e:
            logger.error(f"Error during processing: {str(e)}", exc_info=True)
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

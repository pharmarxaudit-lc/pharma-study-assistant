import json
import logging
import os
from datetime import datetime

from config import Config
from content_analyzer import PharmacyContentAnalyzer
from database import get_database
from database_models import Document, Question, StudySession, UserAttempt
from flask import Flask, Response, jsonify, request, send_file
from flask_cors import CORS
from llm_formatter import ClaudeFormatter
from pdf_extractor import PDFExtractor
from sqlalchemy import func
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

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')
CORS(app)

os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)

processing_status = {}

# Initialize database connection
db = get_database(Config.DATABASE_PATH)

def parse_options(options_json: str) -> dict:
    """
    Parse options from database format to API format.
    Database stores: ["A. text", "B. text", "C. text", "D. text"]
    API expects: {"A": "text", "B": "text", "C": "text", "D": "text"}
    """
    try:
        options_data = json.loads(options_json)

        # If already a dict, return as-is
        if isinstance(options_data, dict):
            return options_data

        # If it's an array, parse it
        if isinstance(options_data, list):
            result = {}
            for option in options_data:
                # Extract letter and text from "A. Some text" format
                if isinstance(option, str) and len(option) > 2 and option[1] == '.':
                    letter = option[0]
                    text = option[2:].strip()
                    result[letter] = text
            return result

        return {}
    except Exception as e:
        logger.error(f"Error parsing options: {e}")
        return {}

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

# ============================================================================
# QUESTION ENDPOINTS
# ============================================================================

@app.route('/api/questions/<file_id>', methods=['GET'])
def get_questions(file_id):
    """
    Retrieve questions for a document with optional filtering.

    Query params:
    - topic: Filter by topic name
    - difficulty: Filter by difficulty (basic/intermediate/advanced)
    - type: Filter by question type (single_answer/choose_all)
    - limit: Number of results (default 50)
    - offset: Pagination offset (default 0)
    """
    logger.info(f"GET /api/questions/{file_id}")

    try:
        with db.session() as session:
            # Get document
            document = session.query(Document).filter_by(file_id=file_id).first()
            if not document:
                return jsonify({"error": "Document not found"}), 404

            # Build query with filters
            query = session.query(Question).filter_by(document_id=document.id)

            topic = request.args.get('topic')
            if topic:
                query = query.filter_by(topic_name=topic)

            difficulty = request.args.get('difficulty')
            if difficulty:
                query = query.filter_by(difficulty=difficulty)

            question_type = request.args.get('type')
            if question_type:
                query = query.filter_by(question_type=question_type)

            # Pagination
            limit = int(request.args.get('limit', 50))
            offset = int(request.args.get('offset', 0))

            total = query.count()
            questions = query.offset(offset).limit(limit).all()

            # Serialize questions
            questions_data = []
            for q in questions:
                questions_data.append({
                    'id': q.id,
                    'topic_id': q.topic_id,
                    'topic_name': q.topic_name,
                    'question_type': q.question_type,
                    'difficulty': q.difficulty,
                    'question_text': q.question_text,
                    'options': parse_options(q.options_json),
                    'correct_answer': q.correct_answer,
                    'explanation': q.explanation,
                    'key_terms': json.loads(q.key_terms_json) if q.key_terms_json else [],
                    'regulatory_context': q.regulatory_context,
                    'pages': q.pages,
                    'times_seen': q.times_seen,
                    'times_correct': q.times_correct,
                    'accuracy_rate': round((q.times_correct / q.times_seen * 100) if q.times_seen > 0 else 0, 1)
                })

            return jsonify({
                'total': total,
                'limit': limit,
                'offset': offset,
                'questions': questions_data
            })

    except Exception as e:
        logger.error(f"Error getting questions: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/questions/<file_id>/stats', methods=['GET'])
def get_question_stats(file_id):
    """Get statistics about questions for a document."""
    logger.info(f"GET /api/questions/{file_id}/stats")

    try:
        with db.session() as session:
            # Get document
            document = session.query(Document).filter_by(file_id=file_id).first()
            if not document:
                return jsonify({"error": "Document not found"}), 404

            # Total questions
            total = session.query(Question).filter_by(document_id=document.id).count()

            # By topic
            by_topic = session.query(
                Question.topic_name,
                func.count(Question.id).label('count')
            ).filter_by(document_id=document.id).group_by(Question.topic_name).all()

            # By difficulty
            by_difficulty = session.query(
                Question.difficulty,
                func.count(Question.id).label('count')
            ).filter_by(document_id=document.id).group_by(Question.difficulty).all()

            # By type
            by_type = session.query(
                Question.question_type,
                func.count(Question.id).label('count')
            ).filter_by(document_id=document.id).group_by(Question.question_type).all()

            return jsonify({
                'total': total,
                'by_topic': [{'topic': t[0], 'count': t[1]} for t in by_topic],
                'by_difficulty': [{'difficulty': d[0], 'count': d[1]} for d in by_difficulty],
                'by_type': [{'type': t[0], 'count': t[1]} for t in by_type]
            })

    except Exception as e:
        logger.error(f"Error getting question stats: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/questions/single/<int:question_id>', methods=['GET'])
def get_single_question(question_id):
    """Get a single question by ID."""
    logger.info(f"GET /api/questions/single/{question_id}")

    try:
        with db.session() as session:
            question = session.query(Question).filter_by(id=question_id).first()
            if not question:
                return jsonify({"error": "Question not found"}), 404

            return jsonify({
                'id': question.id,
                'document_id': question.document_id,
                'topic_id': question.topic_id,
                'topic_name': question.topic_name,
                'question_type': question.question_type,
                'difficulty': question.difficulty,
                'question_text': question.question_text,
                'options': parse_options(question.options_json),
                'correct_answer': question.correct_answer,
                'explanation': question.explanation,
                'key_terms': json.loads(question.key_terms_json) if question.key_terms_json else [],
                'regulatory_context': question.regulatory_context,
                'pages': question.pages,
                'times_seen': question.times_seen,
                'times_correct': question.times_correct
            })

    except Exception as e:
        logger.error(f"Error getting question: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# ============================================================================
# SESSION ENDPOINTS
# ============================================================================

@app.route('/api/sessions/start', methods=['POST'])
def start_session():
    """
    Start a new study session.

    Request body:
    {
        "file_id": "20251016_113156",
        "session_type": "study|practice|mock",
        "num_questions": 10,
        "topics": ["Topic 1", "Topic 2"] (optional, null = all topics),
        "difficulty": "basic|intermediate|advanced" (optional, null = all difficulties),
        "include_review": false (optional, prioritize questions with low accuracy)
    }

    Response:
    {
        "session_id": 123,
        "total_questions": 10,
        "first_question": {...}
    }
    """
    logger.info("POST /api/sessions/start")
    data = request.get_json()

    try:
        file_id = data.get('file_id')
        session_type = data.get('session_type', 'study')
        num_questions = data.get('num_questions', 10)
        topics = data.get('topics')  # None = all topics
        difficulty = data.get('difficulty')  # None = all difficulties
        include_review = data.get('include_review', False)
        pass_threshold = data.get('pass_threshold', 70)  # Default 70%

        with db.session() as session:
            # Get document
            document = session.query(Document).filter_by(file_id=file_id).first()
            if not document:
                return jsonify({"error": "Document not found"}), 404

            # Build question query
            query = session.query(Question).filter_by(document_id=document.id)

            if topics:
                query = query.filter(Question.topic_name.in_(topics))

            if difficulty:
                query = query.filter_by(difficulty=difficulty)

            # If include_review, prioritize questions with low accuracy
            if include_review:
                query = query.order_by(
                    (Question.times_correct * 1.0 / Question.times_seen).asc(),
                    func.random()
                )
            else:
                query = query.order_by(func.random())

            # Get questions
            questions = query.limit(num_questions).all()

            if not questions:
                return jsonify({"error": "No questions found matching criteria"}), 404

            # Create session
            new_session = StudySession(
                document_id=document.id,
                session_type=session_type,
                start_time=datetime.now(),
                total_questions=len(questions),
                correct_answers=0,
                score_percentage=0.0,
                pass_threshold=pass_threshold
            )
            session.add(new_session)
            session.flush()

            session_id = new_session.id

            # Store question IDs in session (we'll track them in memory for now)
            # In production, you might want to store this in a separate table
            processing_status[f'session_{session_id}'] = {
                'question_ids': [q.id for q in questions],
                'current_index': 0,
                'answers': {}
            }

            session.commit()

            # Return first question
            first_q = questions[0]
            return jsonify({
                'session_id': session_id,
                'total_questions': len(questions),
                'session_type': session_type,
                'pass_threshold': pass_threshold,
                'first_question': {
                    'id': first_q.id,
                    'question_number': 1,
                    'topic_name': first_q.topic_name,
                    'question_type': first_q.question_type,
                    'difficulty': first_q.difficulty,
                    'question_text': first_q.question_text,
                    'options': parse_options(first_q.options_json)
                }
            })

    except Exception as e:
        logger.error(f"Error starting session: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/sessions/<int:session_id>/answer', methods=['POST'])
def submit_answer(session_id):
    """
    Submit an answer for the current question.

    Request body:
    {
        "question_id": 123,
        "selected_answer": "A" or "A,B,C",
        "time_spent_seconds": 45
    }

    Response:
    {
        "is_correct": true,
        "correct_answer": "B",
        "explanation": "...",
        "key_terms": [...],
        "next_question": {...} or null if session complete
    }
    """
    logger.info(f"POST /api/sessions/{session_id}/answer")
    data = request.get_json()

    try:
        question_id = data.get('question_id')
        selected_answer = data.get('selected_answer')
        time_spent = data.get('time_spent_seconds', 0)

        with db.session() as db_session:
            # Get question
            question = db_session.query(Question).filter_by(id=question_id).first()
            if not question:
                return jsonify({"error": "Question not found"}), 404

            # Check answer
            is_correct = (selected_answer == question.correct_answer)

            # Record attempt
            attempt = UserAttempt(
                question_id=question_id,
                session_id=session_id,
                selected_answer=selected_answer,
                is_correct=is_correct,
                attempt_date=datetime.now(),
                time_spent_seconds=time_spent
            )
            db_session.add(attempt)

            # Update question statistics
            question.times_seen += 1
            if is_correct:
                question.times_correct += 1

            # Update session
            study_session = db_session.query(StudySession).filter_by(id=session_id).first()
            if is_correct:
                study_session.correct_answers += 1

            db_session.commit()

            # Get next question
            session_data = processing_status.get(f'session_{session_id}')
            if session_data:
                session_data['current_index'] += 1
                session_data['answers'][question_id] = {
                    'selected': selected_answer,
                    'correct': is_correct
                }

                question_ids = session_data['question_ids']
                current_index = session_data['current_index']

                next_question = None
                if current_index < len(question_ids):
                    next_q = db_session.query(Question).filter_by(
                        id=question_ids[current_index]
                    ).first()
                    if next_q:
                        next_question = {
                            'id': next_q.id,
                            'question_number': current_index + 1,
                            'topic_name': next_q.topic_name,
                            'question_type': next_q.question_type,
                            'difficulty': next_q.difficulty,
                            'question_text': next_q.question_text,
                            'options': parse_options(next_q.options_json)
                        }
            else:
                next_question = None

            return jsonify({
                'is_correct': is_correct,
                'correct_answer': question.correct_answer,
                'explanation': question.explanation,
                'key_terms': json.loads(question.key_terms_json) if question.key_terms_json else [],
                'next_question': next_question
            })

    except Exception as e:
        logger.error(f"Error submitting answer: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/sessions/<int:session_id>/results', methods=['GET'])
def get_session_results(session_id):
    """Get results for a completed session."""
    logger.info(f"GET /api/sessions/{session_id}/results")

    try:
        with db.session() as session:
            # Get session
            study_session = session.query(StudySession).filter_by(id=session_id).first()
            if not study_session:
                return jsonify({"error": "Session not found"}), 404

            # Mark as complete
            if not study_session.end_time:
                study_session.end_time = datetime.now()
                study_session.score_percentage = (
                    (study_session.correct_answers / study_session.total_questions * 100)
                    if study_session.total_questions > 0 else 0
                )
                session.commit()

            # Get all attempts for this session
            attempts = session.query(UserAttempt).filter_by(session_id=session_id).all()

            # Get questions with attempts
            attempts_data = []
            topic_breakdown = {}

            for attempt in attempts:
                question = session.query(Question).filter_by(id=attempt.question_id).first()
                if question:
                    attempts_data.append({
                        'question_id': question.id,
                        'topic_name': question.topic_name,
                        'difficulty': question.difficulty,
                        'question_text': question.question_text,
                        'options': parse_options(question.options_json),
                        'selected_answer': attempt.selected_answer,
                        'correct_answer': question.correct_answer,
                        'is_correct': attempt.is_correct,
                        'explanation': question.explanation,
                        'time_spent_seconds': attempt.time_spent_seconds
                    })

                    # Topic breakdown
                    if question.topic_name not in topic_breakdown:
                        topic_breakdown[question.topic_name] = {'correct': 0, 'total': 0}
                    topic_breakdown[question.topic_name]['total'] += 1
                    if attempt.is_correct:
                        topic_breakdown[question.topic_name]['correct'] += 1

            # Calculate timing
            duration_seconds = 0
            if study_session.end_time and study_session.start_time:
                # Parse datetime strings from SQLite
                end_dt = datetime.fromisoformat(study_session.end_time) if isinstance(study_session.end_time, str) else study_session.end_time
                start_dt = datetime.fromisoformat(study_session.start_time) if isinstance(study_session.start_time, str) else study_session.start_time
                duration_seconds = int((end_dt - start_dt).total_seconds())

            return jsonify({
                'session_id': session_id,
                'session_type': study_session.session_type,
                'score': study_session.correct_answers,
                'total': study_session.total_questions,
                'percentage': round(study_session.score_percentage, 1),
                'pass_threshold': study_session.pass_threshold,
                'duration_seconds': duration_seconds,
                'topic_breakdown': [
                    {
                        'topic': topic,
                        'correct': stats['correct'],
                        'total': stats['total'],
                        'percentage': round((stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0, 1)
                    }
                    for topic, stats in topic_breakdown.items()
                ],
                'attempts': attempts_data
            })

    except Exception as e:
        logger.error(f"Error getting session results: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/sessions/history', methods=['GET'])
def get_session_history():
    """Get all past sessions with optional filtering."""
    logger.info("GET /api/sessions/history")

    try:
        session_type = request.args.get('type')  # Filter by type
        limit = int(request.args.get('limit', 20))

        with db.session() as session:
            query = session.query(StudySession).filter(StudySession.end_time.isnot(None))

            if session_type:
                query = query.filter_by(session_type=session_type)

            query = query.order_by(StudySession.start_time.desc()).limit(limit)
            sessions = query.all()

            sessions_data = []
            for s in sessions:
                # Handle datetime fields - they may be strings or datetime objects from SQLite
                start_time = s.start_time
                if start_time and not isinstance(start_time, str):
                    start_time = start_time.isoformat()

                end_time = s.end_time
                if end_time and not isinstance(end_time, str):
                    end_time = end_time.isoformat()

                sessions_data.append({
                    'id': s.id,
                    'session_type': s.session_type,
                    'start_time': start_time,
                    'end_time': end_time,
                    'score': s.correct_answers,
                    'total': s.total_questions,
                    'percentage': round(s.score_percentage, 1),
                    'pass_threshold': s.pass_threshold
                })

            return jsonify({
                'sessions': sessions_data,
                'total': len(sessions_data)
            })

    except Exception as e:
        logger.error(f"Error getting session history: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'
    logger.info(f"Starting Flask server on port {port} (debug={debug_mode})")
    app.run(host='0.0.0.0', port=port, debug=debug_mode, use_reloader=debug_mode)

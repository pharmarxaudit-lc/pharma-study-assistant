"""
Question generator for pharmacy exam prep application.

Generates multiple-choice questions from analyzed PDF content using Claude API.
Supports both single-answer and "choose all that apply" question types.
"""
import json
import logging
import os
import random
import time
from datetime import datetime
from typing import Dict, List, Optional

import anthropic

from config import Config
from database import get_database
from database_models import Document, Question


class QuestionGenerator:
    """Generate exam questions from topic analysis using Claude API."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize question generator.

        Args:
            logger: Optional logger instance for progress tracking
        """
        self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.logger = logger or logging.getLogger(__name__)
        self.db = get_database(Config.DATABASE_PATH)

    def load_analysis(self, file_id: str) -> Dict:
        """
        Load topic analysis from JSON file.

        Args:
            file_id: Timestamp-based file identifier

        Returns:
            Dictionary containing topic analysis data

        Raises:
            FileNotFoundError: If analysis file doesn't exist
            json.JSONDecodeError: If JSON is invalid
        """
        analysis_path = os.path.join(
            Config.OUTPUT_FOLDER,
            file_id,
            f"{file_id}_analysis.json"
        )

        if not os.path.exists(analysis_path):
            raise FileNotFoundError(f"Analysis file not found: {analysis_path}")

        with open(analysis_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def generate_question(
        self,
        topic: Dict,
        question_type: str,
        difficulty: str,
        doc_context: str
    ) -> Optional[Dict]:
        """
        Generate a single question using Claude API.

        Args:
            topic: Topic data from analysis
            question_type: "single_answer" or "choose_all"
            difficulty: "basic", "intermediate", or "advanced"
            doc_context: Document filename for context

        Returns:
            Question dictionary or None if generation failed
        """
        # Build prompt based on question type
        if question_type == "single_answer":
            format_instruction = """
Format your response as JSON:
{
  "question_text": "The question text in Spanish",
  "options": ["A. Option 1", "B. Option 2", "C. Option 3", "D. Option 4"],
  "correct_answer": "A",
  "explanation": "Detailed explanation with law citation",
  "key_terms": [{"term": "Term", "definition": "Definition"}]
}"""
        else:
            format_instruction = """
Format your response as JSON:
{
  "question_text": "The question text in Spanish (indicate 'Seleccione todas las correctas')",
  "options": ["A. Option 1", "B. Option 2", "C. Option 3", "D. Option 4", "E. Option 5"],
  "correct_answer": "A,C,D",
  "explanation": "Detailed explanation with law citation",
  "key_terms": [{"term": "Term", "definition": "Definition"}]
}"""

        prompt = f"""Genera una pregunta de selección múltiple para el examen de reválida de farmacia de Puerto Rico.

TEMA: {topic['main_topic']}
SUBTEMAS: {', '.join(topic.get('subtopics', []))}
CONTEXTO REGULATORIO: {topic.get('regulatory_context', 'Ley 247 de 2004')}
TIPO DE PREGUNTA: {"Respuesta única (4 opciones)" if question_type == "single_answer" else "Seleccionar todas las correctas (4-5 opciones, 2-3 correctas)"}
DIFICULTAD: {difficulty}

TÉRMINOS CLAVE DISPONIBLES:
{json.dumps(topic.get('key_terms', []), indent=2, ensure_ascii=False)}

PUNTOS CRÍTICOS PARA EL EXAMEN:
{json.dumps(topic.get('exam_critical_points', []), indent=2, ensure_ascii=False)}

INSTRUCCIONES:
1. La pregunta DEBE estar completamente en ESPAÑOL
2. Usa términos y conceptos específicos del tema
3. {"Una sola respuesta correcta" if question_type == "single_answer" else "2-3 respuestas correctas"}
4. Distractores plausibles basados en:
   - Conceptos erróneos comunes
   - Términos similares del mismo tema
   - Variaciones numéricas (ej: 1000 vs 1500 horas)
5. Explicación DEBE citar la ley específica (Ley 247, artículos, etc.)
6. Dificultad {difficulty}:
   - basic: Recuerdo directo de hechos
   - intermediate: Aplicación de conceptos
   - advanced: Análisis de escenarios complejos

{format_instruction}

IMPORTANTE: Responde SOLO con el JSON, sin texto adicional."""

        # Call Claude API with retries
        for attempt in range(Config.MAX_RETRIES):
            try:
                response = self.client.messages.create(
                    model=Config.ANTHROPIC_MODEL,
                    max_tokens=2000,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}]
                )

                # Extract JSON from response
                content = response.content[0].text.strip()

                # Remove markdown code blocks if present
                if content.startswith('```'):
                    content = content.split('```')[1]
                    if content.startswith('json'):
                        content = content[4:].strip()

                question_data = json.loads(content)

                # Validate required fields
                required = ['question_text', 'options', 'correct_answer', 'explanation']
                if not all(field in question_data for field in required):
                    self.logger.warning(f"Missing required fields in generated question (attempt {attempt + 1})")
                    if attempt < Config.MAX_RETRIES - 1:
                        time.sleep(Config.RETRY_DELAY)
                        continue
                    return None

                return question_data

            except json.JSONDecodeError as e:
                self.logger.warning(f"JSON parse error (attempt {attempt + 1}): {e}")
                if attempt < Config.MAX_RETRIES - 1:
                    time.sleep(Config.RETRY_DELAY)
                    continue
                return None

            except Exception as e:
                self.logger.error(f"API error (attempt {attempt + 1}): {e}")
                if attempt < Config.MAX_RETRIES - 1:
                    time.sleep(Config.RETRY_DELAY)
                    continue
                return None

        return None

    def generate_questions_for_topic(
        self,
        topic: Dict,
        topic_id: int,
        document_id: int,
        doc_filename: str,
        num_questions: int = None
    ) -> List[Question]:
        """
        Generate multiple questions for a single topic.

        Args:
            topic: Topic data from analysis
            topic_id: Topic number (1-indexed)
            document_id: Database document ID
            doc_filename: Document filename for context
            num_questions: Number of questions to generate (default from config)

        Returns:
            List of Question model instances
        """
        if num_questions is None:
            num_questions = Config.QUESTIONS_PER_TOPIC

        questions = []
        single_answer_count = int(num_questions * Config.SINGLE_ANSWER_RATIO)
        choose_all_count = num_questions - single_answer_count

        # Calculate difficulty distribution
        basic_count = int(num_questions * Config.DIFFICULTY_DISTRIBUTION['basic'])
        advanced_count = int(num_questions * Config.DIFFICULTY_DISTRIBUTION['advanced'])
        intermediate_count = num_questions - basic_count - advanced_count

        # Create difficulty list and shuffle
        difficulties = (
            ['basic'] * basic_count +
            ['intermediate'] * intermediate_count +
            ['advanced'] * advanced_count
        )
        random.shuffle(difficulties)

        # Generate single-answer questions
        for i in range(single_answer_count):
            difficulty = difficulties[i]
            self.logger.info(
                f"  Generating question {i + 1}/{num_questions} "
                f"(type: single_answer, difficulty: {difficulty})"
            )

            question_data = self.generate_question(
                topic, 'single_answer', difficulty, doc_filename
            )

            if question_data:
                question = Question(
                    document_id=document_id,
                    topic_id=topic_id,
                    topic_name=topic['main_topic'],
                    question_type='single_answer',
                    difficulty=difficulty,
                    question_text=question_data['question_text'],
                    options_json=json.dumps(question_data['options'], ensure_ascii=False),
                    correct_answer=question_data['correct_answer'],
                    explanation=question_data['explanation'],
                    key_terms_json=json.dumps(
                        question_data.get('key_terms', []),
                        ensure_ascii=False
                    ),
                    regulatory_context=topic.get('regulatory_context', ''),
                    pages=topic.get('pages', ''),
                    times_seen=0,
                    times_correct=0
                )
                questions.append(question)
            else:
                self.logger.warning(f"  Failed to generate question {i + 1}")

        # Generate choose-all questions
        for i in range(choose_all_count):
            idx = single_answer_count + i
            difficulty = difficulties[idx]
            self.logger.info(
                f"  Generating question {idx + 1}/{num_questions} "
                f"(type: choose_all, difficulty: {difficulty})"
            )

            question_data = self.generate_question(
                topic, 'choose_all', difficulty, doc_filename
            )

            if question_data:
                question = Question(
                    document_id=document_id,
                    topic_id=topic_id,
                    topic_name=topic['main_topic'],
                    question_type='choose_all',
                    difficulty=difficulty,
                    question_text=question_data['question_text'],
                    options_json=json.dumps(question_data['options'], ensure_ascii=False),
                    correct_answer=question_data['correct_answer'],
                    explanation=question_data['explanation'],
                    key_terms_json=json.dumps(
                        question_data.get('key_terms', []),
                        ensure_ascii=False
                    ),
                    regulatory_context=topic.get('regulatory_context', ''),
                    pages=topic.get('pages', ''),
                    times_seen=0,
                    times_correct=0
                )
                questions.append(question)
            else:
                self.logger.warning(f"  Failed to generate question {idx + 1}")

        return questions

    def generate_all_questions(
        self,
        file_id: str,
        questions_per_topic: int = None
    ) -> Dict[str, any]:
        """
        Generate questions for all topics in a document.

        Args:
            file_id: Document file identifier
            questions_per_topic: Override default questions per topic

        Returns:
            Dictionary with generation statistics
        """
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"Question Generation Started: {file_id}")
        self.logger.info(f"{'='*60}\n")

        # Load analysis
        try:
            analysis = self.load_analysis(file_id)
        except Exception as e:
            self.logger.error(f"Failed to load analysis: {e}")
            return {'success': False, 'error': str(e)}

        # Create or get document record
        with self.db.session() as session:
            document = session.query(Document).filter_by(file_id=file_id).first()
            if not document:
                # Create new document record
                document = Document(
                    file_id=file_id,
                    filename=analysis.get('filename', f"{file_id}.pdf"),
                    total_topics=len(analysis['topics']),
                    total_pages=analysis.get('total_pages', 0),
                    analysis_path=f"outputs/{file_id}/{file_id}_analysis.json",
                    formatted_path=f"outputs/{file_id}/{file_id}_formatted.md"
                )
                session.add(document)
                session.flush()

            document_id = document.id
            doc_filename = document.filename

        # Generate questions for each topic
        stats = {
            'total_topics': len(analysis['topics']),
            'total_questions_generated': 0,
            'questions_by_topic': {},
            'questions_by_difficulty': {'basic': 0, 'intermediate': 0, 'advanced': 0},
            'questions_by_type': {'single_answer': 0, 'choose_all': 0},
            'failed_generations': 0
        }

        for topic_idx, topic in enumerate(analysis['topics'], 1):
            self.logger.info(f"\n📚 Topic {topic_idx}/{stats['total_topics']}: {topic['main_topic']}")
            self.logger.info(f"   Pages: {topic.get('pages', 'N/A')}")

            # Generate questions
            questions = self.generate_questions_for_topic(
                topic, topic_idx, document_id, doc_filename, questions_per_topic
            )

            # Calculate statistics before saving (while objects still have attributes)
            if questions:
                topic_stats = {
                    'total': len(questions),
                    'single_answer': sum(1 for q in questions if q.question_type == 'single_answer'),
                    'choose_all': sum(1 for q in questions if q.question_type == 'choose_all'),
                    'basic': sum(1 for q in questions if q.difficulty == 'basic'),
                    'intermediate': sum(1 for q in questions if q.difficulty == 'intermediate'),
                    'advanced': sum(1 for q in questions if q.difficulty == 'advanced')
                }

                # Save questions to database
                with self.db.session() as session:
                    for question in questions:
                        session.add(question)
                    session.commit()

                stats['questions_by_topic'][topic['main_topic']] = topic_stats
                stats['total_questions_generated'] += len(questions)
                stats['questions_by_type']['single_answer'] += topic_stats['single_answer']
                stats['questions_by_type']['choose_all'] += topic_stats['choose_all']
                stats['questions_by_difficulty']['basic'] += topic_stats['basic']
                stats['questions_by_difficulty']['intermediate'] += topic_stats['intermediate']
                stats['questions_by_difficulty']['advanced'] += topic_stats['advanced']

                self.logger.info(f"   ✅ Generated {len(questions)} questions")
            else:
                self.logger.warning(f"   ⚠️  No questions generated for this topic")

        # Final summary
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"Generation Complete!")
        self.logger.info(f"{'='*60}")
        self.logger.info(f"Total Questions: {stats['total_questions_generated']}")
        self.logger.info(f"By Type: Single Answer: {stats['questions_by_type']['single_answer']}, "
                        f"Choose All: {stats['questions_by_type']['choose_all']}")
        self.logger.info(f"By Difficulty: Basic: {stats['questions_by_difficulty']['basic']}, "
                        f"Intermediate: {stats['questions_by_difficulty']['intermediate']}, "
                        f"Advanced: {stats['questions_by_difficulty']['advanced']}")
        self.logger.info(f"{'='*60}\n")

        stats['success'] = True
        return stats

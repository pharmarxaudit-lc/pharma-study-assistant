import os

from dotenv import load_dotenv

load_dotenv()

# Get absolute paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class Config:
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"

    # Model context window and limits
    MODEL_MAX_CONTEXT_TOKENS = 200_000  # Claude 3.5 Sonnet context window
    MAX_CHUNK_TOKENS = 80_000  # Target: 40% of context window for topic identification
    ESTIMATED_TOKENS_PER_PAGE = 500  # Conservative estimate for content + structure

    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    OUTPUT_FOLDER = os.path.join(BASE_DIR, 'outputs')
    MAX_FILE_SIZE = 50 * 1024 * 1024
    BATCH_SIZE = 20

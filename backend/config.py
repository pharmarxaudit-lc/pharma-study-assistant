import os

from dotenv import load_dotenv

load_dotenv()

# Get absolute paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class Config:
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    OUTPUT_FOLDER = os.path.join(BASE_DIR, 'outputs')
    MAX_FILE_SIZE = 50 * 1024 * 1024
    BATCH_SIZE = 20

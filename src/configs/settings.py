"""Configuration settings for the Sales Brochure Generator."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

if sys.platform == "win32":
    os.system("chcp 65001")
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    
BASE_DIR = Path(__file__).parent.parent.parent
OUTPUT_DIR = BASE_DIR / os.getenv('OUTPUT_DIR', 'output/brochures')
LOGS_DIR = BASE_DIR / 'logs'

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'gpt-4o-mini')

# Application Settings
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', '20000'))

# Request Settings
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))

SUPPORTED_LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'zh': 'Chinese',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ua': 'Ukrainian'
}

def validate_config() -> bool:
    """Validate configuration settings"""
    
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is required. Please set it in your .env file.")
    
    if not OPENAI_API_KEY.startswith('sk-'):
        raise ValueError("Invalid OPENAI_API_KEY format. It should start with 'sk-'.")
    
    return True
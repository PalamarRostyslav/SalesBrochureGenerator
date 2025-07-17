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

# ClaudeAI Configuration
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
DEFAULT_CLAUDE_MODEL  = os.getenv('DEFAULT_CLAUDE_MODEL', 'claude-3-haiku-20240307')

# Supported AI providers and models
AI_PROVIDERS = {
    'OpenAI': {
        'models': ['gpt-4o-mini', 'gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo'],
        'api_key_env': 'OPENAI_API_KEY',
        'default_model': DEFAULT_MODEL,
        'api_key': OPENAI_API_KEY
    },
    'Claude': {
        'models': ['claude-3-5-haiku-20241022', 'claude-3-7-sonnet-20250219', 'claude-sonnet-4-20250514'],
        'api_key_env': 'ANTHROPIC_API_KEY', 
        'default_model': DEFAULT_CLAUDE_MODEL,
        'api_key': ANTHROPIC_API_KEY
    }
}

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
    
    if not OPENAI_API_KEY and not ANTHROPIC_API_KEY:
        raise ValueError("At least one API key (OPENAI_API_KEY or ANTHROPIC_API_KEY) is required. Please set it in your .env file.")
    
    # Validate OpenAI API key if provided
    if OPENAI_API_KEY and not OPENAI_API_KEY.startswith('sk-'):
        raise ValueError("Invalid OPENAI_API_KEY format. It should start with 'sk-'.")
    
    # Validate Anthropic API key if provided
    if ANTHROPIC_API_KEY and not ANTHROPIC_API_KEY.startswith('sk-ant-'):
        raise ValueError("Invalid ANTHROPIC_API_KEY format. It should start with 'sk-ant-'.")
    
    return True

def get_available_providers():
    """Get list of available providers based on configured API keys"""
    available = []
    
    if OPENAI_API_KEY:
        available.append('OpenAI')
    
    if ANTHROPIC_API_KEY:
        available.append('Claude')
    
    return available

def get_provider_info(provider_name: str):
    """Get provider information"""
    return AI_PROVIDERS.get(provider_name, {})

def get_default_provider():
    """Get the default provider based on available API keys"""
    available = get_available_providers()
    
    if 'OpenAI' in available:
        return 'OpenAI'
    elif 'Claude' in available:
        return 'Claude'
    else:
        return None
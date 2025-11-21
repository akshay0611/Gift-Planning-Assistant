"""
Configuration settings for Gift Planning Agent.
Loads environment variables and configures the Gemini model.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Gemini API Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
MODEL_NAME = 'gemini-2.0-flash'  # Using Gemini 2.0 Flash

# Optional: Google Search Configuration
GOOGLE_SEARCH_API_KEY = os.getenv('GOOGLE_SEARCH_API_KEY')
GOOGLE_SEARCH_ENGINE_ID = os.getenv('GOOGLE_SEARCH_ENGINE_ID')

# Session Configuration
SESSION_TIMEOUT_MINUTES = 60
DEFAULT_USER_ID = 'default_user'

# Logging Configuration
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Configure logging
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)

def validate_config():
    """Validate required configuration."""
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY not found. Please set it in your .env file. "
            "Copy .env.example to .env and add your API key."
        )
    return True

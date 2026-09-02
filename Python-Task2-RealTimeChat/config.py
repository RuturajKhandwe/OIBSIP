import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    """Base application configuration."""
    BASE_DIR = Path(__file__).resolve().parent
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DATABASE_PATH = os.getenv('DATABASE_PATH', str(BASE_DIR / 'database' / 'chat.db'))
    DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')
    HOST = os.getenv('HOST', '127.0.0.1')
    PORT = int(os.getenv('PORT', 5000))
    MAX_MESSAGE_HISTORY = 50
    MAX_MESSAGE_LENGTH = 1000
    MAX_USERNAME_LENGTH = 30
    MIN_USERNAME_LENGTH = 3
    MIN_PASSWORD_LENGTH = 6

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = False
    DATABASE_PATH = str(Config.BASE_DIR / 'database' / 'test_chat.db')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

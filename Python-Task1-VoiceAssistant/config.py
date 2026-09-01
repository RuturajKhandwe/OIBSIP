"""
Configuration Module for Intelligent Python Voice Assistant
Centralized management of environment settings, API keys, and application defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file if present
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)

class Config:
    """Application configuration and credentials container."""

    # General Settings
    APP_ENV: str = os.getenv("APP_ENV", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    USER_NAME: str = os.getenv("USER_NAME", "User")
    ASSISTANT_NAME: str = os.getenv("ASSISTANT_NAME", "Nova")

    # Speech Recognition Defaults
    STT_ENERGY_THRESHOLD: int = int(os.getenv("STT_ENERGY_THRESHOLD", "4000"))
    STT_PAUSE_THRESHOLD: float = float(os.getenv("STT_PAUSE_THRESHOLD", "0.8"))
    STT_LANGUAGE: str = os.getenv("STT_LANGUAGE", "en-US")
    STT_TIMEOUT: float = float(os.getenv("STT_TIMEOUT", "5.0"))
    STT_PHRASE_TIME_LIMIT: float = float(os.getenv("STT_PHRASE_TIME_LIMIT", "10.0"))
    STT_MICROPHONE_INDEX: int | None = int(os.getenv("STT_MICROPHONE_INDEX")) if os.getenv("STT_MICROPHONE_INDEX") else None

    # Text to Speech Defaults
    TTS_RATE: int = int(os.getenv("TTS_RATE", "175"))
    TTS_VOLUME: float = float(os.getenv("TTS_VOLUME", "1.0"))

    # Weather Service Secrets
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY") or os.getenv("WEATHER_API_KEY", "")
    WEATHER_API_KEY: str = OPENWEATHER_API_KEY
    WEATHER_DEFAULT_CITY: str = os.getenv("WEATHER_DEFAULT_CITY", "Pune")
    WEATHER_BASE_URL: str = "https://api.openweathermap.org/data/2.5/weather"

    # Email Service Credentials
    EMAIL_SMTP_HOST: str = os.getenv("EMAIL_SMTP_HOST") or os.getenv("SMTP_SERVER", "smtp.gmail.com")
    EMAIL_SMTP_PORT: int = int(os.getenv("EMAIL_SMTP_PORT") or os.getenv("SMTP_PORT", "587"))
    EMAIL_USERNAME: str = os.getenv("EMAIL_USERNAME") or os.getenv("SMTP_EMAIL", "")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD") or os.getenv("SMTP_PASSWORD", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM") or EMAIL_USERNAME
    EMAIL_USE_TLS: bool = os.getenv("EMAIL_USE_TLS", "true").lower() in ("true", "1", "yes")

    # Legacy Aliases
    SMTP_SERVER: str = EMAIL_SMTP_HOST
    SMTP_PORT: int = EMAIL_SMTP_PORT
    SMTP_EMAIL: str = EMAIL_USERNAME
    SMTP_PASSWORD: str = EMAIL_PASSWORD

    # Paths
    INTENTS_FILE: Path = BASE_DIR / "nlp" / "intents.json"
    CUSTOM_COMMANDS_FILE: Path = BASE_DIR / "config" / "custom_commands.json"
    LOGS_DIR: Path = BASE_DIR / "logs"

    # NLU Defaults
    NLU_CONFIDENCE_THRESHOLD: float = float(os.getenv("NLU_CONFIDENCE_THRESHOLD", "0.45"))

    @classmethod
    def validate_secrets_loaded(cls) -> dict:
        """Helper to inspect secret configuration status without exposing sensitive values."""
        key = cls.OPENWEATHER_API_KEY or cls.WEATHER_API_KEY
        email_configured = bool(
            cls.EMAIL_USERNAME
            and cls.EMAIL_PASSWORD
            and cls.EMAIL_USERNAME.strip()
            and cls.EMAIL_PASSWORD.strip()
            and cls.EMAIL_USERNAME != "your_test_email@gmail.com"
            and cls.EMAIL_PASSWORD != "your_app_password_here"
        )
        return {
            "weather_api_configured": bool(key and key.strip() and key != "your_openweathermap_api_key_here"),
            "email_configured": email_configured,
            "smtp_configured": email_configured,
        }

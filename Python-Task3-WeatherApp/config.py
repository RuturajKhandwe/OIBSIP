import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    """Centralized Application Configuration."""

    APP_NAME = "Atmos"
    APP_SUBTITLE = "Advanced Real-Time Weather Dashboard"
    VERSION = "2.0.0"

    # API Keys
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()
    IPINFO_TOKEN = os.getenv("IPINFO_TOKEN", "").strip()

    # Base API URLs
    OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"
    IPINFO_BASE_URL = "https://ipinfo.io/json"

    # Network Request Timeouts (Seconds)
    REQUEST_TIMEOUT = 10

    # Default Settings
    DEFAULT_CITY = "Pune"
    DEFAULT_UNITS = "metric"  # metric = Celsius, imperial = Fahrenheit

    # Cache TTL (Seconds) - 10 minutes cache to avoid redundant API hits
    CACHE_TTL_SECONDS = 600

    @classmethod
    def is_api_key_configured(cls) -> bool:
        """Returns True if a valid OpenWeatherMap API key is set."""
        return bool(cls.OPENWEATHER_API_KEY and cls.OPENWEATHER_API_KEY != "your_openweather_api_key_here")

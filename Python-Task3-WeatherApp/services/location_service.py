from typing import Tuple, Optional
from api.weather_api import WeatherAPIClient, LocationError
from config import Config

class LocationService:
    """Service handling IP-based automatic location detection and default location fallbacks."""

    @staticmethod
    def detect_user_location() -> Tuple[bool, str, Optional[str]]:
        """
        Attempts to detect current user city via IP.
        Returns (success, city_name_or_error_msg, country_code).
        """
        try:
            data = WeatherAPIClient.get_ip_location()
            city = data.get("city", "").strip()
            country = data.get("country", "").strip()

            if city:
                location_str = f"{city}, {country}" if country else city
                return True, location_str, country
            else:
                return False, "Unable to detect city from IP address.", None

        except LocationError as e:
            return False, str(e), None
        except Exception as e:
            return False, f"Location detection failed: {str(e)}", None

    @staticmethod
    def get_default_location() -> str:
        """Returns the fallback default city configured in application settings."""
        return Config.DEFAULT_CITY

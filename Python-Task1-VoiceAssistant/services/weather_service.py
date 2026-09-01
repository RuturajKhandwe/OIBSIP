"""
Weather Service Module for Intelligent Python Voice Assistant.
Integrates live weather data fetching via OpenWeatherMap API with robust error handling.
"""

from typing import Dict, Any, Optional
import requests
from config import Config
from core.logger import get_logger

logger = get_logger("WeatherService")

class WeatherService:
    """Weather API integration handler using OpenWeatherMap API."""

    @classmethod
    def fetch_weather_data(cls, city: str) -> Dict[str, Any]:
        """
        Calls OpenWeatherMap API to retrieve current weather data for target city.
        Returns a structured dictionary with parsed weather parameters or error status.
        Never exposes API key in logs or error messages.
        """
        if not city or not city.strip():
            logger.warning("Weather fetch requested with empty city name.")
            return {
                "success": False,
                "city": "",
                "error_type": "empty_location",
                "error": "Location name was not provided."
            }

        target_city = city.strip()
        api_key = Config.OPENWEATHER_API_KEY or Config.WEATHER_API_KEY

        # Validate API key configuration
        secrets_status = Config.validate_secrets_loaded()
        if not secrets_status["weather_api_configured"] or not api_key:
            logger.warning(f"[WeatherService] OpenWeatherMap API key is not configured for target city: {target_city}")
            return {
                "success": False,
                "city": target_city,
                "error_type": "missing_key",
                "error": "Weather API key is not configured."
            }

        logger.info(f"[WeatherService] Fetching weather for: {target_city}")

        params = {
            "q": target_city,
            "appid": api_key,
            "units": "metric"
        }

        try:
            response = requests.get(Config.WEATHER_BASE_URL, params=params, timeout=5.0)

            if response.status_code == 200:
                data = response.json()
                parsed_result = {
                    "success": True,
                    "city": data.get("name", target_city),
                    "country": data.get("sys", {}).get("country", ""),
                    "temperature_c": round(data.get("main", {}).get("temp", 0.0), 1),
                    "feels_like_c": round(data.get("main", {}).get("feels_like", 0.0), 1),
                    "humidity": data.get("main", {}).get("humidity", 0),
                    "condition": data.get("weather", [{}])[0].get("main", ""),
                    "description": data.get("weather", [{}])[0].get("description", ""),
                    "wind_speed": round(data.get("wind", {}).get("speed", 0.0), 1),
                    "error_type": None,
                    "error": None
                }
                logger.info(f"[WeatherService] Weather request successful for {parsed_result['city']}")
                return parsed_result

            elif response.status_code == 404:
                logger.warning(f"[WeatherService] City not found: '{target_city}' (HTTP 404)")
                return {
                    "success": False,
                    "city": target_city,
                    "error_type": "city_not_found",
                    "error": f"City '{target_city}' not found."
                }

            elif response.status_code == 401:
                logger.error("[WeatherService] Invalid OpenWeatherMap API key (HTTP 401)")
                return {
                    "success": False,
                    "city": target_city,
                    "error_type": "invalid_key",
                    "error": "Invalid API key provided."
                }

            else:
                logger.error(f"[WeatherService] API returned non-200 status code: {response.status_code}")
                return {
                    "success": False,
                    "city": target_city,
                    "error_type": "api_error",
                    "error": f"API error with status code {response.status_code}."
                }

        except requests.Timeout:
            logger.error(f"[WeatherService] Request timeout while reaching weather API for {target_city}")
            return {
                "success": False,
                "city": target_city,
                "error_type": "timeout",
                "error": "Request timed out."
            }

        except requests.RequestException as e:
            logger.error(f"[WeatherService] Network error during weather API call: {e}")
            return {
                "success": False,
                "city": target_city,
                "error_type": "network_error",
                "error": "Network request failed."
            }

        except Exception as e:
            logger.error(f"[WeatherService] Unexpected error parsing weather data: {e}")
            return {
                "success": False,
                "city": target_city,
                "error_type": "malformed_response",
                "error": "Failed to parse weather response."
            }

    @classmethod
    def format_weather_response(cls, data: Dict[str, Any]) -> str:
        """
        Converts structured weather result into a human-readable spoken response.
        """
        if data.get("success"):
            city = data.get("city")
            temp = data.get("temperature_c")
            feels_like = data.get("feels_like_c")
            humidity = data.get("humidity")
            desc = data.get("description", "clear skies")
            wind_speed = data.get("wind_speed")
            
            return (
                f"The current weather in {city} is {temp} degrees Celsius with {desc}. "
                f"It feels like {feels_like} degrees, humidity is {humidity} percent, "
                f"and wind speed is {wind_speed} meters per second."
            )

        error_type = data.get("error_type")

        if error_type == "missing_key" or error_type == "invalid_key":
            return "The weather service is not configured yet."

        if error_type == "city_not_found":
            return "I couldn't find weather information for that location."

        if error_type == "empty_location":
            return "Which city would you like the weather for?"

        # Network error, timeout, malformed response, or api error
        return "I'm unable to reach the weather service right now."

    @classmethod
    def get_weather(cls, city: Optional[str] = None) -> str:
        """
        Main entry point for command router.
        Fetches live weather data and returns spoken response string.
        """
        target_city = city or Config.WEATHER_DEFAULT_CITY
        data = cls.fetch_weather_data(target_city)
        return cls.format_weather_response(data)

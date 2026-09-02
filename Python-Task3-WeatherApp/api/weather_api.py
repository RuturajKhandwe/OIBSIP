import requests
from typing import Dict, Any, Optional
from config import Config

class WeatherAPIError(Exception):
    """Custom exception raised when an API error occurs."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class LocationError(Exception):
    """Custom exception raised when IP-based location detection fails."""
    pass

class WeatherAPIClient:
    """Client for making HTTP requests to OpenWeatherMap and IPInfo APIs."""

    def __init__(self, api_key: Optional[str] = None, timeout: int = Config.REQUEST_TIMEOUT):
        self.api_key = api_key or Config.OPENWEATHER_API_KEY
        self.timeout = timeout

    def get_current_weather(self, location: str, units: str = "metric") -> Dict[str, Any]:
        """
        Fetches current weather data for a given city or ZIP code.
        """
        if not self.api_key or self.api_key == "your_openweather_api_key_here":
            raise WeatherAPIError("OpenWeatherMap API key is not configured. Please add your key to .env file.")

        url = f"{Config.OPENWEATHER_BASE_URL}/weather"
        params = {
            "q": location.strip(),
            "appid": self.api_key,
            "units": units
        }

        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                raise WeatherAPIError(f"Location '{location}' not found. Please check the city or ZIP code.", 404)
            elif response.status_code == 401:
                raise WeatherAPIError("Weather service configuration is invalid (Invalid API Key).", 401)
            elif response.status_code == 429:
                raise WeatherAPIError("Weather service request limit reached. Please try again later.", 429)
            else:
                raise WeatherAPIError(f"Weather API returned status code {response.status_code}.", response.status_code)

        except requests.exceptions.Timeout:
            raise WeatherAPIError("Request timed out while connecting to weather service. Please try again.")
        except requests.exceptions.ConnectionError:
            raise WeatherAPIError("Unable to connect to the weather service. Please check your internet connection.")
        except requests.exceptions.RequestException as e:
            raise WeatherAPIError(f"Network error: {str(e)}")

    def get_weather_forecast(self, location: str, units: str = "metric") -> Dict[str, Any]:
        """
        Fetches 5-day / 3-hour interval weather forecast for a given location.
        """
        if not self.api_key or self.api_key == "your_openweather_api_key_here":
            raise WeatherAPIError("OpenWeatherMap API key is not configured.")

        url = f"{Config.OPENWEATHER_BASE_URL}/forecast"
        params = {
            "q": location.strip(),
            "appid": self.api_key,
            "units": units
        }

        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                raise WeatherAPIError(f"Forecast for '{location}' not found.", 404)
            elif response.status_code == 401:
                raise WeatherAPIError("Invalid OpenWeatherMap API Key.", 401)
            else:
                raise WeatherAPIError(f"Forecast API returned error code {response.status_code}.", response.status_code)

        except requests.exceptions.Timeout:
            raise WeatherAPIError("Forecast request timed out.")
        except requests.exceptions.ConnectionError:
            raise WeatherAPIError("Connection error fetching weather forecast.")
        except requests.exceptions.RequestException as e:
            raise WeatherAPIError(f"Forecast error: {str(e)}")

    @staticmethod
    def get_ip_location(token: Optional[str] = None, timeout: int = Config.REQUEST_TIMEOUT) -> Dict[str, Any]:
        """
        Fetches approximate user location via ipinfo.io API.
        """
        url = Config.IPINFO_BASE_URL
        token = token or Config.IPINFO_TOKEN
        params = {"token": token} if token else {}

        try:
            response = requests.get(url, params=params, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                if "city" in data:
                    return data
                raise LocationError("IPInfo response did not contain city information.")
            else:
                raise LocationError(f"IPInfo service returned status {response.status_code}")
        except Exception as e:
            raise LocationError(f"Failed to detect location: {str(e)}")

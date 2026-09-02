import unittest
from unittest.mock import patch, MagicMock
import requests
from api.weather_api import WeatherAPIClient, WeatherAPIError

class TestWeatherAPI(unittest.TestCase):
    """Test suite for WeatherAPIClient using mocked HTTP responses."""

    def setUp(self):
        self.client = WeatherAPIClient(api_key="test_dummy_key")

    @patch("requests.get")
    def test_fetch_current_weather_success(self, mock_get):
        """Test successful current weather API response parsing."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "Pune",
            "sys": {"country": "IN"},
            "main": {"temp": 28.5, "feels_like": 30.0, "humidity": 72, "pressure": 1012},
            "weather": [{"main": "Clear", "description": "clear sky", "icon": "01d"}],
            "wind": {"speed": 4.8},
            "visibility": 10000
        }
        mock_get.return_value = mock_response

        data = self.client.get_current_weather("Pune", units="metric")
        self.assertEqual(data["name"], "Pune")
        self.assertEqual(data["main"]["temp"], 28.5)

    @patch("requests.get")
    def test_city_not_found_404_error(self, mock_get):
        """Test 404 city not found error handling."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with self.assertRaises(WeatherAPIError) as ctx:
            self.client.get_current_weather("InvalidCity12345")
        
        self.assertIn("not found", str(ctx.exception).lower())

    @patch("requests.get")
    def test_invalid_api_key_401_error(self, mock_get):
        """Test 401 invalid API key error handling."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        with self.assertRaises(WeatherAPIError) as ctx:
            self.client.get_current_weather("London")

        self.assertIn("invalid api key", str(ctx.exception).lower())

    @patch("requests.get")
    def test_timeout_exception_handling(self, mock_get):
        """Test network timeout exception handling."""
        mock_get.side_effect = requests.exceptions.Timeout()

        with self.assertRaises(WeatherAPIError) as ctx:
            self.client.get_current_weather("Tokyo")

        self.assertIn("timed out", str(ctx.exception).lower())

if __name__ == '__main__':
    unittest.main()

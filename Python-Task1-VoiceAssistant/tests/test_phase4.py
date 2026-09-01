"""
Unit tests for Phase 4 Weather Service, Knowledge Service, NLU, and Command Routing.
Uses mocks for external API HTTP requests and network calls.
"""

import unittest
from unittest.mock import patch, MagicMock
import requests
from config import Config
from nlp.intent_engine import IntentClassifier
from services.weather_service import WeatherService
from services.knowledge_service import KnowledgeService
from core.command_router import CommandRouter

class TestPhase4Capabilities(unittest.TestCase):
    """Test suite for Phase 4 capabilities."""

    def setUp(self):
        self.classifier = IntentClassifier()
        self.router = CommandRouter()

    # --- WEATHER SERVICE TESTS ---

    # 1. Valid Weather Response
    @patch("requests.get")
    @patch.object(Config, "OPENWEATHER_API_KEY", "mock_valid_key")
    def test_weather_valid_response(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "Pune",
            "sys": {"country": "IN"},
            "main": {"temp": 28.5, "feels_like": 29.1, "humidity": 65},
            "weather": [{"main": "Clouds", "description": "scattered clouds"}],
            "wind": {"speed": 3.2}
        }
        mock_get.return_value = mock_response

        data = WeatherService.fetch_weather_data("Pune")
        self.assertTrue(data["success"])
        self.assertEqual(data["city"], "Pune")
        self.assertEqual(data["country"], "IN")
        self.assertEqual(data["temperature_c"], 28.5)
        self.assertEqual(data["feels_like_c"], 29.1)
        self.assertEqual(data["humidity"], 65)
        self.assertEqual(data["condition"], "Clouds")
        self.assertEqual(data["description"], "scattered clouds")
        self.assertEqual(data["wind_speed"], 3.2)

    # 2. City Not Found (HTTP 404)
    @patch("requests.get")
    @patch.object(Config, "OPENWEATHER_API_KEY", "mock_valid_key")
    def test_weather_city_not_found(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        data = WeatherService.fetch_weather_data("NonExistentCityXYZ")
        self.assertFalse(data["success"])
        self.assertEqual(data["error_type"], "city_not_found")
        spoken = WeatherService.format_weather_response(data)
        self.assertIn("couldn't find weather information", spoken)

    # 3. API Key Missing
    @patch.object(Config, "OPENWEATHER_API_KEY", "")
    @patch.object(Config, "WEATHER_API_KEY", "")
    def test_weather_api_key_missing(self):
        data = WeatherService.fetch_weather_data("Pune")
        self.assertFalse(data["success"])
        self.assertEqual(data["error_type"], "missing_key")
        spoken = WeatherService.format_weather_response(data)
        self.assertIn("not configured yet", spoken)

    # 4. API / Network Failure
    @patch("requests.get")
    @patch.object(Config, "OPENWEATHER_API_KEY", "mock_valid_key")
    def test_weather_network_failure(self, mock_get):
        mock_get.side_effect = requests.RequestException("Connection error")
        data = WeatherService.fetch_weather_data("Pune")
        self.assertFalse(data["success"])
        self.assertEqual(data["error_type"], "network_error")
        spoken = WeatherService.format_weather_response(data)
        self.assertIn("unable to reach the weather service", spoken)

    # 5. Request Timeout
    @patch("requests.get")
    @patch.object(Config, "OPENWEATHER_API_KEY", "mock_valid_key")
    def test_weather_timeout(self, mock_get):
        mock_get.side_effect = requests.Timeout("Read timeout")
        data = WeatherService.fetch_weather_data("Pune")
        self.assertFalse(data["success"])
        self.assertEqual(data["error_type"], "timeout")
        spoken = WeatherService.format_weather_response(data)
        self.assertIn("unable to reach the weather service", spoken)

    # 6. Empty Location
    def test_weather_empty_location(self):
        data = WeatherService.fetch_weather_data("")
        self.assertFalse(data["success"])
        self.assertEqual(data["error_type"], "empty_location")
        spoken = WeatherService.format_weather_response(data)
        self.assertIn("Which city would you like", spoken)

    # 7. Weather Response Formatting
    def test_weather_response_formatting(self):
        sample_data = {
            "success": True,
            "city": "Pune",
            "country": "IN",
            "temperature_c": 28.5,
            "feels_like_c": 29.1,
            "humidity": 65,
            "condition": "Clouds",
            "description": "scattered clouds",
            "wind_speed": 3.2
        }
        spoken = WeatherService.format_weather_response(sample_data)
        self.assertIn("Pune", spoken)
        self.assertIn("28.5 degrees", spoken)
        self.assertIn("scattered clouds", spoken)
        self.assertIn("65 percent", spoken)

    # --- NLU & ENTITY EXTRACTION TESTS ---

    # 8. Weather Intent Recognition
    def test_weather_intent_recognition(self):
        phrases = [
            "what's the weather in Pune",
            "tell me the weather in Mumbai",
            "how hot is it in Delhi",
            "what is the temperature in Nagpur",
            "is it raining in Pune",
            "weather forecast for Pune"
        ]
        for phrase in phrases:
            res = self.classifier.predict_intent(phrase)
            self.assertEqual(res["intent"], "get_weather", f"Failed for phrase: '{phrase}'")

    # 9. Weather Location Extraction
    def test_weather_location_extraction(self):
        test_cases = [
            ("what's the weather in Pune", "Pune"),
            ("tell me the weather in Mumbai", "Mumbai"),
            ("how hot is it in Delhi", "Delhi"),
            ("what is the temperature in Nagpur", "Nagpur"),
            ("is it raining in Pune", "Pune")
        ]
        for input_text, expected_city in test_cases:
            res = self.classifier.predict_intent(input_text)
            self.assertEqual(res["intent"], "get_weather")
            self.assertEqual(res["entities"].get("city"), expected_city, f"Failed city extraction for: '{input_text}'")

    # 10. Knowledge Intent Recognition
    def test_knowledge_intent_recognition(self):
        phrases = [
            "what is Python",
            "what is machine learning",
            "who was Albert Einstein",
            "explain artificial intelligence",
            "what is a neural network",
            "explain deep learning"
        ]
        for phrase in phrases:
            res = self.classifier.predict_intent(phrase)
            self.assertEqual(res["intent"], "knowledge_query", f"Failed for phrase: '{phrase}'")

    # 11. Unknown Question Handling
    def test_unknown_question_handling(self):
        res = self.classifier.predict_intent("xyz123 random invalid request string 999")
        self.assertEqual(res["intent"], "unknown")

    # --- KNOWLEDGE SERVICE TESTS ---

    # 12. Successful Knowledge Response
    @patch("requests.get")
    def test_knowledge_successful_response(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "type": "standard",
            "title": "Python (programming language)",
            "extract": "Python is a high-level, general-purpose programming language. Its design philosophy emphasizes code readability."
        }
        mock_get.return_value = mock_response

        res = KnowledgeService.query_knowledge("what is Python")
        self.assertTrue(res["success"])
        self.assertIn("high-level, general-purpose programming language", res["answer"])

    # 13. Knowledge Topic No Result (404)
    @patch("requests.get")
    def test_knowledge_no_result(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        res = KnowledgeService.query_knowledge("asdfghjkl nonexistent topic")
        self.assertFalse(res["success"])
        self.assertEqual(res["error_type"], "no_result")
        self.assertIn("couldn't find information", res["answer"])

    # 14. Knowledge Network/API Failure
    @patch("requests.get")
    def test_knowledge_network_failure(self, mock_get):
        mock_get.side_effect = requests.RequestException("Connection error")

        res = KnowledgeService.query_knowledge("what is Python")
        self.assertFalse(res["success"])
        self.assertEqual(res["error_type"], "network_error")
        self.assertIn("unable to reach the knowledge service", res["answer"])

    # --- COMMAND ROUTER INTEGRATION TESTS ---

    # 15. Weather Command Reaches Weather Service
    @patch("services.weather_service.WeatherService.fetch_weather_data")
    def test_command_router_weather_dispatch(self, mock_fetch_weather):
        mock_fetch_weather.return_value = {
            "success": True,
            "city": "Pune",
            "country": "IN",
            "temperature_c": 28.5,
            "feels_like_c": 29.1,
            "humidity": 65,
            "condition": "Clouds",
            "description": "scattered clouds",
            "wind_speed": 3.2
        }

        response, should_exit, nlu_res = self.router.process_command("what's the weather in Pune")
        self.assertFalse(should_exit)
        self.assertEqual(nlu_res["intent"], "get_weather")
        self.assertIn("Pune", response)

    # 16. Knowledge Command Reaches Knowledge Service
    @patch("services.knowledge_service.KnowledgeService.get_answer")
    def test_command_router_knowledge_dispatch(self, mock_get_answer):
        mock_get_answer.return_value = "Python is a programming language."

        response, should_exit, nlu_res = self.router.process_command("what is Python")
        self.assertFalse(should_exit)
        self.assertEqual(nlu_res["intent"], "knowledge_query")
        self.assertIn("programming language", response)

    # 17. Existing Commands Still Work
    def test_command_router_existing_commands(self):
        # Time
        resp_time, _, nlu_time = self.router.process_command("what time is it")
        self.assertEqual(nlu_time["intent"], "get_time")
        self.assertIn("The current time is", resp_time)

        # Date
        resp_date, _, nlu_date = self.router.process_command("what is today's date")
        self.assertEqual(nlu_date["intent"], "get_date")
        self.assertIn("Today is", resp_date)

        # Web Search
        with patch("webbrowser.open"):
            resp_search, _, nlu_search = self.router.process_command("search for Python tutorials")
            self.assertEqual(nlu_search["intent"], "web_search")
            self.assertIn("Searching the web", resp_search)

        # Greeting
        resp_greet, _, nlu_greet = self.router.process_command("hello")
        self.assertEqual(nlu_greet["intent"], "greeting")

        # Exit
        resp_exit, should_exit, nlu_exit = self.router.process_command("exit")
        self.assertTrue(should_exit)
        self.assertEqual(nlu_exit["intent"], "exit")

if __name__ == "__main__":
    unittest.main()

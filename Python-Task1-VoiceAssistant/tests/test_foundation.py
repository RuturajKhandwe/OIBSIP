"""
Unit tests for Phase 1 Foundation verification.
"""

import unittest
from config import Config
from nlp.intent_engine import IntentClassifier
from services.datetime_service import DateTimeService

class TestFoundation(unittest.TestCase):
    """Test suite verifying core system components."""

    def setUp(self):
        self.classifier = IntentClassifier()

    def test_config_defaults(self):
        """Test configuration defaults and secret safety validation."""
        self.assertIsNotNone(Config.ASSISTANT_NAME)
        secrets = Config.validate_secrets_loaded()
        self.assertIn("weather_api_configured", secrets)
        self.assertIn("smtp_configured", secrets)

    def test_datetime_service(self):
        """Test date and time formatting."""
        greeting = DateTimeService.get_greeting()
        current_time = DateTimeService.get_current_time()
        current_date = DateTimeService.get_current_date()

        self.assertIn(Config.USER_NAME, greeting)
        self.assertIn("The current time is", current_time)
        self.assertIn("Today is", current_date)

    def test_intent_classification_variations(self):
        """Test NLU intent classification for natural language variations."""
        test_cases = [
            ("what time is it", "get_time"),
            ("could you tell me the current time", "get_time"),
            ("do you know what time it is", "get_time"),
            ("search for Python tutorials", "web_search"),
            ("look up Python tutorials online", "web_search"),
            ("can you search the web for Python tutorials", "web_search"),
            ("hello", "greeting"),
            ("exit", "exit")
        ]

        for text, expected_intent in test_cases:
            intent, score = self.classifier.predict(text)
            self.assertEqual(intent, expected_intent, f"Failed for '{text}': expected {expected_intent}, got {intent} ({score:.2f})")

    def test_unknown_intent_fallback(self):
        """Test fallback for unrecognized gibberish input."""
        intent, score = self.classifier.predict("xyz123 random invalid command string")
        self.assertEqual(intent, "unknown")

if __name__ == "__main__":
    unittest.main()

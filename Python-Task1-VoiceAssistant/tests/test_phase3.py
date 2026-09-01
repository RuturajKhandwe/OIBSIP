"""
Unit tests for Phase 3 Advanced NLU, Entity Extraction, Custom Commands, and Command Router.
Verifies NLU precision, confidence thresholds, custom command security, and backward compatibility.
"""

import os
import json
import tempfile
import unittest
from unittest.mock import MagicMock, patch
from config import Config
from nlp.intent_engine import IntentClassifier
from nlp.entity_extractor import EntityExtractor
from services.custom_service import CustomCommandService
from core.command_router import CommandRouter

class TestPhase3NLUAndCustomCommands(unittest.TestCase):
    """Test suite for Phase 3 advanced NLU, entity extraction, and custom command capabilities."""

    def setUp(self):
        self.classifier = IntentClassifier()
        self.router = CommandRouter()

    # 1. Greeting Variations Test
    def test_greeting_variations(self):
        phrases = ["hello", "hi", "hey assistant", "good morning", "good afternoon", "greetings"]
        for phrase in phrases:
            res = self.classifier.predict_intent(phrase)
            self.assertEqual(res["intent"], "greeting", f"Failed for phrase: '{phrase}'")
            self.assertGreaterEqual(res["confidence"], Config.NLU_CONFIDENCE_THRESHOLD)

    # 2. Time Variations Test
    def test_time_variations(self):
        phrases = [
            "what time is it",
            "tell me the time",
            "what's the current time",
            "can you tell me the time",
            "do you know what time it is"
        ]
        for phrase in phrases:
            res = self.classifier.predict_intent(phrase)
            self.assertEqual(res["intent"], "get_time", f"Failed for phrase: '{phrase}'")

    # 3. Date Variations Test
    def test_date_variations(self):
        phrases = [
            "what is today's date",
            "tell me today's date",
            "what date is it",
            "what day is today"
        ]
        for phrase in phrases:
            res = self.classifier.predict_intent(phrase)
            self.assertEqual(res["intent"], "get_date", f"Failed for phrase: '{phrase}'")

    # 4. Search Intent Variations Test
    def test_search_intent_variations(self):
        phrases = [
            "search for Python tutorials",
            "look up machine learning",
            "search the web for FastAPI",
            "find information about computer vision",
            "google neural networks",
            "look for Python pandas documentation"
        ]
        for phrase in phrases:
            res = self.classifier.predict_intent(phrase)
            self.assertEqual(res["intent"], "web_search", f"Failed for phrase: '{phrase}'")

    # 5. Search Query Entity Extraction Test
    def test_search_query_entity_extraction(self):
        test_cases = [
            ("search for Python tutorials", "Python tutorials"),
            ("look up machine learning", "machine learning"),
            ("search the web for FastAPI documentation", "FastAPI documentation"),
            ("find information about neural networks", "neural networks"),
            ("google Python pandas tutorial", "Python pandas tutorial")
        ]

        for input_text, expected_query in test_cases:
            res = self.classifier.predict_intent(input_text)
            self.assertEqual(res["intent"], "web_search")
            self.assertIn("query", res["entities"])
            self.assertEqual(res["entities"]["query"], expected_query)

    # 6. Unknown Commands Test
    def test_unknown_commands(self):
        res = self.classifier.predict_intent("qwertyuiop random 12345 invalid command")
        self.assertEqual(res["intent"], "unknown")
        self.assertEqual(res["confidence"], 0.0)

    # 7. Low-Confidence Threshold Test
    def test_low_confidence_command_routing(self):
        response, should_exit, nlu_res = self.router.process_command("random unrecognized phrase zzz999")
        self.assertFalse(should_exit)
        self.assertEqual(nlu_res["intent"], "unknown")
        self.assertIn("I'm not sure what you mean", response)

    # 8. Custom Command Loading & Schema Validation Test
    def test_custom_command_loading_and_matching(self):
        custom_json = {
            "commands": [
                {
                    "name": "open test site",
                    "phrases": ["launch test site", "open test site"],
                    "action_type": "open_url",
                    "action_value": "https://example.com"
                },
                {
                    "name": "say secret",
                    "phrases": ["tell me secret"],
                    "action_type": "response",
                    "action_value": "The secret code is 42"
                }
            ]
        }

        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as tf:
            json.dump(custom_json, tf)
            temp_path = tf.name

        try:
            custom_svc = CustomCommandService(custom_config_path=temp_path)
            self.assertEqual(len(custom_svc.commands), 2)

            # Test matching response action
            matched, resp = custom_svc.match_and_execute("tell me secret")
            self.assertTrue(matched)
            self.assertEqual(resp, "The secret code is 42")

            # Test matching URL action
            with patch("webbrowser.open") as mock_browser_open:
                matched_url, resp_url = custom_svc.match_and_execute("launch test site")
                self.assertTrue(matched_url)
                mock_browser_open.assert_called_with("https://example.com")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    # 9. Custom Command Security Validation (Rejection of Unsafe Actions) Test
    def test_custom_command_security_rejections(self):
        unsafe_json = {
            "commands": [
                {
                    "name": "unsafe shell",
                    "phrases": ["run shell"],
                    "action_type": "exec",  # Unsafe action type!
                    "action_value": "rm -rf /"
                },
                {
                    "name": "unsafe url scheme",
                    "phrases": ["open script"],
                    "action_type": "open_url",
                    "action_value": "javascript:alert(1)"  # Non-http/https URL!
                }
            ]
        }

        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as tf:
            json.dump(unsafe_json, tf)
            temp_path = tf.name

        try:
            custom_svc = CustomCommandService(custom_config_path=temp_path)
            # Both unsafe definitions must be rejected by validator
            self.assertEqual(len(custom_svc.commands), 0)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    # 10. Command Router Integration Test
    def test_command_router_pipeline(self):
        # Built-in exit
        resp, exit_flag, _ = self.router.process_command("exit")
        self.assertTrue(exit_flag)
        self.assertIn("Goodbye", resp)

        # Built-in time
        resp_time, exit_flag, _ = self.router.process_command("what time is it")
        self.assertFalse(exit_flag)
        self.assertIn("The current time is", resp_time)

        # Custom command integration
        resp_custom, exit_flag, _ = self.router.process_command("who created you")
        self.assertFalse(exit_flag)
        self.assertIn("intelligent python voice assistant", resp_custom.lower())

if __name__ == "__main__":
    unittest.main()

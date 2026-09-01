"""
Unit tests for Phase 6 Security Audit, Logging, Error Handling, and Pipeline Polish.
Verifies secret isolation, custom command safety, friendly error outputs, and full intent routing.
"""

import unittest
from unittest.mock import patch, MagicMock
from config import Config
from nlp.intent_engine import IntentClassifier
from services.custom_service import CustomCommandService
from services.email_service import EmailService
from services.weather_service import WeatherService
from services.knowledge_service import KnowledgeService
from services.reminder_service import ReminderService
from core.command_router import CommandRouter

class TestPhase6QualityAndSecurity(unittest.TestCase):
    """Test suite for Phase 6 security, error handling, and pipeline verification."""

    def setUp(self):
        self.classifier = IntentClassifier()
        self.router = CommandRouter()

    def tearDown(self):
        ReminderService.cancel_all()

    # 1. Environment Secrets Validation & Placeholder Detection Test
    @patch.object(Config, "OPENWEATHER_API_KEY", "your_openweathermap_api_key_here")
    @patch.object(Config, "EMAIL_USERNAME", "your_test_email@gmail.com")
    @patch.object(Config, "EMAIL_PASSWORD", "your_app_password_here")
    def test_security_env_secrets_validation(self):
        secrets_status = Config.validate_secrets_loaded()
        self.assertFalse(secrets_status["weather_api_configured"])
        self.assertFalse(secrets_status["email_configured"])

    # 2. Custom Command Security Rejection Test
    def test_security_custom_command_rejections(self):
        custom_svc = CustomCommandService()
        # Test unsafe single command validation
        unsafe_exec = {
            "name": "dangerous exec",
            "phrases": ["run exec"],
            "action_type": "exec",
            "action_value": "import os; os.system('calc')"
        }
        unsafe_js_url = {
            "name": "dangerous url",
            "phrases": ["open script"],
            "action_type": "open_url",
            "action_value": "javascript:alert('hacked')"
        }
        self.assertFalse(custom_svc._validate_single_command(unsafe_exec))
        self.assertFalse(custom_svc._validate_single_command(unsafe_js_url))

    # 3. Logger Redaction / No Password Output Test
    @patch("core.logger.logging.Logger.info")
    @patch("core.logger.logging.Logger.error")
    @patch("smtplib.SMTP")
    @patch.object(Config, "EMAIL_USERNAME", "myuser@gmail.com")
    @patch.object(Config, "EMAIL_PASSWORD", "SuperSecretPassword123!")
    def test_security_logger_no_credentials(self, mock_smtp, mock_log_error, mock_log_info):
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        EmailService.send_email("recipient@example.com", "Subject", "Body")

        # Collect all logged strings
        logged_texts = []
        for call_args in mock_log_info.call_args_list + mock_log_error.call_args_list:
            args, _ = call_args
            if args:
                logged_texts.append(str(args[0]))

        # Password must NEVER appear in any log call
        for log_str in logged_texts:
            self.assertNotIn("SuperSecretPassword123!", log_str)

    # 4. Friendly Spoken Responses on Service Failure Test
    def test_error_handling_friendly_spoken_responses(self):
        # Weather unconfigured
        weather_res = WeatherService.format_weather_response({"success": False, "error_type": "missing_key"})
        self.assertEqual(weather_res, "The weather service is not configured yet.")

        # Weather city not found
        weather_404 = WeatherService.format_weather_response({"success": False, "error_type": "city_not_found"})
        self.assertEqual(weather_404, "I couldn't find weather information for that location.")

        # Email unconfigured
        email_res = EmailService.format_email_response({"success": False, "error_type": "missing_config"})
        self.assertEqual(email_res, "Email service is not configured yet.")

        # Email auth error
        email_auth = EmailService.format_email_response({"success": False, "error_type": "auth_error"})
        self.assertEqual(email_auth, "Email authentication failed. Please check your email credentials.")

    # 5. Pipeline All Intents Routing Test
    def test_pipeline_all_intents_routing(self):
        intents_to_test = [
            ("hello", "greeting"),
            ("what time is it", "get_time"),
            ("what is today's date", "get_date"),
            ("search for Python tutorials", "web_search"),
            ("what's the weather in Pune", "get_weather"),
            ("what is machine learning", "knowledge_query"),
            ("send an email to test@example.com saying hello", "send_email"),
            ("remind me in 5 minutes", "set_reminder"),
            ("exit", "exit")
        ]

        for text, expected_intent in intents_to_test:
            self.router.pending_context = None
            res = self.classifier.predict_intent(text)
            self.assertEqual(res["intent"], expected_intent, f"Classification failed for '{text}'")

if __name__ == "__main__":
    unittest.main()

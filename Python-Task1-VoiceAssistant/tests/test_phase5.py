"""
Unit tests for Phase 5 Email Automation, Timed Reminders, NLU, Entity Extraction, and Command Router.
Uses mocks for SMTP network connections, timers, and TTS speaker calls.
"""

import time
import unittest
from unittest.mock import patch, MagicMock
import smtplib
from config import Config
from nlp.intent_engine import IntentClassifier
from nlp.entity_extractor import EntityExtractor
from services.email_service import EmailService
from services.reminder_service import ReminderService
from core.command_router import CommandRouter

class TestPhase5Capabilities(unittest.TestCase):
    """Test suite for Phase 5 capabilities."""

    def setUp(self):
        self.classifier = IntentClassifier()
        self.router = CommandRouter()

    def tearDown(self):
        ReminderService.cancel_all()

    # --- EMAIL SERVICE TESTS ---

    # 1. Email Service Initializes Correctly
    def test_email_service_initialization(self):
        self.assertTrue(hasattr(EmailService, "send_email"))
        self.assertTrue(hasattr(EmailService, "format_email_response"))
        self.assertTrue(hasattr(EmailService, "validate_recipient"))

    # 2. Missing Email Configuration
    @patch.object(Config, "EMAIL_USERNAME", "")
    @patch.object(Config, "EMAIL_PASSWORD", "")
    @patch.object(Config, "SMTP_EMAIL", "")
    @patch.object(Config, "SMTP_PASSWORD", "")
    def test_email_missing_configuration(self):
        res = EmailService.send_email("test@example.com", "Test Subject", "Test Body")
        self.assertFalse(res["success"])
        self.assertEqual(res["error_type"], "missing_config")
        spoken = EmailService.format_email_response(res)
        self.assertIn("not configured yet", spoken)

    # 3. Invalid Recipient Address
    @patch.object(Config, "EMAIL_USERNAME", "sender@example.com")
    @patch.object(Config, "EMAIL_PASSWORD", "validpassword123")
    def test_email_invalid_recipient(self):
        invalid_addresses = ["invalid-email-address", "test@", "@domain.com", ""]
        for addr in invalid_addresses:
            res = EmailService.send_email(addr, "Subject", "Body")
            self.assertFalse(res["success"], f"Failed to reject invalid recipient: '{addr}'")
            self.assertEqual(res["error_type"], "invalid_recipient")
            spoken = EmailService.format_email_response(res)
            self.assertIn("Invalid recipient email address", spoken)

    # 4. SMTP Connection Failure
    @patch("smtplib.SMTP")
    @patch.object(Config, "EMAIL_USERNAME", "sender@example.com")
    @patch.object(Config, "EMAIL_PASSWORD", "validpassword123")
    def test_email_connection_failure(self, mock_smtp):
        mock_smtp.side_effect = OSError("Connection refused")
        res = EmailService.send_email("test@example.com", "Subject", "Body")
        self.assertFalse(res["success"])
        self.assertEqual(res["error_type"], "connection_error")
        spoken = EmailService.format_email_response(res)
        self.assertIn("Unable to connect to the email server", spoken)

    # 5. SMTP Authentication Failure
    @patch("smtplib.SMTP")
    @patch.object(Config, "EMAIL_USERNAME", "sender@example.com")
    @patch.object(Config, "EMAIL_PASSWORD", "wrongpassword")
    def test_email_auth_failure(self, mock_smtp):
        mock_server = MagicMock()
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, b"Authentication failed")
        mock_smtp.return_value.__enter__.return_value = mock_server

        res = EmailService.send_email("test@example.com", "Subject", "Body")
        self.assertFalse(res["success"])
        self.assertEqual(res["error_type"], "auth_error")
        spoken = EmailService.format_email_response(res)
        self.assertIn("authentication failed", spoken)

    # 6. Successful Email Sending with Mocked SMTP
    @patch("smtplib.SMTP")
    @patch.object(Config, "EMAIL_USERNAME", "sender@example.com")
    @patch.object(Config, "EMAIL_PASSWORD", "validpassword123")
    def test_email_successful_send(self, mock_smtp):
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        res = EmailService.send_email("recipient@example.com", "Project Update", "Meeting is at 5 PM")
        self.assertTrue(res["success"])
        self.assertEqual(res["recipient"], "recipient@example.com")
        mock_server.send_message.assert_called_once()
        spoken = EmailService.format_email_response(res)
        self.assertIn("Email sent successfully to recipient@example.com", spoken)

    # 7. TLS Configuration
    @patch("smtplib.SMTP")
    @patch.object(Config, "EMAIL_USERNAME", "sender@example.com")
    @patch.object(Config, "EMAIL_PASSWORD", "validpassword123")
    @patch.object(Config, "EMAIL_USE_TLS", True)
    def test_email_tls_configuration(self, mock_smtp):
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        res = EmailService.send_email("recipient@example.com", "Subject", "Body")
        self.assertTrue(res["success"])
        mock_server.starttls.assert_called_once()

    # 8. Email Intent Recognition
    def test_email_intent_recognition(self):
        phrases = [
            "send an email",
            "send an email to John",
            "email John",
            "send a message to John",
            "send an email to john@example.com",
            "send an email to Rahul saying I'll call you later"
        ]
        for phrase in phrases:
            res = self.classifier.predict_intent(phrase)
            self.assertEqual(res["intent"], "send_email", f"Failed for phrase: '{phrase}'")

    # 9. Email Address Extraction
    def test_email_address_extraction(self):
        res = self.classifier.predict_intent("send an email to test@example.com saying meeting is at 5 PM")
        self.assertEqual(res["intent"], "send_email")
        self.assertEqual(res["entities"].get("email_address"), "test@example.com")

    # 10. Email Body Extraction
    def test_email_body_extraction(self):
        res = self.classifier.predict_intent("send an email to test@example.com saying meeting is at 5 PM")
        self.assertEqual(res["intent"], "send_email")
        self.assertEqual(res["entities"].get("body"), "meeting is at 5 PM")

    # 11. Email Follow-up Context
    @patch("services.email_service.EmailService.send_email")
    def test_email_followup_context(self, mock_send_email):
        mock_send_email.return_value = {
            "success": True,
            "recipient": "test@example.com",
            "subject": "Voice Assistant Message",
            "error_type": None,
            "error": None
        }
        # Step A: User says "send an email" -> prompts "Who should I send it to?"
        resp1, exit1, _ = self.router.process_command("send an email")
        self.assertFalse(exit1)
        self.assertIn("Who should I send it to", resp1)

        # Step B: User provides email address -> prompts "What should the email say?"
        resp2, exit2, _ = self.router.process_command("test@example.com")
        self.assertFalse(exit2)
        self.assertIn("What should the email say", resp2)

        # Step C: User provides body -> sends email
        resp3, exit3, _ = self.router.process_command("Tell them the meeting is at 5 PM")
        self.assertFalse(exit3)
        self.assertIn("Email sent successfully", resp3)

    # 12. Existing Commands Remain Functional
    def test_existing_commands_remain_functional(self):
        # Greeting
        resp_g, _, nlu_g = self.router.process_command("hello")
        self.assertEqual(nlu_g["intent"], "greeting")

        # Time
        resp_t, _, nlu_t = self.router.process_command("what time is it")
        self.assertEqual(nlu_t["intent"], "get_time")

        # Date
        resp_d, _, nlu_d = self.router.process_command("what is today's date")
        self.assertEqual(nlu_d["intent"], "get_date")

    # --- REMINDER SERVICE TESTS ---

    # 13. Reminder Service Initializes
    def test_reminder_service_initialization(self):
        self.assertTrue(hasattr(ReminderService, "set_reminder"))
        self.assertTrue(hasattr(ReminderService, "parse_duration"))

    # 14. Parse Seconds
    def test_parse_duration_seconds(self):
        secs = ReminderService.parse_duration("10", "seconds")
        self.assertEqual(secs, 10.0)
        secs_short = ReminderService.parse_duration("30", "sec")
        self.assertEqual(secs_short, 30.0)

    # 15. Parse Minutes
    def test_parse_duration_minutes(self):
        mins = ReminderService.parse_duration("5", "minutes")
        self.assertEqual(mins, 300.0)
        mins_short = ReminderService.parse_duration("10", "min")
        self.assertEqual(mins_short, 600.0)

    # 16. Parse Hours
    def test_parse_duration_hours(self):
        hrs = ReminderService.parse_duration("2", "hours")
        self.assertEqual(hrs, 7200.0)

    # 17. Parse "An Hour" / "A Minute"
    def test_parse_duration_words(self):
        an_hr = ReminderService.parse_duration("an", "hour")
        self.assertEqual(an_hr, 3600.0)
        a_min = ReminderService.parse_duration("a", "minute")
        self.assertEqual(a_min, 60.0)

    # 18. Reminder Intent Recognition
    def test_reminder_intent_recognition(self):
        phrases = [
            "remind me in 5 minutes",
            "set a reminder for 10 minutes",
            "remind me to drink water in 30 minutes",
            "remind me to call Rahul in an hour"
        ]
        for phrase in phrases:
            res = self.classifier.predict_intent(phrase)
            self.assertEqual(res["intent"], "set_reminder", f"Failed for phrase: '{phrase}'")

    # 19. Duration Extraction
    def test_reminder_duration_extraction(self):
        res = self.classifier.predict_intent("remind me to drink water in 30 minutes")
        self.assertEqual(res["intent"], "set_reminder")
        self.assertEqual(res["entities"].get("duration_value"), "30")
        self.assertIn("minute", res["entities"].get("duration_unit"))
        self.assertEqual(res["entities"].get("duration_seconds"), 1800.0)

    # 20. Reminder Message Extraction
    def test_reminder_message_extraction(self):
        res = self.classifier.predict_intent("remind me to drink water in 30 minutes")
        self.assertEqual(res["intent"], "set_reminder")
        self.assertEqual(res["entities"].get("reminder_message"), "drink water")

    # 21. Reminder Scheduling
    @patch("threading.Timer")
    def test_reminder_scheduling(self, mock_timer_cls):
        mock_timer_inst = MagicMock()
        mock_timer_cls.return_value = mock_timer_inst

        resp = ReminderService.set_reminder(300.0, "take medicine")
        self.assertIn("Reminder set for 5 minutes from now", resp)
        self.assertIn("take medicine", resp)
        mock_timer_cls.assert_called_once()
        mock_timer_inst.start.assert_called_once()

    # 22. Multiple Reminders
    @patch("threading.Timer")
    def test_multiple_reminders(self, mock_timer_cls):
        mock_timer_cls.side_effect = lambda dur, func, args: MagicMock()

        resp1 = ReminderService.set_reminder(30.0, "drink water")
        resp2 = ReminderService.set_reminder(120.0, "check email")

        self.assertIn("drink water", resp1)
        self.assertIn("check email", resp2)
        self.assertEqual(mock_timer_cls.call_count, 2)

    # 23. Reminder Expiration Callback
    def test_reminder_expiration_callback(self):
        callback_mock = MagicMock()

        # Schedule a 0.05 second timer for fast deterministic testing
        ReminderService.set_reminder(0.05, "test callback", callback=callback_mock)
        time.sleep(0.15)

        callback_mock.assert_called_once_with("test callback")

    # 24. TTS Alert Triggered
    def test_reminder_tts_alert_triggered(self):
        mock_tts = MagicMock()

        ReminderService.set_reminder(0.05, "drink water", tts_engine=mock_tts)
        time.sleep(0.15)

        mock_tts.speak.assert_called_once_with("Reminder: drink water")

    # 25. Main Application Continues After Reminder
    def test_main_app_continues_after_reminder(self):
        mock_tts = MagicMock()
        ReminderService.set_reminder(0.05, "fast reminder", tts_engine=mock_tts)

        # Immediately send another command without blocking
        resp, exit_flag, nlu_res = self.router.process_command("what time is it")
        self.assertFalse(exit_flag)
        self.assertEqual(nlu_res["intent"], "get_time")
        self.assertIn("The current time is", resp)

        time.sleep(0.15)
        mock_tts.speak.assert_called_once_with("Reminder: fast reminder")

    # 26. Invalid Duration Handling
    def test_reminder_invalid_duration_handling(self):
        resp = ReminderService.set_reminder(-5.0, "invalid timer")
        self.assertIn("valid future time", resp)

if __name__ == "__main__":
    unittest.main()

"""
Unit tests for Phase 2 Core Speech I/O, NLU, Services, and Error Handling.
Mocks hardware dependencies (microphone and pyttsx3 speaker).
"""

import unittest
from unittest.mock import MagicMock, patch
from config import Config
from nlp.intent_engine import IntentClassifier
from services.datetime_service import DateTimeService
from services.search_service import SearchService
from core.stt import SpeechToTextEngine
from core.tts import TextToSpeechEngine
import speech_recognition as sr

class TestPhase2Capabilities(unittest.TestCase):
    """Test suite for Phase 2 voice assistant capabilities."""

    def setUp(self):
        self.classifier = IntentClassifier()

    # 1. Greeting Intent Classification
    def test_greeting_intent_variations(self):
        phrases = ["hello", "hi", "hey", "good morning", "good afternoon", "greetings"]
        for phrase in phrases:
            intent, score = self.classifier.predict(phrase)
            self.assertEqual(intent, "greeting", f"Failed for phrase: '{phrase}'")

    # 2. Time Intent Classification
    def test_time_intent_variations(self):
        phrases = [
            "what time is it",
            "tell me the time",
            "what's the current time",
            "can you tell me the time"
        ]
        for phrase in phrases:
            intent, score = self.classifier.predict(phrase)
            self.assertEqual(intent, "get_time", f"Failed for phrase: '{phrase}'")

    # 3. Date Intent Classification
    def test_date_intent_variations(self):
        phrases = [
            "what is today's date",
            "what's the date",
            "tell me today's date",
            "what day is it"
        ]
        for phrase in phrases:
            intent, score = self.classifier.predict(phrase)
            self.assertEqual(intent, "get_date", f"Failed for phrase: '{phrase}'")

    # 4. Web Search Intent Classification
    def test_web_search_intent_variations(self):
        phrases = [
            "search for Python tutorials",
            "search machine learning",
            "google artificial intelligence",
            "look up weather in Pune",
            "search for Python machine learning tutorials"
        ]
        for phrase in phrases:
            intent, score = self.classifier.predict(phrase)
            self.assertEqual(intent, "web_search", f"Failed for phrase: '{phrase}'")

    # 5. Exit Intent Classification
    def test_exit_intent_variations(self):
        phrases = ["exit", "quit", "stop", "goodbye", "close assistant"]
        for phrase in phrases:
            intent, score = self.classifier.predict(phrase)
            self.assertEqual(intent, "exit", f"Failed for phrase: '{phrase}'")

    # 6. Search Query Extraction
    def test_search_query_extraction(self):
        test_cases = [
            ("search for Python machine learning tutorials", "Python machine learning tutorials"),
            ("search machine learning", "machine learning"),
            ("google artificial intelligence", "artificial intelligence"),
            ("look up weather in Pune", "weather in Pune"),
            ("can you search the web for climate news", "climate news"),
            ("Python decorators", "Python decorators")
        ]

        for input_text, expected_query in test_cases:
            query = SearchService.extract_search_query(input_text)
            self.assertEqual(query, expected_query, f"Failed extracting query from: '{input_text}'")

    # 7. Unknown Intent Handling
    def test_unknown_intent_handling(self):
        intent, score = self.classifier.predict("asdfghjkl random unsupported phrase 999")
        self.assertEqual(intent, "unknown")

    # 8. STT Failure Handling & Mocks
    @patch("speech_recognition.Microphone")
    @patch("speech_recognition.Recognizer.adjust_for_ambient_noise")
    @patch("speech_recognition.Recognizer.listen")
    @patch("speech_recognition.Recognizer.recognize_google")
    def test_stt_success_and_failures(self, mock_recognize, mock_listen, mock_adjust, mock_mic):
        mock_mic_instance = MagicMock()
        mock_mic.return_value.__enter__.return_value = mock_mic_instance

        # Mock successful speech recognition
        mock_recognize.return_value = "hello assistant"
        stt = SpeechToTextEngine()
        stt.microphone_available = True
        
        result = stt.listen(timeout=1.0)
        self.assertEqual(result, "hello assistant")

        # Mock Timeout
        mock_listen.side_effect = sr.WaitTimeoutError()
        result_timeout = stt.listen(timeout=1.0)
        self.assertEqual(result_timeout, "")

        # Mock Unknown Value (Unintelligible speech)
        mock_listen.side_effect = None
        mock_recognize.side_effect = sr.UnknownValueError()
        result_unknown = stt.listen(timeout=1.0)
        self.assertEqual(result_unknown, "")

        # Mock Request Error (Network / Service Failure)
        mock_recognize.side_effect = sr.RequestError("Network error")
        result_request_error = stt.listen(timeout=1.0)
        self.assertEqual(result_request_error, "")

    # 9. TTS Interface Behavior & Error Mocks
    @patch("pyttsx3.init")
    def test_tts_interface_behavior(self, mock_pyttsx3_init):
        mock_engine = MagicMock()
        mock_pyttsx3_init.return_value = mock_engine

        tts = TextToSpeechEngine()
        self.assertTrue(tts.is_initialized)

        # Test normal speak call
        tts.speak("Testing Text to Speech", print_output=False)
        mock_engine.say.assert_called_with("Testing Text to Speech")
        mock_engine.runAndWait.assert_called()

        # Test empty text handling
        mock_engine.reset_mock()
        tts.speak("", print_output=False)
        mock_engine.say.assert_not_called()

if __name__ == "__main__":
    unittest.main()

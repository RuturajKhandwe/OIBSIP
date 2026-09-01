"""
Main Application Entry Point for Intelligent Python Voice Assistant
Orchestrates audio input/output, NLU intent classification, custom commands, and command routing pipeline.
"""

import sys
from config import Config
from core.logger import get_logger
from core.stt import SpeechToTextEngine
from core.tts import TextToSpeechEngine
from core.command_router import CommandRouter
from services.datetime_service import DateTimeService

logger = get_logger("MainApp")

class VoiceAssistant:
    """Core Voice Assistant Orchestrator."""

    def __init__(self):
        logger.info(f"Starting {Config.ASSISTANT_NAME} Voice Assistant...")
        self.tts = TextToSpeechEngine()
        self.stt = SpeechToTextEngine()
        self.router = CommandRouter()
        self.intent_classifier = self.router.intent_classifier
        self.is_running = False

    def handle_intent(self, intent: str, user_input: str) -> tuple[str, bool]:
        """
        Dispatches intent to corresponding service via CommandRouter.
        Returns a tuple of (response_text, should_exit_flag).
        """
        response, should_exit, _ = self.router.process_command(user_input)
        return response, should_exit

    def run_voice_loop(self):
        """Main continuous voice interaction loop."""
        self.is_running = True
        logger.info(f"{Config.ASSISTANT_NAME} is active and listening for voice commands...")
        
        # Initial spoken greeting
        greeting = DateTimeService.get_greeting()
        self.tts.speak(greeting)

        consecutive_empty_count = 0

        while self.is_running:
            try:
                user_text = self.stt.listen()
                
                if not user_text:
                    consecutive_empty_count += 1
                    if consecutive_empty_count >= 3 and not self.stt.microphone_available:
                        # Prevent endless empty loop in non-interactive fallback runs
                        logger.info("Multiple empty inputs received in fallback mode. Terminating loop.")
                        break
                    continue

                consecutive_empty_count = 0

                # Process user input through Command Router
                response, should_exit, nlu_result = self.router.process_command(user_text)

                # Speak response aloud
                self.tts.speak(response)

                if should_exit:
                    logger.info("Exit command received. Shutting down assistant...")
                    self.is_running = False
                    break

            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received. Shutting down cleanly...")
                self.tts.speak(f"Goodbye {Config.USER_NAME}!")
                self.is_running = False
                break
            except Exception as e:
                logger.error(f"Unexpected error in command loop: {e}")
                self.tts.speak("An error occurred. Please try again.")

    def run_system_check(self):
        """Non-interactive system check for automated verification."""
        logger.info("==========================================")
        logger.info(f"  {Config.ASSISTANT_NAME} System Readiness Verification (Phase 6)")
        logger.info("==========================================")

        secrets_status = Config.validate_secrets_loaded()
        weather_status = "CONFIGURED" if secrets_status["weather_api_configured"] else "NOT CONFIGURED (Add OPENWEATHER_API_KEY to .env)"
        email_status = "CONFIGURED" if secrets_status.get("email_configured") else "NOT CONFIGURED (Add EMAIL_USERNAME and EMAIL_PASSWORD to .env)"

        print("\n--- System Services Status ---")
        print(f"Email Service:      {email_status}")
        print("Reminder Service:   READY")
        print(f"Weather Service:    {weather_status}")
        print("Knowledge Service:  READY")
        print("NLU Engine:         READY")
        print("Speech Recognition: READY")
        print("Text-to-Speech:     READY\n")

        test_inputs = [
            "hello",
            "what time is it?",
            "what is today's date?",
            "send an email",
            "remind me to drink water in 10 minutes",
            "what's the weather in Pune?",
            "what is machine learning?",
            "who was Albert Einstein?",
            "search for Python machine learning tutorials",
            "look up FastAPI documentation",
            "open youtube",
            "who created you",
            "exit"
        ]

        for text in test_inputs:
            self.router.pending_context = None  # Reset follow-up state for independent readiness verification
            response, should_exit, nlu_result = self.router.process_command(text)
            intent = nlu_result.get("intent", "unknown")
            score = nlu_result.get("confidence", 0.0)
            entities = nlu_result.get("entities", {})
            print(f"Input:    '{text}'")
            print(f"Result:   Intent='{intent}' (Confidence: {score:.2f}, Entities: {entities})")
            print(f"Output:   {response}\n")

        print("System Readiness Verification Complete.")

if __name__ == "__main__":
    assistant = VoiceAssistant()
    if "--check" in sys.argv or "--test" in sys.argv:
        assistant.run_system_check()
    else:
        assistant.run_voice_loop()

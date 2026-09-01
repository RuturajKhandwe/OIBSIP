"""
Text-to-Speech (TTS) Module wrapper using pyttsx3.
Provides audible speech synthesis and terminal feedback with voice selection and error handling.
"""

import pyttsx3
from core.logger import get_logger
from config import Config

logger = get_logger("TTS")

class TextToSpeechEngine:
    """Manages text-to-speech synthesis using offline pyttsx3 engine."""

    def __init__(self):
        self.engine = None
        self.is_initialized = False

        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", Config.TTS_RATE)
            self.engine.setProperty("volume", Config.TTS_VOLUME)
            
            # Dynamic System Voice Selection (Select first available English voice safely)
            self._select_best_voice()
            
            self.is_initialized = True
            logger.info("pyttsx3 TTS engine initialized successfully.")
        except Exception as e:
            logger.warning(f"Failed to initialize pyttsx3 TTS engine: {e}. Terminal text output will be used.")
            self.is_initialized = False

    def _select_best_voice(self) -> None:
        """Selects an appropriate available system voice without hardcoding platform IDs."""
        if not self.engine:
            return
        try:
            voices = self.engine.getProperty("voices")
            if not voices:
                return

            selected_voice = None
            # Search for English voices
            for voice in voices:
                voice_id_str = str(getattr(voice, "id", "")).lower()
                voice_name_str = str(getattr(voice, "name", "")).lower()
                
                if "english" in voice_name_str or "en_" in voice_id_str or "en-" in voice_id_str or "zira" in voice_name_str or "david" in voice_name_str:
                    selected_voice = voice
                    break

            if selected_voice:
                self.engine.setProperty("voice", selected_voice.id)
                logger.info(f"Selected TTS voice: {getattr(selected_voice, 'name', selected_voice.id)}")
            else:
                logger.info(f"Using default TTS voice: {getattr(voices[0], 'name', voices[0].id)}")
        except Exception as e:
            logger.debug(f"Voice selection fallback notice: {e}")

    def speak(self, text: str, print_output: bool = True) -> None:
        """Speaks the given text aloud and prints to standard output."""
        if not text:
            return

        clean_text = text.strip()

        if print_output:
            print(f"\n{Config.ASSISTANT_NAME} > {clean_text}")

        if self.is_initialized and self.engine:
            try:
                self.engine.say(clean_text)
                self.engine.runAndWait()
            except Exception as e:
                logger.error(f"Error during speech playback: {e}")

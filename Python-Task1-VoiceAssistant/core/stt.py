"""
Speech-to-Text (STT) Module wrapper using speech_recognition.
Handles microphone audio capture, noise adjustment, and speech recognition with robust error handling.
"""

from typing import Optional
import speech_recognition as sr
from core.logger import get_logger
from config import Config

logger = get_logger("STT")

class SpeechToTextEngine:
    """Manages audio capture and Speech-to-Text conversion."""

    def __init__(self, device_index: Optional[int] = None):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = Config.STT_ENERGY_THRESHOLD
        self.recognizer.pause_threshold = Config.STT_PAUSE_THRESHOLD
        self.device_index = device_index if device_index is not None else Config.STT_MICROPHONE_INDEX
        self.microphone_available = False

        self._check_microphone_availability()

    def _check_microphone_availability(self) -> None:
        """Inspects system input audio devices to determine microphone availability."""
        try:
            mic_list = sr.Microphone.list_microphone_names()
            if mic_list:
                self.microphone_available = True
                device_info = f"device index {self.device_index}" if self.device_index is not None else "default device"
                logger.info(f"Microphone detected using {device_info}. ({len(mic_list)} total input devices found)")
            else:
                logger.warning("No input microphone devices detected. STT will fall back to keyboard prompt.")
                self.microphone_available = False
        except Exception as e:
            logger.warning(f"Unable to query microphone devices: {e}. STT will fall back to keyboard prompt.")
            self.microphone_available = False

    def listen(self, timeout: Optional[float] = None, phrase_time_limit: Optional[float] = None) -> str:
        """
        Listens for audio from the microphone and returns recognized clean text.
        Returns an empty string if speech is unintelligible, timed out, or on error.
        If microphone is unavailable, falls back gracefully to a terminal text prompt.
        """
        listen_timeout = timeout if timeout is not None else Config.STT_TIMEOUT
        time_limit = phrase_time_limit if phrase_time_limit is not None else Config.STT_PHRASE_TIME_LIMIT

        if not self.microphone_available:
            try:
                logger.info("Microphone unavailable. Prompting user via terminal fallback...")
                user_text = input("\nUser (Text Fallback) > ").strip()
                return user_text
            except (EOFError, KeyboardInterrupt):
                logger.info("User cancelled terminal input.")
                return "exit"
            except Exception as e:
                logger.error(f"Error during terminal fallback input: {e}")
                return ""

        try:
            mic_kwargs = {}
            if self.device_index is not None:
                mic_kwargs["device_index"] = self.device_index

            with sr.Microphone(**mic_kwargs) as source:
                logger.info("Listening for command...")
                # Ambient noise calibration
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=listen_timeout, phrase_time_limit=time_limit)

            logger.info("Processing speech recognition...")
            text = self.recognizer.recognize_google(audio, language=Config.STT_LANGUAGE)
            logger.info(f"Speech Recognized: '{text}'")
            return text.strip()

        except sr.WaitTimeoutError:
            logger.info("No speech detected within timeout limit.")
            return ""
        except sr.UnknownValueError:
            logger.warning("Speech was unintelligible or could not be decoded.")
            return ""
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error (Network/API issue): {e}")
            return ""
        except Exception as e:
            logger.error(f"Unexpected error in STT module: {e}")
            return ""

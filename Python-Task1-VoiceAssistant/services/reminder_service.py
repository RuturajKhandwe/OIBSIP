"""
Reminder Service Module for Intelligent Python Voice Assistant.
Handles background thread timers and audible TTS alerts for scheduled reminders.
"""

import re
import threading
from typing import Optional, Callable, Dict, Any, List
from core.logger import get_logger
from core.tts import TextToSpeechEngine

logger = get_logger("ReminderService")

class ReminderService:
    """Timed reminder and audible alert engine."""

    # Active running timer references for tracking / testing
    _active_timers: List[threading.Timer] = []
    _lock = threading.Lock()

    @classmethod
    def parse_duration(cls, val_str: str, unit_str: str) -> float:
        """
        Parses numerical value and duration unit into total seconds.
        Supports phrases like 'an hour', 'a minute', '10 sec', '5 minutes'.
        """
        val_clean = (val_str or "").strip().lower()
        unit_clean = (unit_str or "").strip().lower()

        # Handle words like 'an', 'a', 'one'
        if val_clean in ("an", "a", "one"):
            num = 1.0
        else:
            try:
                num = float(val_clean)
            except ValueError:
                num = 1.0

        if "hour" in unit_clean or unit_clean in ("hr", "hrs"):
            return num * 3600.0
        elif "min" in unit_clean:
            return num * 60.0
        elif "sec" in unit_clean:
            return num
        else:
            # Default to minutes if unspecified
            return num * 60.0

    @classmethod
    def format_duration_string(cls, seconds: float) -> str:
        """Converts total seconds into human-readable duration text."""
        if seconds < 60:
            secs = int(seconds) if seconds == int(seconds) else round(seconds, 1)
            unit = "second" if secs == 1 else "seconds"
            return f"{secs} {unit}"
        elif seconds < 3600:
            mins = int(seconds / 60) if (seconds / 60) == int(seconds / 60) else round(seconds / 60, 1)
            unit = "minute" if mins == 1 else "minutes"
            return f"{mins} {unit}"
        else:
            hrs = int(seconds / 3600) if (seconds / 3600) == int(seconds / 3600) else round(seconds / 3600, 1)
            unit = "hour" if hrs == 1 else "hours"
            return f"{hrs} {unit}"

    @classmethod
    def _trigger_reminder(cls, message: str, tts_engine: Optional[TextToSpeechEngine] = None, callback: Optional[Callable[[str], None]] = None) -> None:
        """
        Callback executed when a scheduled reminder timer expires.
        Logs the reminder and triggers an audible TTS alert safely.
        """
        logger.info(f"[ReminderService] Reminder expired alert: '{message}'")

        try:
            if callback:
                callback(message)
            else:
                engine = tts_engine or TextToSpeechEngine()
                engine.speak(f"Reminder: {message}")
        except Exception as e:
            logger.error(f"[ReminderService] Error speaking reminder alert: {e}")

    @classmethod
    def set_reminder(cls, duration_seconds: float, message: Optional[str] = None, tts_engine: Optional[TextToSpeechEngine] = None, callback: Optional[Callable[[str], None]] = None) -> str:
        """
        Schedules an asynchronous background timer for a reminder.
        Returns a confirmation message string immediately without blocking.
        """
        if duration_seconds <= 0:
            logger.warning("[ReminderService] Negative or zero duration specified for reminder.")
            return "Please specify a valid future time for the reminder."

        reminder_msg = (message or "Your reminder").strip()
        duration_text = cls.format_duration_string(duration_seconds)

        # Create background Timer daemon thread
        timer = threading.Timer(
            duration_seconds,
            cls._trigger_reminder,
            args=(reminder_msg, tts_engine, callback)
        )
        timer.daemon = True

        with cls._lock:
            cls._active_timers.append(timer)

        timer.start()

        logger.info(f"[ReminderService] Scheduled background reminder in {duration_seconds}s: '{reminder_msg}'")
        return f"Reminder set for {duration_text} from now: '{reminder_msg}'."

    @classmethod
    def cancel_all(cls) -> None:
        """Helper to cancel all active timers (used primarily in tests/cleanup)."""
        with cls._lock:
            for timer in cls._active_timers:
                timer.cancel()
            cls._active_timers.clear()

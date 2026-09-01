"""
Date, Time, and Greeting Service.
"""

import datetime
from config import Config

class DateTimeService:
    """Handles time, date, and time-based greetings."""

    @staticmethod
    def get_greeting() -> str:
        """Returns time-appropriate greeting."""
        hour = datetime.datetime.now().hour
        if 5 <= hour < 12:
            time_of_day = "Good morning"
        elif 12 <= hour < 18:
            time_of_day = "Good afternoon"
        else:
            time_of_day = "Good evening"
            
        return f"{time_of_day}, {Config.USER_NAME}! How can I assist you today?"

    @staticmethod
    def get_current_time() -> str:
        """Returns formatted string of current local time."""
        now = datetime.datetime.now()
        return f"The current time is {now.strftime('%I:%M %p')}."

    @staticmethod
    def get_current_date() -> str:
        """Returns formatted string of today's date."""
        now = datetime.datetime.now()
        return f"Today is {now.strftime('%A, %B %d, %Y')}."

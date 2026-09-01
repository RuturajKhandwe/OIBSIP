"""
Entity Extractor Module for Intelligent Python Voice Assistant.
Extracts structured entity parameters (e.g. search queries, cities, topics, emails, reminders) from natural language utterances.
"""

import re
from typing import Dict, Any
from core.logger import get_logger

logger = get_logger("EntityExtractor")

class EntityExtractor:
    """Extracts named entities and command arguments from spoken text."""

    SEARCH_PREFIX_PATTERNS = [
        r"^(can you\s+)?search\s+for\s+",
        r"^(can you\s+)?search\s+the\s+web\s+for\s+",
        r"^(can you\s+)?search\s+online\s+for\s+",
        r"^(can you\s+)?look\s+up\s+",
        r"^(can you\s+)?google\s+search\s+",
        r"^(can you\s+)?google\s+",
        r"^search\s+",
        r"^find\s+information\s+about\s+",
        r"^find\s+information\s+on\s+",
        r"^find\s+info\s+about\s+",
        r"^find\s+info\s+on\s+",
        r"^find\s+",
        r"^look\s+for\s+",
    ]

    KNOWLEDGE_PREFIX_PATTERNS = [
        r"^(can you\s+)?tell me about\s+",
        r"^(can you\s+)?explain\s+to me\s+",
        r"^(can you\s+)?explain\s+",
        r"^what\s+is\s+a\s+",
        r"^what\s+is\s+an\s+",
        r"^what\s+is\s+",
        r"^what\s+are\s+",
        r"^who\s+was\s+a\s+",
        r"^who\s+was\s+",
        r"^who\s+is\s+a\s+",
        r"^who\s+is\s+",
        r"^definition\s+of\s+",
        r"^define\s+",
    ]

    CITY_PREPOSITION_PATTERNS = [
        r"\b(?:in|for|at)\s+([A-Za-z\s]+?)(?:\s+today|\s+right now|\?|\.|$)",
    ]

    WEATHER_KEYWORDS = {"weather", "temperature", "temp", "hot", "cold", "rain", "raining", "forecast", "report", "climate"}
    EMAIL_REGEX = re.compile(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")

    @classmethod
    def extract_entities(cls, text: str, intent: str) -> Dict[str, Any]:
        """
        Extracts structured entities dictionary based on the classified intent and text.
        Returns a dict of extracted parameter keys and values.
        """
        entities: Dict[str, Any] = {}

        if not text or not text.strip():
            return entities

        clean_text = text.strip()

        if intent == "web_search":
            query = cls._extract_search_query(clean_text)
            if query:
                entities["query"] = query

        elif intent == "get_weather":
            city = cls._extract_city_name(clean_text)
            if city:
                entities["city"] = city

        elif intent == "knowledge_query":
            topic = cls._extract_knowledge_topic(clean_text)
            if topic:
                entities["topic"] = topic

        elif intent == "send_email":
            email_entities = cls._extract_email_entities(clean_text)
            entities.update(email_entities)

        elif intent == "set_reminder":
            reminder_entities = cls._extract_reminder_entities(clean_text)
            entities.update(reminder_entities)

        return entities

    @classmethod
    def _extract_search_query(cls, text: str) -> str:
        """Strips command prefixes to yield the search query target."""
        for pattern in cls.SEARCH_PREFIX_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted = text[match.end():].strip()
                if extracted:
                    return extracted
        return text

    @classmethod
    def _extract_city_name(cls, text: str) -> str:
        """Extracts target city name from weather query phrases if present."""
        clean_text = text.strip()

        for pattern in cls.CITY_PREPOSITION_PATTERNS:
            match = re.search(pattern, clean_text, re.IGNORECASE)
            if match:
                city = match.group(1).strip()
                city = re.sub(r"[^\w\s]", "", city).strip()
                if city and city.lower() not in cls.WEATHER_KEYWORDS:
                    return city

        match = re.search(r"\bin\s+([A-Za-z\s]+)$", clean_text, re.IGNORECASE)
        if match:
            city = match.group(1).strip()
            city = re.sub(r"[^\w\s]", "", city).strip()
            if city:
                return city

        return ""

    @classmethod
    def _extract_knowledge_topic(cls, text: str) -> str:
        """Strips question prefixes to isolate knowledge topic query."""
        clean_text = text.strip().rstrip("?.").strip()

        for pattern in cls.KNOWLEDGE_PREFIX_PATTERNS:
            match = re.search(pattern, clean_text, re.IGNORECASE)
            if match:
                extracted = clean_text[match.end():].strip()
                if extracted:
                    return extracted

        return clean_text

    @classmethod
    def _extract_email_entities(cls, text: str) -> Dict[str, Any]:
        """Extracts email_address, recipient, subject, and body from utterance."""
        result: Dict[str, Any] = {}
        clean_text = text.strip()

        # Check for explicit email address
        email_match = cls.EMAIL_REGEX.search(clean_text)
        if email_match:
            email_addr = email_match.group(1).strip()
            result["email_address"] = email_addr
            result["recipient"] = email_addr

        # Check for recipient name if no explicit email address
        if "recipient" not in result:
            name_match = re.search(r"\b(?:to|email)\s+([A-Za-z]+)\b", clean_text, re.IGNORECASE)
            if name_match:
                name = name_match.group(1).strip()
                ignored_words = {"an", "a", "email", "me", "my", "saying", "and", "regarding", "message"}
                if name.lower() not in ignored_words:
                    result["recipient"] = name

        # Check for body content
        body_match = re.search(r"\b(?:saying|and tell him|and tell her|and tell them|that|regarding)\s+(.+)$", clean_text, re.IGNORECASE)
        if body_match:
            body_text = body_match.group(1).strip().rstrip(".")
            if body_text:
                result["body"] = body_text

        return result

    @classmethod
    def _extract_reminder_entities(cls, text: str) -> Dict[str, Any]:
        """Extracts duration_value, duration_unit, duration_seconds, and reminder_message."""
        result: Dict[str, Any] = {}
        clean_text = text.strip()

        # Extract duration: e.g. "in 5 minutes", "for 10 seconds", "in an hour"
        dur_match = re.search(r"\b(?:in|for)\s+(an?|\d+(?:\.\d+)?)\s*(seconds?|secs?|minutes?|mins?|hours?|hrs?)\b", clean_text, re.IGNORECASE)
        if dur_match:
            val_str = dur_match.group(1).strip()
            unit_str = dur_match.group(2).strip()
            result["duration_value"] = val_str
            result["duration_unit"] = unit_str

            # Parse total seconds using ReminderService helper logic
            from services.reminder_service import ReminderService
            result["duration_seconds"] = ReminderService.parse_duration(val_str, unit_str)

        # Extract reminder message: e.g. "remind me to drink water in 30 minutes"
        msg_match = re.search(r"\bremind me\s+(?:to\s+)?(.+?)\s+(?:in|for)\b", clean_text, re.IGNORECASE)
        if msg_match:
            msg_text = msg_match.group(1).strip()
            ignored_msg = {"to", "me", "a reminder", "reminder"}
            if msg_text and msg_text.lower() not in ignored_msg:
                result["reminder_message"] = msg_text

        return result

"""
Knowledge Service Module for Intelligent Python Voice Assistant.
Answers general knowledge questions using Wikipedia public API with concise summaries.
"""

import re
from typing import Dict, Any, Optional
import requests
from core.logger import get_logger

logger = get_logger("KnowledgeService")

class KnowledgeService:
    """General Knowledge QA Service using Wikipedia REST API."""

    WIKIPEDIA_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/"
    USER_AGENT = "NovaVoiceAssistant/1.0 (Python Intelligent Voice Assistant)"

    QUESTION_PREFIX_PATTERNS = [
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

    @classmethod
    def extract_topic(cls, text: str) -> str:
        """
        Strips question prefix words to isolate the target query topic.
        Example: 'what is machine learning' -> 'machine learning'
        """
        if not text or not text.strip():
            return ""

        clean_text = text.strip().rstrip("?.").strip()

        for pattern in cls.QUESTION_PREFIX_PATTERNS:
            match = re.search(pattern, clean_text, re.IGNORECASE)
            if match:
                extracted = clean_text[match.end():].strip()
                if extracted:
                    return extracted

        return clean_text

    @classmethod
    def _truncate_extract(cls, text: str, max_sentences: int = 2) -> str:
        """Truncates long article extracts to 1-2 concise sentences for TTS."""
        if not text:
            return ""

        # Remove parenthetical pronunciation guides or citations if any
        cleaned = re.sub(r"\s*\([^)]*\)", "", text)
        cleaned = re.sub(r"\s*\[[^\]]*\]", "", cleaned)

        # Split into sentences
        sentences = re.split(r"(?<=[.!?])\s+", cleaned.strip())
        selected = sentences[:max_sentences]
        result = " ".join(selected).strip()

        return result

    @classmethod
    def query_knowledge(cls, query: str) -> Dict[str, Any]:
        """
        Performs a knowledge lookup for a topic or natural language question.
        Returns a structured result dictionary.
        """
        if not query or not query.strip():
            logger.warning("[KnowledgeService] Empty query received.")
            return {
                "success": False,
                "topic": "",
                "answer": "Please provide a topic to look up.",
                "error_type": "empty_query"
            }

        raw_query = query.strip()
        topic = cls.extract_topic(raw_query)

        if not topic:
            topic = raw_query

        logger.info(f"[KnowledgeService] Processing knowledge query for topic: '{topic}' (from input: '{raw_query}')")

        headers = {
            "User-Agent": cls.USER_AGENT,
            "Accept": "application/json"
        }

        # Format title for Wikipedia URL (replace spaces with underscores)
        encoded_title = requests.utils.quote(topic.replace(" ", "_"))
        url = f"{cls.WIKIPEDIA_SUMMARY_URL}{encoded_title}"

        try:
            response = requests.get(url, headers=headers, timeout=5.0)

            if response.status_code == 200:
                data = response.json()
                page_type = data.get("type", "")

                if page_type == "disambiguation":
                    logger.info(f"[KnowledgeService] Topic '{topic}' returned disambiguation page.")
                    extract = data.get("extract", "")
                    short_answer = cls._truncate_extract(extract, max_sentences=2) or f"'{topic}' refers to multiple topics."
                    return {
                        "success": True,
                        "topic": topic,
                        "answer": short_answer,
                        "error_type": None
                    }

                extract = data.get("extract", "")
                if extract:
                    short_answer = cls._truncate_extract(extract, max_sentences=2)
                    logger.info(f"[KnowledgeService] Knowledge lookup successful for topic: '{topic}'")
                    return {
                        "success": True,
                        "topic": data.get("title", topic),
                        "answer": short_answer,
                        "error_type": None
                    }
                else:
                    logger.warning(f"[KnowledgeService] Page found for '{topic}' but contains no extract.")
                    return {
                        "success": False,
                        "topic": topic,
                        "answer": f"I couldn't find detailed information about {topic}.",
                        "error_type": "no_result"
                    }

            elif response.status_code == 404:
                logger.info(f"[KnowledgeService] No Wikipedia entry found for '{topic}' (HTTP 404)")
                return {
                    "success": False,
                    "topic": topic,
                    "answer": f"I couldn't find information about {topic}.",
                    "error_type": "no_result"
                }

            else:
                logger.error(f"[KnowledgeService] Wikipedia API status code {response.status_code} for topic '{topic}'")
                return {
                    "success": False,
                    "topic": topic,
                    "answer": "I'm unable to reach the knowledge service right now.",
                    "error_type": "api_error"
                }

        except requests.Timeout:
            logger.error(f"[KnowledgeService] Request timeout during knowledge lookup for '{topic}'")
            return {
                "success": False,
                "topic": topic,
                "answer": "I'm unable to reach the knowledge service right now.",
                "error_type": "timeout"
            }

        except requests.RequestException as e:
            logger.error(f"[KnowledgeService] Network error during knowledge lookup: {e}")
            return {
                "success": False,
                "topic": topic,
                "answer": "I'm unable to reach the knowledge service right now.",
                "error_type": "network_error"
            }

        except Exception as e:
            logger.error(f"[KnowledgeService] Unexpected error during knowledge lookup: {e}")
            return {
                "success": False,
                "topic": topic,
                "answer": "An error occurred while looking up that information.",
                "error_type": "malformed_response"
            }

    @classmethod
    def get_answer(cls, query: str) -> str:
        """
        Main entry point for command router.
        Performs knowledge lookup and returns spoken answer string.
        """
        result = cls.query_knowledge(query)
        return result.get("answer", "I couldn't find information about that topic.")

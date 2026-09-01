"""
Web Search Service module.
Handles search query extraction and launching the user's default browser.
"""

import re
import webbrowser
import urllib.parse
from core.logger import get_logger

logger = get_logger("SearchService")

class SearchService:
    """Handles web search queries."""

    # Common spoken prefixes for web search queries
    SEARCH_PREFIX_PATTERNS = [
        r"^(can you\s+)?search\s+for\s+",
        r"^(can you\s+)?search\s+the\s+web\s+for\s+",
        r"^(can you\s+)?search\s+online\s+for\s+",
        r"^(can you\s+)?look\s+up\s+",
        r"^(can you\s+)?google\s+search\s+",
        r"^(can you\s+)?google\s+",
        r"^search\s+",
        r"^find\s+information\s+on\s+",
        r"^find\s+info\s+on\s+",
        r"^find\s+",
    ]

    @classmethod
    def extract_search_query(cls, user_input: str) -> str:
        """
        Extracts the clean target search query by stripping common command prefixes.
        Example: 'search for Python decorators' -> 'Python decorators'
        """
        if not user_input or not user_input.strip():
            return ""

        clean_text = user_input.strip()

        for pattern in cls.SEARCH_PREFIX_PATTERNS:
            match = re.search(pattern, clean_text, re.IGNORECASE)
            if match:
                extracted = clean_text[match.end():].strip()
                if extracted:
                    return extracted

        return clean_text

    @classmethod
    def search_web(cls, user_input_or_query: str) -> str:
        """
        Extracts query from user input and opens standard browser with search results.
        """
        query = cls.extract_search_query(user_input_or_query)
        
        if not query:
            return "What would you like me to search for?"
            
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.google.com/search?q={encoded_query}"
        logger.info(f"Opening browser search for query: '{query}'")
        
        try:
            webbrowser.open(url)
            return f"Searching the web for '{query}'."
        except Exception as e:
            logger.error(f"Failed to open web browser: {e}")
            return f"Sorry, I couldn't open the browser to search for '{query}'."

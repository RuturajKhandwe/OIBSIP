import re
from typing import Tuple

def validate_location_query(query: str) -> Tuple[bool, str]:
    """
    Validates a location search query string.
    Returns (is_valid, error_message).
    """
    if not query or not isinstance(query, str):
        return False, "Please enter a city or ZIP code."

    query_str = query.strip()
    if len(query_str) == 0:
        return False, "Please enter a city or ZIP code."

    if len(query_str) < 2:
        return False, "Location name must be at least 2 characters long."

    if len(query_str) > 80:
        return False, "Location query is too long."

    # Allow letters, numbers, spaces, commas, hyphens, periods, and apostrophes
    if not re.match(r"^[a-zA-Z0-9\s,\.\-\']+$", query_str):
        return False, "Location query contains invalid characters."

    return True, ""

def is_zip_code(query: str) -> bool:
    """Returns True if the query looks like a numeric or alphanumeric postal code."""
    if not query:
        return False
    clean = query.strip()
    # US 5 or 9 digit, UK postal, India 6-digit pin code
    return bool(re.match(r"^\d{5}(-\d{4})?$", clean) or 
                re.match(r"^\d{6}$", clean) or 
                re.match(r"^[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}$", clean, re.IGNORECASE))

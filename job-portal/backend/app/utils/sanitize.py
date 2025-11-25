"""
Input sanitization utilities for security.
"""
import re
import html
from typing import Optional


def sanitize_string(value: Optional[str], max_length: int = 1000) -> Optional[str]:
    """
    Sanitize string input to prevent injection attacks.

    - Strips whitespace
    - HTML escapes special characters
    - Truncates to max length

    Args:
        value: Input string to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string or None if input was None
    """
    if value is None:
        return None

    # Strip whitespace
    value = value.strip()

    # HTML escape to prevent XSS
    value = html.escape(value)

    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]

    return value


def sanitize_for_regex(value: str) -> str:
    """
    Escape special regex characters to prevent ReDoS attacks.

    Use this when user input will be used in a regex pattern.

    Args:
        value: String to escape

    Returns:
        Regex-safe string with special characters escaped
    """
    return re.escape(value)


def sanitize_search_query(query: str, max_length: int = 200) -> str:
    """
    Sanitize a search query for safe use in database queries.

    - Strips whitespace
    - Escapes regex special characters
    - Truncates to max length

    Args:
        query: Search query string
        max_length: Maximum allowed length

    Returns:
        Sanitized search query
    """
    if not query:
        return ""

    # Strip whitespace
    query = query.strip()

    # Truncate first to limit processing
    if len(query) > max_length:
        query = query[:max_length]

    # Escape regex special characters
    query = sanitize_for_regex(query)

    return query

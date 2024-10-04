# url_snapshotter/patterns.py

import re


def get_patterns() -> list[dict[str, any]]:
    """
    Returns a list of patterns for cleaning content.

    Each pattern is a dictionary containing:
    - "pattern": A compiled regular expression to match specific content.
    - "message": A string message indicating the type of content detected and removed.

    Feel free to expand this function with additional patterns as needed.

    Patterns included:
    1. Script nonce pattern.
    2. CSRF token pattern.
    3. Anti-forgery token pattern.
    4. XSRF token pattern.

    Returns:
        list[dict[str, any]]: A list of dictionaries with compiled regex patterns and corresponding messages.
    """

    return [
        {
            "pattern": re.compile(
                r'<script nonce="[^"]+">window\.\w+_CSP_NONCE\s*=\s*\'[^\']+\';</script>'
            ),
            "message": "Script nonce detected and removed.",
        },
        {
            "pattern": re.compile(r'name="csrf-token" content="[^"]+"'),
            "message": "CSRF token detected and removed.",
        },
        {
            "pattern": re.compile(
                r'<input type="hidden" name="__RequestVerificationToken" value="[^"]+" ?/?>'
            ),
            "message": "Anti-forgery token detected and removed.",
        },
        {
            "pattern": re.compile(r"XSRF-TOKEN=[^;]+;"),
            "message": "XSRF token detected and removed.",
        },
    ]

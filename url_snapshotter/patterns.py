# url_snapshotter/patterns.py

import re


def get_patterns() -> list[dict[str, any]]:
    """Returns a list of patterns for cleaning content."""
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

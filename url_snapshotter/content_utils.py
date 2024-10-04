# url_snapshotter/content_utils.py

import hashlib
import re
from url_snapshotter.logger_utils import setup_logger
from url_snapshotter.patterns import get_patterns

logger = setup_logger()


def hash_content(content: str) -> str:
    """
    Create an SHA-256 hash of the given content.

    Args:
        content (str): The content to be hashed.

    Returns:
        str: The SHA-256 hash of the content as a hexadecimal string.
    """

    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def clean_content(content: str, url: str) -> str:
    """
    Remove specific elements from content that can cause false positives in diffs.

    Args:
        content (str): The HTML or text content to be cleaned.
        url (str): The URL associated with the content, used for logging purposes.

    Returns:
        str: The cleaned content with specified patterns removed.

    Raises:
        Warning: Logs a warning if the pattern structure is invalid or if individual patterns/messages are invalid.
        Error: Logs an error if an unexpected exception occurs during content processing.
    """

    patterns = get_patterns()

    # Validate that patterns is a list of dictionaries
    if not isinstance(patterns, list) or any(
        not isinstance(item, dict) or "pattern" not in item or "message" not in item
        for item in patterns
    ):
        logger.warning(
            f"Invalid pattern structure detected for URL: {url}. Skipping content cleaning."
        )
        return content

    try:
        # Loop through all patterns and apply substitutions
        for item in patterns:
            # Ensure 'pattern' is a compiled regex and 'message' is a string
            if not isinstance(item["pattern"], re.Pattern) or not isinstance(
                item["message"], str
            ):
                logger.warning(
                    f"Invalid pattern or message for URL: {url}. Skipping this pattern."
                )
                continue

            # Perform the substitution if pattern matches
            if item["pattern"].search(content):
                logger.info(f"{item['message']} URL: {url}")
                content = item["pattern"].sub("", content)

    except Exception as e:
        # Handle any unexpected errors in content processing
        logger.error(
            f"Error occurred while cleaning content for URL: {url}. Error: {str(e)}"
        )

    return content

import hashlib
from url_snapshotter.logger_utils import setup_logger
from url_snapshotter.patterns import get_patterns
import re

logger = setup_logger()

def hash_content(content):
    """Create an SHA-256 hash of the content."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def clean_content(content, url):
    """Remove specific elements from content that can cause false positives in diffs."""
    patterns = get_patterns()

    # Validate that patterns is a list of dictionaries
    if not isinstance(patterns, list) or any(not isinstance(item, dict) or 'pattern' not in item or 'message' not in item for item in patterns):
        logger.warning(f"Invalid pattern structure detected for URL: {url}. Skipping content cleaning.")
        return content

    try:
        # Loop through all patterns and apply substitutions
        for item in patterns:
            # Ensure 'pattern' is a compiled regex and 'message' is a string
            if not isinstance(item['pattern'], re.Pattern) or not isinstance(item['message'], str):
                logger.warning(f"Invalid pattern or message for URL: {url}. Skipping this pattern.")
                continue

            # Perform the substitution if pattern matches
            if item['pattern'].search(content):
                logger.info(f"{item['message']} URL: {url}")
                content = item['pattern'].sub('', content)

    except Exception as e:
        # Handle any unexpected errors in content processing
        logger.error(f"Error occurred while cleaning content for URL: {url}. Error: {str(e)}")
    
    return content


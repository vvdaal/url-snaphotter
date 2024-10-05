# url_snapshotter/snapshot_fetcher.py

# This module provides the functionality to fetch a list of URLs concurrently, clean their content, and return structured data including the URL, HTTP code, content hash, and cleaned full content.

import asyncio
from url_snapshotter.async_requests import fetch_all_urls
from url_snapshotter.content_utils import clean_content, hash_content
import structlog

logger = structlog.get_logger()


async def fetch_and_clean_urls(
    urls: list[str], concurrent: int
) -> list[dict[str, any]]:
    """
    Fetch URLs asynchronously and clean their content.

    Args:
        urls (list[str]): A list of URLs to fetch.
        concurrent (int): The number of concurrent fetch operations.

    Returns:
        list[dict[str, any]]: A list of dictionaries containing the URL, HTTP code,
        content hash, and cleaned full content.

    Raises:
        Exception: If an error occurs while fetching URLs, it logs the error and returns an empty list.
    """

    url_data = []
    logger.info("Starting to fetch and clean URLs")

    try:
        # Fetch all URLs concurrently
        urls_content = await fetch_all_urls(urls, concurrent)
    except Exception as e:
        logger.error("An error occurred while fetching URLs", error=str(e))
        return []

    # Process each URL result individually
    for result in urls_content:
        url = result.get("url", "")
        http_code = result.get("status") or result.get("http_code", "Unknown")
        content = result.get("content", "")

        try:
            if content:
                cleaned_content = clean_content(content, url)
                content_hash = hash_content(cleaned_content)
                url_data.append(
                    {
                        "url": url,
                        "http_code": http_code,
                        "content_hash": content_hash,
                        "full_content": cleaned_content,
                    }
                )
                logger.info(f"Processed URL: {url} with HTTP code {http_code}")
            else:
                # Handle cases where content is missing or empty
                url_data.append(
                    {
                        "url": url,
                        "http_code": http_code,
                        "content_hash": "",
                        "full_content": "",
                    }
                )
                logger.warning(f"No content for URL: {url} with HTTP code {http_code}")

        except Exception as process_error:
            # Log and continue if processing fails for a specific URL
            logger.error(
                f"Error processing URL: {url}",
                error=str(process_error),
                http_code=http_code,
            )
            url_data.append(
                {
                    "url": url,
                    "http_code": http_code,
                    "content_hash": "",
                    "full_content": "",
                }
            )

    logger.info(f"Completed processing {len(url_data)} URLs")
    return url_data

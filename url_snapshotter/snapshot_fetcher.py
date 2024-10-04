# url_snapshotter/snapshot_fetcher.py

import asyncio
from url_snapshotter.async_requests import fetch_all_urls
from url_snapshotter.content_utils import clean_content, hash_content
from url_snapshotter.logger_utils import setup_logger

logger = setup_logger()


async def fetch_and_clean_urls(
    urls: list[str], concurrent: int
) -> list[dict[str, any]]:
    """Fetch URLs asynchronously and clean their content."""
    url_data = []
    logger.info("Starting to fetch and clean URLs")

    try:
        urls_content = await fetch_all_urls(urls, concurrent)
    except Exception as e:
        logger.error(f"An error occurred while fetching URLs: {e}")
        return []

    for result in urls_content:
        url = result["url"]
        http_code = result.get("status") or result.get("http_code")
        content = result["content"]

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
            url_data.append(
                {
                    "url": url,
                    "http_code": http_code,
                    "content_hash": "",
                    "full_content": "",
                }
            )
            logger.info(f"Processed URL: {url} with HTTP code {http_code}, no content.")
    return url_data

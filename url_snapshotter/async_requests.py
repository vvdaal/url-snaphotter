# url_snapshotter/async_requests.py

import aiohttp
import asyncio
from url_snapshotter.logger_utils import setup_logger
from aiohttp import ClientError

logger = setup_logger()


async def fetch_url(
    session: aiohttp.ClientSession, url: str, max_retries: int = 3
) -> dict:
    """Fetch a URL asynchronously with retry logic."""
    logger.debug(f"Fetching URL: {url}")
    retries = 0

    while retries < max_retries:
        try:
            async with session.get(url) as response:
                content = await response.text()
                http_code = response.status
                logger.debug(f"Fetched {url} with HTTP code {http_code}")
                return {"url": url, "http_code": http_code, "content": content}

        except (ClientError, asyncio.TimeoutError) as e:
            retries += 1
            logger.warning(f"Error for {url}: {e}. Retry {retries}/{max_retries}")
            await asyncio.sleep(1)  # Optional backoff strategy

        except Exception as e:
            logger.error(f"Unexpected error while fetching {url}: {e}")
            return {"url": url, "http_code": None, "content": None}

    logger.error(f"Failed to fetch {url} after {max_retries} retries")
    return {"url": url, "http_code": None, "content": None}


async def fetch_all_urls(
    urls: list[str], concurrent: int, max_retries: int = 3
) -> list[dict]:
    """Fetch all URLs asynchronously."""
    results = []
    connector = aiohttp.TCPConnector(limit=concurrent)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch_url(session, url, max_retries) for url in urls]
        for task in asyncio.as_completed(tasks):
            result = await task
            if result.get("content") is not None:
                results.append(result)
            else:
                logger.warning(f"Skipping URL due to repeated failure: {result['url']}")
    return results

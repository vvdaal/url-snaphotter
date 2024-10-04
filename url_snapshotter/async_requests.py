# url_snapshotter/async_requests.py

import aiohttp
import asyncio
from url_snapshotter.logger_utils import setup_logger
from aiohttp import ClientError

logger = setup_logger()


async def fetch_url(
    session: aiohttp.ClientSession, url: str, max_retries: int = 3
) -> dict:
    """
    Fetch a URL asynchronously with retry logic.

    Args:
        session (aiohttp.ClientSession): The aiohttp client session to use for making the request.
        url (str): The URL to fetch.
        max_retries (int, optional): The maximum number of retries in case of failure. Defaults to 3.

    Returns:
        dict: A dictionary containing the URL, HTTP status code, and content of the response.
              If the request fails after the maximum number of retries, the HTTP status code and content will be None.

    Raises:
        ClientError: If there is a client error during the request.
        asyncio.TimeoutError: If the request times out.
        Exception: For any other unexpected errors.
    """

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
    results = []
    connector = aiohttp.TCPConnector(limit=concurrent)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch_url(session, url, max_retries) for url in urls]

        # Use asyncio.gather to collect all results
        completed_results = await asyncio.gather(*tasks)

        for result in completed_results:
            await process_task_result(result, results)

    return results


async def process_task_result(task_result, results):
    result = await task_result
    content = result.get("content")

    if content is not None:
        results.append(result)
    else:
        logger.warning(f"Skipping URL due to repeated failure: {result['url']}")

# url_snapshotter/async_requests.py

import asyncio

import aiohttp
from aiohttp import ClientError

from url_snapshotter.logger_utils import setup_logger

logger = setup_logger()


async def fetch_url(session, url, max_retries=3):
    """
    Fetches the content of a URL using an asynchronous HTTP GET request with retry logic.

    Args:
        session (aiohttp.ClientSession): The aiohttp session to use for making the request.
        url (str): The URL to fetch.
        max_retries (int, optional): The maximum number of retries in case of failure. Defaults to 3.

    Returns:
        tuple: A tuple containing the URL, the HTTP status code, and the response content.
               If the request fails after the maximum number of retries, the HTTP status code and content will be None.

    Raises:
        ClientError: If a client error occurs during the request.
        asyncio.TimeoutError: If the request times out.
        Exception: If an unexpected error occurs.
    """
    logger.debug(f"Fetching URL: {url}")
    retries = 0

    while retries < max_retries:
        try:
            async with session.get(url) as response:
                content = await response.text()
                http_code = response.status
                logger.debug(f"Fetched {url} with HTTP code {http_code}")
                return url, http_code, content

        except ClientError as e:
            retries += 1
            logger.warning(f"ClientError for {url}: {e}. Retry {retries}/{max_retries}")
            await asyncio.sleep(1)  # Optional: Backoff strategy

        except asyncio.TimeoutError:
            retries += 1
            logger.warning(f"TimeoutError for {url}. Retry {retries}/{max_retries}")
            await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Unexpected error while fetching {url}: {e}")
            return url, None, None  # Return None to indicate failure

    logger.error(f"Failed to fetch {url} after {max_retries} retries")
    return url, None, None


async def fetch_all_urls(urls, concurrent, max_retries=3):
    """
    Fetches content from a list of URLs concurrently with a specified number of retries.

    Args:
        urls (list): A list of URLs to fetch.
        concurrent (int): The maximum number of concurrent requests.
        max_retries (int, optional): The maximum number of retries for each URL. Defaults to 3.

    Returns:
        list: A list of tuples containing the URL, HTTP status code, and content for each successfully fetched URL.

    Raises:
        aiohttp.ClientError: If there is an issue with the HTTP request.
        asyncio.TimeoutError: If a request times out.

    Notes:
        - If a URL fails to fetch after the specified number of retries, it will be skipped and a warning will be logged.
        - The function uses aiohttp for asynchronous HTTP requests and asyncio for concurrency management.
    """
    results = []
    connector = aiohttp.TCPConnector(limit=concurrent)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch_url(session, url, max_retries) for url in urls]
        for task in asyncio.as_completed(tasks):
            url, http_code, content = await task
            if content is not None:
                results.append((url, http_code, content))
            else:
                logger.warning(f"Skipping URL due to repeated failure: {url}")
    return results

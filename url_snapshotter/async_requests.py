# url_snapshotter/async_requests.py

# This module provides the functionality to fetch URLs asynchronously with retry logic.

import aiohttp
import asyncio
import structlog
from aiohttp import ClientError

logger = structlog.get_logger()


async def fetch_url(
    session: aiohttp.ClientSession, url: str, max_retries: int = 3
) -> dict:
    """
    Fetches the content of a URL asynchronously with retry logic.

    Args:
        session (aiohttp.ClientSession): The aiohttp session to use for making the request.
        url (str): The URL to fetch.
        max_retries (int, optional): The maximum number of retries in case of failure. Defaults to 3.

    Returns:
        dict: A dictionary containing the URL, HTTP status code, and content. If an error occurs,
              the HTTP status code and content will be None.

    Raises:
        ClientError: If there is an error with the client request.
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
    """
    Fetches content from a list of URLs asynchronously with a specified level of concurrency and retry attempts.

    Args:
        urls (list[str]): A list of URLs to fetch.
        concurrent (int): The maximum number of concurrent requests.
        max_retries (int, optional): The maximum number of retry attempts for each URL. Defaults to 3.

    Returns:
        list[dict]: A list of dictionaries containing the results of the fetch operations.
    """

    results = []
    connector = aiohttp.TCPConnector(limit=concurrent)
    timeout = aiohttp.ClientTimeout(total=5)  # Set a 5-second timeout for each request

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        logger.info(f"Starting to fetch {len(urls)} URLs with concurrency {concurrent}")

        tasks = [fetch_url(session, url, max_retries=max_retries) for url in urls]

        # Use asyncio.gather to collect all results with exception handling
        completed_results = await asyncio.gather(*tasks, return_exceptions=True)

        for index, result in enumerate(completed_results):
            if isinstance(result, Exception):
                logger.error(
                    f"Task {index+1}/{len(urls)}: Encountered an exception: {result}"
                )
            else:
                logger.debug(f"Task {index+1}/{len(urls)}: Completed successfully.")
            process_task_result(result, results)

        logger.info(f"Completed fetching {len(urls)} URLs.")

    return results


def process_task_result(task_result: dict, results: list[dict]):
    """
    Processes the result of a task and appends it to the results list if it contains content.

    Args:
        task_result (dict): A dictionary containing the result of a task. Expected to have a key "content".
        results (list[dict]): A list of dictionaries where successful task results are appended.

    Returns:
        None
    """

    content = task_result.get("content")

    if content is not None:
        results.append(task_result)
    else:
        logger.warning(f"Skipping URL due to repeated failure: {task_result['url']}")

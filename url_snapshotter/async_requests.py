import aiohttp
import asyncio
from url_snapshotter.logger_utils import setup_logger
from aiohttp import ClientError

logger = setup_logger()

async def fetch_url(session, url, max_retries=3):
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

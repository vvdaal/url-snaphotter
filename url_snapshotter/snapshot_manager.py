# url_snapshotter/snapshot_manager.py

# This module provides the functionality to manage URL snapshots, including creating, fetching, comparing, and viewing snapshots.

import asyncio
from dataclasses import dataclass
import structlog
from url_snapshotter.db_utils import DatabaseManager
from url_snapshotter.async_requests import fetch_all_urls
from url_snapshotter.content_utils import clean_content, hash_content
from rich.markup import escape

logger = structlog.get_logger()

@dataclass
class URLSnapshot:
    """
    Represents a single URL snapshot with its metadata.
    """
    url: str
    http_code: str
    content_hash: str
    full_content: str

    def is_different(self, other: 'URLSnapshot') -> bool:
        """
        Compare this snapshot with another to check for differences.

        Args:
            other (URLSnapshot): The other URLSnapshot to compare.

        Returns:
            bool: True if any meaningful field is different, False otherwise.
        """
        return (
            self.http_code != other.http_code or 
            self.content_hash != other.content_hash
        )


class SnapshotManager:
    """
    SnapshotManager is responsible for managing URL snapshots, including creating, fetching, comparing, and viewing snapshots.

    Args:
        db_manager (DatabaseManager): An instance of DatabaseManager to handle database operations.
    """

    def __init__(self, db_manager: DatabaseManager):
        """
        Initializes the SnapshotManager with a DatabaseManager instance.

        Args:
            db_manager (DatabaseManager): An instance of DatabaseManager to handle database operations.
        """
        self.db_manager = db_manager

    def create_snapshot(self, urls: list[str], name: str, concurrent: int, batch_size: int = 50):
        """
        Create a snapshot of the provided URLs and save it to the database.

        Args:
            urls (list[str]): A list of URLs to be included in the snapshot.
            name (str): The name to assign to the snapshot.
            concurrent (int): The number of concurrent requests to make while fetching URLs.
            batch_size (int): Number of URLs to fetch concurrently per batch to optimize performance.
        """
        logger.info("Creating snapshot", name=name, concurrent=concurrent, total_urls=len(urls))

        try:
            # Use asyncio.run to perform async fetch and clean
            url_data = asyncio.run(self.fetch_and_clean_urls(urls, concurrent, batch_size))

            # Save the snapshot to the database
            self.db_manager.save_snapshot(name, url_data)
            logger.info("Snapshot creation completed", name=name)
        except Exception as e:
            self._log_exception("An error occurred while creating snapshot", e)

    async def fetch_and_clean_urls(
        self, urls: list[str], concurrent: int, batch_size: int
    ) -> list[dict[str, str | int]]:
        """
        Fetch URLs asynchronously in batches and clean their content.

        Args:
            urls (list[str]): A list of URLs to fetch.
            concurrent (int): The number of concurrent fetch operations.
            batch_size (int): The size of each batch of URLs to fetch concurrently.

        Returns:
            list[dict[str, str | int]]: A list of dictionaries containing the URL, HTTP code,
            content hash, and cleaned full content.
        """
        logger.info("Starting to fetch and clean URLs", total=len(urls))

        all_results = []

        # Process URLs in batches to avoid overloading system or API rate limits
        for i in range(0, len(urls), batch_size):
            batch = urls[i:i + batch_size]
            try:
                batch_results = await self._fetch_urls_batch(batch, concurrent)
                all_results.extend(batch_results)
            except Exception as e:
                self._log_exception("Error fetching a batch of URLs", e, {"batch_size": len(batch)})

        return all_results

    async def _fetch_urls_batch(self, urls_batch: list[str], concurrent: int) -> list[dict[str, str | int]]:
        """
        Fetch a batch of URLs concurrently.

        Args:
            urls_batch (list[str]): A batch of URLs to fetch.
            concurrent (int): The number of concurrent fetch operations.

        Returns:
            list[dict[str, str | int]]: A list of processed URL data.
        """
        urls_content = await fetch_all_urls(urls_batch, concurrent)
        return [self._process_url_result(result) for result in urls_content]

    def _process_url_result(self, result: dict) -> dict[str, str | int]:
        """
        Process the result of a fetched URL by cleaning its content and generating a content hash.

        Args:
            result (dict): A dictionary containing URL fetch details.

        Returns:
            dict[str, str | int]: A dictionary with URL details including HTTP code, content hash,
                                  and cleaned full content.
        """
        url = result.get("url", "")
        http_code = result.get("status") or result.get("http_code", "Unknown")
        content = result.get("content", "")

        try:
            if content:
                cleaned_content = clean_content(content, url)
                content_hash = hash_content(cleaned_content)
                logger.info("Processed URL", url=url, http_code=http_code)
                return {
                    "url": url,
                    "http_code": http_code,
                    "content_hash": content_hash,
                    "full_content": cleaned_content,
                }
            else:
                logger.warning("No content for URL", url=url, http_code=http_code)
                return {
                    "url": url,
                    "http_code": http_code,
                    "content_hash": "",
                    "full_content": "",
                }
        except Exception as e:
            self._log_exception(f"Error processing URL: {url}", e, {"http_code": http_code})
            return {
                "url": url,
                "http_code": http_code,
                "content_hash": "",
                "full_content": "",
            }

    def compare_snapshots(
        self, snapshot1_id: int, snapshot2_id: int
    ) -> list[dict[str, str]]:
        """
        Compare two snapshots and return the differences.

        Args:
            snapshot1_id (int): The ID of the first snapshot.
            snapshot2_id (int): The ID of the second snapshot.

        Returns:
            list[dict[str, str]]: A list of dictionaries representing the differences
                                  between the two snapshots.
        """
        try:
            snapshot1_data = self.db_manager.get_snapshot_data(snapshot1_id)
            snapshot2_data = self.db_manager.get_snapshot_data(snapshot2_id)
        except Exception as e:
            self._log_exception("Error retrieving snapshots", e)
            return []

        return self._find_differences(snapshot1_data, snapshot2_data)

    def _find_differences(
        self, snapshot1_data: list[dict[str, str]], snapshot2_data: list[dict[str, str]]
    ) -> list[dict[str, str]]:
        """
        Compare two snapshots and find differences between them.

        Args:
            snapshot1_data (list[dict[str, str]]): The first snapshot data.
            snapshot2_data (list[dict[str, str]]): The second snapshot data.

        Returns:
            list[dict[str, str]]: A list of dictionaries, each representing a URL with differences between the two snapshots.
        """
        differences = []

        # Convert list of dicts to dict with URL as key for faster comparison
        snapshot1_dict = {entry["url"]: URLSnapshot(**entry) for entry in snapshot1_data}
        snapshot2_dict = {entry["url"]: URLSnapshot(**entry) for entry in snapshot2_data}

        all_urls = set(snapshot1_dict.keys()).union(snapshot2_dict.keys())

        for url in all_urls:
            data1 = snapshot1_dict.get(url)
            data2 = snapshot2_dict.get(url)

            # Compare URL snapshots
            if not data1 or not data2 or data1.is_different(data2):
                differences.append(
                    {
                        "url": url,
                        "snapshot1_http_code": data1.http_code if data1 else "N/A",
                        "snapshot2_http_code": data2.http_code if data2 else "N/A",
                        "snapshot1_content_hash": data1.content_hash if data1 else "",
                        "snapshot2_content_hash": data2.content_hash if data2 else "",
                        "snapshot1_full_content": escape(data1.full_content) if data1 else "",
                        "snapshot2_full_content": escape(data2.full_content) if data2 else "",
                    }
                )
                logger.info("URL has changed", url=url)

        return differences

    def _log_exception(self, message: str, exception: Exception, extra: dict = None):
        """
        Log an exception message with its details.

        Args:
            message (str): The log message to be prefixed to the exception details.
            exception (Exception): The caught exception.
            extra (dict, optional): Additional context to include in the log entry.
        """
        logger.error(message, error=str(exception), **(extra or {}))

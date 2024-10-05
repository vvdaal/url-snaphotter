# url_snapshotter/snapshot_manager.py

# This module provides the functionality to manage URL snapshots, including creating, fetching, comparing, and viewing snapshots.

import asyncio
import structlog
from url_snapshotter.db_utils import DatabaseManager
from url_snapshotter.async_requests import fetch_all_urls
from url_snapshotter.content_utils import clean_content, hash_content
from rich.markup import escape

logger = structlog.get_logger()


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

    def create_snapshot(self, urls: list[str], name: str, concurrent: int):
        """
        Create a snapshot of the provided URLs and save it to the database.

        Args:
            urls (list[str]): A list of URLs to be included in the snapshot.
            name (str): The name to assign to the snapshot.
            concurrent (int): The number of concurrent requests to make while fetching URLs.

        Raises:
            Exception: If an error occurs during the snapshot creation process.
        """
        logger.info(f"Creating snapshot with name: {name}")

        try:
            # Use asyncio.run to perform async fetch and clean
            url_data = asyncio.run(self.fetch_and_clean_urls(urls, concurrent))

            # Save the snapshot to the database
            self.db_manager.save_snapshot(name, url_data)
            logger.info("Snapshot creation completed.")
        except Exception as e:
            self._log_exception("An error occurred while creating snapshot", e)

    async def fetch_and_clean_urls(
        self, urls: list[str], concurrent: int
    ) -> list[dict[str, str | int]]:
        """
        Fetch URLs asynchronously and clean their content.

        Args:
            urls (list[str]): A list of URLs to fetch.
            concurrent (int): The number of concurrent fetch operations.

        Returns:
            list[dict[str, str | int]]: A list of dictionaries containing the URL, HTTP code,
            content hash, and cleaned full content.
        """
        logger.info("Starting to fetch and clean URLs")

        try:
            # Fetch all URLs concurrently
            urls_content = await fetch_all_urls(urls, concurrent)
        except Exception as e:
            self._log_exception("An error occurred while fetching URLs", e)
            return []

        # Process each URL result and return the cleaned data
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
                logger.info(f"Processed URL: {url} with HTTP code {http_code}")
                return {
                    "url": url,
                    "http_code": http_code,
                    "content_hash": content_hash,
                    "full_content": cleaned_content,
                }
            else:
                logger.warning(f"No content for URL: {url} with HTTP code {http_code}")
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
                                  between the two snapshots. Each dictionary contains
                                  the details of a difference.
        """
        try:
            snapshot1_data = self.db_manager.get_snapshot_data(snapshot1_id)
            snapshot2_data = self.db_manager.get_snapshot_data(snapshot2_id)
        except Exception as e:
            self._log_exception("Error retrieving snapshots", e)
            return []

        return self._find_differences(snapshot1_data, snapshot2_data)

    def view_snapshot(self, snapshot_id: int) -> list[dict[str, str]]:
        """
        Retrieve the details of a specific snapshot.

        Args:
            snapshot_id (int): The unique identifier of the snapshot to retrieve.

        Returns:
            list[dict[str, str]]: A list of dictionaries containing the snapshot details.
                                  Returns an empty list if no data is found or an error occurs.
        """
        try:
            snapshot_data = self.db_manager.get_snapshot_data(snapshot_id)
            if not snapshot_data:
                logger.warning("No data found for this snapshot.")
                return []
            return snapshot_data
        except Exception as e:
            self._log_exception("An error occurred while viewing the snapshot", e)
            return []

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

        # Convert list of dicts to dict with URL as key
        snapshot1_dict = {entry["url"]: entry for entry in snapshot1_data}
        snapshot2_dict = {entry["url"]: entry for entry in snapshot2_data}

        all_urls = set(snapshot1_dict.keys()).union(snapshot2_dict.keys())

        for url in all_urls:
            data1 = snapshot1_dict.get(url, {})
            data2 = snapshot2_dict.get(url, {})

            code1 = data1.get("http_code", "N/A")
            code2 = data2.get("http_code", "N/A")
            content_hash1 = data1.get("content_hash", "")
            content_hash2 = data2.get("content_hash", "")
            content1 = escape(data1.get("full_content", ""))
            content2 = escape(data2.get("full_content", ""))

            if code1 != code2 or content_hash1 != content_hash2:
                differences.append(
                    {
                        "url": url,
                        "snapshot1_http_code": code1,
                        "snapshot2_http_code": code2,
                        "snapshot1_content_hash": content_hash1,
                        "snapshot2_content_hash": content_hash2,
                        "snapshot1_full_content": content1,
                        "snapshot2_full_content": content2,
                    }
                )
                logger.info(f"URL: {url} has changed.")

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

# url_snapshotter/snapshot_manager.py

import asyncio
from url_snapshotter.db_utils import DatabaseManager
from url_snapshotter.snapshot_fetcher import fetch_and_clean_urls
from url_snapshotter.logger_utils import setup_logger

logger = setup_logger()


class SnapshotManager:
    """
    SnapshotManager is responsible for managing URL snapshots, including creating, comparing, and viewing snapshots.

    Args:
        db_manager (DatabaseManager): An instance of DatabaseManager to handle database operations.

    Methods:
        __init__(db_manager: DatabaseManager):
            Initializes the SnapshotManager with a DatabaseManager instance.

        create_snapshot(urls: list[str], name: str, concurrent: int):
            Creates a snapshot of the provided URLs and saves it to the database.

        compare_snapshots(snapshot1_id: int, snapshot2_id: int) -> list[dict[str, any]]:
            Compares two snapshots by their IDs and returns the differences.

        view_snapshot(snapshot_id: int) -> list[dict[str, any]]:
            Retrieves the details of a specific snapshot by its ID.

        _find_differences(snapshot1_data: list[dict[str, any]], snapshot2_data: list[dict[str, any]]) -> list[dict[str, any]]:
            Identifies differences between two snapshots.
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
            url_data = asyncio.run(fetch_and_clean_urls(urls, concurrent))

            # Save the snapshot to the database
            self.db_manager.save_snapshot(name, url_data)
            logger.info("Snapshot creation completed.")
        except Exception as e:
            logger.error(f"An error occurred while creating snapshot: {e}")

    def compare_snapshots(
        self, snapshot1_id: int, snapshot2_id: int
    ) -> list[dict[str, any]]:
        """
        Compare two snapshots and return the differences.

        Args:
            snapshot1_id (int): The ID of the first snapshot.
            snapshot2_id (int): The ID of the second snapshot.

        Returns:
            list[dict[str, any]]: A list of dictionaries representing the differences
                                  between the two snapshots. Each dictionary contains
                                  the details of a difference.
        """

        try:
            snapshot1_data = self.db_manager.get_snapshot_data(snapshot1_id)
            snapshot2_data = self.db_manager.get_snapshot_data(snapshot2_id)
        except Exception as e:
            logger.error(f"Error retrieving snapshots: {e}")
            return []

        differences = self._find_differences(snapshot1_data, snapshot2_data)
        return differences

    def view_snapshot(self, snapshot_id: int) -> list[dict[str, any]]:
        """
        Retrieve the details of a specific snapshot.

        Args:
            snapshot_id (int): The unique identifier of the snapshot to retrieve.

        Returns:
            list[dict[str, any]]: A list of dictionaries containing the snapshot details.
                                  Returns an empty list if no data is found or an error occurs.

        Raises:
            Exception: If an error occurs while retrieving the snapshot data.
        """

        try:
            snapshot_data = self.db_manager.get_snapshot_data(snapshot_id)
            if not snapshot_data:
                print("[bold yellow]⚠️ No data found for this snapshot.[/bold yellow]")
                return []
            return snapshot_data
        except Exception as e:
            print(
                f"[bold red]🚨 An error occurred while viewing the snapshot: {e}[/bold red]"
            )
            return []

    def _find_differences(
        self, snapshot1_data: list[dict[str, any]], snapshot2_data: list[dict[str, any]]
    ) -> list[dict[str, any]]:
        """
        Compare two snapshots and find differences between them.

        This method compares two lists of dictionaries, each representing a snapshot of URLs and their associated data.
        It identifies differences in HTTP status codes and content hashes between the two snapshots.

        Args:
            snapshot1_data (list[dict[str, any]]): The first snapshot data, where each dictionary contains URL data.
            snapshot2_data (list[dict[str, any]]): The second snapshot data, where each dictionary contains URL data.

        Returns:
            list[dict[str, any]]: A list of dictionaries, each representing a URL with differences between the two snapshots.
            Each dictionary contains the URL, HTTP codes, content hashes, and full content from both snapshots.
        """

        differences = []

        # Convert list of dicts to dict with URL as key
        snapshot1_dict = {entry["url"]: entry for entry in snapshot1_data}
        snapshot2_dict = {entry["url"]: entry for entry in snapshot2_data}

        all_urls = set(snapshot1_dict.keys()).union(set(snapshot2_dict.keys()))

        for url in all_urls:
            data1 = snapshot1_dict.get(url, {})
            data2 = snapshot2_dict.get(url, {})

            code1 = data1.get("http_code", "N/A")
            code2 = data2.get("http_code", "N/A")
            content_hash1 = data1.get("content_hash", "")
            content_hash2 = data2.get("content_hash", "")
            content1 = data1.get("full_content", "")
            content2 = data2.get("full_content", "")

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
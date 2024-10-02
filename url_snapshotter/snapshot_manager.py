# url_snapshotter/snapshot_manager.py

import asyncio

from url_snapshotter.async_requests import fetch_all_urls
from url_snapshotter.content_utils import clean_content, hash_content
from url_snapshotter.db_utils import DatabaseManager
from url_snapshotter.logger_utils import setup_logger


class SnapshotManager:
    def __init__(self, db_manager: DatabaseManager):
        self.logger = setup_logger()
        self.db_manager = db_manager
        self.debug = False  # Set this accordingly

    async def fetch_and_clean_urls(self, urls: list[str], concurrent: int) -> list[dict[str, any]]:
        """Fetch URLs asynchronously and clean their content."""
        url_data = []
        self.logger.info("Starting to fetch and clean URLs")

        try:
            urls_content = await fetch_all_urls(urls, concurrent)
        except Exception as e:
            self.logger.error(f"An error occurred while fetching URLs: {e}")
            return []

        for result in urls_content:
            url = result['url']
            http_code = result.get('status') or result.get('http_code')
            content = result['content']

            if content:
                cleaned_content = clean_content(content, url)
                content_hash = hash_content(cleaned_content)
                url_data.append({
                    'url': url,
                    'http_code': http_code,
                    'content_hash': content_hash,
                    'full_content': cleaned_content
                })
                self.logger.info(f"Processed URL: {url} with HTTP code {http_code}")
            else:
                url_data.append({
                    'url': url,
                    'http_code': http_code,
                    'content_hash': '',
                    'full_content': ''
                })
                self.logger.info(f"Processed URL: {url} with HTTP code {http_code}, no content.")
        return url_data

    def create_snapshot(self, urls: list[str], name: str, concurrent: int):
        """Create a snapshot of URLs and save it to the database."""
        self.logger.info(f"Creating snapshot with name: {name}")

        try:
            # Use asyncio.run to perform async fetch and clean
            url_data = asyncio.run(self.fetch_and_clean_urls(urls, concurrent))

            # Save the snapshot to the database
            self.db_manager.save_snapshot(name, url_data)
            self.logger.info("Snapshot creation completed.")
        except Exception as e:
            self.logger.error(f"An error occurred while creating snapshot: {e}")

    def compare_snapshots(self, snapshot1_id: int, snapshot2_id: int) -> list[dict[str, any]]:
        """Compare two snapshots and return differences."""
        try:
            snapshot1_data = self.db_manager.get_snapshot_data(snapshot1_id)
            snapshot2_data = self.db_manager.get_snapshot_data(snapshot2_id)
        except Exception as e:
            self.logger.error(f"Error retrieving snapshots: {e}")
            return []

        differences = self._find_differences(snapshot1_data, snapshot2_data)
        return differences

    def view_snapshot(self, snapshot_id: int) -> list[dict[str, any]]:
        """Retrieve the details of a specific snapshot."""
        try:
            snapshot_data = self.db_manager.get_snapshot_data(snapshot_id)
            if not snapshot_data:
                print("[bold yellow]⚠️ No data found for this snapshot.[/bold yellow]")
                return []
            return snapshot_data
        except Exception as e:
            print(f"[bold red]🚨 An error occurred while viewing the snapshot: {e}[/bold red]")
            if self.debug:
                self.logger.exception("Exception in view_snapshot")
            return []

    def _find_differences(self, snapshot1_data: list[dict[str, any]], snapshot2_data: list[dict[str, any]]) -> list[dict[str, any]]:
        """Identify differences between two snapshots."""
        differences = []

        # Convert list of dicts to dict with URL as key
        snapshot1_dict = {entry['url']: entry for entry in snapshot1_data}
        snapshot2_dict = {entry['url']: entry for entry in snapshot2_data}

        all_urls = set(snapshot1_dict.keys()).union(set(snapshot2_dict.keys()))

        for url in all_urls:
            data1 = snapshot1_dict.get(url, {})
            data2 = snapshot2_dict.get(url, {})

            code1 = data1.get('http_code', 'N/A')
            code2 = data2.get('http_code', 'N/A')
            content_hash1 = data1.get('content_hash', '')
            content_hash2 = data2.get('content_hash', '')
            content1 = data1.get('full_content', '')
            content2 = data2.get('full_content', '')

            if code1 != code2 or content_hash1 != content_hash2:
                differences.append({
                    'url': url,
                    'snapshot1_http_code': code1,
                    'snapshot2_http_code': code2,
                    'snapshot1_content_hash': content_hash1,
                    'snapshot2_content_hash': content_hash2,
                    'snapshot1_full_content': content1,
                    'snapshot2_full_content': content2
                })
                self.logger.info(f"URL: {url} has changed.")

        return differences

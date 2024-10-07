# url_snapshotter/commands/list_command.py

# This module provides the functionality to list all available snapshots.

from url_snapshotter.snapshot_manager import SnapshotManager
from url_snapshotter.db_utils import DatabaseManager
from url_snapshotter.output_formatter import display_snapshots_list
from rich.console import Console

console = Console()
db_manager = DatabaseManager()
snapshot_manager = SnapshotManager(db_manager)


def handle_list_snapshots():
    """
    List all available snapshots.

    This function retrieves all snapshots from the database using the db_manager,
    displays them using the display_snapshots_list function, and handles any
    exceptions that may occur during this process. After displaying the snapshots,
    it prompts the user to press Enter to return to the main menu.

    Raises:
        Exception: If an error occurs while retrieving or displaying snapshots.
    """

    try:
        snapshots = db_manager.get_snapshots()
        display_snapshots_list(snapshots)
    except Exception as e:
        console.print(f"[bold red]🚨 An error occurred: {e}[/bold red]")

    console.print("[bold cyan]Press Enter to return to the main menu...[/bold cyan]")
    input()

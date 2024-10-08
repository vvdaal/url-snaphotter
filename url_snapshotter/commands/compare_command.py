# url_snapshotter/commands/compare_command.py

# This module provides the functionality to compare two snapshots.

from url_snapshotter.snapshot_manager import SnapshotManager
from url_snapshotter.db_utils import DatabaseManager
from url_snapshotter.input_handler import prompt_for_snapshots
from url_snapshotter.output_formatter import display_differences
from rich.console import Console

console = Console()
db_manager = DatabaseManager()
snapshot_manager = SnapshotManager(db_manager)


def handle_compare(snapshot1_id: int | None = None, snapshot2_id: int | None = None):
    """
    Handle the comparison of two snapshots.

    This function compares two snapshots identified by their IDs. If the IDs are not provided,
    it prompts the user to input them. The differences between the snapshots are then displayed.

    Args:
        snapshot1_id (int | None): The ID of the first snapshot. Defaults to None.
        snapshot2_id (int | None): The ID of the second snapshot. Defaults to None.

    Returns:
        None
    """
    try:
        if snapshot1_id is None or snapshot2_id is None:
            snapshot1_id, snapshot2_id = prompt_for_snapshots()
            if snapshot1_id is None or snapshot2_id is None:
                return

        differences = snapshot_manager.compare_snapshots(snapshot1_id, snapshot2_id)
        display_differences(differences)
    except Exception as e:
        console.print(f"[bold red]🚨 An error occurred: {e}[/bold red]")

    console.print("[bold cyan]Press Enter to return to the main menu...[/bold cyan]")
    input()

# url_snapshotter/commands/view_command.py

from url_snapshotter.snapshot_manager import SnapshotManager
from url_snapshotter.db_utils import DatabaseManager
from url_snapshotter.input_handler import prompt_for_snapshot_id
from url_snapshotter.output_formatter import display_snapshot_details
from rich.console import Console

console = Console()
db_manager = DatabaseManager()
snapshot_manager = SnapshotManager(db_manager)


def handle_view(snapshot_id: int | None = None):
    """
    Handle viewing the details of a snapshot.

    Parameters:
    snapshot_id (int | None): The ID of the snapshot to view. If None, the user will be prompted to enter a snapshot ID.

    Returns:
    None
    """

    try:
        if snapshot_id is None:
            snapshot_id = prompt_for_snapshot_id()
            if snapshot_id is None:
                return

        snapshot_data = snapshot_manager.view_snapshot(snapshot_id)
        display_snapshot_details(snapshot_data)
    except Exception as e:
        console.print(f"[bold red]🚨 An error occurred: {e}[/bold red]")

    console.print("[bold cyan]Press Enter to return to the main menu...[/bold cyan]")
    input()

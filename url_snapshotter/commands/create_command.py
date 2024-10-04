# url_snapshotter/commands/create_command.py

import time
from yaspin import yaspin
from url_snapshotter.snapshot_manager import SnapshotManager
from url_snapshotter.db_utils import DatabaseManager
from url_snapshotter.input_handler import prompt_for_file, prompt_for_snapshot_name
from rich.console import Console

console = Console()
db_manager = DatabaseManager()
snapshot_manager = SnapshotManager(db_manager)


def handle_create(file: str | None, name: str | None, concurrent: int):
    """
    Handle the creation of a new snapshot.

    Parameters:
    file (str | None): The path to the file containing URLs. If None, the user will be prompted to provide a file.
    name (str | None): The name of the snapshot. If None, the user will be prompted to provide a name.
    concurrent (int): The number of concurrent operations to perform during snapshot creation.

    Returns:
    None
    """

    try:
        file_path = file or prompt_for_file()
        if not file_path:
            return
        urls = snapshot_manager.load_urls_from_file(file_path)
        name = name or prompt_for_snapshot_name()
        if not name:
            return

        with yaspin(text="Creating snapshot...", color="cyan") as spinner:
            snapshot_manager.create_snapshot(urls, name, concurrent)
            time.sleep(0.5)
            spinner.ok("✔")

        console.print("[bold green]✅ Snapshot created successfully![/bold green]")
    except Exception as e:
        console.print(f"[bold red]🚨 An error occurred: {e}[/bold red]")

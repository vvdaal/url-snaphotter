# url_snapshotter/input_handler.py

from InquirerPy import inquirer
from rich.console import Console
from rich.prompt import Prompt
from url_snapshotter.db_utils import DatabaseManager

console = Console()
db_manager = DatabaseManager()


def prompt_for_file() -> str | None:
    """
    Prompt the user to enter a file path for URLs.

    This function uses the `Prompt.ask` method to request a file path from the user.
    If the user provides an empty input, a message is printed to the console, and the function returns None.
    The function also handles `KeyboardInterrupt` and `EOFError` exceptions, returning None in these cases.

    Returns:
        str | None: The file path entered by the user, or None if no input is provided or an exception occurs.
    """
    try:
        file_path = Prompt.ask(
            "[bold yellow]📂 Enter the path to a file containing URLs[/bold yellow]"
        ).strip()
        if not file_path:
            console.print("[bold red]🚨 No file path provided.[/bold red]")
            return None
        return file_path
    except (KeyboardInterrupt, EOFError):
        return None


def prompt_for_snapshot_name() -> str | None:
    """
    Prompt the user to enter a snapshot name.

    This function uses the `Prompt.ask` method to request a name for the snapshot from the user.
    If the user provides an empty input or if an interruption occurs (e.g., KeyboardInterrupt or EOFError),
    the function will return None.

    Returns:
        str | None: The name entered by the user, or None if no name was provided or an interruption occurred.
    """
    try:
        name = Prompt.ask(
            "[bold yellow]📝 Enter a name for the snapshot[/bold yellow]"
        ).strip()
        if not name:
            console.print("[bold red]🚨 No snapshot name provided.[/bold red]")
            return None
        return name
    except (KeyboardInterrupt, EOFError):
        return None


def prompt_for_snapshots() -> tuple[int | None, int | None]:
    """
    Prompt the user to select two snapshots for comparison from a list of available snapshots.

    Returns:
        tuple[int | None, int | None]: A tuple containing the IDs of the two selected snapshots.
        If the user chooses to return to the main menu or if there are not enough snapshots,
        the function returns (None, None).
    """
    snapshots = db_manager.get_snapshots()
    if len(snapshots) < 2:
        console.print(
            "[bold red]🚨 Not enough snapshots available to compare.[/bold red]"
        )
        console.print(
            "[bold cyan]Press Enter to return to the main menu...[/bold cyan]"
        )
        input()
        return None, None

    options = ["🔙 Return to Main Menu"] + [
        f"{snapshot.snapshot_id}: {snapshot.name} ({snapshot.created_at.strftime('%Y-%m-%d %H:%M:%S')})"
        for snapshot in snapshots
    ]

    console.print(
        "[bold cyan]🕹️ Use arrow keys to select snapshots to compare, and press Enter.[/bold cyan]"
    )

    try:
        console.print("Select the first snapshot:")
        selected_option1 = inquirer.select(
            message="",
            choices=options,
            pointer="> ",
            default=None,
        ).execute()
    except KeyboardInterrupt:
        return None, None

    if selected_option1 == "🔙 Return to Main Menu":
        return None, None

    try:
        console.print("Select the second snapshot:")
        selected_option2 = inquirer.select(
            message="",
            choices=options,
            pointer="> ",
            default=None,
        ).execute()
    except KeyboardInterrupt:
        return None, None

    if selected_option2 == "🔙 Return to Main Menu":
        return None, None

    idx1 = options.index(selected_option1) - 1
    idx2 = options.index(selected_option2) - 1

    snapshot1_id = snapshots[idx1].snapshot_id
    snapshot2_id = snapshots[idx2].snapshot_id

    return snapshot1_id, snapshot2_id


def prompt_for_snapshot_id() -> int | None:
    """
    Prompt the user to select a snapshot ID from a list of available snapshots.

    Returns:
        int | None: The selected snapshot ID, or None if no snapshots are available
        or the user chooses to return to the main menu.
    """
    snapshots = db_manager.get_snapshots()
    if not snapshots:
        console.print("[bold red]🚨 No snapshots available.[/bold red]")
        console.print(
            "[bold cyan]Press Enter to return to the main menu...[/bold cyan]"
        )
        input()
        return None

    options = ["🔙 Return to Main Menu"] + [
        f"{snapshot.snapshot_id}: {snapshot.name} ({snapshot.created_at.strftime('%Y-%m-%d %H:%M:%S')})"
        for snapshot in snapshots
    ]

    console.print(
        "[bold cyan]🕹️ Use arrow keys to select a snapshot to view, and press Enter.[/bold cyan]"
    )

    try:
        console.print("Select a snapshot to view:")
        selected_option = inquirer.select(
            message="",
            choices=options,
            pointer=">",
            default=None,
        ).execute()
    except KeyboardInterrupt:
        return None

    if selected_option == "🔙 Return to Main Menu":
        return None

    idx = options.index(selected_option) - 1
    snapshot_id = snapshots[idx].snapshot_id

    return snapshot_id

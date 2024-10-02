# url_snapshotter/cli.py

import difflib
import sys
import time
from signal import SIGINT, signal

import click
from InquirerPy import inquirer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from yaspin import yaspin

from url_snapshotter.db_utils import DatabaseManager
from url_snapshotter.logger_utils import setup_logger
from url_snapshotter.snapshot_manager import SnapshotManager

console = Console()


class SnapshotCLI:
    """
    SnapshotCLI is a command-line interface for managing URL snapshots. It provides functionalities to create, compare, view, and list snapshots of URLs.

    Methods
    -------
    __init__(self, debug: bool = False)
        Initialize the SnapshotCLI with optional debug mode.

    set_debug_mode(self, debug: bool)
        Enable or disable debug logging based on the debug flag.

    prompt_for_file(self) -> str | None
        Prompt the user to enter a file path for URLs.

    prompt_for_snapshot_name(self) -> str | None
        Prompt the user to enter a snapshot name.

    load_urls_from_file(self, file_path: str) -> list[str]
        Load URLs from a specified file.

    handle_create(self, file: str | None, name: str | None, concurrent: int)
        Handle the creation of a new snapshot.

    handle_compare(self, snapshot1_id: int | None = None, snapshot2_id: int | None = None)
        Handle the comparison of two snapshots.

    handle_view(self, snapshot_id: int | None = None)
        Handle viewing the details of a snapshot.

    list_snapshots(self)
        List all available snapshots.

    prompt_for_snapshots(self) -> tuple[int | None, int | None]
        Prompt the user to select snapshots for comparison.

    prompt_for_snapshot_id(self) -> int | None
        Prompt the user to select a snapshot ID.

    display_differences(self, differences: list[dict[str, any]])
        Display content differences between snapshots.

    display_snapshot_details(self, snapshot_data: list[dict[str, any]])
        Display the details of a specific snapshot.

    _signal_handler(self, signal_received, frame)
        Handle exit gracefully on SIGINT (Ctrl+C).

    setup_signal_handling(self)
        Set up signal handler for SIGINT.

    display_main_menu(self)
        Display the main menu and handle navigation.
    """

    def __init__(self, debug: bool = False):
        """
        Initializes the CLI class.

        Args:
            debug (bool): If True, enables debug mode. Defaults to False.

        Attributes:
            logger (Logger): Logger instance for logging messages.
            db_manager (DatabaseManager): Manages database operations.
            snapshot_manager (SnapshotManager): Manages snapshot operations.
            debug (bool): Indicates if debug mode is enabled.
        """
        self.logger = setup_logger(debug)
        self.db_manager = DatabaseManager()
        self.snapshot_manager = SnapshotManager(self.db_manager)
        self.setup_signal_handling()
        self.debug = debug

    def set_debug_mode(self, debug: bool):
        """
        Set the logging level to DEBUG if the debug flag is True, otherwise set it to INFO.

        Args:
            debug (bool): A flag indicating whether to enable debug logging.
        """
        self.logger.setLevel("DEBUG" if debug else "INFO")

    def prompt_for_file(self) -> str | None:
        """
        Prompt the user to enter a file path for URLs.

        Returns:
            str | None: The file path entered by the user, or None if no path is provided or if an interruption occurs.
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

    def prompt_for_snapshot_name(self) -> str | None:
        """
        Prompt the user to enter a snapshot name.

        Returns:
            str | None: The name entered by the user, or None if no name is provided
            or if the input is interrupted by KeyboardInterrupt or EOFError.
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

    def load_urls_from_file(self, file_path: str) -> list[str]:
        """
        Load URLs from a specified file.

        Args:
            file_path (str): The path to the file containing URLs.

        Returns:
            list[str]: A list of URLs loaded from the file.

        Raises:
            ValueError: If the file is empty.
            FileNotFoundError: If the file does not exist.
            Exception: If any other error occurs while loading URLs.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                urls = [line.strip() for line in f if line.strip()]
            if not urls:
                console.print(
                    f"[bold red]🚨 The file '{file_path}' is empty.[/bold red]"
                )
                raise ValueError("Empty URL file.")
            return urls
        except FileNotFoundError:
            console.print(f"[bold red]🚨 File '{file_path}' not found.[/bold red]")
            raise
        except Exception as e:
            console.print(
                f"[bold red]🚨 An error occurred while loading URLs: {e}[/bold red]"
            )
            raise

    def handle_create(self, file: str | None, name: str | None, concurrent: int):
        """
        Handle the creation of a new snapshot.

        Parameters:
        file (str | None): The path to the file containing URLs. If None, the user will be prompted to provide it.
        name (str | None): The name of the snapshot. If None, the user will be prompted to provide it.
        concurrent (int): The number of concurrent operations to perform during snapshot creation.

        Returns:
        None

        This method prompts the user for a file path and snapshot name if they are not provided. It then loads the URLs from the specified file and creates a snapshot using the snapshot manager. A spinner is displayed during the snapshot creation process. If an error occurs, it is logged and displayed to the user. The user is prompted to press Enter to return to the main menu after the operation completes.
        """
        try:
            file_path = file or self.prompt_for_file()
            if not file_path:
                return
            urls = self.load_urls_from_file(file_path)
            name = name or self.prompt_for_snapshot_name()
            if not name:
                return

            with yaspin(text="Creating snapshot...", color="cyan") as spinner:
                self.snapshot_manager.create_snapshot(urls, name, concurrent)
                time.sleep(0.5)
                spinner.ok("✔")

            console.print("[bold green]✅ Snapshot created successfully![/bold green]")
        except Exception as e:
            console.print(f"[bold red]🚨 An error occurred: {e}[/bold red]")
            if self.debug:
                self.logger.exception("Exception in handle_create")

        console.print(
            "[bold cyan]Press Enter to return to the main menu...[/bold cyan]"
        )
        input()

    def handle_compare(
        self, snapshot1_id: int | None = None, snapshot2_id: int | None = None
    ):
        """
        Handle the comparison of two snapshots.

        This method compares two snapshots identified by their IDs. If the IDs are not provided,
        it prompts the user to input them. The differences between the snapshots are then displayed.

        Args:
            snapshot1_id (int | None): The ID of the first snapshot to compare. Defaults to None.
            snapshot2_id (int | None): The ID of the second snapshot to compare. Defaults to None.

        Raises:
            Exception: If an error occurs during the comparison process, it is caught and logged.
        """
        try:
            if snapshot1_id is None or snapshot2_id is None:
                snapshot1_id, snapshot2_id = self.prompt_for_snapshots()
                if snapshot1_id is None or snapshot2_id is None:
                    return

            differences = self.snapshot_manager.compare_snapshots(
                snapshot1_id, snapshot2_id
            )
            self.display_differences(differences)
        except Exception as e:
            console.print(f"[bold red]🚨 An error occurred: {e}[/bold red]")
            if self.debug:
                self.logger.exception("Exception in handle_compare")

        console.print(
            "[bold cyan]Press Enter to return to the main menu...[/bold cyan]"
        )
        input()

    def handle_view(self, snapshot_id: int | None = None):
        """
        Handle viewing the details of a snapshot.

        Parameters:
        snapshot_id (int | None): The ID of the snapshot to view. If None, the user will be prompted to enter an ID.

        This method retrieves and displays the details of a snapshot. If no snapshot ID is provided, it prompts the user to enter one.
        If an error occurs during the process, it logs the exception and displays an error message to the user.
        After displaying the snapshot details, it waits for the user to press Enter to return to the main menu.
        """
        try:
            if snapshot_id is None:
                snapshot_id = self.prompt_for_snapshot_id()
                if snapshot_id is None:
                    return

            snapshot_data = self.snapshot_manager.view_snapshot(snapshot_id)
            self.display_snapshot_details(snapshot_data)
        except Exception as e:
            console.print(f"[bold red]🚨 An error occurred: {e}[/bold red]")
            if self.debug:
                self.logger.exception("Exception in handle_view")

        console.print(
            "[bold cyan]Press Enter to return to the main menu...[/bold cyan]"
        )
        input()

    def list_snapshots(self):
        """
        Lists all available snapshots stored in the database.

        This method retrieves snapshots from the database using the db_manager,
        and displays them in a formatted table using the console. If no snapshots
        are found, a warning message is displayed. In case of an error during
        retrieval, an error message is shown and the exception is logged if debug
        mode is enabled.

        Raises:
            Exception: If an error occurs during the retrieval of snapshots.

        Notes:
            - The table displays the snapshot ID, name, and creation timestamp.
            - The user is prompted to press Enter to return to the main menu after
              the snapshots are listed or an error message is displayed.
        """
        try:
            snapshots = self.db_manager.get_snapshots()
            if not snapshots:
                console.print("[bold yellow]⚠️ No snapshots found.[/bold yellow]")
            else:
                table = Table(title="Available Snapshots", show_lines=True)
                table.add_column("ID", style="cyan", no_wrap=True)
                table.add_column("Name", style="magenta")
                table.add_column("Created At", style="green")
                for snapshot in snapshots:
                    table.add_row(
                        str(snapshot.snapshot_id),
                        snapshot.name,
                        snapshot.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    )
                console.print(table)
        except Exception as e:
            console.print(f"[bold red]🚨 An error occurred: {e}[/bold red]")
            if self.debug:
                self.logger.exception("Exception in list_snapshots")

        console.print(
            "[bold cyan]Press Enter to return to the main menu...[/bold cyan]"
        )
        input()

    def prompt_for_snapshots(self) -> tuple[int | None, int | None]:
        """
        Prompts the user to select two snapshots for comparison from a list of available snapshots.

        Returns:
            tuple[int | None, int | None]: A tuple containing the IDs of the two selected snapshots.
            If the user chooses to return to the main menu or if there are not enough snapshots,
            the function returns (None, None).

        Raises:
            KeyboardInterrupt: If the user interrupts the selection process.

        Notes:
            - The function uses the `inquirer` library to display a selection menu.
            - If there are fewer than two snapshots available, the user is notified and prompted to return to the main menu.
            - The user can return to the main menu at any selection prompt by choosing the "Return to Main Menu" option.
        """
        snapshots = self.db_manager.get_snapshots()
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

    def prompt_for_snapshot_id(self) -> int | None:
        """
        Prompt the user to select a snapshot ID from a list of available snapshots.

        This method retrieves a list of snapshots from the database manager and displays them
        to the user in a selectable menu. The user can navigate the menu using arrow keys and
        select a snapshot to view. If no snapshots are available, a message is displayed and
        the user is prompted to press Enter to return to the main menu.

        Returns:
            int | None: The selected snapshot ID, or None if no snapshots are available or the
                user chooses to return to the main menu.
        """
        snapshots = self.db_manager.get_snapshots()
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
                pointer="> ",
                default=None,
            ).execute()
        except KeyboardInterrupt:
            return None

        if selected_option == "🔙 Return to Main Menu":
            return None

        idx = options.index(selected_option) - 1
        snapshot_id = snapshots[idx].snapshot_id

        return snapshot_id

    def display_differences(self, differences: list[dict[str, any]]):
        """
        Display content differences between snapshots.

        Args:
            differences (list[dict[str, any]]): A list of dictionaries containing the differences between snapshots.
                Each dictionary should have the following keys:
                    - 'url': The URL of the snapshot.
                    - 'snapshot1_http_code': The HTTP status code of the first snapshot.
                    - 'snapshot2_http_code': The HTTP status code of the second snapshot.
                    - 'snapshot1_full_content': The full content of the first snapshot.
                    - 'snapshot2_full_content': The full content of the second snapshot.

        Returns:
            None

        Behavior:
            - If no differences are found, a message indicating no differences will be printed.
            - For each difference, the URL and HTTP status codes of both snapshots will be printed.
            - The user will be prompted to view the content differences for each URL.
            - If the user chooses to view the differences, a unified diff of the content will be displayed.
            - If there are no content differences, a message indicating no differences will be printed.
            - Handles user interruption (KeyboardInterrupt, EOFError) gracefully by returning to the main menu.
        """
        if not differences:
            console.print(
                "[bold green]✅ No differences found between the snapshots.[/bold green]"
            )
            return

        for diff in differences:
            url = diff["url"]
            code1 = diff["snapshot1_http_code"]
            code2 = diff["snapshot2_http_code"]
            content1 = diff["snapshot1_full_content"]
            content2 = diff["snapshot2_full_content"]
            console.print(f"[bold cyan]🌐 URL: {url}[/bold cyan]")
            console.print(f"  [yellow]📄 Snapshot 1 - HTTP Code: {code1}[/yellow]")
            console.print(f"  [yellow]📄 Snapshot 2 - HTTP Code: {code2}[/yellow]")

            try:
                show_diff = (
                    Prompt.ask(
                        f"[bold cyan]📝 Do you want to see the content differences for {url}? (y/N)[/bold cyan]",
                        default="N",
                        choices=["y", "n", "Y", "N"],
                        show_choices=False,
                    ).lower()
                    == "y"
                )
            except (KeyboardInterrupt, EOFError):
                console.print("\n[bold yellow]Returning to main menu...[/bold yellow]")
                return

            if show_diff:
                diff_lines = list(
                    difflib.unified_diff(
                        content1.splitlines(),
                        content2.splitlines(),
                        fromfile="Snapshot 1",
                        tofile="Snapshot 2",
                        lineterm="",
                    )
                )
                if diff_lines:
                    console.print("[bold magenta]--- Differences ---[/bold magenta]")
                    for line in diff_lines:
                        if line.startswith("+"):
                            console.print(line, style="green", highlight=False)
                        elif line.startswith("-"):
                            console.print(line, style="red", highlight=False)
                        else:
                            console.print(line, highlight=False)
                else:
                    console.print("[bold green]No differences in content.[/bold green]")

    def display_snapshot_details(self, snapshot_data: list[dict[str, any]]):
        """
        Display the details of a specific snapshot.

        Args:
            snapshot_data (list[dict[str, any]]): A list of dictionaries containing snapshot details.
                Each dictionary should have the following keys:
                    - 'url' (str): The URL of the snapshot.
                    - 'http_code' (int): The HTTP status code of the snapshot.
                    - 'content_hash' (str): The content hash of the snapshot.

        Returns:
            None
        """
        if not snapshot_data:
            console.print(
                "[bold yellow]⚠️ No data found for this snapshot.[/bold yellow]"
            )
            return

        table = Table(title="Snapshot Details", show_lines=True)
        table.add_column("URL", style="cyan")
        table.add_column("HTTP Code", style="magenta")
        table.add_column("Content Hash", style="green")

        for entry in snapshot_data:
            url = entry["url"]
            http_code = str(entry["http_code"])
            content_hash = entry["content_hash"]
            table.add_row(url, http_code, content_hash)

        console.print(table)

    def _signal_handler(self, signal_received, frame):
        """
        Handle exit gracefully on SIGINT (Ctrl+C).

        Args:
            signal_received (int): The signal number received.
            frame (FrameType): The current stack frame.

        This method prints a message to the console and exits the program with a status code of 0.
        """
        console.print(
            "\n[bold yellow]🚨 Received exit signal. Exiting gracefully...[/bold yellow]"
        )
        sys.exit(0)

    def setup_signal_handling(self):
        """
        Set up signal handler for SIGINT.

        This method registers a custom signal handler for the SIGINT signal,
        which is typically sent when the user interrupts the program (e.g., by
        pressing Ctrl+C). The custom signal handler is defined in the
        `_signal_handler` method of the class.

        Raises:
            ValueError: If the signal handler cannot be set.
        """
        signal(SIGINT, self._signal_handler)

    def display_main_menu(self):
        """
        Display the main menu and handle user navigation.

        This method continuously displays the main menu until the user chooses to exit.
        It provides options for creating new snapshots, comparing snapshots, viewing a snapshot,
        listing all snapshots, or exiting the application. User input is handled using the
        `inquirer` library, and appropriate methods are called based on the user's choice.

        Menu Options:
        - 🆕 Create new snapshot of URLs: Initiates the process to create a new snapshot.
        - 📊 Compare snapshots: Initiates the process to compare existing snapshots.
        - 🔍 View snapshot: Allows the user to view a specific snapshot.
        - 📄 List snapshots: Lists all available snapshots.
        - 🚪 Exit: Exits the application.

        If the user interrupts the process (e.g., via Ctrl+C), the application will exit gracefully.

        Raises:
            SystemExit: Exits the application when the user chooses to exit or interrupts the process.
        """
        while True:
            console.clear()
            banner = """[bold green]URL Snapshotter - Monitor changes in web content[/bold green]
[bold yellow]Licensed under the MIT License[/bold yellow]"""
            console.print(Panel(banner, expand=False, style="bold blue"))

            console.print("🎯 [bold]Enter your choice:[/bold]")
            try:
                choice = inquirer.select(
                    message="",
                    choices=[
                        "🆕 Create new snapshot of URLs",
                        "📊 Compare snapshots",
                        "🔍 View snapshot",
                        "📄 List snapshots",
                        "🚪 Exit",
                    ],
                    pointer=">",
                    default=None,
                ).execute()
            except KeyboardInterrupt:
                console.print(
                    "\n[bold yellow]👋 Exiting the application...[/bold yellow]"
                )
                sys.exit(0)

            if choice == "🆕 Create new snapshot of URLs":
                self.handle_create(None, None, 4)
            elif choice == "📊 Compare snapshots":
                self.handle_compare()
            elif choice == "🔍 View snapshot":
                self.handle_view()
            elif choice == "📄 List snapshots":
                self.list_snapshots()
            elif choice == "🚪 Exit":
                console.print(
                    "[bold yellow]👋 Exiting the application...[/bold yellow]"
                )
                sys.exit(0)
            else:
                console.print("[bold red]🚨 Invalid choice. Try again.[/bold red]")


@click.group(invoke_without_command=True)
@click.option("--debug", is_flag=True, help="Enable debug logging.")
@click.pass_context
def cli(ctx, debug):
    """
    URL Snapshotter CLI

    Parameters:
    ctx (click.Context): The Click context object which holds metadata about the command execution.
    debug (bool): Flag to enable or disable debug mode.

    Returns:
    None
    """
    ctx.obj = SnapshotCLI(debug)
    if ctx.invoked_subcommand is None:
        ctx.obj.display_main_menu()


@cli.command()
@click.option(
    "--file",
    "-f",
    type=click.Path(exists=True),
    help="Path to the file containing URLs.",
)
@click.option("--name", "-n", type=str, help="Name for the snapshot.")
@click.option(
    "--concurrent",
    "-c",
    default=4,
    show_default=True,
    help="Number of concurrent requests.",
)
@click.pass_obj
def create(cli_obj, file, name, concurrent):
    """
    Create a new snapshot of URLs.

    Parameters:
    cli_obj (SnapshotCLI): The CLI object that handles the creation process.
    file (str | None): The path to the file containing the URLs to snapshot. If None, the user will be prompted to provide it.
    name (str | None): The name of the snapshot. If None, the user will be prompted to provide it.
    concurrent (int): The number of concurrent requests to perform during snapshot creation.
    """
    cli_obj.handle_create(file, name, concurrent)


@cli.command()
@click.option("--snapshot1", "-s1", type=int, help="ID of the first snapshot.")
@click.option("--snapshot2", "-s2", type=int, help="ID of the second snapshot.")
@click.pass_obj
def compare(cli_obj, snapshot1, snapshot2):
    """
    Compare two snapshots.

    Args:
        cli_obj: An instance of the CLI object that handles the comparison.
        snapshot1: The first snapshot to compare.
        snapshot2: The second snapshot to compare.
    """
    cli_obj.handle_compare(snapshot1, snapshot2)


@cli.command()
@click.option("--snapshot-id", "-id", type=int, help="ID of the snapshot to view.")
@click.pass_obj
def view(cli_obj, snapshot_id):
    """
    View the details of a snapshot.

    Args:
        cli_obj: An instance of the CLI object that handles the view operation.
        snapshot_id (int): The unique identifier of the snapshot to be viewed.
    """
    cli_obj.handle_view(snapshot_id)


@cli.command()
@click.pass_obj
def list_snapshots(cli_obj):
    """
    List all available snapshots.

    This function calls the `list_snapshots` method on the provided `cli_obj`
    to retrieve and display a list of all available snapshots.

    Args:
        cli_obj: An object that has a `list_snapshots` method to list snapshots.
    """
    """List all available snapshots."""
    cli_obj.list_snapshots()


if __name__ == "__main__":
    cli()

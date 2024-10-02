# url_snapshotter/cli.py

import sys
import time
import difflib
from signal import signal, SIGINT

import click
from InquirerPy import inquirer
from yaspin import yaspin

from url_snapshotter.snapshot_manager import SnapshotManager
from url_snapshotter.db_utils import DatabaseManager
from url_snapshotter.logger_utils import setup_logger

from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel

console = Console()


class SnapshotCLI:
    def __init__(self, debug: bool = False):
        self.logger = setup_logger(debug)
        self.db_manager = DatabaseManager()
        self.snapshot_manager = SnapshotManager(self.db_manager)
        self.setup_signal_handling()
        self.debug = debug

    def set_debug_mode(self, debug: bool):
        """Enable debug logging if the debug flag is set."""
        self.logger.setLevel('DEBUG' if debug else 'INFO')

    def prompt_for_file(self) -> str | None:
        """Prompt the user to enter a file path for URLs."""
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
        """Prompt the user to enter a snapshot name."""
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
        """Load URLs from a specified file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
            if not urls:
                console.print(f"[bold red]🚨 The file '{file_path}' is empty.[/bold red]")
                raise ValueError("Empty URL file.")
            return urls
        except FileNotFoundError:
            console.print(f"[bold red]🚨 File '{file_path}' not found.[/bold red]")
            raise
        except Exception as e:
            console.print(f"[bold red]🚨 An error occurred while loading URLs: {e}[/bold red]")
            raise

    def handle_create(self, file: str | None, name: str | None, concurrent: int):
        """Handle the creation of a new snapshot."""
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

        console.print("[bold cyan]Press Enter to return to the main menu...[/bold cyan]")
        input()

    def handle_compare(self, snapshot1_id: int | None = None, snapshot2_id: int | None = None):
        """Handle the comparison of two snapshots."""
        try:
            if snapshot1_id is None or snapshot2_id is None:
                snapshot1_id, snapshot2_id = self.prompt_for_snapshots()
                if snapshot1_id is None or snapshot2_id is None:
                    return

            differences = self.snapshot_manager.compare_snapshots(snapshot1_id, snapshot2_id)
            self.display_differences(differences)
        except Exception as e:
            console.print(f"[bold red]🚨 An error occurred: {e}[/bold red]")
            if self.debug:
                self.logger.exception("Exception in handle_compare")

        console.print("[bold cyan]Press Enter to return to the main menu...[/bold cyan]")
        input()

    def handle_view(self, snapshot_id: int | None = None):
        """Handle viewing the details of a snapshot."""
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

        console.print("[bold cyan]Press Enter to return to the main menu...[/bold cyan]")
        input()

    def list_snapshots(self):
        """List all available snapshots."""
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
                        snapshot.created_at.strftime("%Y-%m-%d %H:%M:%S")
                    )
                console.print(table)
        except Exception as e:
            console.print(f"[bold red]🚨 An error occurred: {e}[/bold red]")
            if self.debug:
                self.logger.exception("Exception in list_snapshots")

        console.print("[bold cyan]Press Enter to return to the main menu...[/bold cyan]")
        input()

    def prompt_for_snapshots(self) -> tuple[int | None, int | None]:
        """Prompt the user to select snapshots for comparison."""
        snapshots = self.db_manager.get_snapshots()
        if len(snapshots) < 2:
            console.print("[bold red]🚨 Not enough snapshots available to compare.[/bold red]")
            console.print("[bold cyan]Press Enter to return to the main menu...[/bold cyan]")
            input()
            return None, None

        options = ["🔙 Return to Main Menu"] + [
            f"{snapshot.snapshot_id}: {snapshot.name} ({snapshot.created_at.strftime('%Y-%m-%d %H:%M:%S')})"
            for snapshot in snapshots
        ]

        console.print("[bold cyan]🕹️ Use arrow keys to select snapshots to compare, and press Enter.[/bold cyan]")

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
        """Prompt the user to select a snapshot ID."""
        snapshots = self.db_manager.get_snapshots()
        if not snapshots:
            console.print("[bold red]🚨 No snapshots available.[/bold red]")
            console.print("[bold cyan]Press Enter to return to the main menu...[/bold cyan]")
            input()
            return None

        options = ["🔙 Return to Main Menu"] + [
            f"{snapshot.snapshot_id}: {snapshot.name} ({snapshot.created_at.strftime('%Y-%m-%d %H:%M:%S')})"
            for snapshot in snapshots
        ]

        console.print("[bold cyan]🕹️ Use arrow keys to select a snapshot to view, and press Enter.[/bold cyan]")

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

    def display_differences(self, differences: list[dict[str, any]]):
        """Display content differences between snapshots."""
        if not differences:
            console.print("[bold green]✅ No differences found between the snapshots.[/bold green]")
            return

        for diff in differences:
            url = diff['url']
            code1 = diff['snapshot1_http_code']
            code2 = diff['snapshot2_http_code']
            content1 = diff['snapshot1_full_content']
            content2 = diff['snapshot2_full_content']
            console.print(f"[bold cyan]🌐 URL: {url}[/bold cyan]")
            console.print(f"  [yellow]📄 Snapshot 1 - HTTP Code: {code1}[/yellow]")
            console.print(f"  [yellow]📄 Snapshot 2 - HTTP Code: {code2}[/yellow]")

            # Prompt user to see content differences
            try:
                show_diff = Prompt.ask(
                    f"[bold cyan]📝 Do you want to see the content differences for {url}? (y/N)[/bold cyan]",
                    default="N",
                    choices=["y", "n", "Y", "N"],
                    show_choices=False,
                ).lower() == 'y'
            except (KeyboardInterrupt, EOFError):
                console.print("\n[bold yellow]Returning to main menu...[/bold yellow]")
                return

            if show_diff:
                diff_lines = list(difflib.unified_diff(
                    content1.splitlines(), content2.splitlines(),
                    fromfile='Snapshot 1', tofile='Snapshot 2',
                    lineterm=''
                ))
                if diff_lines:
                    console.print("[bold magenta]--- Differences ---[/bold magenta]")
                    for line in diff_lines:
                        if line.startswith('+'):
                            console.print(line, style="green", highlight=False)
                        elif line.startswith('-'):
                            console.print(line, style="red", highlight=False)
                        else:
                            console.print(line, highlight=False)
                else:
                    console.print("[bold green]No differences in content.[/bold green]")

    def display_snapshot_details(self, snapshot_data: list[dict[str, any]]):
        """Display the details of a specific snapshot."""
        if not snapshot_data:
            console.print("[bold yellow]⚠️ No data found for this snapshot.[/bold yellow]")
            return

        table = Table(title="Snapshot Details", show_lines=True)
        table.add_column("URL", style="cyan")
        table.add_column("HTTP Code", style="magenta")
        table.add_column("Content Hash", style="green")

        for entry in snapshot_data:
            url = entry['url']
            http_code = str(entry['http_code'])
            content_hash = entry['content_hash']
            table.add_row(url, http_code, content_hash)

        console.print(table)

    def _signal_handler(self, signal_received, frame):
        """Handle exit gracefully on SIGINT (Ctrl+C)."""
        console.print("\n[bold yellow]🚨 Received exit signal. Exiting gracefully...[/bold yellow]")
        sys.exit(0)

    def setup_signal_handling(self):
        """Set up signal handler for SIGINT."""
        signal(SIGINT, self._signal_handler)

    def display_main_menu(self):
        """Display the main menu and handle navigation."""
        while True:
            console.clear()
            # Create a fancy banner for the main menu
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
                        "🚪 Exit"
                    ],
                    pointer=">",
                    default=None,
                ).execute()
            except KeyboardInterrupt:
                console.print("\n[bold yellow]👋 Exiting the application...[/bold yellow]")
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
                console.print("[bold yellow]👋 Exiting the application...[/bold yellow]")
                sys.exit(0)
            else:
                console.print("[bold red]🚨 Invalid choice. Try again.[/bold red]")


@click.group(invoke_without_command=True)
@click.option('--debug', is_flag=True, help="Enable debug logging.")
@click.pass_context
def cli(ctx, debug):
    """URL Snapshotter CLI"""
    ctx.obj = SnapshotCLI(debug)
    if ctx.invoked_subcommand is None:
        ctx.obj.display_main_menu()


@cli.command()
@click.option('--file', '-f', type=click.Path(exists=True), help='Path to the file containing URLs.')
@click.option('--name', '-n', type=str, help='Name for the snapshot.')
@click.option('--concurrent', '-c', default=4, show_default=True, help='Number of concurrent requests.')
@click.pass_obj
def create(cli_obj, file, name, concurrent):
    """Create a new snapshot of URLs."""
    cli_obj.handle_create(file, name, concurrent)


@cli.command()
@click.option('--snapshot1', '-s1', type=int, help='ID of the first snapshot.')
@click.option('--snapshot2', '-s2', type=int, help='ID of the second snapshot.')
@click.pass_obj
def compare(cli_obj, snapshot1, snapshot2):
    """Compare two snapshots."""
    cli_obj.handle_compare(snapshot1, snapshot2)


@cli.command()
@click.option('--snapshot-id', '-id', type=int, help='ID of the snapshot to view.')
@click.pass_obj
def view(cli_obj, snapshot_id):
    """View the details of a snapshot."""
    cli_obj.handle_view(snapshot_id)


@cli.command()
@click.pass_obj
def list_snapshots(cli_obj):
    """List all available snapshots."""
    cli_obj.list_snapshots()


if __name__ == '__main__':
    cli()

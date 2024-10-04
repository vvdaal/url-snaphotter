# url_snapshotter/cli.py

import sys
from signal import signal, SIGINT

import click
from InquirerPy import inquirer

from url_snapshotter.commands.create_command import handle_create
from url_snapshotter.commands.compare_command import handle_compare
from url_snapshotter.commands.view_command import handle_view
from url_snapshotter.commands.list_command import handle_list_snapshots
from url_snapshotter.logger_utils import setup_logger
from rich.console import Console
from rich.panel import Panel

console = Console()
logger = setup_logger()


def _signal_handler(signal_received, frame):
    """Handle exit gracefully on SIGINT (Ctrl+C)."""
    console.print(
        "\n[bold yellow]🚨 Received exit signal. Exiting gracefully...[/bold yellow]"
    )
    sys.exit(0)


def setup_signal_handling():
    """Set up signal handler for SIGINT."""
    signal(SIGINT, _signal_handler)


@click.group(invoke_without_command=True)
@click.option("--debug", is_flag=True, help="Enable debug logging.")
@click.pass_context
def cli(ctx, debug):
    """URL Snapshotter CLI"""
    setup_signal_handling()

    if debug:
        logger.setLevel("DEBUG")

    if ctx.invoked_subcommand is None:
        display_main_menu()


def display_main_menu():
    """Display the main menu and handle navigation."""
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
            console.print("\n[bold yellow]👋 Exiting the application...[/bold yellow]")
            sys.exit(0)

        if choice == "🆕 Create new snapshot of URLs":
            handle_create(None, None, 4)
        elif choice == "📊 Compare snapshots":
            handle_compare()
        elif choice == "🔍 View snapshot":
            handle_view()
        elif choice == "📄 List snapshots":
            handle_list_snapshots()
        elif choice == "🚪 Exit":
            console.print("[bold yellow]👋 Exiting the application...[/bold yellow]")
            sys.exit(0)
        else:
            console.print("[bold red]🚨 Invalid choice. Try again.[/bold red]")


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
def create(file, name, concurrent):
    """Create a new snapshot of URLs."""
    handle_create(file, name, concurrent)


@cli.command()
@click.option("--snapshot1", "-s1", type=int, help="ID of the first snapshot.")
@click.option("--snapshot2", "-s2", type=int, help="ID of the second snapshot.")
def compare(snapshot1, snapshot2):
    """Compare two snapshots."""
    handle_compare(snapshot1, snapshot2)


@cli.command()
@click.option("--snapshot-id", "-id", type=int, help="ID of the snapshot to view.")
def view(snapshot_id):
    """View the details of a snapshot."""
    handle_view(snapshot_id)


@cli.command()
def list_snapshots():
    """List all available snapshots."""
    handle_list_snapshots()


if __name__ == "__main__":
    cli()

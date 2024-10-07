# url_snapshotter/cli.py

# This module provides the functionality for the command-line interface (CLI).

import sys
from signal import signal, SIGINT

import click
from InquirerPy import inquirer

from url_snapshotter.commands.create_command import handle_create
from url_snapshotter.commands.compare_command import handle_compare
from url_snapshotter.commands.view_command import handle_view
from url_snapshotter.commands.list_command import handle_list_snapshots
from url_snapshotter.logging_config import configure_structlog
from rich.console import Console
from rich.panel import Panel
import logging

console = Console()
logger = logging.getLogger("url_snapshotter")


def _signal_handler(signal_received, frame):
    """
    Handle exit gracefully on SIGINT (Ctrl+C).

    Args:
        signal_received (int): The signal number received.
        frame (FrameType): The current stack frame.

    This function prints a message to the console and exits the program with a status code of 0.
    """

    console.print(
        "\n[bold yellow]🚨 Received exit signal. Exiting gracefully...[/bold yellow]"
    )
    sys.exit(0)


def setup_signal_handling():
    """
    Sets up signal handling for the application.

    This function registers a signal handler for the SIGINT signal (typically
    generated by pressing Ctrl+C). When the SIGINT signal is received, the
    specified _signal_handler function will be called to handle the signal.
    """

    signal(SIGINT, _signal_handler)


@click.group(invoke_without_command=True)
@click.option("--debug", is_flag=True, help="Enable debug logging.")
@click.pass_context
def cli(ctx, debug):
    """
    This function sets up the command-line interface for the URL Snapshotter application.
    It handles signal setup and logging configuration based on the debug flag.

    Args:
        ctx (click.Context): The context object provided by Click, containing information about the command execution.
        debug (bool): A flag indicating whether to enable debug mode. If True, the logger level is set to DEBUG.

    Returns:
        None
    """

    # Set up signal handling
    setup_signal_handling()
    # Set up logger
    configure_structlog(debug)

    logger.debug(
        "Starting URL Snapshotter CLI with debug mode enabled."
        if debug
        else "Starting URL Snapshotter CLI."
    )

    # Display the main menu if no subcommand is provided
    if ctx.invoked_subcommand is None:
        display_main_menu()


def display_main_menu():
    """
    Display the main menu and handle user navigation.

    The main menu provides the following options:
    - Create a new snapshot of URLs
    - Compare snapshots
    - View a snapshot
    - List all snapshots
    - Exit the application

    The function continuously displays the menu until the user chooses to exit.
    It handles user input using an interactive selection prompt and calls the
    appropriate handler functions based on the user's choice.

    If the user interrupts the program (e.g., via Ctrl+C), the function will
    gracefully exit the application.

    Raises:
        SystemExit: Exits the application when the user chooses to exit or interrupts.
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
    """
    Create a new snapshot of URLs.

    Parameters:
    file (str): The path to the file containing URLs to snapshot.
    name (str): The name for the snapshot.
    concurrent (int): The number of concurrent snapshot operations to perform.

    Returns:
    None
    """

    handle_create(file, name, concurrent)


@cli.command()
@click.option("--snapshot1", "-s1", type=int, help="ID of the first snapshot.")
@click.option("--snapshot2", "-s2", type=int, help="ID of the second snapshot.")
def compare(snapshot1, snapshot2):
    """
    Compare two snapshots.

    Args:
        snapshot1 (str): The file path or identifier for the first snapshot.
        snapshot2 (str): The file path or identifier for the second snapshot.

    Returns:
        None
    """

    handle_compare(snapshot1, snapshot2)


@cli.command()
@click.option("--snapshot-id", "-id", type=int, help="ID of the snapshot to view.")
def view(snapshot_id):
    """
    View the details of a snapshot.

    Args:
        snapshot_id (str): The unique identifier of the snapshot to view.
    """

    handle_view(snapshot_id)


@cli.command()
def list_snapshots():
    """
    List all available snapshots by invoking the handle_list_snapshots function.

    This function does not take any parameters and does not return any values.
    It simply calls the handle_list_snapshots function to perform the listing operation.
    """

    handle_list_snapshots()


if __name__ == "__main__":
    logger.debug("Starting URL Snapshotter CLI...")
    cli()

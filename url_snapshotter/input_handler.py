# url_snapshotter/input_handler.py

# This module provides the functionality to handle user input.

import structlog
import validators
from time import sleep

from InquirerPy import inquirer
from rich.console import Console
from rich.prompt import Prompt

from url_snapshotter.db_utils import DatabaseManager

console = Console()
db_manager = DatabaseManager()
logger = structlog.get_logger()


def load_urls_from_file(file_path: str) -> list[str]:
    """
    Load URLs from a specified file.

    This function reads a file line by line, validates each line to ensure it is a valid URL
    starting with "http://" or "https://", and returns a list of valid URLs. If the file is
    empty or contains no valid URLs, or if the file does not exist, appropriate exceptions
    are raised.

    Args:
        file_path (str): The path to the file containing URLs.

    Returns:
        list[str]: A list of valid URLs.

    Raises:
        ValueError: If the file is empty or contains no valid URLs, or if an invalid URL is detected.
        FileNotFoundError: If the specified file does not exist.
        Exception: If an unexpected error occurs while loading URLs.
    """

    logger.debug(f"Attempting to load URLs from file: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            urls = []
            for line in f:
                stripped_line = line.strip()
                if stripped_line:
                    # Check if the line is a valid URL and starts with http or https
                    if validators.url(stripped_line) and (
                        stripped_line.startswith("http://")
                        or stripped_line.startswith("https://")
                    ):
                        urls.append(stripped_line)
                    else:
                        logger.error(f"Invalid URL detected: '{stripped_line}'")
                        raise ValueError(f"Invalid URL detected: '{stripped_line}'")

        if not urls:
            logger.error(
                f"Raising exception that file '{file_path}' is empty or contains no valid URLs."
            )
            raise ValueError(
                f"The file '{file_path}' is empty or contains no valid URLs."
            )

        logger.info(f"Loaded {len(urls)} valid URLs from '{file_path}'")
        return urls

    except FileNotFoundError:
        logger.error(f"Raising exception that '{file_path}' is not found.")
        raise
    except Exception as e:
        logger.exception(f"An unexpected error occurred while loading URLs: {e}")
        raise


def prompt_for_file() -> list[str] | None:
    """
    Prompts the user to enter the path to a file containing URLs or type 'exit' to return to the main menu.

    Returns:
        list[str] | None: A list of URLs if the file is successfully loaded, or None if the user chooses to exit or an error occurs.
    """

    while True:
        try:
            file_path = Prompt.ask(
                "[bold yellow]📂 Enter the path to a file containing URLs (or type 'exit' to return to the main menu)[/bold yellow]"
            ).strip()

            if not file_path:
                console.print(
                    "[bold red]🚨 No file path provided. Please try again.[/bold red]"
                )
                logger.warning("No file path provided by the user.")
            elif file_path.lower() == "exit":
                console.print(
                    "[bold yellow]👋 Returning to the main menu...[/bold yellow]"
                )
                logger.info("User chose to exit to the main menu from file prompt.")
                return None
            else:
                # Attempt to load URLs from the file
                urls = load_urls_from_file(file_path)
                logger.debug(f"Successfully loaded URLs from file: {file_path}")
                return urls
        except FileNotFoundError:
            console.print(f"[bold red]🚨 File '{file_path}' not found.[/bold red]")
        except ValueError as ve:
            console.print(f"[bold red]🚨 {ve}[/bold red]")
            logger.error(f"ValueError: {ve}")
        except Exception as e:
            console.print(f"[bold red]🚨 An unexpected error occurred: {e}[/bold red]")
            logger.exception(f"An unexpected error occurred: {e}")
            console.input(
                "[bold cyan]Press Enter to return to the main menu...[/bold cyan]",
                markup=True,
            )
            return None


def prompt_for_snapshot_name() -> str | None:
    """
    Prompts the user to enter a name for the snapshot using a console prompt.

    Returns:
        str | None: The name provided by the user, or None if no name is provided,
                    the input is interrupted, or an unexpected error occurs.
    """

    try:
        name = Prompt.ask(
            "[bold yellow]📝 Enter a name for the snapshot (Can contain any character)[/bold yellow]"
        ).strip()
        if not name:
            console.print("[bold red]🚨 No snapshot name provided.[/bold red]")
            logger.warning("No snapshot name provided by the user.")
            return None
        logger.info(f"User provided snapshot name: {name}")
        return name
    except (KeyboardInterrupt, EOFError):
        logger.info("User interrupted input for snapshot name.")
        return None
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        return None


def prompt_for_snapshots() -> tuple[int | None, int | None]:
    """
    Prompts the user to select two snapshots for comparison from a list of available snapshots.

    Retrieves snapshots from the database and displays them to the user for selection.
    If there are fewer than two snapshots available, informs the user and returns to the main menu.
    Allows the user to select two snapshots using a console-based menu.
    Handles user interruptions and other exceptions gracefully.

    Returns:
        tuple[int | None, int | None]: A tuple containing the IDs of the two selected snapshots,
        or (None, None) if the user chooses to return to the main menu or an error occurs.
    """

    try:
        snapshots = db_manager.get_snapshots()
        logger.debug(f"Retrieved {len(snapshots)} snapshots from the database.")
        if len(snapshots) < 2:
            console.print(
                "[bold red]🚨 Not enough snapshots available to compare.[/bold red]"
            )
            console.print(
                "[bold cyan]Press Enter to return to the main menu...[/bold cyan]"
            )
            input()
            logger.info("Not enough snapshots to compare. Returning to main menu.")
            return None, None

        options = ["🔙 Return to Main Menu"] + [
            f"{snapshot.snapshot_id}: {snapshot.name} ({snapshot.created_at.strftime('%Y-%m-%d %H:%M:%S')})"
            for snapshot in snapshots
        ]

        console.print(
            "[bold cyan]🕹️ Use arrow keys to select snapshots to compare, and press Enter.[/bold cyan]"
        )

        console.print("Select the first snapshot:")
        selected_option1 = inquirer.select(
            message="",
            choices=options,
            pointer="> ",
            default=None,
        ).execute()

        if selected_option1 == "🔙 Return to Main Menu":
            logger.info(
                "User chose to return to the main menu from snapshot selection."
            )
            return None, None

        console.print("Select the second snapshot:")
        selected_option2 = inquirer.select(
            message="",
            choices=options,
            pointer="> ",
            default=None,
        ).execute()

        if selected_option2 == "🔙 Return to Main Menu":
            logger.info(
                "User chose to return to the main menu from snapshot selection."
            )
            return None, None

        idx1 = options.index(selected_option1) - 1
        idx2 = options.index(selected_option2) - 1

        snapshot1_id = snapshots[idx1].snapshot_id
        snapshot2_id = snapshots[idx2].snapshot_id

        logger.info(
            f"User selected snapshots {snapshot1_id} and {snapshot2_id} for comparison."
        )

        return snapshot1_id, snapshot2_id
    except KeyboardInterrupt:
        logger.info("User interrupted snapshot selection.")
        return None, None
    except Exception as e:
        logger.exception(f"An error occurred during snapshot selection: {e}")
        console.print(f"[bold red]🚨 An error occurred: {e}[/bold red]")
        return None, None


def prompt_for_snapshot_id() -> int | None:
    """
    Prompts the user to select a snapshot ID from a list of available snapshots.

    Retrieves the list of snapshots from the database and displays them to the user.
    The user can select a snapshot to view or choose to return to the main menu.
    Handles user interruptions and exceptions gracefully.

    Returns:
        int | None: The ID of the selected snapshot, or None if the user chooses to return to the main menu
                    or if an error occurs.
    """

    try:
        snapshots = db_manager.get_snapshots()
        logger.debug(f"Retrieved {len(snapshots)} snapshots from the database.")
        if not snapshots:
            console.print("[bold red]🚨 No snapshots available.[/bold red]")
            console.print(
                "[bold cyan]Press Enter to return to the main menu...[/bold cyan]"
            )
            input()
            logger.info("No snapshots available. Returning to main menu.")
            return None

        options = ["🔙 Return to Main Menu"] + [
            f"{snapshot.snapshot_id}: {snapshot.name} ({snapshot.created_at.strftime('%Y-%m-%d %H:%M:%S')})"
            for snapshot in snapshots
        ]

        console.print(
            "[bold cyan]🕹️ Use arrow keys to select a snapshot to view, and press Enter.[/bold cyan]"
        )

        console.print("Select a snapshot to view:")
        selected_option = inquirer.select(
            message="",
            choices=options,
            pointer=">",
            default=None,
        ).execute()

        if selected_option == "🔙 Return to Main Menu":
            logger.info(
                "User chose to return to the main menu from snapshot selection."
            )
            return None

        idx = options.index(selected_option) - 1
        snapshot_id = snapshots[idx].snapshot_id

        logger.info(f"User selected snapshot {snapshot_id} to view.")

        return snapshot_id
    except KeyboardInterrupt:
        logger.info("User interrupted snapshot selection.")
        return None
    except Exception as e:
        logger.exception(f"An error occurred during snapshot selection: {e}")
        console.print(f"[bold red]🚨 An error occurred: {e}[/bold red]")
        return None

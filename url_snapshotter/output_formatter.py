# url_snapshotter/output_formatter.py

from rich.console import Console
from rich.table import Table
import difflib

console = Console()


def display_snapshots_list(snapshots: list):
    """Display a list of all snapshots."""
    if not snapshots:
        console.print("[bold yellow]⚠️ No snapshots found.[/bold yellow]")
        return

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


def display_differences(differences: list[dict[str, any]]):
    """Display content differences between snapshots."""
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

        # Prompt user to see content differences
        show_diff = (
            console.input(
                f"[bold cyan]📝 Do you want to see the content differences for {url}? (y/N):[/bold cyan] "
            ).lower()
            == "y"
        )

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


def display_snapshot_details(snapshot_data: list[dict[str, any]]):
    """Display the details of a specific snapshot."""
    if not snapshot_data:
        console.print("[bold yellow]⚠️ No data found for this snapshot.[/bold yellow]")
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

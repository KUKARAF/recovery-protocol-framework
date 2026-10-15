"""Terminal UI display for Resurrection Protocol."""

from typing import Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich import box


class GameDisplay:
    """Handles all terminal UI display for the game."""

    def __init__(self):
        self.console = Console()

    def show_chapter_intro(self, chapter_data: Dict[str, Any]):
        """Display chapter introduction."""
        self.console.print("\n" + "=" * 60)
        self.console.print(f"[bold cyan]{chapter_data['title']}[/bold cyan]")
        self.console.print("=" * 60)
        self.console.print(f"\n[yellow]{chapter_data['description']}[/yellow]\n")

        if "context" in chapter_data:
            panel = Panel(
                chapter_data["context"],
                title="[bold]MISSION BRIEF[/bold]",
                border_style="blue",
            )
            self.console.print(panel)
            self.console.print()

    def show_challenge_brief(self, challenge_data: Dict[str, Any]):
        """Display challenge brief."""
        self.console.print("\n" + "─" * 60)
        self.console.print(f"[bold green]Challenge: {challenge_data['title']}[/bold green]")
        self.console.print("─" * 60 + "\n")

        self.console.print(f"[white]{challenge_data['description']}[/white]\n")

        if "objectives" in challenge_data:
            self.console.print("[bold cyan]Objectives:[/bold cyan]")
            for obj in challenge_data["objectives"]:
                self.console.print(f"  • {obj}")
            self.console.print()

        if "constraints" in challenge_data:
            self.console.print("[bold yellow]Constraints:[/bold yellow]")
            for constraint in challenge_data["constraints"]:
                self.console.print(f"  • {constraint}")
            self.console.print()

    def show_challenge_results(self, challenge_data: Dict[str, Any], results: Dict[str, Any]):
        """Display challenge evaluation results in Zachatronics style."""
        self.console.print("\n" + "=" * 60)
        self.console.print("[bold]CHALLENGE EVALUATION[/bold]")
        self.console.print("=" * 60 + "\n")

        if results["passed"]:
            self.console.print("[bold green]✓ SOLUTION ACCEPTED[/bold green]")
            status = "green"
        else:
            self.console.print("[bold red]✗ SOLUTION REJECTED[/bold red]")
            status = "red"

        self.console.print(f"\nExecution Time: [cyan]{results['time_elapsed']:.3f}s[/cyan]")

        # Show test output
        self.console.print("\n[bold]Test Output:[/bold]")
        self.console.print(Panel(results["output"], border_style=status, expand=False))

        self.console.print("\n" + "=" * 60 + "\n")

    def show_progress_bar(self, current: int, total: int, title: str = "Progress"):
        """Show a progress bar."""
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:
            progress.add_task(title, total=total, completed=current)


# Future: Textual-based interactive display
class InteractiveGameDisplay:
    """Advanced Textual-based interactive UI (future enhancement)."""

    pass

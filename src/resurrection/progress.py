"""Progress tracking for Resurrection Protocol."""

import json
from pathlib import Path
from typing import Dict
from datetime import datetime


class ProgressTracker:
    """Tracks player progression through the game."""

    def __init__(self):
        self.progress_file = Path.home() / ".resurrection_progress.json"
        self.progress = self._load_progress()

    def _load_progress(self) -> Dict:
        """Load progress from disk."""
        if self.progress_file.exists():
            with open(self.progress_file) as f:
                return json.load(f)
        return {"completed_challenges": {}, "started_at": datetime.now().isoformat()}

    def _save_progress(self):
        """Save progress to disk."""
        with open(self.progress_file, "w") as f:
            json.dump(self.progress, f, indent=2)

    def mark_completed(self, chapter: int, challenge_id: str, score: Dict):
        """Mark a challenge as completed."""
        key = f"chapter_{chapter}_{challenge_id}"
        self.progress["completed_challenges"][key] = {
            "completed_at": datetime.now().isoformat(),
            "score": score,
        }
        self._save_progress()

    def get_completed_count(self) -> int:
        """Get total completed challenges."""
        return len(self.progress["completed_challenges"])

    def display_status(self):
        """Display current progression."""
        from rich.console import Console
        from rich.table import Table

        console = Console()
        console.print("\n[cyan]═══════════════════════════════════════[/cyan]")
        console.print("[cyan]     RESURRECTION PROTOCOL - STATUS[/cyan]")
        console.print("[cyan]═══════════════════════════════════════[/cyan]\n")

        completed = self.get_completed_count()
        console.print(f"Challenges Completed: [green]{completed}[/green]")
        console.print(f"Progress File: {self.progress_file}\n")

        if self.progress["completed_challenges"]:
            table = Table(title="Completed Challenges")
            table.add_column("Challenge", style="cyan")
            table.add_column("Completed At", style="magenta")

            for key, data in self.progress["completed_challenges"].items():
                table.add_row(key, data["completed_at"])

            console.print(table)

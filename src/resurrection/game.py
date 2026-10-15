"""Main game orchestration for Resurrection Protocol."""

import json
from pathlib import Path
from typing import Optional
from resurrection.evaluator import Evaluator
from resurrection.tui.display import GameDisplay


class ResurrectionGame:
    """Main game coordinator for Resurrection Protocol."""

    def __init__(self):
        self.chapters_dir = Path(__file__).parent.parent.parent.parent / "chapters"
        self.evaluator = Evaluator()
        self.display = GameDisplay()

    def run(self, chapter: int = 1, challenge: Optional[int] = None):
        """Run the game."""
        chapter_path = self.chapters_dir / f"chapter_{chapter}"

        if not chapter_path.exists():
            raise FileNotFoundError(f"Chapter {chapter} not found")

        # Load chapter metadata
        metadata_file = chapter_path / "metadata.json"
        if not metadata_file.exists():
            raise FileNotFoundError(f"Chapter metadata not found at {metadata_file}")

        with open(metadata_file) as f:
            chapter_data = json.load(f)

        # Display chapter intro
        self.display.show_chapter_intro(chapter_data)

        # Get list of challenges
        challenges = chapter_data.get("challenges", [])

        if challenge is not None:
            challenges = [c for c in challenges if c["id"] == challenge]

        # Run each challenge
        for ch in challenges:
            self.run_challenge(chapter, ch)

    def run_challenge(self, chapter: int, challenge_data: dict):
        """Run a single challenge."""
        challenge_id = challenge_data["id"]

        # Show challenge brief
        self.display.show_challenge_brief(challenge_data)

        # Get challenge solution file path
        challenge_file = self.get_challenge_file(chapter, challenge_id)

        # Display path to solution file
        print(f"\n[*] Open {challenge_file} in your editor to solve this challenge")
        print(f"[*] After saving your solution, return here and press Enter")

        input("\nPress Enter when you've saved your solution...")

        # Evaluate the solution
        results = self.evaluator.evaluate_challenge(chapter, challenge_id)

        # Display results with TUI
        self.display.show_challenge_results(challenge_data, results)

    def get_challenge_file(self, chapter: int, challenge_id: str) -> Path:
        """Get the path to the challenge solution file."""
        return self.chapters_dir / f"chapter_{chapter}" / "challenges" / f"{challenge_id}.py"

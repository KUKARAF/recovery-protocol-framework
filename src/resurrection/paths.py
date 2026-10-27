"""Find the game folder (the directory holding `modules/`) from anywhere inside it."""

import subprocess
from pathlib import Path
from typing import Optional


def _git_toplevel(start: Path) -> Optional[Path]:
    """Ask git for the work tree root, if `start` is inside one."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=start,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return Path(result.stdout.strip())


def find_game_root(start: Optional[Path] = None) -> Path:
    """Find the game folder: the directory that contains `modules/`.

    Lets `recovery` run from any subdirectory of the game folder, not just
    its root. Prefers asking git for the work tree's top level - git already
    does exactly this upward scan, and does it correctly from any depth.
    Falls back to walking up by hand (looking for a `modules/` directory)
    when we're not inside a git work tree at all.

    Returns `start` unchanged if neither finds anything; callers see a clear
    "no modules found" error from whatever uses the result.
    """
    start = Path(start or Path.cwd()).resolve()

    git_root = _git_toplevel(start)
    if git_root is not None and (git_root / "modules").is_dir():
        return git_root

    for candidate in (start, *start.parents):
        if (candidate / "modules").is_dir():
            return candidate

    return start

"""Recovery validation - runs a single task's tests against the user's solution."""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from resurrection.paths import find_game_root


class ValidationError(Exception):
    """Raised when a validation request cannot be run at all."""


class Validator:
    """Low-level runner: lists modules/tasks, and runs one task's tests at a time.

    Deliberately doesn't know about "which task should I be on" - that's
    ModuleState's job (see state.py). This class only knows how to run one
    task in isolation and report pass/fail plus a minimal error, never the
    raw pytest output.
    """

    def __init__(self, root: Optional[Path] = None):
        # The game folder: the directory that contains the `modules/` folder.
        # Resolved from anywhere inside it (see paths.find_game_root) unless
        # an explicit root is given.
        self.root = Path(root) if root else find_game_root()
        self.modules_dir = self.root / "modules"

    def list_modules(self) -> list[str]:
        """Names of modules available in the game folder."""
        if not self.modules_dir.is_dir():
            return []
        return sorted(
            p.name for p in self.modules_dir.iterdir()
            if p.is_dir() and (p / "tests").is_dir()
        )

    def list_tasks(self, module_name: str) -> list[str]:
        """Task ids for a module, in authored order.

        Prefers the order declared in metadata.json (`missions[].id`), since
        that's the intended play order. Falls back to the tests/ directory,
        sorted, if metadata.json is missing or unreadable.
        """
        module_dir = self.modules_dir / module_name
        metadata_file = module_dir / "metadata.json"
        if metadata_file.is_file():
            try:
                data = json.loads(metadata_file.read_text())
                ids = [m["id"] for m in data.get("missions", []) if "id" in m]
                if ids:
                    return ids
            except (json.JSONDecodeError, OSError):
                pass

        tests_dir = module_dir / "tests"
        if not tests_dir.is_dir():
            return []
        return sorted(
            p.stem[len("test_"):]
            for p in tests_dir.glob("test_*.py")
        )

    def resolve_module(self, module: Optional[str]) -> str:
        """Accept e.g. 'core' or 'core_module'. Defaults to the first available."""
        available = self.list_modules()
        if not available:
            raise ValidationError(
                f"No modules found in {self.modules_dir}. "
                "Run the setup step (git clone) first."
            )
        if module is None:
            return available[0]
        for name in (module, f"{module}_module"):
            if name in available:
                return name
        raise ValidationError(f"Module '{module}' not found. Available: {', '.join(available)}")

    def task_file(self, module_name: str, task: str) -> Path:
        """Path to a task's source file, for opening it in an editor."""
        return self.modules_dir / module_name / "tasks" / f"{task}.py"

    def run_task(self, module_name: str, task_id: str) -> Dict[str, Any]:
        """Run one task's tests in isolation.

        Returns a minimal result - pass/fail, timing, and (on failure) a
        single one-line error summary. Never the full pytest output; that's
        captured for internal use only and not meant to reach the player.
        """
        tests_dir = self.modules_dir / module_name / "tests"
        test_file = tests_dir / f"test_{task_id}.py"
        if not test_file.exists():
            raise ValidationError(f"No tests for task '{task_id}' in {module_name}")

        result = self._run_pytest(test_file, task_id=task_id)
        result["module_name"] = module_name
        result["task_file"] = self.task_file(module_name, task_id)
        return result

    def _run_pytest(self, path: Path, task_id: str) -> Dict[str, Any]:
        """Run pytest from the game root so `modules.<name>` imports resolve."""
        fd, timing_path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        fd, error_path = tempfile.mkstemp(suffix=".txt")
        os.close(fd)
        try:
            env = dict(
                os.environ,
                RECOVERY_TIMING_FILE=timing_path,
                RECOVERY_ERROR_FILE=error_path,
            )
            cmd = [
                sys.executable, "-m", "pytest", str(path),
                "-q", "--tb=no", "-p", "no:cacheprovider",
                "-p", "resurrection.timing", "-p", "resurrection.errors",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.modules_dir.parent, env=env)
            with open(timing_path) as f:
                durations = json.load(f)
            error_text = Path(error_path).read_text().strip()
            error = error_text or None
        finally:
            os.unlink(timing_path)
            os.unlink(error_path)

        # Metric = time spent inside the test calls (the solution's runtime),
        # not interpreter startup or pytest's own overhead.
        return {
            "passed": result.returncode == 0,
            "time_elapsed": sum(durations.values()),
            "output": result.stdout + result.stderr,  # internal only - never shown to the player
            "return_code": result.returncode,
            "task_id": task_id,
            "error": None if result.returncode == 0 else error,
        }

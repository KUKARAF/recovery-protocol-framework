"""Recovery validation - runs a module's tests against the user's solutions."""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional


class ValidationError(Exception):
    """Raised when a validation request cannot be run at all."""


class Validator:
    """Runs module tests for one task, or for a whole module."""

    def __init__(self, root: Optional[Path] = None):
        # The game folder: the directory that contains the `modules/` folder
        self.root = Path(root) if root else Path.cwd()
        self.modules_dir = self.root / "modules"

    def list_modules(self) -> list[str]:
        """Names of modules available in the game folder."""
        if not self.modules_dir.is_dir():
            return []
        return sorted(
            p.name for p in self.modules_dir.iterdir()
            if p.is_dir() and (p / "tests").is_dir()
        )

    def resolve_module(self, module: Optional[str]) -> str:
        """Accept 'back_to_basics' or 'back_to_basics_module'. Defaults to the only module."""
        available = self.list_modules()
        if not available:
            raise ValidationError(
                f"No modules found in {self.modules_dir}. "
                "Run the setup step (git clone) first."
            )
        if module is None:
            if len(available) == 1:
                return available[0]
            raise ValidationError(f"Several modules available, pick one with --module: {', '.join(available)}")
        for name in (module, f"{module}_module"):
            if name in available:
                return name
        raise ValidationError(f"Module '{module}' not found. Available: {', '.join(available)}")

    def validate(self, module: Optional[str] = None, task: Optional[str] = None) -> Dict[str, Any]:
        """Run tests for one task (module + task) or for all tasks in a module."""
        module_name = self.resolve_module(module)
        tests_dir = self.modules_dir / module_name / "tests"

        if task:
            test_file = tests_dir / f"test_{task}.py"
            if not test_file.exists():
                raise ValidationError(f"No tests for task '{task}' in {module_name}")
            return self._run_pytest(test_file, task_id=task)

        return self._run_pytest(tests_dir, task_id=None)

    def _run_pytest(self, path: Path, task_id: Optional[str]) -> Dict[str, Any]:
        """Run pytest from the game root so `modules.<name>` imports resolve."""
        fd, timing_path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        try:
            env = dict(os.environ, RECOVERY_TIMING_FILE=timing_path)
            cmd = [
                sys.executable, "-m", "pytest", str(path),
                "-v", "--tb=short", "-p", "no:cacheprovider", "-p", "resurrection.timing",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.modules_dir.parent, env=env)
            with open(timing_path) as f:
                durations = json.load(f)
        finally:
            os.unlink(timing_path)

        # Metric = time spent inside the test calls (the solution's runtime),
        # not interpreter startup or pytest's own overhead.
        return {
            "passed": result.returncode == 0,
            "time_elapsed": sum(durations.values()),
            "output": result.stdout + result.stderr,
            "return_code": result.returncode,
            "task_id": task_id,
        }

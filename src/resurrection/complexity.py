"""Empirical time/space complexity estimation.

Runs a solved task's function at several input sizes in a fresh subprocess
(see _complexity_runner.py) and fits a log-log slope to estimate how time
and peak memory scale with input size. This is an empirical ESTIMATE, not a
formal proof - it can be misleading for borderline cases (O(n) vs.
O(n log n) look nearly identical at modest sizes).

Only available for tasks that define a `scale_input(n)` benchmark generator
under modules/<module>/benchmarks/<task_id>.py. Tasks whose signature is a
handful of fixed scalars (clamp_value, swap_pair, distance_2d, ...) have no
"n" to scale, and correctly report unavailable rather than a fabricated
number.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

_RUNNER = Path(__file__).parent / "_complexity_runner.py"


def measure(root: Path, module_name: str, task_id: str) -> Dict[str, Any]:
    try:
        result = subprocess.run(
            [sys.executable, str(_RUNNER), module_name, task_id],
            cwd=root, capture_output=True, text=True, timeout=30,
        )
    except subprocess.TimeoutExpired:
        return {"available": False, "error": "timed out"}

    try:
        return json.loads(result.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError):
        return {"available": False, "error": result.stderr.strip()[:200] or "no output"}

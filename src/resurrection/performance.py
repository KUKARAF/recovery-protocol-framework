"""Zachtronics-style performance benchmarking.

Those games never collapse a solution to one number - they score it on two
independent axes you trade off against each other (cycles vs. area, in
TIS-100/Opus Magnum terms). This does the same with SPEED (execution time)
and SIZE (solution length), instead of inventing a single blended score.

Only meaningful for a solution that already passes - benchmarking a broken
one isn't a performance question, it's a correctness one.
"""

import statistics
from pathlib import Path
from typing import Any, Dict

from resurrection.validator import Validator

DEFAULT_RUNS = 10


def solution_size(task_file: Path) -> int:
    """Non-blank lines in the task file.

    Approximate on purpose: it includes the fixed docstring and signature
    every player starts from, so it's only meaningful compared against your
    own other attempts at the same task, not an absolute "lines of code you
    wrote" count.
    """
    return sum(1 for line in task_file.read_text().splitlines() if line.strip())


def measure(validator: Validator, module_name: str, task_id: str, runs: int = DEFAULT_RUNS) -> Dict[str, Any]:
    """Run a task's tests `runs` times to build a timing reading.

    Stops at the first failure and reports it the same minimal way `recovery
    validate` does - if the solution doesn't pass, there's nothing to
    benchmark yet.
    """
    times_ms = []
    for _ in range(runs):
        result = validator.run_task(module_name, task_id)
        if not result["passed"]:
            return {
                "passed": False,
                "module_name": module_name,
                "task_id": task_id,
                "task_file": result["task_file"],
                "error": result["error"],
            }
        times_ms.append(result["time_elapsed"] * 1000)

    task_file = validator.task_file(module_name, task_id)
    return {
        "passed": True,
        "module_name": module_name,
        "task_id": task_id,
        "task_file": task_file,
        "runs": runs,
        "time_ms_best": min(times_ms),
        "time_ms_median": statistics.median(times_ms),
        "size_lines": solution_size(task_file),
    }

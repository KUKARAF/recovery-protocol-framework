"""Zachtronics-style performance benchmarking.

Those games never collapse a solution to one number - they score it on two
independent axes you trade off against each other (cycles vs. area, in
TIS-100/Opus Magnum terms). This does the same with SPEED (execution time)
and SIZE (solution length), plus - when a task defines a size-scaling
benchmark (see complexity.py) - an empirical estimate of TIME and SPACE
complexity class.

Only meaningful for a solution that already passes - benchmarking a broken
one isn't a performance question, it's a correctness one.
"""

import ast
import statistics
from pathlib import Path
from typing import Any, Dict

from resurrection import complexity
from resurrection.validator import Validator

DEFAULT_RUNS = 10


def solution_size(task_file: Path, function_name: str) -> int:
    """Lines of actual code in `function_name`'s body - not the whole file.

    Parsed via `ast`, so it never counts: the module's own narrative
    docstring, the function's signature line, the function's own docstring
    (the fixed boilerplate every player starts from), or any comment -
    hint comments that shipped with the stub, or ones the player adds
    themselves. Comments don't exist in the AST at all, so there's nothing
    to specifically filter out for them.

    Only meaningful compared against your own other attempts at the same
    task - it's not an absolute "good code" measure.
    """
    source = task_file.read_text()
    tree = ast.parse(source)
    source_lines = source.splitlines()

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            body = node.body
            if body and _is_docstring(body[0]):
                body = body[1:]
            if not body:
                return 0

            lines = set()
            for stmt in body:
                end = getattr(stmt, "end_lineno", stmt.lineno)
                lines.update(range(stmt.lineno, end + 1))
            return sum(1 for ln in lines if source_lines[ln - 1].strip())

    return 0


def _is_docstring(stmt) -> bool:
    return (
        isinstance(stmt, ast.Expr)
        and isinstance(stmt.value, ast.Constant)
        and isinstance(stmt.value.value, str)
    )


def no_imports_bonus(task_file: Path) -> bool:
    """Whether the task file uses no `import` statement at all - module-
    level or inside the function, either way. A solution that reaches for
    nothing but builtins earns a bonus star."""
    tree = ast.parse(task_file.read_text())
    return not any(isinstance(node, (ast.Import, ast.ImportFrom)) for node in ast.walk(tree))


def measure(validator: Validator, module_name: str, task_id: str, runs: int = DEFAULT_RUNS) -> Dict[str, Any]:
    """Run a task's tests `runs` times to build a timing reading, then add
    an empirical time/space complexity estimate when the task has a
    size-scaling benchmark defined (see complexity.py) - not every task
    has an "n" to scale (clamp_value takes three fixed scalars, for
    instance), so that part may come back unavailable.

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
    reading = {
        "passed": True,
        "module_name": module_name,
        "task_id": task_id,
        "task_file": task_file,
        "runs": runs,
        "time_ms_best": min(times_ms),
        "time_ms_median": statistics.median(times_ms),
        "size_lines": solution_size(task_file, task_id),
        "no_imports_bonus": no_imports_bonus(task_file),
    }
    reading["complexity"] = complexity.measure(validator.root, module_name, task_id)
    return reading

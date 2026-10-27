"""Standalone runner for empirical time/space complexity estimation.

Run as a subprocess by resurrection.complexity.measure() - never inside the
long-lived CLI process, since a slow or memory-heavy solution shouldn't be
able to hang or bloat it. Prints exactly one JSON object to stdout.

Usage: python _complexity_runner.py <module_name> <task_id>
(run with cwd = the game root, so `import modules.<module>...` resolves the
same way it does for `recovery validate`)
"""

import importlib
import json
import math
import os
import statistics
import sys
import time
import tracemalloc

# `python /path/to/this_script.py` puts this script's own directory on
# sys.path[0], not the current working directory - unlike `python -c` or
# `python -m`. Without this, `import modules.<module>...` fails to find
# the game folder's modules/ package even though we're run with
# cwd = game root specifically so that import would work.
sys.path.insert(0, os.getcwd())

# Kept modest on purpose: a buggy O(n^2)+ solution at the largest size still
# finishes in a reasonable time, and the whole sweep has a timeout from the
# caller as a backstop anyway.
SIZES = [50, 150, 450, 1350, 4050]
REPEATS = 3


def classify(exponent: float) -> str:
    """Snap a fitted log-log slope to the nearest common complexity class.

    This is an estimate, not a proof: O(n) and O(n log n) look nearly
    identical at these input sizes, so a slope near 1 is reported as
    covering both rather than picked apart.
    """
    if exponent < 0.3:
        return "O(1)"
    if exponent < 1.3:
        return "O(n) or O(n log n)"
    if exponent < 2.3:
        return "O(n^2)"
    return "O(n^3) or worse"


def fit_log_log_slope(points) -> float:
    """Least-squares slope of log(measurement) vs log(n) - the exponent in
    measurement ~= n^slope."""
    xs = [math.log(n) for n, _ in points]
    ys = [math.log(max(v, 1e-12)) for _, v in points]
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    denominator = sum((x - mean_x) ** 2 for x in xs)
    if denominator == 0:
        return 0.0
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    return numerator / denominator


def main():
    module_name, task_id = sys.argv[1], sys.argv[2]

    try:
        bench = importlib.import_module(f"modules.{module_name}.benchmarks.{task_id}")
        scale_input = bench.scale_input
    except (ImportError, AttributeError):
        print(json.dumps({"available": False}))
        return

    task_module = importlib.import_module(f"modules.{module_name}.tasks.{task_id}")
    func = getattr(task_module, task_id)

    time_points = []
    space_points = []
    for n in SIZES:
        args = scale_input(n)

        samples = []
        for _ in range(REPEATS):
            start = time.perf_counter()
            func(*args)
            samples.append(time.perf_counter() - start)
        time_points.append((n, statistics.median(samples)))

        tracemalloc.start()
        func(*args)
        _current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        space_points.append((n, peak))

    time_exponent = fit_log_log_slope(time_points)
    space_exponent = fit_log_log_slope(space_points)
    print(json.dumps({
        "available": True,
        "time_exponent": round(time_exponent, 2),
        "time_class": classify(time_exponent),
        "space_exponent": round(space_exponent, 2),
        "space_class": classify(space_exponent),
    }))


if __name__ == "__main__":
    main()

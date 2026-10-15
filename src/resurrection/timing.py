"""pytest plugin: record how long each test's call phase takes.

Loaded by the validator with `-p resurrection.timing`. Writes a JSON map of
test node id -> seconds to the file named in RECOVERY_TIMING_FILE. This is the
solution's runtime, without pytest's own startup or reporting overhead.
"""

import json
import os
import time

import pytest

_durations = {}


@pytest.hookimpl(wrapper=True)
def pytest_runtest_call(item):
    start = time.perf_counter()
    try:
        return (yield)
    finally:
        _durations[item.nodeid] = time.perf_counter() - start


def pytest_sessionfinish(session):
    path = os.environ.get("RECOVERY_TIMING_FILE")
    if path:
        with open(path, "w") as f:
            json.dump(_durations, f)

"""pytest plugin: capture a one-line summary of the first failure only.

Loaded by the validator with `-p resurrection.errors`. Writes the first
failing test's crash message to the file named in RECOVERY_ERROR_FILE. This
is how the CLI shows one concise line instead of pytest's full verbose
output and traceback - the raw pytest output is never shown to the player.
"""

import os

import pytest

_first_failure = None


@pytest.hookimpl
def pytest_runtest_logreport(report):
    global _first_failure
    if _first_failure is not None or report.when != "call" or not report.failed:
        return
    crash = getattr(getattr(report, "longrepr", None), "reprcrash", None)
    _first_failure = str(crash.message) if crash is not None else str(report.longrepr)


def pytest_sessionfinish(session):
    path = os.environ.get("RECOVERY_ERROR_FILE")
    if path and _first_failure is not None:
        with open(path, "w") as f:
            f.write(_first_failure)

"""Command-line interface for Recovery Protocol."""

import json
import os
import re
import shlex
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

import typer

from resurrection.metrics import MetricsTracker
from resurrection.paths import find_game_root
from resurrection.performance import DEFAULT_RUNS, measure
from resurrection.state import ModuleState
from resurrection.validator import ValidationError, Validator

app = typer.Typer(
    help="Recovery Protocol - validate your capability recovery",
    invoke_without_command=True,
)


@app.callback()
def main(ctx: typer.Context):
    """With no subcommand, `recovery` is `recovery validate`: it finds
    where you are and checks that, with nothing to remember or type."""
    if ctx.invoked_subcommand is None:
        validate(module=None, task=None)


@app.command()
def validate(
    module: Optional[str] = typer.Option(None, "--module", "-m", help="Module to validate, e.g. core"),
    task: Optional[str] = typer.Option(None, "--task", "-t", help="Single task, e.g. sort_signals"),
):
    """
    Check your current task's solution.

    With no flags, finds the first task that isn't passing yet in the
    first module, and checks that - nothing to remember or type. Works
    from anywhere inside the game folder, not just its root.

    Examples:
        recovery validate
        recovery validate --module core --task sort_signals
    """
    root = find_game_root()
    validator = Validator(root=root)
    tracker = MetricsTracker(root=root)

    def already_solved(task_id: str) -> bool:
        return tracker.get_best(task_id)["best_time"] is not None

    try:
        module_name = validator.resolve_module(module)
        if task:
            result = validator.run_task(module_name, task)
        else:
            result = ModuleState(validator).current(module_name, already_solved)
            if result is None:
                typer.echo(f"[!] No tasks found in module '{module_name}'.", err=True)
                raise typer.Exit(code=2)
    except ValidationError as e:
        typer.echo(f"[!] {e}", err=True)
        raise typer.Exit(code=2)

    if not result["passed"]:
        # Minimal, narrative output only: which file, and the one error
        # that broke it. Never pytest's raw per-test listing or traceback.
        typer.echo(f"\nunrecoverable error in {result['task_file'].name}")
        if result["error"]:
            typer.echo(result["error"])
        _offer_manual_recovery(result)
        raise typer.Exit(code=1)

    typer.echo("\n✓ All validations passed")

    task_id = result["task_id"]
    module_name = result["module_name"]
    elapsed_ms = result["time_elapsed"] * 1000
    first_solve = not already_solved(task_id)
    comparison = tracker.compare(task_id, elapsed_ms)

    typer.echo("\n" + "=" * 60)
    typer.echo(tracker.get_summary(task_id, elapsed_ms))
    typer.echo("=" * 60)

    if comparison["is_best_time"]:
        if _git_push(root, "best/time"):
            typer.echo("\n⚡ NEW BEST TIME. Pushed to best/time.")
        else:
            typer.echo("\n⚡ NEW BEST TIME. Could not push automatically - push it yourself with:")
            typer.echo(f"   {tracker.get_push_command(task_id, 'time')}")

    tracker.record_solution(task_id, elapsed_ms)

    if first_solve:
        typer.echo(f"\n🎉 First clear! Benchmarking performance ({DEFAULT_RUNS} runs)...")
        reading = measure(validator, module_name, task_id)
        _report_performance(reading, root)

    raise typer.Exit(code=0)


@app.command()
def performance(
    target: Optional[str] = typer.Argument(
        None, help="module/task, e.g. core/sort_signals. Omit to use your current task."
    ),
):
    """
    Benchmark a solved task: SPEED (execution time) and SIZE (solution
    length) - the same two independent axes a Zachtronics game scores a
    solution on, not one blended number. Recorded to the stats page on the
    recovery server's web UI.

    Examples:
        recovery performance
        recovery performance core/sort_signals
    """
    root = find_game_root()
    validator = Validator(root=root)
    tracker = MetricsTracker(root=root)

    def already_solved(tid: str) -> bool:
        return tracker.get_best(tid)["best_time"] is not None

    try:
        if target:
            if "/" not in target:
                typer.echo("[!] Pass module/task, e.g. core/sort_signals.", err=True)
                raise typer.Exit(code=2)
            module_arg, task_id = target.split("/", 1)
            module_name = validator.resolve_module(module_arg)
        else:
            module_name = validator.resolve_module(None)
            current = ModuleState(validator).current(module_name, already_solved)
            if current is None:
                typer.echo(f"[!] No tasks found in module '{module_name}'.", err=True)
                raise typer.Exit(code=2)
            task_id = current["task_id"]
    except ValidationError as e:
        typer.echo(f"[!] {e}", err=True)
        raise typer.Exit(code=2)

    typer.echo(f"Benchmarking {task_id} ({DEFAULT_RUNS} runs)...")
    reading = measure(validator, module_name, task_id)
    _report_performance(reading, root)


def _report_performance(reading: dict, root: Path) -> None:
    """Print a performance reading and submit it to the server, if reachable."""
    if not reading["passed"]:
        typer.echo(f"\nunrecoverable error in {reading['task_file'].name}")
        if reading.get("error"):
            typer.echo(reading["error"])
        raise typer.Exit(code=1)

    typer.echo(f"\nSPEED: {reading['time_ms_best']:.2f}ms best / {reading['time_ms_median']:.2f}ms median")
    typer.echo(f"SIZE:  {reading['size_lines']} lines")

    base = _server_base_url(root)
    if base and _submit_performance(base, reading):
        typer.echo(f"\nRecorded. View it at {base}/stats")
    else:
        typer.echo("\n(Could not reach the recovery server to record this - is it running?)")


def _offer_manual_recovery(result: dict) -> None:
    """On failure, offer to drop straight into an editor on the task file."""
    prompt = (
        f"\nunrecoverable failure in {result['module_name']} detected. "
        "recovery validation failed. initiate manual recovery procedure?"
    )
    if not typer.confirm(prompt):
        return

    editor = shlex.split(os.environ.get("EDITOR", "vim"))
    subprocess.call([*editor, str(result["task_file"])])


def _git_push(root: Path, refspec: str) -> bool:
    """Push HEAD to a branch on origin, e.g. `best/time`. True on success."""
    try:
        result = subprocess.run(
            ["git", "push", "origin", f"HEAD:{refspec}"],
            cwd=root, capture_output=True, text=True, timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def _server_base_url(root: Path) -> Optional[str]:
    """Derive the recovery server's web URL from the game folder's git remote.

    The modules repo is cloned from the same host that serves the web UI
    (ssh://recovery@<host>:2222/... clone, <host>:8080 web), so the remote
    already tells us where to report performance to - no separate config.
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "remote", "get-url", "origin"],
            capture_output=True, text=True, timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    match = re.search(r"@([^:/]+)(?::\d+)?[:/]", result.stdout.strip())
    if not match:
        return None
    return f"http://{match.group(1)}:8080"


def _submit_performance(base: str, reading: dict) -> bool:
    payload = json.dumps({
        "module": reading["module_name"],
        "task": reading["task_id"],
        "time_ms_best": reading["time_ms_best"],
        "time_ms_median": reading["time_ms_median"],
        "size_lines": reading["size_lines"],
    }).encode()
    req = urllib.request.Request(
        f"{base}/performance", data=payload,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except (urllib.error.URLError, OSError):
        return False


@app.command()
def info():
    """List the modules available in this game folder."""
    validator = Validator()
    modules = validator.list_modules()
    if not modules:
        typer.echo("No modules found. Clone the modules repository into ./modules first.", err=True)
        raise typer.Exit(code=1)
    typer.echo("\nAvailable modules:")
    for name in modules:
        typer.echo(f"  {name}")
    typer.echo("")


if __name__ == "__main__":
    app()

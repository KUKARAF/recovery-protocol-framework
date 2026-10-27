"""Command-line interface for Recovery Protocol."""

import os
import shlex
import subprocess
from typing import Optional

import typer

from resurrection.metrics import MetricsTracker
from resurrection.paths import find_game_root
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
    try:
        module_name = validator.resolve_module(module)
        if task:
            result = validator.run_task(module_name, task)
        else:
            result = ModuleState(validator).current(module_name)
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
    elapsed_ms = result["time_elapsed"] * 1000
    tracker = MetricsTracker(root=root)
    comparison = tracker.compare(task_id, elapsed_ms)

    typer.echo("\n" + "=" * 60)
    typer.echo(tracker.get_summary(task_id, elapsed_ms))
    typer.echo("=" * 60)

    if comparison["is_best_time"]:
        typer.echo("\n⚡ NEW BEST TIME. Push it to the server with:")
        typer.echo(f"   {tracker.get_push_command(task_id, 'time')}")

    tracker.record_solution(task_id, elapsed_ms)
    raise typer.Exit(code=0)


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

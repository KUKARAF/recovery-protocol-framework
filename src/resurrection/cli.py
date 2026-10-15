"""Command-line interface for Recovery Protocol."""

from typing import Optional

import typer

from resurrection.metrics import MetricsTracker
from resurrection.validator import ValidationError, Validator

app = typer.Typer(
    help="Recovery Protocol - validate your capability recovery",
    no_args_is_help=True,
)


@app.command()
def validate(
    module: Optional[str] = typer.Option(None, "--module", "-m", help="Module to validate, e.g. back_to_basics"),
    task: Optional[str] = typer.Option(None, "--task", "-t", help="Single task, e.g. sort_signals"),
):
    """
    Run the tests for your solutions.

    Examples:
        recovery validate --module back_to_basics --task sort_signals
        recovery validate --module back_to_basics
    """
    validator = Validator()
    try:
        results = validator.validate(module=module, task=task)
    except ValidationError as e:
        typer.echo(f"[!] {e}", err=True)
        raise typer.Exit(code=2)

    typer.echo(results["output"])

    if not results["passed"]:
        typer.echo("\n✗ Some validations failed")
        raise typer.Exit(code=1)

    typer.echo("\n✓ All validations passed")

    if results["task_id"] is None:
        # Whole-module run: no per-task timing to compare
        raise typer.Exit(code=0)

    task_id = results["task_id"]
    elapsed_ms = results["time_elapsed"] * 1000
    tracker = MetricsTracker()
    comparison = tracker.compare(task_id, elapsed_ms)

    typer.echo("\n" + "=" * 60)
    typer.echo(tracker.get_summary(task_id, elapsed_ms))
    typer.echo("=" * 60)

    if comparison["is_best_time"]:
        typer.echo("\n⚡ NEW BEST TIME. Push it to the server with:")
        typer.echo(f"   {tracker.get_push_command(task_id, 'time')}")

    tracker.record_solution(task_id, elapsed_ms)
    raise typer.Exit(code=0)


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

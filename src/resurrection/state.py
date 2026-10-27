"""Figures out which task is 'current' when the player doesn't name one.

Scans a module's tasks in authored order and runs each one's tests until it
finds something worth stopping on: a task that still fails, or a task that
just started passing and hasn't been recorded as solved yet. A task that
was already recorded as solved on some earlier run is "old news" and gets
skipped over in silence - that's how a player who fixes task A and reruns
sees task A's win (and its first-clear benchmark) before ever being moved
on to task B, rather than the scan silently racing ahead to B's failure.

This is the only place that decides "where we are"; Validator just knows
how to run one task in isolation and never looks at the others.
"""

from typing import Any, Callable, Dict, Optional

from resurrection.validator import Validator


class ModuleState:
    def __init__(self, validator: Validator):
        self.validator = validator

    def current(
        self, module_name: str, is_already_solved: Callable[[str], bool]
    ) -> Optional[Dict[str, Any]]:
        """The first task that still fails, or the first newly-passing task
        that hasn't been recorded as solved yet. If every task is already
        passing *and* already recorded, reports the last one. None if the
        module has no tasks at all.

        `is_already_solved(task_id)` should answer from persisted state
        (e.g. whether a best time is on record for it already), not from
        anything computed during this scan.
        """
        tasks = self.validator.list_tasks(module_name)
        if not tasks:
            return None

        result = None
        for task_id in tasks:
            result = self.validator.run_task(module_name, task_id)
            if not result["passed"]:
                return result
            if not is_already_solved(task_id):
                return result
        return result

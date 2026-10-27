"""Figures out which task is 'current' when the player doesn't name one.

Scans a module's tasks in authored order and runs each one's tests until it
finds the first task that isn't passing yet - that's where the player left
off. If every task passes, it reports the last one (module complete).

This is the only place that decides "where we are"; Validator just knows
how to run one task in isolation and never looks at the others.
"""

from typing import Any, Dict, Optional

from resurrection.validator import Validator


class ModuleState:
    def __init__(self, validator: Validator):
        self.validator = validator

    def current(self, module_name: str) -> Optional[Dict[str, Any]]:
        """The first failing task's result, or the last task's result if
        everything already passes. None if the module has no tasks at all."""
        tasks = self.validator.list_tasks(module_name)
        if not tasks:
            return None

        result = None
        for task_id in tasks:
            result = self.validator.run_task(module_name, task_id)
            if not result["passed"]:
                return result
        return result

"""Metrics tracking and comparison for solution optimization."""

import json
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class SolutionMetrics:
    """Metrics for a solution."""
    task_id: str
    execution_time: float  # milliseconds
    peak_memory: Optional[float] = None  # MB
    timestamp: Optional[str] = None
    branch: Optional[str] = None  # best/time, best/memory, etc.

    def to_dict(self):
        return asdict(self)


class MetricsTracker:
    """Track and compare metrics across solutions."""

    def __init__(self):
        self.best_file = Path.cwd() / ".recovery-best.json"
        self.best_solutions = self._load_best()

    def _load_best(self) -> Dict[str, Any]:
        """Load best solutions from file."""
        if self.best_file.exists():
            with open(self.best_file) as f:
                return json.load(f)
        return {"tasks": {}}

    def _save_best(self):
        """Save best solutions to file."""
        with open(self.best_file, "w") as f:
            json.dump(self.best_solutions, f, indent=2)

    def record_solution(self, task_id: str, execution_time: float, memory: Optional[float] = None):
        """
        Record a solution's metrics.

        Args:
            task_id: Task identifier (e.g., "sort_signals")
            execution_time: Time taken in milliseconds
            memory: Peak memory in MB
        """
        if task_id not in self.best_solutions["tasks"]:
            self.best_solutions["tasks"][task_id] = {
                "best_time": None,
                "best_time_when": None,
                "best_memory": None,
                "best_memory_when": None,
            }

        task = self.best_solutions["tasks"][task_id]

        # Check if this is a new best time
        if task["best_time"] is None or execution_time < task["best_time"]:
            task["best_time"] = execution_time
            task["best_time_when"] = time.time()

        # Check if this is a new best memory
        if memory and (task["best_memory"] is None or memory < task["best_memory"]):
            task["best_memory"] = memory
            task["best_memory_when"] = time.time()

        self._save_best()

    def get_best(self, task_id: str) -> Dict[str, Any]:
        """Get best metrics for a task."""
        if task_id in self.best_solutions["tasks"]:
            return self.best_solutions["tasks"][task_id]
        return {"best_time": None, "best_memory": None}

    def compare(self, task_id: str, execution_time: float, memory: Optional[float] = None) -> Dict[str, Any]:
        """
        Compare current metrics against best.

        Returns:
            Dict with comparison results and recommendations
        """
        best = self.get_best(task_id)
        result = {
            "is_best_time": False,
            "is_best_memory": False,
            "time_improvement": None,
            "memory_improvement": None,
            "recommendations": [],
        }

        # Check time
        if best["best_time"] is None:
            result["is_best_time"] = True
            result["recommendations"].append("time")
        elif execution_time < best["best_time"]:
            result["is_best_time"] = True
            improvement = ((best["best_time"] - execution_time) / best["best_time"]) * 100
            result["time_improvement"] = improvement
            result["recommendations"].append("time")

        # Check memory
        if memory:
            if best["best_memory"] is None:
                result["is_best_memory"] = True
                result["recommendations"].append("memory")
            elif memory < best["best_memory"]:
                result["is_best_memory"] = True
                improvement = ((best["best_memory"] - memory) / best["best_memory"]) * 100
                result["memory_improvement"] = improvement
                result["recommendations"].append("memory")

        return result

    def get_push_command(self, task_id: str, metric_type: str) -> str:
        """Get the git push command for a metric branch."""
        metric_branch = f"best/{metric_type}"
        return f"git push origin HEAD:{metric_branch}"

    def get_summary(self, task_id: str, execution_time: float, memory: Optional[float] = None) -> str:
        """Get a formatted summary of metrics comparison."""
        best = self.get_best(task_id)
        comparison = self.compare(task_id, execution_time, memory)

        summary = []

        if best["best_time"] is None:
            summary.append(f"🎯 NEW RECORD (Time): {execution_time:.2f}ms")
            summary.append(f"   Branch: best/time")
            summary.append(f"   Command: {self.get_push_command(task_id, 'time')}")
        elif comparison["is_best_time"]:
            improvement = comparison["time_improvement"]
            summary.append(f"⚡ NEW BEST TIME: {execution_time:.2f}ms")
            summary.append(f"   Previous: {best['best_time']:.2f}ms")
            summary.append(f"   Improvement: {improvement:.1f}% faster")
            summary.append(f"   Branch: best/time")
            summary.append(f"   Command: {self.get_push_command(task_id, 'time')}")
        else:
            summary.append(f"⏱️  Time: {execution_time:.2f}ms")
            summary.append(f"   Best: {best['best_time']:.2f}ms")
            summary.append(f"   Slower by: {((execution_time - best['best_time']) / best['best_time'] * 100):.1f}%")

        if memory:
            if best["best_memory"] is None:
                summary.append(f"💾 NEW RECORD (Memory): {memory:.2f}MB")
                summary.append(f"   Branch: best/memory")
                summary.append(f"   Command: {self.get_push_command(task_id, 'memory')}")
            elif comparison["is_best_memory"]:
                improvement = comparison["memory_improvement"]
                summary.append(f"💾 NEW BEST MEMORY: {memory:.2f}MB")
                summary.append(f"   Previous: {best['best_memory']:.2f}MB")
                summary.append(f"   Improvement: {improvement:.1f}% less memory")
                summary.append(f"   Branch: best/memory")
                summary.append(f"   Command: {self.get_push_command(task_id, 'memory')}")
            else:
                summary.append(f"💾 Memory: {memory:.2f}MB")
                summary.append(f"   Best: {best['best_memory']:.2f}MB")
                summary.append(f"   Uses more by: {((memory - best['best_memory']) / best['best_memory'] * 100):.1f}%")

        return "\n".join(summary)

"""Production-warrant regeneration from canonical Forest state."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .core import select_next_task


def _state_version(state: dict[str, Any]) -> str:
    current = state.get("warrant", {}).get("state_version")
    if isinstance(current, str) and current:
        return current
    return str(state.get("schema_version", "unversioned"))


def regenerate_warrant(state: dict[str, Any]) -> dict[str, Any] | None:
    """Create the next normalized warrant from the highest-leverage task.

    Task-local warrant metadata overrides conservative defaults. Returning None
    means no unblocked task remains; callers preserve completion/block evidence.
    """
    selection = select_next_task(state)
    task = selection.task
    if task is None:
        return None

    recovery = deepcopy(task.get("recovery") or {})
    recovery.setdefault("retry_allowed", False)
    recovery.setdefault("max_retries", 0)
    recovery.setdefault("rollback_required_on_failure", False)

    task_id = str(task["id"])
    project_objective = state.get("project", {}).get("objective") or "Advance Forest canonical state."
    position = state.get("position", {}).get("current_node") or "unknown"

    return {
        "id": f"warrant-{task_id}",
        "state_version": _state_version(state),
        "objective": task.get("objective", project_objective),
        "position": position,
        "task": task_id,
        "selection_reason": selection.reason,
        "dependencies": list(task.get("dependencies", [])),
        "inputs": list(task.get("inputs", ["canonical state", "selected task"])),
        "outputs": list(task.get("outputs", ["task result", "evidence", "measurements"])),
        "procedures": list(task.get("procedures", ["execute selected task", "verify result", "persist state"])),
        "tests": list(task.get("tests", ["task-specific verification"])),
        "permissions": list(task.get("permissions", [])),
        "recovery": recovery,
        "measurement": list(task.get("measurement", ["attempt count", "result status"])),
        "next_candidates": [
            candidate["id"]
            for candidate in state.get("tasks", [])
            if candidate.get("id") != task_id and candidate.get("status", "pending") == "pending"
        ],
    }


def apply_regenerated_warrant(state: dict[str, Any]) -> dict[str, Any]:
    """Update canonical state in place with its next warrant when one exists."""
    warrant = regenerate_warrant(state)
    if warrant is not None:
        state["warrant"] = warrant
    return state

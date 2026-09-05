"""Deterministic continuation kernel.

The kernel owns selection and state transitions; execution is supplied by an
adapter. This keeps scheduling, persistence, and external tools replaceable.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Iterable


@dataclass(frozen=True)
class Selection:
    task: dict[str, Any] | None
    reason: str


def _completed(state: dict[str, Any]) -> set[str]:
    return set(state.get("position", {}).get("completed_nodes", []))


def is_unblocked(task: dict[str, Any], state: dict[str, Any]) -> bool:
    deps = task.get("dependencies", [])
    completed = _completed(state)
    return all(dep in completed for dep in deps) and task.get("status", "pending") not in {
        "blocked", "complete", "cancelled"
    }


def _score(task: dict[str, Any]) -> float:
    # Explicit leverage is the primary selector signal. Small deterministic
    # tie-breakers reward reusable infrastructure without hiding the score.
    return float(task.get("leverage", 0)) + 0.1 * float(task.get("reuse", 0)) + 0.01 * float(task.get("observability", 0))


def select_next_task(state: dict[str, Any], candidates: Iterable[dict[str, Any]] | None = None) -> Selection:
    tasks = list(candidates if candidates is not None else state.get("tasks", []))
    eligible = [t for t in tasks if is_unblocked(t, state)]
    if not eligible:
        return Selection(None, "No unblocked task remains")
    chosen = max(eligible, key=lambda t: (_score(t), t.get("id", "")))
    return Selection(chosen, f"Highest-leverage unblocked task; score={_score(chosen):g}")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def transition(state: dict[str, Any], task: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    next_state = deepcopy(state)
    pos = next_state.setdefault("position", {})
    active = set(pos.setdefault("active_nodes", []))
    completed = set(pos.setdefault("completed_nodes", []))
    task_id = task["id"]
    active.discard(task_id)

    passed = bool(result.get("passed", False))
    if passed:
        completed.add(task_id)
        task_status = "complete"
    else:
        task_status = "failed"

    pos["active_nodes"] = sorted(active)
    pos["completed_nodes"] = sorted(completed)
    pos["current_node"] = task_id

    for candidate in next_state.setdefault("tasks", []):
        if candidate.get("id") == task_id:
            candidate["status"] = task_status

    event = {
        "timestamp": _now(),
        "type": "task_result",
        "task_id": task_id,
        "passed": passed,
        "evidence": result.get("evidence", []),
        "measurement": result.get("measurement", {}),
    }
    next_state.setdefault("history", []).append(event)
    next_state.setdefault("metrics", {}).setdefault("iterations", 0)
    next_state["metrics"]["iterations"] += 1
    return next_state


def completion_status(state: dict[str, Any]) -> str:
    ledger = state.get("ledger", {})
    items = ledger.get("items", [])
    if not items:
        return "incomplete"
    if all(item.get("status") in {"passed", "waived"} for item in items):
        return "complete"
    return "incomplete"


def continue_once(
    state: dict[str, Any],
    executor: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Run exactly one observable continuation pass.

    Returns the new canonical state and an execution report. The caller owns
    durable persistence, so the same kernel works with Git, a database, or a
    future Forest-native store.
    """
    if completion_status(state) == "complete":
        return state, {"status": "DONE", "reason": "Completion ledger passed"}

    selection = select_next_task(state)
    if selection.task is None:
        return state, {"status": "BLOCKED", "reason": selection.reason}

    task = selection.task
    result = executor(state, task)
    new_state = transition(state, task, result)
    report = {
        "status": "CONTINUED" if result.get("passed") else "FAILED",
        "task_id": task["id"],
        "selection_reason": selection.reason,
        "result": result,
    }
    return new_state, report

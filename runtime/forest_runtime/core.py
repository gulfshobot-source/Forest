"""Deterministic continuation kernel.

The kernel owns selection, bounded recovery, and state transitions; execution is
supplied by an adapter. This keeps scheduling, persistence, and external tools
replaceable while preserving a deterministic control surface.
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


def _recovery(task: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    policy = task.get("recovery")
    if isinstance(policy, dict):
        return policy
    warrant = state.get("warrant", {})
    if isinstance(warrant, dict) and warrant.get("task") == task.get("id"):
        policy = warrant.get("recovery")
        if isinstance(policy, dict):
            return policy
    return {}


def _attempts(task: dict[str, Any]) -> int:
    return int(task.get("attempts", 0))


def retry_available(task: dict[str, Any], state: dict[str, Any]) -> bool:
    policy = _recovery(task, state)
    if not bool(policy.get("retry_allowed", False)):
        return False
    max_retries = max(0, int(policy.get("max_retries", 1)))
    # attempts counts completed execution attempts. A max_retries value of 1
    # therefore permits one additional execution after the initial failure.
    return _attempts(task) <= max_retries


def is_unblocked(task: dict[str, Any], state: dict[str, Any]) -> bool:
    deps = task.get("dependencies", [])
    completed = _completed(state)
    status = task.get("status", "pending")
    if status in {"blocked", "complete", "cancelled"}:
        return False
    if status == "failed" and not retry_available(task, state):
        return False
    return all(dep in completed for dep in deps)


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
    updated_task: dict[str, Any] | None = None
    for candidate in next_state.setdefault("tasks", []):
        if candidate.get("id") == task_id:
            updated_task = candidate
            break
    if updated_task is None:
        updated_task = deepcopy(task)
        next_state["tasks"].append(updated_task)

    updated_task["attempts"] = _attempts(updated_task) + 1
    if passed:
        completed.add(task_id)
        updated_task["status"] = "complete"
    else:
        updated_task["status"] = "failed" if retry_available(updated_task, next_state) else "blocked"

    pos["active_nodes"] = sorted(active)
    pos["completed_nodes"] = sorted(completed)
    pos["current_node"] = task_id

    event = {
        "timestamp": _now(),
        "type": "task_result",
        "task_id": task_id,
        "attempt": updated_task["attempts"],
        "status": updated_task["status"],
        "passed": passed,
        "evidence": result.get("evidence", []),
        "failure": result.get("failure"),
        "measurement": result.get("measurement", {}),
    }
    next_state.setdefault("history", []).append(event)
    metrics = next_state.setdefault("metrics", {})
    metrics["iterations"] = int(metrics.get("iterations", 0)) + 1
    if not passed:
        metrics["failures"] = int(metrics.get("failures", 0)) + 1
        if updated_task["status"] == "failed":
            metrics["retries_scheduled"] = int(metrics.get("retries_scheduled", 0)) + 1
    return next_state


def completion_status(state: dict[str, Any]) -> str:
    ledger = state.get("ledger", {})
    items = ledger.get("items", [])
    if not items:
        return "incomplete"
    if all(item.get("status") in {"passed", "waived"} for item in items):
        return "complete"
    return "incomplete"


def _execute_safely(
    executor: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]],
    state: dict[str, Any],
    task: dict[str, Any],
) -> dict[str, Any]:
    try:
        result = executor(state, task)
    except Exception as exc:  # executor is an isolation boundary by design
        return {
            "passed": False,
            "evidence": [],
            "failure": {
                "classification": "executor_exception",
                "type": type(exc).__name__,
                "message": str(exc),
            },
        }
    if not isinstance(result, dict):
        return {
            "passed": False,
            "evidence": [],
            "failure": {
                "classification": "invalid_executor_result",
                "type": type(result).__name__,
                "message": "Executor must return a dictionary",
            },
        }
    return result


def continue_once(
    state: dict[str, Any],
    executor: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Run exactly one observable continuation pass."""
    if completion_status(state) == "complete":
        return state, {"status": "DONE", "reason": "Completion ledger passed"}

    selection = select_next_task(state)
    if selection.task is None:
        return state, {"status": "BLOCKED", "reason": selection.reason}

    task = selection.task
    result = _execute_safely(executor, state, task)
    new_state = transition(state, task, result)
    updated = next(t for t in new_state.get("tasks", []) if t.get("id") == task["id"])
    if result.get("passed"):
        status = "CONTINUED"
    elif updated.get("status") == "failed":
        status = "RETRY"
    else:
        status = "BLOCKED"
    report = {
        "status": status,
        "task_id": task["id"],
        "selection_reason": selection.reason,
        "result": result,
        "attempt": updated.get("attempts", 0),
        "task_status": updated.get("status"),
    }
    return new_state, report

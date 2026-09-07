"""Reconstructable continuation telemetry and canonical gap scanning."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any


def _completed(state: dict[str, Any]) -> set[str]:
    return set(state.get("position", {}).get("completed_nodes", []))


def gap_scan(state: dict[str, Any]) -> dict[str, Any]:
    """Classify ledger and task gaps using only canonical state."""
    completed = _completed(state)
    ledger_items = state.get("ledger", {}).get("items", [])
    passed_criteria = [item.get("id") for item in ledger_items if item.get("status") in {"passed", "waived"}]
    pending_criteria = [item.get("id") for item in ledger_items if item.get("status") not in {"passed", "waived"}]

    ready_tasks: list[str] = []
    blocked_tasks: list[dict[str, Any]] = []
    for task in state.get("tasks", []):
        if task.get("status", "pending") != "pending":
            continue
        missing = [dep for dep in task.get("dependencies", []) if dep not in completed]
        if missing:
            blocked_tasks.append({"id": task.get("id"), "missing_dependencies": missing})
        else:
            ready_tasks.append(task.get("id"))

    return {
        "passed_criteria": passed_criteria,
        "pending_criteria": pending_criteria,
        "ready_tasks": ready_tasks,
        "blocked_tasks": blocked_tasks,
    }


def record_continuation_observation(
    state: dict[str, Any], report: dict[str, Any]
) -> dict[str, Any]:
    """Append one compact observation and refresh derived progress metrics."""
    gaps = gap_scan(state)
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": "continuation_observation",
        "task_id": report.get("task_id"),
        "status": report.get("status"),
        "selection_reason": report.get("selection_reason"),
        "gaps": deepcopy(gaps),
    }
    state.setdefault("system_observations", []).append(event)

    metrics = state.setdefault("metrics", {})
    total = len(gaps["passed_criteria"]) + len(gaps["pending_criteria"])
    passed = len(gaps["passed_criteria"])
    metrics.update(
        {
            "completion_criteria_total": total,
            "completion_criteria_passed": passed,
            "completion_fraction": (passed / total) if total else 0.0,
            "ready_task_count": len(gaps["ready_tasks"]),
            "blocked_task_count": len(gaps["blocked_tasks"]),
            "observation_count": len(state["system_observations"]),
        }
    )
    return gaps

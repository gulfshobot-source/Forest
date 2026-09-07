"""Persistent continuation runner for Forest.

The runner is intentionally small: canonical JSON state is the durable object,
while the executor is an injected boundary to real production tooling.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .core import continue_once
from .persistence import load_json, save_json
from .warrant import apply_regenerated_warrant

Executor = Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]


@dataclass(frozen=True)
class RunResult:
    state: dict[str, Any]
    report: dict[str, Any]


def validate_minimum_state(state: dict[str, Any]) -> None:
    """Reject malformed canonical state before any mutation is persisted."""
    if not isinstance(state, dict):
        raise ValueError("Canonical state must be an object")
    for key in ("position", "ledger", "tasks"):
        if key not in state:
            raise ValueError(f"Canonical state missing required field: {key}")
    if not isinstance(state["position"], dict):
        raise ValueError("position must be an object")
    if not isinstance(state["ledger"], dict):
        raise ValueError("ledger must be an object")
    if not isinstance(state["tasks"], list):
        raise ValueError("tasks must be an array")


def run_once(
    state_path: str | Path,
    executor: Executor,
) -> RunResult:
    """Load, execute one continuation pass, regenerate its warrant, and persist."""
    state = load_json(state_path)
    validate_minimum_state(state)
    new_state, report = continue_once(state, executor)
    if new_state is not state:
        validate_minimum_state(new_state)
        apply_regenerated_warrant(new_state)
        save_json(state_path, new_state)
    return RunResult(new_state, report)


def run_until_stop(
    state_path: str | Path,
    executor: Executor,
    max_iterations: int | None = None,
) -> list[RunResult]:
    """Continue until DONE, BLOCKED, or an optional iteration bound is hit."""
    results: list[RunResult] = []
    while max_iterations is None or len(results) < max_iterations:
        result = run_once(state_path, executor)
        results.append(result)
        if result.report.get("status") in {"DONE", "BLOCKED"}:
            break
    return results

"""Command-line control surface for Forest continuation."""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
from typing import Any, Callable

from .runner import RunResult, run_once, run_until_stop

Executor = Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]


def load_executor(spec: str) -> Executor:
    """Load an executor from `package.module:function`."""
    if ":" not in spec:
        raise ValueError("Executor must use package.module:function syntax")
    module_name, function_name = spec.rsplit(":", 1)
    module = importlib.import_module(module_name)
    executor = getattr(module, function_name)
    if not callable(executor):
        raise TypeError(f"Executor is not callable: {spec}")
    return executor


def _report(result: RunResult) -> dict[str, Any]:
    return result.report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="forest", description="Forest autonomous continuation runtime")
    subparsers = parser.add_subparsers(dest="command", required=True)

    cont = subparsers.add_parser("continue", help="Advance canonical state")
    cont.add_argument("--state", required=True, type=Path, help="Path to canonical JSON state")
    cont.add_argument("--executor", required=True, help="Executor import path: package.module:function")
    cont.add_argument("--loop", action="store_true", help="Continue until DONE/BLOCKED instead of one pass")
    cont.add_argument("--max-iterations", type=int, default=None, help="Optional bound when --loop is used")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        executor = load_executor(args.executor)
        if args.loop:
            results = run_until_stop(args.state, executor, max_iterations=args.max_iterations)
            payload: Any = [_report(result) for result in results]
            terminal = results[-1].report.get("status") if results else "BLOCKED"
        else:
            result = run_once(args.state, executor)
            payload = _report(result)
            terminal = result.report.get("status")
    except (ImportError, AttributeError, TypeError, ValueError, OSError) as exc:
        print(json.dumps({"status": "ERROR", "type": type(exc).__name__, "message": str(exc)}, sort_keys=True))
        return 2

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 1 if terminal == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())

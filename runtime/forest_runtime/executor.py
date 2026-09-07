"""Portable real-execution adapters for Forest.

The kernel consumes normalized executor results. This module supplies a local
subprocess adapter without coupling selection/recovery logic to a provider.
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path
from typing import Any, Mapping, Sequence


def _command_from_task(task: dict[str, Any]) -> Sequence[str] | str:
    config = task.get("executor") or {}
    command = config.get("command")
    if not command:
        raise ValueError("task.executor.command is required")
    if isinstance(command, str):
        return command
    if isinstance(command, list) and command and all(isinstance(part, str) for part in command):
        return command
    raise ValueError("task.executor.command must be a non-empty string or string array")


def subprocess_executor(state: dict[str, Any], task: dict[str, Any]) -> dict[str, Any]:
    """Execute an explicitly configured local command and normalize the result.

    Task configuration lives under ``task.executor``:
      command: string or argv array (required)
      timeout_seconds: positive number (default 300)
      cwd: optional working directory
      env: optional environment additions
      shell: optional bool; defaults to True only for string commands

    The adapter never raises for ordinary process failure or timeout; those are
    returned as structured evidence so the kernel's bounded recovery policy can
    decide what happens next.
    """
    config = task.get("executor") or {}
    command = _command_from_task(task)
    timeout = float(config.get("timeout_seconds", 300))
    if timeout <= 0:
        raise ValueError("task.executor.timeout_seconds must be positive")

    cwd_value = config.get("cwd")
    cwd = Path(cwd_value) if cwd_value else None
    env_additions = config.get("env") or {}
    if not isinstance(env_additions, Mapping) or not all(
        isinstance(key, str) and isinstance(value, str) for key, value in env_additions.items()
    ):
        raise ValueError("task.executor.env must be an object of string values")

    shell = bool(config.get("shell", isinstance(command, str)))
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=None if not env_additions else {**__import__("os").environ, **dict(env_additions)},
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=shell,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        duration = time.monotonic() - started
        stdout = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        return {
            "passed": False,
            "evidence": [{"type": "subprocess_timeout", "stdout": stdout, "stderr": stderr}],
            "measurement": {"duration_seconds": duration, "timeout_seconds": timeout},
            "failure": {"classification": "timeout", "retryable": True},
        }

    duration = time.monotonic() - started
    passed = completed.returncode == 0
    evidence = [{
        "type": "subprocess_result",
        "command": command,
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }]
    result: dict[str, Any] = {
        "passed": passed,
        "evidence": evidence,
        "measurement": {
            "duration_seconds": duration,
            "exit_code": completed.returncode,
        },
    }
    if not passed:
        result["failure"] = {"classification": "nonzero_exit", "retryable": True}
    return result

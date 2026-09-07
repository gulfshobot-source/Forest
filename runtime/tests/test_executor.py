import sys

import pytest

from forest_runtime.executor import subprocess_executor


def task(command, **executor):
    return {"id": "exec", "executor": {"command": command, **executor}}


def test_subprocess_executor_success():
    result = subprocess_executor({}, task([sys.executable, "-c", "print('forest-ok')"]))
    assert result["passed"] is True
    assert result["measurement"]["exit_code"] == 0
    assert "forest-ok" in result["evidence"][0]["stdout"]


def test_subprocess_executor_nonzero_exit():
    result = subprocess_executor({}, task([sys.executable, "-c", "import sys; sys.exit(7)"]))
    assert result["passed"] is False
    assert result["measurement"]["exit_code"] == 7
    assert result["failure"]["classification"] == "nonzero_exit"


def test_subprocess_executor_timeout():
    result = subprocess_executor(
        {},
        task([sys.executable, "-c", "import time; time.sleep(1)"], timeout_seconds=0.01),
    )
    assert result["passed"] is False
    assert result["failure"]["classification"] == "timeout"
    assert result["measurement"]["timeout_seconds"] == 0.01


def test_subprocess_executor_requires_command():
    with pytest.raises(ValueError, match="command is required"):
        subprocess_executor({}, {"id": "exec", "executor": {}})


def test_subprocess_executor_rejects_invalid_environment():
    with pytest.raises(ValueError, match="env must be an object of string values"):
        subprocess_executor({}, task([sys.executable, "-c", "pass"], env={"COUNT": 1}))

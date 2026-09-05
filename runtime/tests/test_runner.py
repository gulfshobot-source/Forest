from pathlib import Path

import pytest

from forest_runtime.runner import run_once, run_until_stop, validate_minimum_state


def state():
    return {
        "position": {"current_node": None, "completed_nodes": [], "active_nodes": []},
        "ledger": {"criteria": ["ship"], "items": [{"id": "ship", "status": "pending"}]},
        "tasks": [{"id": "one", "status": "pending", "dependencies": [], "leverage": 1}],
        "history": [],
        "metrics": {},
    }


def test_run_once_persists_state(tmp_path: Path):
    path = tmp_path / "state.json"
    from forest_runtime.persistence import save_json

    save_json(path, state())
    result = run_once(path, lambda _state, _task: {"passed": True, "evidence": ["ok"]})
    assert result.report["status"] == "CONTINUED"

    from forest_runtime.persistence import load_json
    persisted = load_json(path)
    assert persisted["position"]["completed_nodes"] == ["one"]


def test_run_until_stop_honors_bound(tmp_path: Path):
    path = tmp_path / "state.json"
    from forest_runtime.persistence import save_json

    s = state()
    s["tasks"].append({"id": "two", "status": "pending", "dependencies": ["one"], "leverage": 1})
    save_json(path, s)
    results = run_until_stop(path, lambda _state, _task: {"passed": True}, max_iterations=1)
    assert len(results) == 1
    assert results[0].report["status"] == "CONTINUED"


def test_malformed_state_is_rejected(tmp_path: Path):
    path = tmp_path / "state.json"
    path.write_text('{"tasks": []}', encoding="utf-8")
    with pytest.raises(ValueError, match="missing required field: position"):
        run_once(path, lambda *_: {"passed": True})


def test_done_run_does_not_rewrite_or_execute(tmp_path: Path):
    path = tmp_path / "state.json"
    from forest_runtime.persistence import save_json

    s = state()
    s["ledger"]["items"][0]["status"] = "passed"
    save_json(path, s)
    before = path.read_text(encoding="utf-8")
    result = run_once(path, lambda *_: (_ for _ in ()).throw(AssertionError("must not execute")))
    assert result.report["status"] == "DONE"
    assert path.read_text(encoding="utf-8") == before

from forest_runtime.core import completion_status, continue_once, select_next_task


def state():
    return {
        "position": {"current_node": None, "completed_nodes": [], "active_nodes": []},
        "ledger": {"criteria": ["ship"], "items": [{"id": "ship", "status": "pending"}]},
        "tasks": [
            {"id": "blocked", "status": "pending", "dependencies": ["missing"], "leverage": 100},
            {"id": "foundation", "status": "pending", "dependencies": [], "leverage": 5, "reuse": 10},
            {"id": "quick", "status": "pending", "dependencies": [], "leverage": 5, "reuse": 1},
        ],
        "history": [],
        "metrics": {},
    }


def test_selection_respects_dependencies_and_leverage():
    chosen = select_next_task(state()).task
    assert chosen["id"] == "foundation"


def test_continue_records_result_and_advances_state():
    old = state()
    new, report = continue_once(old, lambda _state, task: {"passed": True, "evidence": [task["id"]]})
    assert report["status"] == "CONTINUED"
    assert "foundation" in new["position"]["completed_nodes"]
    assert new["tasks"][1]["status"] == "complete"
    assert new["tasks"][1]["attempts"] == 1
    assert new["history"][-1]["passed"] is True


def test_completion_requires_ledger_evidence():
    s = state()
    assert completion_status(s) == "incomplete"
    s["ledger"]["items"][0]["status"] = "passed"
    assert completion_status(s) == "complete"


def test_done_does_not_execute_again():
    s = state()
    s["ledger"]["items"][0]["status"] = "passed"
    new, report = continue_once(s, lambda *_: (_ for _ in ()).throw(AssertionError("must not execute")))
    assert new == s
    assert report["status"] == "DONE"


def test_failure_without_recovery_blocks_task():
    s = state()
    new, report = continue_once(s, lambda *_: {"passed": False, "failure": {"classification": "test"}})
    task = next(t for t in new["tasks"] if t["id"] == "foundation")
    assert report["status"] == "BLOCKED"
    assert task["status"] == "blocked"
    assert new["metrics"]["failures"] == 1


def test_recovery_policy_allows_one_retry_then_blocks():
    s = state()
    task = next(t for t in s["tasks"] if t["id"] == "foundation")
    task["recovery"] = {"retry_allowed": True, "max_retries": 1}

    first, report1 = continue_once(s, lambda *_: {"passed": False})
    assert report1["status"] == "RETRY"
    assert next(t for t in first["tasks"] if t["id"] == "foundation")["status"] == "failed"

    second, report2 = continue_once(first, lambda *_: {"passed": False})
    assert report2["status"] == "BLOCKED"
    retried = next(t for t in second["tasks"] if t["id"] == "foundation")
    assert retried["attempts"] == 2
    assert retried["status"] == "blocked"
    assert second["metrics"]["retries_scheduled"] == 1


def test_executor_exception_is_captured_as_failure_evidence():
    s = state()

    def explode(*_):
        raise RuntimeError("boom")

    new, report = continue_once(s, explode)
    assert report["status"] == "BLOCKED"
    assert report["result"]["failure"]["classification"] == "executor_exception"
    assert report["result"]["failure"]["type"] == "RuntimeError"
    assert new["history"][-1]["failure"]["message"] == "boom"

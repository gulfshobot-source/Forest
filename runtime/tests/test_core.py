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

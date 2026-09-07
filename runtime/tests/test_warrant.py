from forest_runtime.warrant import apply_regenerated_warrant, regenerate_warrant


def state():
    return {
        "schema_version": "0.1",
        "project": {"objective": "Advance Forest."},
        "position": {"current_node": "alpha", "completed_nodes": [], "active_nodes": []},
        "ledger": {"items": [{"id": "done", "status": "pending"}]},
        "tasks": [
            {"id": "low", "status": "pending", "dependencies": [], "leverage": 1},
            {
                "id": "high",
                "status": "pending",
                "dependencies": [],
                "leverage": 9,
                "recovery": {"retry_allowed": True, "max_retries": 2},
            },
        ],
        "warrant": {"state_version": "forest-state-v1"},
    }


def test_regenerate_warrant_selects_highest_leverage_task():
    warrant = regenerate_warrant(state())
    assert warrant is not None
    assert warrant["task"] == "high"
    assert warrant["state_version"] == "forest-state-v1"
    assert warrant["recovery"]["retry_allowed"] is True
    assert warrant["recovery"]["rollback_required_on_failure"] is False


def test_apply_regenerated_warrant_updates_state():
    s = state()
    apply_regenerated_warrant(s)
    assert s["warrant"]["id"] == "warrant-high"


def test_regenerate_warrant_returns_none_when_no_unblocked_task():
    s = state()
    for task in s["tasks"]:
        task["status"] = "complete"
    assert regenerate_warrant(s) is None

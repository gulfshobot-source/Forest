from forest_runtime.telemetry import gap_scan, record_continuation_observation


def state():
    return {
        "position": {"completed_nodes": ["done"]},
        "ledger": {
            "items": [
                {"id": "a", "status": "passed"},
                {"id": "b", "status": "pending"},
            ]
        },
        "tasks": [
            {"id": "ready", "status": "pending", "dependencies": ["done"]},
            {"id": "blocked", "status": "pending", "dependencies": ["missing"]},
            {"id": "complete", "status": "complete", "dependencies": []},
        ],
        "metrics": {},
    }


def test_gap_scan_separates_ready_and_blocked_work():
    gaps = gap_scan(state())
    assert gaps["passed_criteria"] == ["a"]
    assert gaps["pending_criteria"] == ["b"]
    assert gaps["ready_tasks"] == ["ready"]
    assert gaps["blocked_tasks"] == [
        {"id": "blocked", "missing_dependencies": ["missing"]}
    ]


def test_record_observation_refreshes_progress_metrics():
    s = state()
    gaps = record_continuation_observation(
        s,
        {"status": "CONTINUED", "task_id": "ready", "selection_reason": "test"},
    )
    assert gaps["ready_tasks"] == ["ready"]
    assert s["system_observations"][-1]["task_id"] == "ready"
    assert s["metrics"]["completion_fraction"] == 0.5
    assert s["metrics"]["ready_task_count"] == 1
    assert s["metrics"]["blocked_task_count"] == 1
    assert s["metrics"]["observation_count"] == 1

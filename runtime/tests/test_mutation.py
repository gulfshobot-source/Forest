import json

import pytest

from forest_runtime.authority import MutationProposal
from forest_runtime.mutation import MutationExecutionError, apply_plan_to_snapshot, prepare_mutation
from forest_runtime.registry import InjectedRegistryAdapter


SUBJECT = "forest://architecture/downstairs-connector-fabric"


def loaded(state="authoritative-living", revision="abc123"):
    raw = json.dumps({
        "forest": {"id": "forest", "kind": "forest"},
        "architecture": [
            {"id": "downstairs-connector-fabric", "name": "Downstairs Connector Fabric", "state": state}
        ],
    })
    return InjectedRegistryAdapter(
        content=raw,
        source="gulfshobot-source/the-forest:data/forest.json",
        source_revision=revision,
    ).load()


def proposal(**kwargs):
    values = {
        "proposal_id": "proposal:test",
        "candidate_id": "reconcile:test",
        "subject": SUBJECT,
        "proposed_delta": {"state": "verified"},
        "gate_state": "authorized",
        "authorized_fields": ("state",),
        "evidence": ("evidence-1",),
        "source_bindings": ("github://connector/structural",),
    }
    values.update(kwargs)
    return MutationProposal(**values)


def test_authorized_proposal_prepares_revision_pinned_plan():
    registry = loaded()
    plan = prepare_mutation(proposal(), registry, {"state": "authoritative-living"})
    assert plan.state == "ready"
    assert plan.executable is True
    assert plan.changes == {"state": "verified"}
    assert plan.source_revision == "abc123"
    assert plan.source_digest == registry.content_digest


def test_stale_canonical_value_blocks_plan():
    plan = prepare_mutation(proposal(), loaded(state="changed"), {"state": "authoritative-living"})
    assert plan.state == "stale"
    assert plan.executable is False
    assert plan.stale_fields == ("state",)


def test_missing_expected_value_fails_closed():
    plan = prepare_mutation(proposal(), loaded(), {})
    assert plan.state == "stale"
    assert "missing expected canonical value" in plan.reasons[0]


def test_noop_is_explicit_and_not_executable():
    plan = prepare_mutation(
        proposal(proposed_delta={"state": "authoritative-living"}),
        loaded(),
        {"state": "authoritative-living"},
    )
    assert plan.state == "noop"
    assert plan.unchanged_fields == ("state",)
    assert plan.executable is False


def test_partial_or_blocked_proposal_cannot_cross_write_boundary():
    with pytest.raises(MutationExecutionError):
        prepare_mutation(
            proposal(gate_state="partial", blocked_fields=("owner",)),
            loaded(),
            {"state": "authoritative-living"},
        )


def test_delta_must_exactly_match_authorized_fields():
    with pytest.raises(MutationExecutionError):
        prepare_mutation(
            proposal(authorized_fields=("state", "owner")),
            loaded(),
            {"state": "authoritative-living"},
        )


def test_snapshot_application_rechecks_registry_revision_and_digest():
    registry = loaded()
    plan = prepare_mutation(proposal(), registry, {"state": "authoritative-living"})
    updated = apply_plan_to_snapshot(plan, registry)
    assert updated["state"] == "verified"

    with pytest.raises(MutationExecutionError):
        apply_plan_to_snapshot(plan, loaded(revision="new-revision"))

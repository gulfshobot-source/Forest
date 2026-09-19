import json

import pytest

from forest_runtime.authority import MutationProposal
from forest_runtime.mutation import MutationExecutionError, prepare_mutation
from forest_runtime.persistence import execute_verified_mutation
from forest_runtime.registry import InjectedRegistryAdapter

SUBJECT = "forest://architecture/downstairs-connector-fabric"
SOURCE = "gulfshobot-source/the-forest:data/forest.json"


def loaded(state, revision):
    raw = json.dumps({
        "forest": {"id": "forest", "kind": "forest"},
        "architecture": [{"id": "downstairs-connector-fabric", "state": state}],
    })
    return InjectedRegistryAdapter(raw, SOURCE, revision).load()


def plan(before):
    proposal = MutationProposal(
        proposal_id="proposal:test", candidate_id="reconcile:test", subject=SUBJECT,
        proposed_delta={"state": "verified"}, gate_state="authorized",
        authorized_fields=("state",), evidence=("evidence-1",),
        source_bindings=("github://connector/structural",),
    )
    return prepare_mutation(proposal, before, {"state": "authoritative-living"})


class FakeStore:
    def __init__(self, before, after, reject=False):
        self.current = before
        self.after = after
        self.reject = reject
        self.loads = 0
        self.cas_calls = []

    def load(self):
        self.loads += 1
        return self.current

    def compare_and_swap(self, mutation_plan, expected_revision, expected_digest):
        self.cas_calls.append((mutation_plan.plan_id, expected_revision, expected_digest))
        if self.reject:
            raise MutationExecutionError("compare-and-swap rejected by canonical store")
        self.current = self.after


def test_executor_enforces_read_cas_reread_and_returns_receipt():
    before = loaded("authoritative-living", "rev-1")
    store = FakeStore(before, loaded("verified", "rev-2"))
    mutation_plan = plan(before)

    receipt = execute_verified_mutation(mutation_plan, store)

    assert store.loads == 2
    assert store.cas_calls == [(mutation_plan.plan_id, "rev-1", mutation_plan.source_digest)]
    assert receipt.state == "verified"
    assert receipt.after_revision == "rev-2"


def test_executor_rejects_stale_store_before_write():
    prepared_from = loaded("authoritative-living", "rev-1")
    stale_store = FakeStore(loaded("changed", "rev-2"), loaded("verified", "rev-3"))

    with pytest.raises(MutationExecutionError, match="revision/digest changed"):
        execute_verified_mutation(plan(prepared_from), stale_store)
    assert stale_store.cas_calls == []


def test_store_cas_rejection_never_produces_receipt_or_reread():
    before = loaded("authoritative-living", "rev-1")
    store = FakeStore(before, loaded("verified", "rev-2"), reject=True)

    with pytest.raises(MutationExecutionError, match="compare-and-swap rejected"):
        execute_verified_mutation(plan(before), store)
    assert store.loads == 1
    assert len(store.cas_calls) == 1


def test_executor_rejects_false_success_after_write():
    before = loaded("authoritative-living", "rev-1")
    store = FakeStore(before, loaded("wrong", "rev-2"))

    with pytest.raises(MutationExecutionError, match="does not contain planned values"):
        execute_verified_mutation(plan(before), store)
    assert store.loads == 2

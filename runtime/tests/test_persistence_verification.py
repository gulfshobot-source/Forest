import json

import pytest

from forest_runtime.authority import MutationProposal
from forest_runtime.mutation import MutationExecutionError, prepare_mutation
from forest_runtime.persistence import verify_persisted_mutation
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


def test_fresh_reread_produces_verified_receipt():
    before = loaded("authoritative-living", "rev-1")
    receipt = verify_persisted_mutation(plan(before), before, loaded("verified", "rev-2"))
    assert receipt.state == "verified"
    assert receipt.before_revision == "rev-1"
    assert receipt.after_revision == "rev-2"
    assert receipt.verified_fields == ("state",)
    assert receipt.receipt_id.startswith("mutation-receipt:")


def test_unchanged_source_cannot_claim_persistence():
    before = loaded("authoritative-living", "rev-1")
    with pytest.raises(MutationExecutionError, match="did not advance"):
        verify_persisted_mutation(plan(before), before, before)


def test_reread_must_contain_planned_value():
    before = loaded("authoritative-living", "rev-1")
    with pytest.raises(MutationExecutionError, match="does not contain planned values"):
        verify_persisted_mutation(plan(before), before, loaded("different", "rev-2"))


def test_source_switch_fails_closed():
    before = loaded("authoritative-living", "rev-1")
    other_raw = json.dumps({
        "forest": {"id": "forest", "kind": "forest"},
        "architecture": [{"id": "downstairs-connector-fabric", "state": "verified"}],
    })
    other = InjectedRegistryAdapter(other_raw, "other:registry", "rev-2").load()
    with pytest.raises(MutationExecutionError, match="source changed"):
        verify_persisted_mutation(plan(before), before, other)


def test_receipt_identity_is_deterministic_for_same_proof():
    before = loaded("authoritative-living", "rev-1")
    after = loaded("verified", "rev-2")
    mutation_plan = plan(before)
    assert verify_persisted_mutation(mutation_plan, before, after).receipt_id == \
        verify_persisted_mutation(mutation_plan, before, after).receipt_id

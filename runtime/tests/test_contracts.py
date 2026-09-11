import pytest

from forest_runtime.contracts import ContractError, MutationEnvelope, ObservationEnvelope


def test_mutation_envelope_normalizes_subject_and_preserves_authority_requirements():
    envelope = MutationEnvelope(
        intent_id="intent-1",
        subject="forest://tree/irrigation",
        operation="update",
        proposed_delta={"state": "verified"},
        requested_by="user",
        authority_required=("canonical-write",),
        capability_required=("github",),
        evidence_required=("commit", "verification"),
    )
    payload = envelope.as_dict()
    assert payload["subject"] == "forest://tree/irrigation"
    assert payload["status"] == "proposed"
    assert payload["authority_required"] == ["canonical-write"]
    assert payload["evidence_required"] == ["commit", "verification"]


def test_observation_cannot_self_promote_to_canonical():
    observation = ObservationEnvelope(
        observation_id="obs-1",
        subject="forest://architecture/foundational-substrate",
        source_binding="github-actions",
        observed_delta={"tests": "passed"},
        observed_at="2026-09-11T13:00:00Z",
        evidence=("ci-run-1",),
        proposed_reconciliation={"operational_state": "verified"},
    )
    assert observation.reality_state == "observed"
    assert observation.can_self_promote_to_canonical is False
    assert observation.as_dict()["proposed_reconciliation"] == {"operational_state": "verified"}


def test_verified_observation_is_still_only_an_envelope_not_canonical_state():
    observation = ObservationEnvelope(
        observation_id="obs-2",
        subject="forest://tree/trading",
        source_binding="external-test",
        observed_at="2026-09-11T13:00:00Z",
        reality_state="verified",
    )
    assert observation.reality_state == "verified"
    assert observation.can_self_promote_to_canonical is False


def test_invalid_mutation_status_fails():
    with pytest.raises(ContractError, match="invalid mutation status"):
        MutationEnvelope(
            intent_id="intent-2",
            subject="forest://tree/irrigation",
            operation="update",
            status="canonical",
        )


def test_invalid_subject_address_fails_through_shared_address_contract():
    with pytest.raises(ValueError, match="INVALID_ADDRESS"):
        ObservationEnvelope(
            observation_id="obs-3",
            subject="https://example.com/object/1",
            source_binding="external",
            observed_at="2026-09-11T13:00:00Z",
        )


def test_observation_conflicts_are_explicit():
    observation = ObservationEnvelope(
        observation_id="obs-4",
        subject="forest://tree/irrigation",
        source_binding="mirror-a",
        observed_at="2026-09-11T13:00:00Z",
        conflicts=("mirror-b disagrees on state",),
    )
    assert observation.as_dict()["conflicts"] == ["mirror-b disagrees on state"]

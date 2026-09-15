from datetime import datetime, timezone

from forest_runtime.contracts import ObservationEnvelope
from forest_runtime.reconciliation import route_event, route_events
from forest_runtime.synchronization import ingest_observation


NOW = datetime(2026, 9, 15, 13, 0, tzinfo=timezone.utc)
SUBJECT = "forest://architecture/downstairs-connector-fabric"


def event(observation_id: str, **kwargs):
    observation = ObservationEnvelope(
        observation_id=observation_id,
        subject=SUBJECT,
        source_binding=kwargs.pop("source_binding", "github://connector/a"),
        observed_delta=kwargs.pop("observed_delta", {"operational_state": "healthy"}),
        observed_at=kwargs.pop("observed_at", "2026-09-15T12:55:00Z"),
        evidence=kwargs.pop("evidence", (observation_id,)),
        **kwargs,
    )
    return ingest_observation(observation, reference_time=NOW)


def test_candidate_retains_subject_provenance_and_authority_boundary():
    candidate = route_event(event("obs-1", proposed_reconciliation={"operational_state": "verified"}))

    assert candidate.subject == SUBJECT
    assert candidate.source_bindings == ("github://connector/a",)
    assert candidate.observation_ids == ("obs-1",)
    assert candidate.evidence == ("obs-1",)
    assert candidate.proposed_delta == {"operational_state": "verified"}
    assert candidate.routing_state == "ready"
    assert candidate.canonical_mutation_allowed is False
    assert candidate.write_ready is False


def test_duplicate_semantic_observations_have_same_identity_and_are_compressed():
    first = event("obs-a", evidence=("evidence-a",))
    second = event("obs-b", observed_at="2026-09-15T12:56:00Z", evidence=("evidence-b",))

    first_candidate = route_event(first)
    second_candidate = route_event(second)
    assert first_candidate.candidate_id == second_candidate.candidate_id

    merged = route_events([first, second])
    assert len(merged) == 1
    assert merged[0].observation_ids == ("obs-a", "obs-b")
    assert merged[0].evidence == ("evidence-a", "evidence-b")


def test_conflict_remains_explicit_and_never_becomes_write_ready():
    candidate = route_event(event("obs-conflict", conflicts=("authority disagrees",)))

    assert candidate.routing_state == "conflicted"
    assert candidate.conflicts == ("authority disagrees",)
    assert candidate.write_ready is False


def test_failed_observation_is_blocked_even_with_proposed_reconciliation():
    candidate = route_event(
        event(
            "obs-failed",
            reality_state="failed",
            proposed_reconciliation={"operational_state": "verified"},
        )
    )

    assert candidate.routing_state == "blocked"
    assert candidate.proposed_delta == {"operational_state": "verified"}
    assert candidate.canonical_mutation_allowed is False


def test_different_source_bindings_do_not_silently_collapse_authority():
    first = event("obs-source-a", source_binding="github://connector/a")
    second = event("obs-source-b", source_binding="github://connector/b")

    candidates = route_events([first, second])
    assert len(candidates) == 2
    assert candidates[0].candidate_id != candidates[1].candidate_id

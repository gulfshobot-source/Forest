from datetime import datetime, timezone

import pytest

from forest_runtime.contracts import ObservationEnvelope
from forest_runtime.synchronization import SynchronizationError, ingest_observation


REFERENCE_TIME = datetime(2026, 9, 14, 14, 0, tzinfo=timezone.utc)


def test_ingestion_preserves_subject_source_and_observation_boundary():
    observation = ObservationEnvelope(
        observation_id="obs-100",
        subject="forest://architecture/downstairs-connector-fabric",
        source_binding="github://gulfshobot-source/Forest/actions/run/1",
        observed_delta={"tests": "passed"},
        observed_at="2026-09-14T13:30:00Z",
        evidence=("ci-run-1",),
        proposed_reconciliation={"operational_state": "verified"},
    )

    event = ingest_observation(observation, reference_time=REFERENCE_TIME)

    assert event.subject == "forest://architecture/downstairs-connector-fabric"
    assert event.source_binding == observation.source_binding
    assert event.observation_id == "obs-100"
    assert event.reality_state == "observed"
    assert event.freshness == "fresh"
    assert event.reconciliation_state == "candidate"
    assert event.canonical_mutation_allowed is False
    assert event.as_dict()["proposed_reconciliation"] == {"operational_state": "verified"}


def test_stale_observation_remains_visible_instead_of_becoming_conflict():
    observation = ObservationEnvelope(
        observation_id="obs-stale",
        subject="forest://tree/irrigation",
        source_binding="external-system",
        observed_at="2026-09-14T10:00:00Z",
    )

    event = ingest_observation(
        observation,
        reference_time=REFERENCE_TIME,
        stale_after_seconds=3600,
    )

    assert event.freshness == "stale"
    assert event.reconciliation_state == "candidate"


def test_conflicts_are_preserved_and_mark_reconciliation_conflicted():
    observation = ObservationEnvelope(
        observation_id="obs-conflict",
        subject="forest://tree/trading",
        source_binding="mirror-a",
        observed_at="2026-09-14T13:50:00Z",
        conflicts=("mirror-b disagrees on state",),
    )

    event = ingest_observation(observation, reference_time=REFERENCE_TIME)

    assert event.reconciliation_state == "conflicted"
    assert event.conflicts == ("mirror-b disagrees on state",)


def test_failed_reality_state_is_blocked_not_promoted():
    observation = ObservationEnvelope(
        observation_id="obs-failed",
        subject="forest://architecture/downstairs-connector-fabric",
        source_binding="connector-a",
        observed_at="2026-09-14T13:55:00Z",
        reality_state="failed",
        proposed_reconciliation={"operational_state": "verified"},
    )

    event = ingest_observation(observation, reference_time=REFERENCE_TIME)

    assert event.reconciliation_state == "blocked"
    assert event.canonical_mutation_allowed is False


def test_unknown_observation_time_has_unknown_freshness():
    observation = ObservationEnvelope(
        observation_id="obs-unknown-time",
        subject="forest://tree/irrigation",
        source_binding="external",
        observed_at="unknown",
    )

    event = ingest_observation(observation, reference_time=REFERENCE_TIME)
    assert event.freshness == "unknown"


def test_invalid_timestamp_is_rejected_before_reconciliation():
    observation = ObservationEnvelope(
        observation_id="obs-bad-time",
        subject="forest://tree/irrigation",
        source_binding="external",
        observed_at="not-a-timestamp",
    )

    with pytest.raises(SynchronizationError, match="invalid observed_at timestamp"):
        ingest_observation(observation, reference_time=REFERENCE_TIME)


def test_naive_reference_time_is_rejected():
    observation = ObservationEnvelope(
        observation_id="obs-naive-reference",
        subject="forest://tree/irrigation",
        source_binding="external",
        observed_at="2026-09-14T13:55:00Z",
    )

    with pytest.raises(SynchronizationError, match="reference_time must include timezone"):
        ingest_observation(
            observation,
            reference_time=datetime(2026, 9, 14, 14, 0),
        )

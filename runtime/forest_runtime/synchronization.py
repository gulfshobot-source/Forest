from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .contracts import ObservationEnvelope


FRESHNESS_STATES = {"fresh", "stale", "unknown"}
RECONCILIATION_STATES = {"candidate", "conflicted", "blocked"}


class SynchronizationError(ValueError):
    """Raised when an observation cannot be normalized into a synchronization event."""


def _parse_timestamp(value: str) -> datetime | None:
    if value == "unknown":
        return None
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise SynchronizationError(f"invalid observed_at timestamp: {value}") from exc
    if parsed.tzinfo is None:
        raise SynchronizationError("observed_at timestamp must include timezone information")
    return parsed.astimezone(timezone.utc)


def classify_freshness(
    observation: ObservationEnvelope,
    *,
    reference_time: datetime | None = None,
    stale_after_seconds: int = 3600,
) -> str:
    """Classify observation freshness without mutating or interpreting canonical truth."""
    if stale_after_seconds < 0:
        raise SynchronizationError("stale_after_seconds must be non-negative")
    observed_at = _parse_timestamp(observation.observed_at)
    if observed_at is None:
        return "unknown"
    now = reference_time or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise SynchronizationError("reference_time must include timezone information")
    age_seconds = (now.astimezone(timezone.utc) - observed_at).total_seconds()
    return "stale" if age_seconds > stale_after_seconds else "fresh"


@dataclass(frozen=True)
class SynchronizationEvent:
    event_id: str
    subject: str
    source_binding: str
    observation_id: str
    observed_delta: dict[str, Any] = field(default_factory=dict)
    observed_at: str = "unknown"
    reality_state: str = "observed"
    freshness: str = "unknown"
    evidence: tuple[str, ...] = ()
    conflicts: tuple[str, ...] = ()
    reconciliation_state: str = "candidate"
    proposed_reconciliation: dict[str, Any] | None = None

    @property
    def canonical_mutation_allowed(self) -> bool:
        """Synchronization events are reconciliation inputs, never canonical writes."""
        return False

    def as_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "subject": self.subject,
            "source_binding": self.source_binding,
            "observation_id": self.observation_id,
            "observed_delta": self.observed_delta,
            "observed_at": self.observed_at,
            "reality_state": self.reality_state,
            "freshness": self.freshness,
            "evidence": list(self.evidence),
            "conflicts": list(self.conflicts),
            "reconciliation_state": self.reconciliation_state,
            "proposed_reconciliation": self.proposed_reconciliation,
        }


def ingest_observation(
    observation: ObservationEnvelope,
    *,
    reference_time: datetime | None = None,
    stale_after_seconds: int = 3600,
) -> SynchronizationEvent:
    """Normalize a cross-layer observation into a transport-neutral reconciliation candidate.

    The function deliberately does not resolve conflicts or mutate canonical state. It preserves
    source identity, freshness, evidence, and reality-state distinctions so a later reconciliation
    authority can decide whether any canonical change is justified.
    """
    freshness = classify_freshness(
        observation,
        reference_time=reference_time,
        stale_after_seconds=stale_after_seconds,
    )

    if observation.conflicts:
        reconciliation_state = "conflicted"
    elif observation.reality_state == "failed":
        reconciliation_state = "blocked"
    else:
        reconciliation_state = "candidate"

    return SynchronizationEvent(
        event_id=f"sync:{observation.observation_id}",
        subject=observation.subject,
        source_binding=observation.source_binding,
        observation_id=observation.observation_id,
        observed_delta=dict(observation.observed_delta),
        observed_at=observation.observed_at,
        reality_state=observation.reality_state,
        freshness=freshness,
        evidence=tuple(observation.evidence),
        conflicts=tuple(observation.conflicts),
        reconciliation_state=reconciliation_state,
        proposed_reconciliation=(
            dict(observation.proposed_reconciliation)
            if observation.proposed_reconciliation is not None
            else None
        ),
    )

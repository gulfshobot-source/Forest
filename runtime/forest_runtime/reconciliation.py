from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, Iterable

from .synchronization import SynchronizationEvent


ROUTING_STATES = {"ready", "conflicted", "blocked"}


class ReconciliationError(ValueError):
    """Raised when a synchronization event cannot become a reconciliation candidate."""


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _candidate_identity(event: SynchronizationEvent) -> str:
    """Derive identity from semantic reconciliation content, not transport/event IDs.

    Repeated observations of the same proposed change from the same authoritative binding
    therefore collapse to one candidate while distinct evidence can still be accumulated.
    """
    payload = {
        "subject": event.subject,
        "source_binding": event.source_binding,
        "observed_delta": event.observed_delta,
        "reality_state": event.reality_state,
        "conflicts": sorted(event.conflicts),
        "proposed_reconciliation": event.proposed_reconciliation,
    }
    digest = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()[:24]
    return f"reconcile:{digest}"


@dataclass(frozen=True)
class ReconciliationCandidate:
    candidate_id: str
    subject: str
    source_bindings: tuple[str, ...]
    observation_ids: tuple[str, ...]
    event_ids: tuple[str, ...]
    proposed_delta: dict[str, Any] = field(default_factory=dict)
    routing_state: str = "ready"
    freshness_states: tuple[str, ...] = ()
    reality_states: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    conflicts: tuple[str, ...] = ()

    @property
    def canonical_mutation_allowed(self) -> bool:
        """Candidates require a separate authority/verification step before mutation."""
        return False

    @property
    def write_ready(self) -> bool:
        """Routing readiness is not canonical-write authorization."""
        return False

    def as_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "subject": self.subject,
            "source_bindings": list(self.source_bindings),
            "observation_ids": list(self.observation_ids),
            "event_ids": list(self.event_ids),
            "proposed_delta": self.proposed_delta,
            "routing_state": self.routing_state,
            "freshness_states": list(self.freshness_states),
            "reality_states": list(self.reality_states),
            "evidence": list(self.evidence),
            "conflicts": list(self.conflicts),
        }


def route_event(event: SynchronizationEvent) -> ReconciliationCandidate:
    """Route one normalized event without granting it canonical mutation authority."""
    if event.reconciliation_state == "conflicted":
        routing_state = "conflicted"
    elif event.reconciliation_state == "blocked" or event.reality_state == "failed":
        routing_state = "blocked"
    else:
        routing_state = "ready"

    proposed_delta = (
        dict(event.proposed_reconciliation)
        if event.proposed_reconciliation is not None
        else dict(event.observed_delta)
    )

    return ReconciliationCandidate(
        candidate_id=_candidate_identity(event),
        subject=event.subject,
        source_bindings=(event.source_binding,),
        observation_ids=(event.observation_id,),
        event_ids=(event.event_id,),
        proposed_delta=proposed_delta,
        routing_state=routing_state,
        freshness_states=(event.freshness,),
        reality_states=(event.reality_state,),
        evidence=tuple(event.evidence),
        conflicts=tuple(event.conflicts),
    )


def deduplicate_candidates(candidates: Iterable[ReconciliationCandidate]) -> list[ReconciliationCandidate]:
    """Compress repeated semantic candidates while retaining their provenance/evidence."""
    grouped: dict[str, list[ReconciliationCandidate]] = {}
    order: list[str] = []
    for candidate in candidates:
        if candidate.candidate_id not in grouped:
            grouped[candidate.candidate_id] = []
            order.append(candidate.candidate_id)
        grouped[candidate.candidate_id].append(candidate)

    merged: list[ReconciliationCandidate] = []
    rank = {"ready": 0, "blocked": 1, "conflicted": 2}
    for candidate_id in order:
        group = grouped[candidate_id]
        first = group[0]
        if any(item.subject != first.subject or item.proposed_delta != first.proposed_delta for item in group):
            raise ReconciliationError(f"candidate identity collision: {candidate_id}")

        def unique(values: Iterable[str]) -> tuple[str, ...]:
            return tuple(dict.fromkeys(values))

        merged.append(
            ReconciliationCandidate(
                candidate_id=candidate_id,
                subject=first.subject,
                source_bindings=unique(v for item in group for v in item.source_bindings),
                observation_ids=unique(v for item in group for v in item.observation_ids),
                event_ids=unique(v for item in group for v in item.event_ids),
                proposed_delta=dict(first.proposed_delta),
                routing_state=max((item.routing_state for item in group), key=rank.__getitem__),
                freshness_states=unique(v for item in group for v in item.freshness_states),
                reality_states=unique(v for item in group for v in item.reality_states),
                evidence=unique(v for item in group for v in item.evidence),
                conflicts=unique(v for item in group for v in item.conflicts),
            )
        )
    return merged


def route_events(events: Iterable[SynchronizationEvent]) -> list[ReconciliationCandidate]:
    return deduplicate_candidates(route_event(event) for event in events)

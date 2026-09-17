from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, Mapping

from .addressing import build_identity_index
from .authority import MutationProposal
from .registry import LoadedRegistry


class MutationExecutionError(ValueError):
    """Raised when an authorized proposal cannot safely cross the write boundary."""


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass(frozen=True)
class CanonicalMutationPlan:
    """Compare-before-write plan pinned to one canonical registry snapshot.

    This object is intentionally not a persistence adapter. It proves that an authorized
    proposal still matches the canonical state it was prepared against and records the
    exact source revision/digest that a downstream writer must compare before commit.
    """

    plan_id: str
    proposal_id: str
    subject: str
    source: str
    source_revision: str | None
    source_digest: str | None
    changes: dict[str, Any] = field(default_factory=dict)
    unchanged_fields: tuple[str, ...] = ()
    stale_fields: tuple[str, ...] = ()
    state: str = "ready"
    reasons: tuple[str, ...] = ()

    @property
    def executable(self) -> bool:
        return self.state == "ready" and not self.stale_fields

    def as_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "proposal_id": self.proposal_id,
            "subject": self.subject,
            "source": self.source,
            "source_revision": self.source_revision,
            "source_digest": self.source_digest,
            "changes": self.changes,
            "unchanged_fields": list(self.unchanged_fields),
            "stale_fields": list(self.stale_fields),
            "state": self.state,
            "reasons": list(self.reasons),
            "executable": self.executable,
        }


def _plan_id(proposal: MutationProposal, registry: LoadedRegistry, expected_current: Mapping[str, Any]) -> str:
    payload = {
        "proposal_id": proposal.proposal_id,
        "subject": proposal.subject,
        "source_revision": registry.source_revision,
        "source_digest": registry.content_digest,
        "expected_current": dict(expected_current),
    }
    digest = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()[:24]
    return f"mutation-plan:{digest}"


def prepare_mutation(
    proposal: MutationProposal,
    registry: LoadedRegistry,
    expected_current: Mapping[str, Any],
) -> CanonicalMutationPlan:
    """Prepare a mutation only when authority and optimistic concurrency both hold."""
    if not proposal.canonical_mutation_allowed:
        raise MutationExecutionError("proposal is not fully authorized for canonical mutation")

    resolved = registry.resolve(proposal.subject)
    record = resolved["record"]
    authorized = set(proposal.authorized_fields)
    proposed_fields = set(proposal.proposed_delta)
    if proposed_fields != authorized:
        raise MutationExecutionError("proposal delta must exactly match its authorized field set")

    changes: dict[str, Any] = {}
    unchanged: list[str] = []
    stale: list[str] = []
    reasons: list[str] = []

    for field_name, proposed_value in proposal.proposed_delta.items():
        if field_name not in expected_current:
            stale.append(field_name)
            reasons.append(f"{field_name}: missing expected canonical value")
            continue
        actual = record.get(field_name)
        expected = expected_current[field_name]
        if actual != expected:
            stale.append(field_name)
            reasons.append(f"{field_name}: canonical value changed since proposal preparation")
        elif actual == proposed_value:
            unchanged.append(field_name)
        else:
            changes[field_name] = proposed_value

    state = "stale" if stale else ("noop" if not changes else "ready")
    return CanonicalMutationPlan(
        plan_id=_plan_id(proposal, registry, expected_current),
        proposal_id=proposal.proposal_id,
        subject=proposal.subject,
        source=registry.source,
        source_revision=registry.source_revision,
        source_digest=registry.content_digest,
        changes=changes,
        unchanged_fields=tuple(unchanged),
        stale_fields=tuple(stale),
        state=state,
        reasons=tuple(reasons),
    )


def apply_plan_to_snapshot(plan: CanonicalMutationPlan, registry: LoadedRegistry) -> dict[str, Any]:
    """Apply a ready plan to an in-memory snapshot for validation; never persists it.

    A real writer must independently compare source_revision/content_digest immediately
    before persistence. This function exists so mutation semantics can be tested without
    granting the runtime hidden repository authority.
    """
    if not plan.executable:
        raise MutationExecutionError(f"mutation plan is not executable: {plan.state}")
    if plan.source != registry.source:
        raise MutationExecutionError("canonical source changed before mutation")
    if plan.source_revision != registry.source_revision or plan.source_digest != registry.content_digest:
        raise MutationExecutionError("canonical registry revision/digest changed before mutation")

    index = build_identity_index(registry.registry)
    record = index.get(plan.subject)
    if record is None:
        raise MutationExecutionError("canonical subject disappeared before mutation")

    updated = dict(record)
    updated.update(plan.changes)
    return updated

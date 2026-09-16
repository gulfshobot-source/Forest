from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, Mapping

from .reconciliation import ReconciliationCandidate


class AuthorityGateError(ValueError):
    """Raised when a reconciliation candidate cannot be evaluated safely."""


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass(frozen=True)
class AuthorityPolicy:
    """Field-scoped authority and evidence requirements for one Forest subject."""

    subject: str
    authoritative_bindings: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    required_evidence: Mapping[str, int] = field(default_factory=dict)
    protected_fields: tuple[str, ...] = ()


@dataclass(frozen=True)
class MutationProposal:
    proposal_id: str
    candidate_id: str
    subject: str
    proposed_delta: dict[str, Any]
    gate_state: str
    authorized_fields: tuple[str, ...] = ()
    blocked_fields: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    source_bindings: tuple[str, ...] = ()

    @property
    def canonical_mutation_allowed(self) -> bool:
        # The gate emits an authorized proposal; persistence remains a separate operation.
        return self.gate_state == "authorized" and not self.blocked_fields

    def as_dict(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "candidate_id": self.candidate_id,
            "subject": self.subject,
            "proposed_delta": self.proposed_delta,
            "gate_state": self.gate_state,
            "authorized_fields": list(self.authorized_fields),
            "blocked_fields": list(self.blocked_fields),
            "reasons": list(self.reasons),
            "evidence": list(self.evidence),
            "source_bindings": list(self.source_bindings),
            "canonical_mutation_allowed": self.canonical_mutation_allowed,
        }


def _proposal_id(candidate: ReconciliationCandidate, policy: AuthorityPolicy) -> str:
    payload = {
        "candidate_id": candidate.candidate_id,
        "subject": candidate.subject,
        "delta": candidate.proposed_delta,
        "policy_subject": policy.subject,
    }
    digest = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()[:24]
    return f"proposal:{digest}"


def evaluate_candidate(candidate: ReconciliationCandidate, policy: AuthorityPolicy) -> MutationProposal:
    """Evaluate authority/evidence without mutating canonical state."""
    if candidate.subject != policy.subject:
        raise AuthorityGateError("authority policy subject does not match candidate subject")

    reasons: list[str] = []
    authorized: list[str] = []
    blocked: list[str] = []

    if candidate.routing_state != "ready":
        reasons.append(f"candidate routing state is {candidate.routing_state}")
        blocked.extend(candidate.proposed_delta)
    else:
        source_set = set(candidate.source_bindings)
        evidence_count = len(set(candidate.evidence))
        for field_name in candidate.proposed_delta:
            allowed = set(policy.authoritative_bindings.get(field_name, ()))
            required = policy.required_evidence.get(field_name, 1)
            if field_name in policy.protected_fields and not allowed:
                blocked.append(field_name)
                reasons.append(f"{field_name}: protected field has no configured authority")
            elif allowed and not source_set.intersection(allowed):
                blocked.append(field_name)
                reasons.append(f"{field_name}: source binding is not authoritative")
            elif evidence_count < required:
                blocked.append(field_name)
                reasons.append(f"{field_name}: requires {required} evidence item(s), found {evidence_count}")
            else:
                authorized.append(field_name)

    if blocked and authorized:
        gate_state = "partial"
    elif blocked:
        gate_state = "blocked"
    else:
        gate_state = "authorized"

    return MutationProposal(
        proposal_id=_proposal_id(candidate, policy),
        candidate_id=candidate.candidate_id,
        subject=candidate.subject,
        proposed_delta=dict(candidate.proposed_delta),
        gate_state=gate_state,
        authorized_fields=tuple(authorized),
        blocked_fields=tuple(dict.fromkeys(blocked)),
        reasons=tuple(reasons),
        evidence=tuple(candidate.evidence),
        source_bindings=tuple(candidate.source_bindings),
    )

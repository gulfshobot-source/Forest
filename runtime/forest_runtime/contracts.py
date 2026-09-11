from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .addressing import normalize_address


MUTATION_STATUSES = {
    "proposed",
    "authorized",
    "executing",
    "observed",
    "verified",
    "reconciled",
    "failed",
    "blocked",
}

OBSERVATION_REALITY_STATES = {"observed", "verified", "failed", "unknown"}


class ContractError(ValueError):
    """Raised when a cross-layer contract envelope is invalid."""


def _require_text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{field_name} must be a non-empty string")
    return value.strip()


@dataclass(frozen=True)
class MutationEnvelope:
    intent_id: str
    subject: str
    operation: str
    proposed_delta: dict[str, Any] = field(default_factory=dict)
    requested_by: str = "unknown"
    authority_required: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    capability_required: tuple[str, ...] = ()
    evidence_required: tuple[str, ...] = ()
    status: str = "proposed"

    def __post_init__(self) -> None:
        object.__setattr__(self, "intent_id", _require_text(self.intent_id, "intent_id"))
        object.__setattr__(self, "subject", normalize_address(self.subject))
        object.__setattr__(self, "operation", _require_text(self.operation, "operation"))
        object.__setattr__(self, "requested_by", _require_text(self.requested_by, "requested_by"))
        if self.status not in MUTATION_STATUSES:
            raise ContractError(f"invalid mutation status: {self.status}")
        if not isinstance(self.proposed_delta, dict):
            raise ContractError("proposed_delta must be an object")

    def as_dict(self) -> dict[str, Any]:
        return {
            "intent_id": self.intent_id,
            "subject": self.subject,
            "operation": self.operation,
            "proposed_delta": self.proposed_delta,
            "requested_by": self.requested_by,
            "authority_required": list(self.authority_required),
            "dependencies": list(self.dependencies),
            "capability_required": list(self.capability_required),
            "evidence_required": list(self.evidence_required),
            "status": self.status,
        }


@dataclass(frozen=True)
class ObservationEnvelope:
    observation_id: str
    subject: str
    source_binding: str
    observed_delta: dict[str, Any] = field(default_factory=dict)
    observed_at: str = "unknown"
    reality_state: str = "observed"
    evidence: tuple[str, ...] = ()
    conflicts: tuple[str, ...] = ()
    proposed_reconciliation: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "observation_id", _require_text(self.observation_id, "observation_id"))
        object.__setattr__(self, "subject", normalize_address(self.subject))
        object.__setattr__(self, "source_binding", _require_text(self.source_binding, "source_binding"))
        object.__setattr__(self, "observed_at", _require_text(self.observed_at, "observed_at"))
        if self.reality_state not in OBSERVATION_REALITY_STATES:
            raise ContractError(f"invalid observation reality_state: {self.reality_state}")
        if not isinstance(self.observed_delta, dict):
            raise ContractError("observed_delta must be an object")
        if self.proposed_reconciliation is not None and not isinstance(self.proposed_reconciliation, dict):
            raise ContractError("proposed_reconciliation must be an object or null")

    @property
    def can_self_promote_to_canonical(self) -> bool:
        """Observations can propose reconciliation but never self-promote."""
        return False

    def as_dict(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "subject": self.subject,
            "source_binding": self.source_binding,
            "observed_delta": self.observed_delta,
            "observed_at": self.observed_at,
            "reality_state": self.reality_state,
            "evidence": list(self.evidence),
            "conflicts": list(self.conflicts),
            "proposed_reconciliation": self.proposed_reconciliation,
        }

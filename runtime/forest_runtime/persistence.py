"""Persistence primitives and canonical mutation verification boundary."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from .mutation import CanonicalMutationPlan, MutationExecutionError, apply_plan_to_snapshot
from .registry import LoadedRegistry


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Canonical object must be a JSON object: {path}")
    return value


def save_json(path: str | Path, value: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
    temporary.replace(target)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass(frozen=True)
class MutationReceipt:
    """Evidence that a revision-pinned mutation survived persistence and reread."""
    plan_id: str
    proposal_id: str
    subject: str
    source: str
    before_revision: str | None
    before_digest: str | None
    after_revision: str | None
    after_digest: str | None
    verified_fields: tuple[str, ...]
    receipt_id: str
    state: str = "verified"

    def as_dict(self) -> dict[str, Any]:
        return {
            "receipt_id": self.receipt_id, "plan_id": self.plan_id,
            "proposal_id": self.proposal_id, "subject": self.subject,
            "source": self.source, "before_revision": self.before_revision,
            "before_digest": self.before_digest, "after_revision": self.after_revision,
            "after_digest": self.after_digest, "verified_fields": list(self.verified_fields),
            "state": self.state,
        }


def _receipt_id(plan: CanonicalMutationPlan, after: LoadedRegistry) -> str:
    payload = {
        "plan_id": plan.plan_id, "subject": plan.subject,
        "before_revision": plan.source_revision, "before_digest": plan.source_digest,
        "after_revision": after.source_revision, "after_digest": after.content_digest,
        "changes": plan.changes,
    }
    digest = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()[:24]
    return f"mutation-receipt:{digest}"


def verify_persisted_mutation(
    plan: CanonicalMutationPlan, before: LoadedRegistry, after: LoadedRegistry,
) -> MutationReceipt:
    """Verify an external compare-and-swap canonical write from a fresh reread.

    This performs no write. Store-specific credentials/mutation logic stay outside the
    kernel: an adapter must compare-and-swap using the plan revision/digest and then
    supply the reread. The kernel owns the universal proof contract.
    """
    if not plan.executable:
        raise MutationExecutionError(f"mutation plan is not executable: {plan.state}")
    apply_plan_to_snapshot(plan, before)
    if after.source != plan.source:
        raise MutationExecutionError("canonical source changed across persistence boundary")
    if after.source_revision == plan.source_revision and after.content_digest == plan.source_digest:
        raise MutationExecutionError("canonical source did not advance after mutation")

    record: Mapping[str, Any] = after.resolve(plan.subject)["record"]
    mismatched = tuple(k for k, expected in plan.changes.items() if record.get(k) != expected)
    if mismatched:
        raise MutationExecutionError(
            "canonical reread does not contain planned values: " + ", ".join(mismatched)
        )
    return MutationReceipt(
        plan_id=plan.plan_id, proposal_id=plan.proposal_id, subject=plan.subject,
        source=plan.source, before_revision=plan.source_revision,
        before_digest=plan.source_digest, after_revision=after.source_revision,
        after_digest=after.content_digest, verified_fields=tuple(sorted(plan.changes)),
        receipt_id=_receipt_id(plan, after),
    )

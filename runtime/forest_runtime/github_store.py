"""GitHub provider adapter for the universal canonical-store persistence contract.

The adapter contains no GitHub SDK dependency. An authorized connector supplies the
small transport surface, while this module owns Forest-specific CAS semantics. This
keeps credentials and provider mechanics outside the runtime kernel without creating a
second mutation law.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Mapping, Protocol

from .addressing import parse_address
from .mutation import CanonicalMutationPlan, MutationExecutionError
from .registry import InjectedRegistryAdapter, LoadedRegistry


class GitHubTransport(Protocol):
    """Minimum authorized GitHub transport required by the Forest adapter."""

    def read_text(self, repository: str, path: str, ref: str) -> tuple[str, str, str]:
        """Return (content, commit_revision, content_blob_sha)."""
        ...

    def replace_text(
        self, repository: str, path: str, content: str, blob_sha: str, message: str, branch: str
    ) -> str:
        """Replace one file iff blob_sha is current and return resulting commit revision."""
        ...


def _digest(content: str) -> str:
    return f"sha256:{hashlib.sha256(content.encode('utf-8')).hexdigest()}"


def _locate_record(registry: Mapping[str, Any], subject: str) -> dict[str, Any]:
    address = parse_address(subject)
    if address.scheme != "forest":
        raise MutationExecutionError("GitHub canonical store accepts canonical Forest identities only")

    if address.kind == "forest":
        record = registry.get("forest")
        if isinstance(record, dict) and record.get("id") == address.object_id:
            return record

    collection_by_kind = {
        "tree": "trees", "architecture": "architecture", "vine": "vines", "registry": "registries"
    }
    collection = collection_by_kind.get(address.kind)
    if collection is None:
        raise MutationExecutionError(f"unsupported canonical subject kind: {address.kind}")
    records = registry.get(collection)
    if not isinstance(records, list):
        raise MutationExecutionError(f"canonical collection missing: {collection}")
    matches = [r for r in records if isinstance(r, dict) and r.get("id") == address.object_id]
    if len(matches) != 1:
        raise MutationExecutionError(f"canonical subject must resolve exactly once: {subject}")
    return matches[0]


@dataclass
class GitHubCanonicalStore:
    """Revision-pinned adapter for a canonical registry stored as one GitHub JSON file."""

    transport: GitHubTransport
    repository: str = "gulfshobot-source/the-forest"
    path: str = "data/forest.json"
    branch: str = "main"
    source: str = "gulfshobot-source/the-forest:data/forest.json"

    def load(self) -> LoadedRegistry:
        content, revision, _blob_sha = self.transport.read_text(
            self.repository, self.path, self.branch
        )
        return InjectedRegistryAdapter(
            content=content,
            source=self.source,
            source_revision=revision,
            transport="github-authorized-connector",
        ).load()

    def compare_and_swap(
        self,
        plan: CanonicalMutationPlan,
        expected_revision: str | None,
        expected_digest: str | None,
    ) -> None:
        if not plan.executable:
            raise MutationExecutionError(f"mutation plan is not executable: {plan.state}")
        if plan.source != self.source:
            raise MutationExecutionError("mutation plan targets a different canonical source")

        content, revision, blob_sha = self.transport.read_text(
            self.repository, self.path, self.branch
        )
        if revision != expected_revision or _digest(content) != expected_digest:
            raise MutationExecutionError("GitHub canonical store compare-and-swap rejected stale plan")

        try:
            registry = json.loads(content)
        except json.JSONDecodeError as exc:
            raise MutationExecutionError("GitHub canonical registry is invalid JSON") from exc
        if not isinstance(registry, dict):
            raise MutationExecutionError("GitHub canonical registry must be a JSON object")

        record = _locate_record(registry, plan.subject)
        record.update(plan.changes)
        rendered = json.dumps(registry, indent=2, ensure_ascii=False) + "\n"
        message = f"Forest canonical mutation: {plan.subject} ({plan.plan_id})"
        self.transport.replace_text(
            self.repository, self.path, rendered, blob_sha, message, self.branch
        )

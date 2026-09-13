from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping, Protocol

from .addressing import resolve_address


class RegistryUnavailable(RuntimeError):
    """Raised when the structural authority registry cannot be loaded."""


class RegistryLoader(Protocol):
    def load(self) -> "LoadedRegistry": ...


@dataclass(frozen=True)
class LoadedRegistry:
    registry: Mapping[str, Any]
    source: str
    loaded_at: str
    freshness: str = "live"
    authority: str = "structural-authority"
    source_revision: str | None = None
    content_digest: str | None = None
    transport: str | None = None

    def resolve(self, forest_address: str) -> dict[str, Any]:
        result = dict(resolve_address(forest_address, self.registry))
        result["registry_source"] = self.source
        result["registry_authority"] = self.authority
        result["registry_loaded_at"] = self.loaded_at
        result["freshness"] = self.freshness
        result["registry_source_revision"] = self.source_revision
        result["registry_content_digest"] = self.content_digest
        result["registry_transport"] = self.transport
        return result


def _parse_registry(raw: str) -> Mapping[str, Any]:
    try:
        registry = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RegistryUnavailable(f"UNAVAILABLE: canonical registry is not valid JSON: {exc}") from exc
    if not isinstance(registry, dict) or not isinstance(registry.get("forest"), dict):
        raise RegistryUnavailable("UNAVAILABLE: canonical registry has invalid top-level shape")
    return registry


def _digest(raw: str) -> str:
    return f"sha256:{hashlib.sha256(raw.encode('utf-8')).hexdigest()}"


@dataclass(frozen=True)
class FileRegistryAdapter:
    """Read-only adapter for a checked-out canonical Forest registry.

    The adapter never writes through to the structural authority repository.
    Its output is derived runtime state and is safe to discard/rebuild.
    """

    path: Path
    source: str = "gulfshobot-source/the-forest:data/forest.json"
    source_revision: str | None = None

    def load(self) -> LoadedRegistry:
        try:
            raw = self.path.read_text(encoding="utf-8")
        except OSError as exc:
            raise RegistryUnavailable(f"UNAVAILABLE: canonical registry {self.path}: {exc}") from exc
        registry = _parse_registry(raw)
        return LoadedRegistry(
            registry=registry,
            source=self.source,
            loaded_at=datetime.now(timezone.utc).isoformat(),
            source_revision=self.source_revision,
            content_digest=_digest(raw),
            transport="filesystem-mount",
        )


@dataclass(frozen=True)
class InjectedRegistryAdapter:
    """Read-only transport boundary for registry content supplied by an authorized connector.

    This adapter deliberately accepts content plus provenance instead of teaching the
    runtime how to authenticate to every possible source. The connector remains the
    transport authority; the runtime remains the resolution authority over the supplied
    immutable snapshot. No injected content is promoted or persisted as canonical truth.
    """

    content: str
    source: str
    source_revision: str
    freshness: str = "live"
    transport: str = "authorized-connector"

    def load(self) -> LoadedRegistry:
        registry = _parse_registry(self.content)
        return LoadedRegistry(
            registry=registry,
            source=self.source,
            loaded_at=datetime.now(timezone.utc).isoformat(),
            freshness=self.freshness,
            authority="structural-authority",
            source_revision=self.source_revision,
            content_digest=_digest(self.content),
            transport=self.transport,
        )


def canonical_registry_adapter_from_env() -> FileRegistryAdapter:
    value = os.environ.get("FOREST_CANONICAL_REGISTRY_PATH")
    if not value:
        raise RegistryUnavailable(
            "UNAVAILABLE: FOREST_CANONICAL_REGISTRY_PATH is not configured; "
            "runtime will not silently fall back to a shadow registry"
        )
    return FileRegistryAdapter(
        Path(value),
        source_revision=os.environ.get("FOREST_CANONICAL_REGISTRY_REVISION"),
    )


def resolve_canonical_address(forest_address: str, loader: RegistryLoader | None = None) -> dict[str, Any]:
    adapter = loader or canonical_registry_adapter_from_env()
    return adapter.load().resolve(forest_address)

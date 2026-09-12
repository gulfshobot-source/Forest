from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
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

    def resolve(self, forest_address: str) -> dict[str, Any]:
        result = dict(resolve_address(forest_address, self.registry))
        result["registry_source"] = self.source
        result["registry_authority"] = self.authority
        result["registry_loaded_at"] = self.loaded_at
        result["freshness"] = self.freshness
        return result


@dataclass(frozen=True)
class FileRegistryAdapter:
    """Read-only adapter for a checked-out canonical Forest registry.

    The adapter never writes through to the structural authority repository.
    Its output is derived runtime state and is safe to discard/rebuild.
    """

    path: Path
    source: str = "gulfshobot-source/the-forest:data/forest.json"

    def load(self) -> LoadedRegistry:
        try:
            raw = self.path.read_text(encoding="utf-8")
            registry = json.loads(raw)
        except (OSError, json.JSONDecodeError) as exc:
            raise RegistryUnavailable(f"UNAVAILABLE: canonical registry {self.path}: {exc}") from exc
        if not isinstance(registry, dict) or not isinstance(registry.get("forest"), dict):
            raise RegistryUnavailable("UNAVAILABLE: canonical registry has invalid top-level shape")
        loaded_at = datetime.now(timezone.utc).isoformat()
        return LoadedRegistry(registry=registry, source=self.source, loaded_at=loaded_at)


def canonical_registry_adapter_from_env() -> FileRegistryAdapter:
    value = os.environ.get("FOREST_CANONICAL_REGISTRY_PATH")
    if not value:
        raise RegistryUnavailable(
            "UNAVAILABLE: FOREST_CANONICAL_REGISTRY_PATH is not configured; "
            "runtime will not silently fall back to a shadow registry"
        )
    return FileRegistryAdapter(Path(value))


def resolve_canonical_address(forest_address: str, loader: RegistryLoader | None = None) -> dict[str, Any]:
    adapter = loader or canonical_registry_adapter_from_env()
    return adapter.load().resolve(forest_address)

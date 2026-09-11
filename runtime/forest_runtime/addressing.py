from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping
from urllib.parse import urlparse


CANONICAL_SCHEME = "forest"
PROVISIONAL_SCHEME = "forest+provisional"


class AddressError(ValueError):
    """Raised when a Forest address cannot be parsed or resolved."""


@dataclass(frozen=True)
class ForestAddress:
    scheme: str
    kind: str
    object_id: str

    @property
    def canonical(self) -> str:
        return f"{self.scheme}://{self.kind}/{self.object_id}"


def parse_address(value: str) -> ForestAddress:
    parsed = urlparse(value)
    if parsed.scheme not in {CANONICAL_SCHEME, PROVISIONAL_SCHEME}:
        raise AddressError("INVALID_ADDRESS: unsupported Forest address scheme")
    if not parsed.netloc:
        raise AddressError("INVALID_ADDRESS: missing object kind")
    object_id = parsed.path.strip("/")
    if not object_id or "/" in object_id:
        raise AddressError("INVALID_ADDRESS: address must contain exactly one object id")
    if parsed.params or parsed.query or parsed.fragment:
        raise AddressError("INVALID_ADDRESS: params, query, and fragment are not part of identity")
    return ForestAddress(parsed.scheme, parsed.netloc, object_id)


def normalize_address(value: str) -> str:
    return parse_address(value).canonical


def address_for(kind: str, object_id: str, *, provisional: bool = False) -> str:
    if not kind or not object_id or "/" in kind or "/" in object_id:
        raise AddressError("INVALID_ADDRESS: kind and id must be non-empty path-safe segments")
    scheme = PROVISIONAL_SCHEME if provisional else CANONICAL_SCHEME
    return ForestAddress(scheme, kind, object_id).canonical


def _iter_registry_objects(registry: Mapping[str, Any]) -> Iterable[dict[str, Any]]:
    forest = registry.get("forest")
    if isinstance(forest, dict) and forest.get("id"):
        yield {**forest, "kind": forest.get("kind", "forest")}

    for collection, default_kind in (
        ("trees", "tree"),
        ("architecture", "architecture"),
        ("vines", "vine"),
        ("registries", "registry"),
    ):
        values = registry.get(collection, [])
        if not isinstance(values, list):
            continue
        for value in values:
            if isinstance(value, dict) and value.get("id"):
                yield {**value, "kind": value.get("kind", default_kind)}


def build_identity_index(registry: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    """Build a disposable lookup index from canonical registry records.

    The returned index is derived state. It must never be persisted as a competing
    canonical object graph.
    """
    index: dict[str, dict[str, Any]] = {}
    for record in _iter_registry_objects(registry):
        address = address_for(str(record["kind"]), str(record["id"]))
        if address in index:
            raise AddressError(f"AMBIGUOUS: duplicate canonical identity {address}")
        index[address] = record
    return index


def resolve_address(value: str, registry: Mapping[str, Any]) -> dict[str, Any]:
    address = parse_address(value)
    if address.scheme == PROVISIONAL_SCHEME:
        raise AddressError("NOT_FOUND: provisional identities require an explicit provisional registry")

    index = build_identity_index(registry)
    canonical = address.canonical
    record = index.get(canonical)
    if record is None:
        raise AddressError(f"NOT_FOUND: {canonical}")

    canonical_home = record.get("canonical_path")
    reality_state = record.get("reality_state") or record.get("state") or "unknown"
    operational_state = record.get("operational_state")

    return {
        "forest_address": canonical,
        "canonical_id": record["id"],
        "kind": record["kind"],
        "canonical_home": canonical_home,
        "authority": "canonical",
        "reality_state": reality_state,
        "operational_state": operational_state,
        "freshness": "live",
        "record": record,
    }

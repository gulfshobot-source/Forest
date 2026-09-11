import pytest

from forest_runtime.addressing import (
    AddressError,
    address_for,
    build_identity_index,
    normalize_address,
    parse_address,
    resolve_address,
)


@pytest.fixture
def registry():
    return {
        "forest": {"id": "forest", "name": "The Forest", "kind": "forest", "state": "operational-prototype"},
        "trees": [
            {"id": "irrigation", "name": "Irrigation", "kind": "tree", "canonical_path": "trees/irrigation/README.md", "state": "foundation"}
        ],
        "architecture": [
            {
                "id": "foundational-substrate",
                "name": "Foundational Substrate",
                "canonical_path": "architecture/FOUNDATIONAL_SUBSTRATE.md",
                "state": "authoritative-living",
            }
        ],
        "vines": [
            {"id": "vine-substrate-forest", "from": "foundational-substrate", "to": "forest", "label": "Substrate ↔ Forest"}
        ],
    }


def test_parse_and_normalize_address():
    address = parse_address("forest://tree/irrigation")
    assert address.kind == "tree"
    assert address.object_id == "irrigation"
    assert normalize_address("forest://tree/irrigation") == "forest://tree/irrigation"


def test_address_for_supports_provisional_identity():
    assert address_for("experiment", "thread-map", provisional=True) == "forest+provisional://experiment/thread-map"


def test_resolver_uses_canonical_registry_identity(registry):
    result = resolve_address("forest://architecture/foundational-substrate", registry)
    assert result["canonical_id"] == "foundational-substrate"
    assert result["canonical_home"] == "architecture/FOUNDATIONAL_SUBSTRATE.md"
    assert result["authority"] == "canonical"
    assert result["reality_state"] == "authoritative-living"


def test_identity_index_is_derived_not_separate_schema(registry):
    index = build_identity_index(registry)
    assert set(index) == {
        "forest://forest/forest",
        "forest://tree/irrigation",
        "forest://architecture/foundational-substrate",
        "forest://vine/vine-substrate-forest",
    }


def test_unknown_address_fails_explicitly(registry):
    with pytest.raises(AddressError, match="NOT_FOUND"):
        resolve_address("forest://tree/missing", registry)


def test_provisional_address_cannot_silently_resolve_as_canonical(registry):
    with pytest.raises(AddressError, match="provisional identities"):
        resolve_address("forest+provisional://experiment/thread-map", registry)


def test_duplicate_identity_is_ambiguous():
    duplicate = {
        "forest": {"id": "forest", "kind": "forest"},
        "trees": [
            {"id": "same", "kind": "tree"},
            {"id": "same", "kind": "tree"},
        ],
    }
    with pytest.raises(AddressError, match="AMBIGUOUS"):
        build_identity_index(duplicate)


@pytest.mark.parametrize(
    "value",
    [
        "https://tree/irrigation",
        "forest:///irrigation",
        "forest://tree/",
        "forest://tree/a/b",
        "forest://tree/irrigation?copy=1",
    ],
)
def test_invalid_addresses_fail(value):
    with pytest.raises(AddressError, match="INVALID_ADDRESS"):
        parse_address(value)

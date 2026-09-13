from forest_runtime.bindings import binding_index, derive_bindings


def test_canonical_document_binding_is_derived_not_hand_maintained():
    record = {
        "id": "agentic-harness",
        "canonical_path": "architecture/AGENTIC_HARNESS.md",
        "state": "authoritative",
    }
    bindings = derive_bindings(record)
    assert bindings == [{
        "binding_id": "github-canonical-document",
        "system": "github",
        "role": "canonical-representation",
        "locator": "gulfshobot-source/the-forest:architecture/AGENTIC_HARNESS.md",
        "authority_scope": ["document-content"],
        "freshness": "live",
        "verified_at": None,
        "capabilities": ["read"],
    }]


def test_record_can_have_canonical_and_experimental_bindings_without_authority_escalation():
    record = {
        "id": "foundational-substrate",
        "canonical_path": "architecture/FOUNDATIONAL_SUBSTRATE.md",
        "prototype": "gulfshobot-source/Forest:experiments/substrate/",
    }
    bindings = derive_bindings(record)
    roles = {binding["role"] for binding in bindings}
    assert roles == {"canonical-representation", "working-copy"}
    prototype = next(binding for binding in bindings if binding["binding_id"] == "github-prototype")
    assert prototype["locator"] == "gulfshobot-source/Forest:experiments/substrate/"
    assert prototype["authority_scope"] == ["experimental-implementation"]
    assert prototype["capabilities"] == ["read"]


def test_data_paths_generate_reconstructable_bindings():
    record = {
        "id": "world-engine",
        "canonical_path": "architecture/WORLD_ENGINE.md",
        "data_paths": ["data/world.json", "data/live_state.json", "data/terrain.json"],
    }
    bindings = derive_bindings(record)
    data = [binding for binding in bindings if "canonical-data" in binding["binding_id"]]
    assert [binding["locator"] for binding in data] == [
        "gulfshobot-source/the-forest:data/world.json",
        "gulfshobot-source/the-forest:data/live_state.json",
        "gulfshobot-source/the-forest:data/terrain.json",
    ]


def test_binding_index_is_disposable_projection_keyed_by_canonical_id():
    index = binding_index([
        {"id": "connectors", "path": "data/connectors.json"},
        {"id": "empty"},
    ])
    assert index["connectors"][0]["locator"] == "gulfshobot-source/the-forest:data/connectors.json"
    assert index["empty"] == []

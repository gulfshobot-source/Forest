import json
import os
from pathlib import Path

import pytest

from forest_runtime.registry import (
    FileRegistryAdapter,
    RegistryUnavailable,
    canonical_registry_adapter_from_env,
    resolve_canonical_address,
)


def test_file_adapter_resolves_canonical_identity(tmp_path: Path):
    registry_path = tmp_path / "forest.json"
    registry_path.write_text(json.dumps({
        "forest": {"id": "forest", "name": "The Forest", "kind": "forest", "state": "operational"},
        "trees": [{"id": "irrigation", "name": "Irrigation", "kind": "tree", "state": "foundation", "canonical_path": "trees/irrigation/README.md"}],
        "architecture": [], "registries": [], "vines": []
    }), encoding="utf-8")

    result = resolve_canonical_address("forest://tree/irrigation", FileRegistryAdapter(registry_path))
    assert result["canonical_id"] == "irrigation"
    assert result["canonical_home"] == "trees/irrigation/README.md"
    assert result["registry_authority"] == "structural-authority"
    assert result["registry_source"] == "gulfshobot-source/the-forest:data/forest.json"
    assert result["freshness"] == "live"


def test_missing_registry_is_explicitly_unavailable(tmp_path: Path):
    with pytest.raises(RegistryUnavailable, match="UNAVAILABLE"):
        FileRegistryAdapter(tmp_path / "missing.json").load()


def test_env_adapter_never_silently_uses_shadow_registry(monkeypatch):
    monkeypatch.delenv("FOREST_CANONICAL_REGISTRY_PATH", raising=False)
    with pytest.raises(RegistryUnavailable, match="shadow registry"):
        canonical_registry_adapter_from_env()


@pytest.mark.skipif(
    "FOREST_CANONICAL_REGISTRY_PATH" not in os.environ,
    reason="live structural-authority registry not mounted in this execution environment",
)
def test_live_canonical_registry_resolves_known_objects():
    registry_path = Path(os.environ["FOREST_CANONICAL_REGISTRY_PATH"])
    adapter = FileRegistryAdapter(registry_path)

    expected = {
        "forest://forest/forest": None,
        "forest://tree/irrigation": "trees/irrigation/README.md",
        "forest://architecture/foundational-substrate": "architecture/FOUNDATIONAL_SUBSTRATE.md",
        "forest://architecture/agentic-harness": "architecture/AGENTIC_HARNESS.md",
        "forest://architecture/world-engine": "architecture/WORLD_ENGINE.md",
        "forest://registry/connectors": None,
    }
    for address, canonical_home in expected.items():
        result = resolve_canonical_address(address, adapter)
        assert result["forest_address"] == address
        assert result["canonical_home"] == canonical_home
        assert result["registry_authority"] == "structural-authority"

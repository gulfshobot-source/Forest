from copy import deepcopy
from pathlib import Path
import json

import pytest

from forest_runtime.validation import ValidationFailure, validate_canonical_state, validate_warrant

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "kernel" / "schemas"


def canonical_state():
    return json.loads((ROOT / "state" / "canonical-state.json").read_text(encoding="utf-8"))


def test_repository_canonical_state_validates():
    validate_canonical_state(canonical_state(), SCHEMAS)


def test_missing_required_canonical_field_fails():
    state = canonical_state()
    del state["project"]
    with pytest.raises(ValidationFailure):
        validate_canonical_state(state, SCHEMAS)


def test_invalid_warrant_fails():
    warrant = deepcopy(canonical_state()["warrant"])
    warrant["recovery"]["max_retries"] = -1
    with pytest.raises(ValidationFailure):
        validate_warrant(warrant, SCHEMAS)


def test_invalid_project_status_fails():
    state = canonical_state()
    state["project"]["status"] = "invalid-status"
    with pytest.raises(ValidationFailure):
        validate_canonical_state(state, SCHEMAS)

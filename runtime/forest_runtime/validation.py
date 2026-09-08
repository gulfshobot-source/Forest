"""Canonical JSON Schema validation at Forest runtime boundaries."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


@dataclass(frozen=True)
class ValidationFailure(ValueError):
    schema: str
    path: str
    message: str

    def __str__(self) -> str:
        location = self.path or "<root>"
        return f"{self.schema} validation failed at {location}: {self.message}"


def default_schema_root() -> Path:
    return Path(__file__).resolve().parents[2] / "kernel" / "schemas"


def _load_schema(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        schema = json.load(handle)
    if not isinstance(schema, dict):
        raise ValueError(f"Schema must be a JSON object: {path}")
    Draft202012Validator.check_schema(schema)
    return schema


def _error_path(error: Any) -> str:
    parts = [str(part) for part in error.absolute_path]
    return ".".join(parts)


def _raise_first(schema_name: str, validator: Draft202012Validator, value: Any) -> None:
    errors = sorted(validator.iter_errors(value), key=lambda item: list(item.absolute_path))
    if errors:
        error = errors[0]
        raise ValidationFailure(schema_name, _error_path(error), error.message)


def validate_warrant(warrant: dict[str, Any], schema_root: str | Path | None = None) -> None:
    root = Path(schema_root) if schema_root is not None else default_schema_root()
    schema = _load_schema(root / "production-warrant.schema.json")
    _raise_first("production-warrant", Draft202012Validator(schema), warrant)


def validate_canonical_state(state: dict[str, Any], schema_root: str | Path | None = None) -> None:
    """Validate canonical state and its embedded production warrant.

    The warrant schema is loaded once and embedded into a transient copy of the
    canonical schema. This resolves Forest's custom URI without introducing a
    second persistent schema registry or duplicating canonical definitions.
    """
    root = Path(schema_root) if schema_root is not None else default_schema_root()
    state_schema = _load_schema(root / "canonical-state.schema.json")
    warrant_schema = _load_schema(root / "production-warrant.schema.json")

    resolved = deepcopy(state_schema)
    resolved.setdefault("properties", {})["warrant"] = warrant_schema
    _raise_first("canonical-state", Draft202012Validator(resolved), state)

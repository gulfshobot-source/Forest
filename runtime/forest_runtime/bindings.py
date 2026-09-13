from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Iterable, Mapping


@dataclass(frozen=True)
class Binding:
    binding_id: str
    system: str
    role: str
    locator: str
    authority_scope: tuple[str, ...]
    freshness: str
    verified_at: str | None
    capabilities: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["authority_scope"] = list(self.authority_scope)
        value["capabilities"] = list(self.capabilities)
        return value


def _github_binding(binding_id: str, role: str, repo: str, path: str, *, authority_scope: tuple[str, ...]) -> Binding:
    return Binding(
        binding_id=binding_id,
        system="github",
        role=role,
        locator=f"{repo}:{path}",
        authority_scope=authority_scope,
        freshness="live",
        verified_at=None,
        capabilities=("read",),
    )


def derive_bindings(record: Mapping[str, Any], *, structural_repo: str = "gulfshobot-source/the-forest") -> list[dict[str, Any]]:
    """Derive disposable physical bindings from a canonical registry record.

    Bindings are projections over canonical fields. They are reconstructable and must
    not be persisted as a competing object registry.
    """
    bindings: list[Binding] = []
    canonical_path = record.get("canonical_path")
    if isinstance(canonical_path, str) and canonical_path:
        bindings.append(
            _github_binding(
                "github-canonical-document",
                "canonical-representation",
                structural_repo,
                canonical_path,
                authority_scope=("document-content",),
            )
        )

    data_path = record.get("data_path")
    if isinstance(data_path, str) and data_path:
        bindings.append(
            _github_binding(
                "github-canonical-data",
                "canonical-representation",
                structural_repo,
                data_path,
                authority_scope=("structured-data",),
            )
        )

    data_paths = record.get("data_paths")
    if isinstance(data_paths, list):
        for index, path in enumerate(data_paths):
            if isinstance(path, str) and path:
                bindings.append(
                    _github_binding(
                        f"github-canonical-data-{index + 1}",
                        "canonical-representation",
                        structural_repo,
                        path,
                        authority_scope=("structured-data",),
                    )
                )

    implementation_path = record.get("implementation_path")
    if isinstance(implementation_path, str) and implementation_path:
        bindings.append(
            _github_binding(
                "github-implementation",
                "working-copy",
                structural_repo,
                implementation_path,
                authority_scope=("implementation",),
            )
        )

    prototype = record.get("prototype")
    if isinstance(prototype, str) and prototype:
        if ":" in prototype:
            repo, path = prototype.split(":", 1)
        else:
            repo, path = structural_repo, prototype
        bindings.append(
            _github_binding(
                "github-prototype",
                "working-copy",
                repo,
                path,
                authority_scope=("experimental-implementation",),
            )
        )

    path = record.get("path")
    if isinstance(path, str) and path and not canonical_path:
        bindings.append(
            _github_binding(
                "github-canonical-registry",
                "canonical-representation",
                structural_repo,
                path,
                authority_scope=("structured-data",),
            )
        )

    return [binding.to_dict() for binding in bindings]


def binding_index(records: Iterable[Mapping[str, Any]], *, structural_repo: str = "gulfshobot-source/the-forest") -> dict[str, list[dict[str, Any]]]:
    """Create a disposable id-keyed binding index for a sequence of canonical records."""
    result: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        object_id = record.get("id")
        if object_id:
            result[str(object_id)] = derive_bindings(record, structural_repo=structural_repo)
    return result

"""Host-injected bridge from an authorized GitHub connector to Forest's store adapter.

The Forest runtime must not own connector credentials or depend on a specific SDK. A
host that already has an authorized GitHub connection injects two narrow callables;
this bridge validates their outputs and exposes the GitHubTransport contract used by
GitHubCanonicalStore.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .mutation import MutationExecutionError

ReadConnector = Callable[[str, str, str], tuple[str, str, str]]
WriteConnector = Callable[[str, str, str, str, str, str], str]


def _nonempty(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MutationExecutionError(f"connector returned invalid {label}")
    return value


@dataclass(frozen=True)
class GitHubConnectorTransport:
    """Validate a host-authorized connector at the runtime/provider boundary."""

    reader: ReadConnector
    writer: WriteConnector

    def read_text(self, repository: str, path: str, ref: str) -> tuple[str, str, str]:
        result = self.reader(repository, path, ref)
        if not isinstance(result, tuple) or len(result) != 3:
            raise MutationExecutionError("connector read must return (content, revision, blob_sha)")
        content, revision, blob_sha = result
        if not isinstance(content, str):
            raise MutationExecutionError("connector returned invalid content")
        return content, _nonempty(revision, "revision"), _nonempty(blob_sha, "blob_sha")

    def replace_text(
        self,
        repository: str,
        path: str,
        content: str,
        blob_sha: str,
        message: str,
        branch: str,
    ) -> str:
        # blob_sha is deliberately mandatory: the host may not downgrade CAS to an
        # unconditional overwrite without violating the Forest mutation law.
        _nonempty(blob_sha, "blob_sha precondition")
        revision = self.writer(repository, path, content, blob_sha, message, branch)
        return _nonempty(revision, "post-write revision")

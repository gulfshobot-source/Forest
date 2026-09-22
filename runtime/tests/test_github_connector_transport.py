import pytest

from forest_runtime.github_connector_transport import GitHubConnectorTransport
from forest_runtime.mutation import MutationExecutionError


def test_bridge_preserves_connector_cas_inputs_and_revision():
    calls = []
    transport = GitHubConnectorTransport(
        reader=lambda repo, path, ref: ("{}\n", "rev-1", "blob-1"),
        writer=lambda repo, path, content, blob, message, branch: calls.append(
            (repo, path, content, blob, message, branch)
        ) or "rev-2",
    )

    assert transport.read_text("owner/repo", "data/forest.json", "main") == (
        "{}\n", "rev-1", "blob-1"
    )
    assert transport.replace_text(
        "owner/repo", "data/forest.json", "{\"x\": 1}\n", "blob-1", "change", "main"
    ) == "rev-2"
    assert calls[0][3] == "blob-1"


def test_bridge_rejects_malformed_read_contract():
    transport = GitHubConnectorTransport(
        reader=lambda repo, path, ref: ("{}", "rev-1"),  # type: ignore[arg-type]
        writer=lambda *args: "rev-2",
    )
    with pytest.raises(MutationExecutionError, match="connector read must return"):
        transport.read_text("owner/repo", "data/forest.json", "main")


@pytest.mark.parametrize("result", [("{}", "", "blob"), ("{}", "rev", "")])
def test_bridge_rejects_missing_revision_or_blob(result):
    transport = GitHubConnectorTransport(
        reader=lambda repo, path, ref: result,
        writer=lambda *args: "rev-2",
    )
    with pytest.raises(MutationExecutionError, match="connector returned invalid"):
        transport.read_text("owner/repo", "data/forest.json", "main")


def test_bridge_rejects_write_without_post_write_revision():
    transport = GitHubConnectorTransport(
        reader=lambda repo, path, ref: ("{}", "rev-1", "blob-1"),
        writer=lambda *args: "",
    )
    with pytest.raises(MutationExecutionError, match="post-write revision"):
        transport.replace_text("owner/repo", "data/forest.json", "{}", "blob-1", "change", "main")

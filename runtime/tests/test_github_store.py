import json

import pytest

from forest_runtime.authority import MutationProposal
from forest_runtime.github_store import GitHubCanonicalStore
from forest_runtime.mutation import MutationExecutionError, prepare_mutation
from forest_runtime.persistence import execute_verified_mutation

SUBJECT = "forest://architecture/downstairs-connector-fabric"
SOURCE = "gulfshobot-source/the-forest:data/forest.json"


def registry(state="authoritative-living"):
    return json.dumps({
        "forest": {"id": "forest", "kind": "forest"},
        "architecture": [{"id": "downstairs-connector-fabric", "state": state}],
    })


class MemoryGitHubTransport:
    def __init__(self, content, revision="rev-1"):
        self.content = content
        self.revision = revision
        self.blob_sha = "blob-1"
        self.writes = []

    def read_text(self, repository, path, ref):
        return self.content, self.revision, self.blob_sha

    def replace_text(self, repository, path, content, blob_sha, message, branch):
        if blob_sha != self.blob_sha:
            raise MutationExecutionError("provider blob precondition failed")
        self.writes.append((repository, path, blob_sha, message, branch))
        self.content = content
        self.revision = "rev-2"
        self.blob_sha = "blob-2"
        return self.revision


def proposal():
    return MutationProposal(
        proposal_id="proposal:github", candidate_id="reconcile:github", subject=SUBJECT,
        proposed_delta={"state": "verified"}, gate_state="authorized",
        authorized_fields=("state",), evidence=("evidence-1",),
        source_bindings=("github://connector/structural",),
    )


def test_github_store_executes_through_universal_verified_mutation_kernel():
    transport = MemoryGitHubTransport(registry())
    store = GitHubCanonicalStore(transport)
    before = store.load()
    plan = prepare_mutation(proposal(), before, {"state": "authoritative-living"})

    receipt = execute_verified_mutation(plan, store)

    assert receipt.state == "verified"
    assert receipt.before_revision == "rev-1"
    assert receipt.after_revision == "rev-2"
    assert json.loads(transport.content)["architecture"][0]["state"] == "verified"
    assert len(transport.writes) == 1


def test_github_store_rejects_revision_drift_before_provider_write():
    transport = MemoryGitHubTransport(registry())
    store = GitHubCanonicalStore(transport)
    before = store.load()
    plan = prepare_mutation(proposal(), before, {"state": "authoritative-living"})
    transport.revision = "rev-external"

    with pytest.raises(MutationExecutionError, match="revision/digest changed"):
        execute_verified_mutation(plan, store)
    assert transport.writes == []


def test_github_store_rejects_digest_drift_even_when_revision_is_reused():
    transport = MemoryGitHubTransport(registry())
    store = GitHubCanonicalStore(transport)
    before = store.load()
    plan = prepare_mutation(proposal(), before, {"state": "authoritative-living"})
    transport.content = registry("changed-outside-runtime")

    with pytest.raises(MutationExecutionError, match="revision/digest changed"):
        execute_verified_mutation(plan, store)
    assert transport.writes == []


def test_github_store_rejects_plan_for_different_source():
    transport = MemoryGitHubTransport(registry())
    store = GitHubCanonicalStore(transport)
    before = store.load()
    plan = prepare_mutation(proposal(), before, {"state": "authoritative-living"})
    other = GitHubCanonicalStore(transport, source="other/repo:data/forest.json")

    with pytest.raises(MutationExecutionError, match="different canonical source"):
        other.compare_and_swap(plan, plan.source_revision, plan.source_digest)
    assert transport.writes == []

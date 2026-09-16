from forest_runtime.authority import AuthorityGateError, AuthorityPolicy, evaluate_candidate
from forest_runtime.reconciliation import ReconciliationCandidate


SUBJECT = "forest://architecture/downstairs-connector-fabric"


def candidate(**kwargs):
    values = {
        "candidate_id": "reconcile:test",
        "subject": SUBJECT,
        "source_bindings": ("github://connector/a",),
        "observation_ids": ("obs-1",),
        "event_ids": ("sync-1",),
        "proposed_delta": {"operational_state": "verified"},
        "routing_state": "ready",
        "evidence": ("evidence-1",),
    }
    values.update(kwargs)
    return ReconciliationCandidate(**values)


def policy(**kwargs):
    values = {
        "subject": SUBJECT,
        "authoritative_bindings": {"operational_state": ("github://connector/a",)},
        "required_evidence": {"operational_state": 1},
    }
    values.update(kwargs)
    return AuthorityPolicy(**values)


def test_authoritative_candidate_becomes_mutation_proposal_not_mutation():
    proposal = evaluate_candidate(candidate(), policy())
    assert proposal.gate_state == "authorized"
    assert proposal.authorized_fields == ("operational_state",)
    assert proposal.blocked_fields == ()
    assert proposal.canonical_mutation_allowed is True
    assert proposal.subject == SUBJECT
    assert proposal.evidence == ("evidence-1",)


def test_non_authoritative_source_is_blocked():
    proposal = evaluate_candidate(
        candidate(source_bindings=("github://connector/b",)),
        policy(),
    )
    assert proposal.gate_state == "blocked"
    assert proposal.canonical_mutation_allowed is False
    assert proposal.blocked_fields == ("operational_state",)


def test_conflicted_candidate_cannot_pass_gate():
    proposal = evaluate_candidate(candidate(routing_state="conflicted"), policy())
    assert proposal.gate_state == "blocked"
    assert proposal.canonical_mutation_allowed is False


def test_evidence_requirement_is_enforced():
    proposal = evaluate_candidate(
        candidate(evidence=("only-one",)),
        policy(required_evidence={"operational_state": 2}),
    )
    assert proposal.gate_state == "blocked"
    assert "requires 2 evidence item(s)" in proposal.reasons[0]


def test_field_scoped_authority_can_partially_authorize_delta():
    proposal = evaluate_candidate(
        candidate(proposed_delta={"operational_state": "verified", "owner": "runtime"}),
        policy(
            authoritative_bindings={
                "operational_state": ("github://connector/a",),
                "owner": ("github://connector/structural",),
            }
        ),
    )
    assert proposal.gate_state == "partial"
    assert proposal.authorized_fields == ("operational_state",)
    assert proposal.blocked_fields == ("owner",)
    assert proposal.canonical_mutation_allowed is False


def test_policy_subject_mismatch_fails_closed():
    try:
        evaluate_candidate(candidate(), policy(subject="forest://other/object"))
    except AuthorityGateError:
        pass
    else:
        raise AssertionError("subject mismatch must fail closed")

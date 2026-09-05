# Autonomous Loop Contract v0.1

## State transition

`S(t) + W(t) + Inputs(t) → Task(t) → Artifact(t) → Tests(t) → S(t+1) + W(t+1)`

## Every iteration MUST

1. Load only the canonical state required to safely determine the next operation.
2. Reconcile state against completion criteria and dependencies.
3. Select the highest-leverage unblocked task.
4. Execute at the maximum appropriate depth permitted by resource and safety policy.
5. Test the artifact and relevant regressions.
6. Record measured output and uncertainty.
7. Persist a versioned state delta.
8. Run a gap scan.
9. Generate the next Production Warrant.
10. Continue unless DONE, blocked by an irreducible human decision, or prohibited by permissions/safety rules.

## Recovery

If execution fails: capture failure → classify → identify smallest repair → repair → retest → preserve failure evidence → continue.

If state is inconsistent: stop mutation, reconstruct from last verified state and change history, validate, then resume.

If context is insufficient: retrieve the minimum missing canonical objects rather than asking the user to restate the project.

## Human gate

A human gate is valid only when the required choice is genuinely authorial, legal/rights-sensitive, permission-sensitive, or otherwise impossible to infer from the canonical project rules. Complete every unblocked task before presenting the gate.

## Observability

Each iteration should emit concise machine-readable telemetry sufficient to reconstruct:

- current position
- task selected and why
- artifacts changed
- tests run/results
- measured progress
- blockers
- next warrant
- state version

The human-facing UI may expose this as WHERE YOU ARE and POSITION AFTER THIS PASS.

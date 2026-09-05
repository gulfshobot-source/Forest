# AI-Native Protocol v0.1

This is an intermediate representation, not a human language. Human requests compile into it; agents execute it; results compile back into human-readable status.

## Primitive classes

`@X` = stable reference to canonical object X.

`+` create; `Δ` modify; `?` inspect; `✓` verify; `↻` continue; `→` sequence/flow; `⊕` merge; `⊗` invalidate; `!` priority; `@` reference; `[]` parameters; `{}` state payload.

## Core operations

- `↻ @POS` — resume from canonical production position.
- `? @STATE` — inspect state required for current operation.
- `! ARGMAX[utility,impact,unblocked,cost]` — select next task.
- `+ @ARTIFACT` — create artifact.
- `✓ @TEST` — execute verification.
- `Δ @STATE` — persist state delta.
- `→ @WARRANT'` — generate next warrant.

## Canonical continuation form

`↻ @POS → RECONCILE → !ARGMAX → EXEC → ✓ → MEASURE → GAP → Δ@STATE → +@WARRANT → ↻`

## Compression rules

1. Never compress away a dependency, constraint, uncertainty, provenance edge, acceptance criterion, or safety boundary.
2. Replace repetition with stable references.
3. Replace repeated full state with immutable base + deltas.
4. Replace repeated procedures with reusable validated primitives.
5. Prefer generative representations when reconstruction is deterministic and lossless for the required behavior.
6. Expand references only when required by the active operation.
7. Preserve an audit trail from every compressed representation to its source state.

## Important boundary

This protocol reduces representational redundancy. It does not claim that fewer protocol tokens automatically reduce underlying model FLOPs. Deeper compute savings require runtime/model techniques such as caching, sparse routing, adaptive depth, latent state reuse, or specialized model architecture.

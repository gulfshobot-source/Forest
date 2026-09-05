# Forest Bootstrap Specification v0.1

## Mission

Build and operate a persistent AI production system that turns a supplied project definition and material dump into a verified collection of finished artifacts with minimal recurring human direction.

## Bootstrap inputs

1. Project specification.
2. Material dump: documents, PDFs, notes, images, audio, code, datasets, references, examples, constraints, rights/provenance information.
3. Execution environment and permitted tools.

## Canonical state

The runtime MUST maintain a canonical state containing:

- Collection Atlas
- Production Position Map
- Master Completion Ledger
- Project Memory
- active Genome/Blueprints
- dependency graph
- source/provenance graph
- procedure library
- quality gates
- unresolved decisions
- current Production Warrant
- audit/change history

## Execution law

The next task is selected from all legal, unblocked tasks using a deterministic priority function based on leverage, dependency impact, urgency, confidence, and cost.

A task is not complete merely because generated text exists. Completion requires its acceptance criteria to pass and the resulting state to be persisted.

## Recursive optimization law

Apply the same optimization principle at every layer:

> Preserve complete operative meaning and capability while eliminating redundant representation, repeated computation, and unnecessary regeneration.

Prefer structural/generative representations, stable references, cached validated results, deltas, reusable primitives, and sparse execution where they preserve behavior and quality.

## Loop

OBSERVE → RECONCILE → SELECT → EXECUTE → TEST → VERIFY → COMMIT → MEASURE → GAP-SCAN → REPLAN → CONTINUE.

Failures route to diagnosis and repair. Human escalation is limited to decisions that cannot be inferred from canonical state and explicit rules.

## Modes

- RUN: continue autonomously within granted permissions.
- SUPERVISE: continue while surfacing significant events.
- AUTHORIZE: pause only at defined human-decision gates.

## Completion contract

DONE requires all required artifacts, tests, quality gates, dependencies, provenance records, accessibility requirements, and release requirements to pass. No silent compression, no false completion credit, and no unresolved critical blockers.

## User protocol

After bootstrap, `continue` is sufficient to advance the system. The user should not need to restate context or paste warrants.

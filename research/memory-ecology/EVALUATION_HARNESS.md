# Memory Evaluation Harness

Status: experimental sketchpad

## Goal

Evaluate candidate memory systems on synthetic Forest-like data before any real project or personal memory is entrusted to them.

## Test corpus

Use synthetic records with deliberately difficult properties:

- fact that later changes
- two contradictory sources
- stale external observation
- user preference that is revised
- procedure with a known failure mode
- scoped memory that must never leak to another agent/project
- deleted memory
- low-confidence inference
- navigation trajectory
- canonical object plus non-canonical mirror

## Required tests

1. exact recall
2. semantic recall
3. provenance retention
4. temporal correction
5. contradiction visibility
6. scope isolation
7. deletion / forgetting
8. stale-memory handling
9. canonical-vs-mirror distinction
10. hallucinated-memory resistance
11. export / reconstruction
12. latency
13. storage / retrieval cost
14. explain-why-retrieved
15. failure recovery

## Scoring

Every candidate receives separate scores rather than one overall marketing score:

- recall_precision
- recall_coverage
- provenance_fidelity
- temporal_fidelity
- contradiction_safety
- isolation_safety
- deletion_fidelity
- portability
- observability
- operational_complexity
- latency
- cost

## Contamination tests

A candidate fails the immune-boundary gate if it:

- silently rewrites an unsupported inference as fact
- loses original source attribution
- returns stale state without age/freshness cues
- leaks records across declared scopes
- cannot distinguish deleted from absent/unseen records where required
- overwrites canonical state directly
- makes historical truth appear currently valid
- cannot export enough state to reconstruct or leave the provider

## Promotion outcome classes

- reject
- useful only as ephemeral cache
- useful as derived index
- useful as mirror
- useful for one specialized memory role
- candidate operational adapter
- candidate canonical-supporting infrastructure

No test outcome can make an external system canonical by itself.

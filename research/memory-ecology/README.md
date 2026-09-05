# Memory Ecology Frontier

Status: experimental sketchpad / quarantine zone
Canonical Forest impact: none until explicit promotion
Updated: 2026-09-05

## Purpose

Explore memory as an ecology of specialized roles, stores, connectors, policies, retrieval systems, temporal models, and agent-learning mechanisms rather than as one undifferentiated feature or database.

This area exists specifically to prevent frontier exploration from clouding canonical Forest state. Findings here are hypotheses, probes, evidence, comparisons, and implementation spikes. They do not become canonical merely because they are interesting or technically impressive.

## Governing separation

- `gulfshobot-source/the-forest` = canonical Forest.
- `gulfshobot-source/Forest` = sketchpad / lab / quarantine / nursery.
- External memory systems = mirrors, accelerators, episodic stores, indexes, agent-state stores, or context engines unless deliberately promoted to a defined canonical role.
- No external memory mirror may silently overwrite canonical truth.

## Why memory is a frontier

The canonical Downstairs architecture already distinguishes multiple memory roles:

- canonical knowledge memory
- capability memory
- procedural / skill memory
- failure memory
- uncertainty memory
- navigation memory
- evolution / version memory
- motion / trajectory memory
- external-state memory
- synchronization memory
- credential-metadata memory

The unexplored frontier is the external ecosystem capable of inhabiting, composing, accelerating, or extending those roles.

## Memory ecology dimensions

Every candidate system should be evaluated across at least:

1. **Role** — episodic, semantic, procedural, working, trajectory, user preference, external-state, failure, uncertainty, skill, synchronization, or hybrid.
2. **Authority** — canonical, mirror, cache, derived index, temporary state, or external source authority.
3. **Temporal model** — timeless fact, event log, valid-time/history, checkpoint, decay/forgetting, conflict/invalidation.
4. **Retrieval** — exact, full-text, vector, graph, temporal, hybrid, agent-directed, rule-based.
5. **Write model** — append, infer/extract, update, invalidate, merge, delete, expire, summarize.
6. **Scope** — user, agent, thread, run, project, tree, collection, organization, global.
7. **Portability** — exportability, self-hosting, open protocol, provider dependence, model dependence.
8. **Security/governance** — permissions, encryption, retention, deletion, audit, sensitive-data handling.
9. **Composability** — MCP/API/SDK/CLI support, event hooks, connectors, ability to coexist with other memory layers.
10. **Observability** — inspectability, provenance, confidence, timestamps, source links, why-retrieved explanation.
11. **Failure behavior** — stale recall, false memory, contamination, cross-scope leakage, duplication, semantic drift.
12. **Cost/latency** — storage, extraction, retrieval, token reduction, operational burden.

## Initial horizon map

### Mem0

Observed model: extracted durable memories plus metadata/scopes, semantic retrieval, managed and OSS modes. Useful candidate for preference/decision/fact recall and lightweight cross-session memory. Must be evaluated for provenance fidelity, update semantics, scope isolation, and canonical-mirror discipline.

### Letta

Observed model: stateful long-lived agents, memory-first harness, continual-learning direction, git-tracked context/memory concepts. Candidate for agent-specific procedural/experiential memory and long-horizon autonomous workers. Must not become a hidden competing Forest state.

### Zep / Graphiti

Observed model: temporal knowledge graphs / Context Graphs with entities, relationships, episodes, changing facts, temporal validity, and hybrid retrieval. Strong candidate for derived temporal relationship memory and external-state/context mirrors because it explicitly models change and invalidation.

### LangGraph persistence

Observed model: thread-scoped checkpoints plus cross-thread stores; supports resumption, human-in-the-loop, time travel, and fault tolerance. Strong candidate for execution-state and trajectory memory rather than canonical knowledge.

### MCP memory ecosystem

The official MCP Registry already contains multiple memory-oriented servers, including hosted, local-first, semantic, adaptive, encrypted, project-memory, and self-evolving approaches. MCP should be treated as a transport/capability surface, not as the memory model itself. The current 2026-07-28 MCP specification is stateless at protocol core, which reinforces the need to keep durable memory behind the protocol rather than assuming the connection/session is memory.

## Biological/ecological metaphor guardrail

Use organism/ecology language only when it helps reasoning. Do not let metaphor classify truth.

Potentially useful ecological roles:

- **soil** = durable canonical state and provenance
- **mycelium** = connective/retrieval/transfer pathways
- **nursery** = sketchpad experiments
- **symbiont** = external system that adds value without owning the host
- **seed bank** = durable reusable procedures, patterns, and dormant possibilities
- **compost** = failed experiments converted into reusable lessons
- **immune boundary** = provenance, scope, authorization, conflict detection, quarantine
- **invasive growth** = external memory or derived inference silently overwriting canonical state, leaking across scopes, or propagating unsupported claims

The correct response to invasive-growth risk is not to avoid exploration; it is to preserve authority boundaries, provenance, isolation, and reversible promotion.

## Immediate research tracks

1. Build a memory-role × candidate-system matrix.
2. Test candidate systems only against synthetic/non-sensitive Forest data first.
3. Measure recall quality, provenance retention, temporal correction, conflict handling, and deletion.
4. Explore MCP memory servers as interchangeable adapters.
5. Design a Forest Memory Router that selects memory systems by role instead of provider.
6. Define write/promotion contracts so derived memory can propose canonical changes but never silently mutate them.
7. Define forgetting/decay, contradiction, stale-memory, and contamination behavior.
8. Explore multi-memory composition: e.g. LangGraph checkpoints + Graphiti temporal graph + canonical Git history + local vector cache.
9. Visualize memory flows and health inside the substrate/world engine.
10. Preserve failed memory experiments as explicit failure memory rather than deleting the evidence.

## Promotion criteria

Nothing in this frontier becomes canonical until it demonstrates:

- clear role
- no hidden authority escalation
- provenance preservation
- scope isolation
- reversible integration
- conflict visibility
- reliable export/recovery
- measurable benefit over simpler existing mechanisms
- acceptable privacy/security boundary
- compatibility with canonical Forest reconstruction

## Current conclusion

Memory is not a side feature. It is likely one of the major foundational ecologies beneath long-horizon Forest operation. The correct next move is broad but disciplined exploration under quarantine, followed by role-specific composition rather than selecting one universal memory product prematurely.

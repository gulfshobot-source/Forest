# Forest Memory Router

Status: experimental sketchpad
Updated: 2026-09-05

## Purpose

Route memory work by role and evidence requirements rather than by provider name.

## Core contract

`memory need -> role -> authority requirement -> temporal requirement -> scope -> retrieval mode -> eligible systems -> conflict/provenance check -> context assembly -> optional promotion proposal`

The router must never treat successful retrieval as canonical truth.

## Memory roles

- canonical knowledge
- procedural / skill
- failure / regression
- uncertainty / contradiction
- navigation / place
- trajectory / execution history
- external-state / freshness-sensitive observation
- synchronization / drift
- user preference / durable personal context
- agent-specific long-horizon state
- temporary working memory

## Routing dimensions

1. role
2. authority: canonical | external-authority | mirror | cache | derived-index | temporary
3. scope: user | agent | thread | project | tree | collection | organization
4. time model: current | event-history | temporal-validity | checkpoint | decaying | immutable-history
5. retrieval: exact | full-text | vector | graph | temporal | hybrid
6. write mode: append | update | invalidate | expire | summarize | infer
7. provenance requirement
8. contradiction sensitivity
9. deletion / forgetting requirement
10. latency / cost budget
11. privacy / security class
12. portability / export requirement

## Candidate routing examples

### Canonical structural truth
Primary: `gulfshobot-source/the-forest` Git history + canonical registry.
Optional mirrors may accelerate search but cannot overwrite canonical state.

### Navigation and trajectory
Primary candidates: canonical `live_state` / trajectory logs; LangGraph checkpoints for execution-state experiments.

### Changing external state
Candidate: Graphiti/Zep-style temporal graph or explicit event store. All observations require timestamps and provider provenance.

### Durable semantic recall
Candidates: Basic Memory Cloud, Mem0, Cortex, Lians, or similar systems depending on ownership, source fidelity, contradiction behavior, and exportability.

### Procedural / experiential agent learning
Candidates: Letta, Mem0 procedural memory, shared-memory systems such as Memco, or Forest-native skill/failure registries.

### Evidence-sensitive recall
Candidate: Dijin-style signed evidence packs or Forest-native provenance-linked retrieval.

## Immune checks before context assembly

Every retrieved memory should be classifiable by:

- source system
- original source/provenance if available
- stored/observed time
- current validity window
- scope
- confidence/evidence state
- whether contradicted by canonical or newer state
- whether it is raw source, derived inference, summary, or generated memory

If these fields are unavailable, the router must downgrade trust rather than infer them.

## Promotion contract

External/derived memory may only propose a canonical change.

Promotion sequence:

`retrieve -> identify source -> compare canonical -> surface conflict -> verify where possible -> create explicit proposed delta -> persist provenance -> deliberate promotion`

No provider receives implicit canonical authority.

## Forgetting contract

Forgetting is role-specific:

- canonical history: preserve; supersede rather than erase except for security/privacy incidents
- caches: freely expire
- working memory: short-lived
- external-state observations: age visibly
- inferred memories: decay or require revalidation
- user-requested deletion: propagate to every controlled mirror where supported
- failed experiments: retain compact failure evidence

## First implementation target

Build an adapter interface with synthetic data only:

```ts
interface MemoryAdapter {
  id: string;
  roles: MemoryRole[];
  search(query: MemoryQuery): Promise<MemoryHit[]>;
  fetch(id: string): Promise<MemoryRecord>;
  proposeWrite?(record: MemoryWriteProposal): Promise<MemoryWriteResult>;
  forget?(id: string): Promise<ForgetResult>;
  health(): Promise<MemoryHealth>;
}
```

The router ranks adapters by role fit, provenance quality, temporal semantics, scope isolation, portability, latency, and current health.

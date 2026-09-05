# Forest — Autonomous Production Kernel

Forest is a turnkey-oriented architecture for persistent, measurable, recursively optimized AI production.

## Core idea

One bootstrap specification + material dump initializes a canonical project state. From then on, `continue` means advance the highest-leverage unblocked task. In a fully provisioned execution environment, the same loop can run autonomously until objective completion.

## Design principles

- Preserve operative information while eliminating redundant representation.
- Treat state, dependencies, procedures, quality gates, and completion criteria as executable structure.
- Prefer reusable generative primitives over repeated prose.
- Track provenance and distinguish source, authorial, generated, verified, and inferred material.
- Never claim completion without evidence against explicit acceptance criteria.
- Use deltas and stable references instead of repeatedly transmitting unchanged state.
- Human intervention is reserved for genuinely irreducible authorial or permission decisions.

## Repository map

- `kernel/` — canonical operating protocol and schemas
- `spec/` — bootstrap specification and completion contract
- `state/` — project-state conventions
- `protocol/` — compressed AI-native control protocol
- `loop/` — autonomous execution model
- `ingest/` — material-ingestion contract
- `quality/` — verification and gap rules

## Bootstrap target

The system is designed to be handed to an agentic coding environment such as Claude Code together with project materials. The repository itself becomes versioned system memory; the runtime environment provides execution.

# Forest Runtime Kernel

This directory is the first executable layer of Forest.

The runtime implements the smallest durable continuation primitive:

`RECOVER → SELECT → EXECUTE(adapter) → TEST/RESULT → TRANSITION → PERSIST(caller) → CONTINUE`

## Design boundary

- **Canonical state remains authoritative.** The runtime consumes and returns state; it does not create a competing store.
- **Execution is an adapter.** Coding agents, research tools, file processors, APIs, and future Forest-native executors can plug into the same kernel.
- **Selection is deterministic.** Unblocked work is ranked by explicit leverage, then reusable value and observability.
- **Completion is evidence-gated.** The kernel reports `DONE` only when every completion-ledger item is `passed` or `waived`.
- **Failure remains state.** Failed execution is recorded in history rather than silently discarded.
- **Self-improvement is allowed by structure.** A task that improves the Forest runtime can be selected like any other task when it is authorized and highest leverage.

This is intentionally small. More sophisticated scheduling, retrieval, provenance, visualization, persistence, and agent adapters should compose around this kernel rather than duplicate its state-transition semantics.

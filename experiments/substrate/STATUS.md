# Substrate Execution Status

## Current phase

`contract-defined -> prototype-built -> build-verified -> experiential-validation`

## Established

- Sketchpad repository is the experimental/incubator surface.
- `gulfshobot-source/the-forest` remains canonical.
- Substrate responsibilities are split into existence substrate and navigation substrate.
- Navigation-state, representation, scale, reality-state, mutation, stale/offline, mobile, and comfort invariants are defined.
- A mobile-first Next.js navigation prototype exists in `experiments/substrate/app/`.
- Navigation state is URL-backed (`locus`, `view`, `scale`).
- Outline, viewport, breadcrumbs, details, search, back/forward, reality cues, and representation switching are implemented.
- A canonical-compatible snapshot adapter keeps the prototype explicitly non-authoritative.
- GitHub Actions CI successfully completed dependency installation, TypeScript checking, and production Next.js build on 2026-09-05.

## Verified

GitHub Actions run `33988575385` / job `101366557766`:

- checkout: success
- Node setup: success
- `npm install`: success
- `npm run typecheck`: success
- `npm run build`: success

## In progress

- Add a zero-dependency portable static projection that can be opened without a Next.js/Vercel runtime.
- Reconcile substrate contract with canonical World Engine, Control Surface, Canonical Data Model, Agentic Harness, and Downstairs Connector Fabric.
- Perform experiential comfort test on mobile and large-screen surfaces.

## Promotion gates

- canonical data remains authoritative
- no duplicated semantic object graph
- stable locus across representation switches
- shareable URL state
- back/forward recovery
- mobile portrait usability
- provenance/reality-state visibility
- stale/offline honesty
- repeatable comfort-test pass

The implementation has passed code-integrity gates. It has **not** yet passed the human comfort/navigation gate, so it remains sketchpad material rather than canonical Forest architecture.

# Forest Substrate — Experimental Foundation

**Status:** experimental / sketchpad

**Purpose:** create the substrate the canonical Forest depends on to exist and the human depends on to navigate it comfortably.

## Separation of concerns

The substrate is not another Forest and not another source of truth.

It has two responsibilities:

1. **Existence substrate** — stable identity, provenance, state, relationships, dependencies, events, permissions, and projections that let the Forest persist and be reconstructed.
2. **Navigation substrate** — persistent location, scale, history, paths, landmarks, search, selection, camera/view state, and multiple synchronized representations that let a person move through the Forest without losing orientation.

The canonical source remains `gulfshobot-source/the-forest`.

## Core contract

Canonical state -> substrate index -> projection/runtime -> human navigation -> interaction intent -> validated mutation -> canonical state

The substrate may cache, index, transform, and project canonical state. It must not silently become a competing authority.

## Human comfort requirements

At all times the user should be able to answer:

- Where am I?
- What am I inside of?
- What surrounds this?
- What connects here?
- What changed?
- Where was I before?
- What path am I following?
- What is canonical vs speculative?
- What can I do here?
- How do I zoom out without losing this place?

## Initial implementation target

A mobile-first spatial control surface with:

- persistent You-Are-Here locus
- breadcrumb / ancestry path
- neighborhood / nearby relationship view
- back-forward navigation history
- search and jump
- zoom across Forest -> tree -> branch -> object -> detail
- canonical/provisional/unknown reality-state cues
- route/path highlighting
- saved locations and trails
- synchronized outline + viewport + inspector
- URL-backed shareable view state
- local persistence of navigation preferences
- adapter boundary for future World Engine 2D/3D renderers

## Promotion condition

This experiment becomes canonical only after it can consume canonical Forest data without duplicating authority, preserve orientation across representation changes, pass mobile navigation tests, and demonstrate that the user can repeatedly enter, move, inspect, leave, and return without losing place or context.

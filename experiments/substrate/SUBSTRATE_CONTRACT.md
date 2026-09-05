# Substrate Contract

## 1. Authority

The substrate is a projection/index/runtime layer over the canonical Forest. It must never silently create a second source of truth.

Authoritative structural state remains in `gulfshobot-source/the-forest`.

## 2. Required layers

### A. Identity layer
Every navigable locus must resolve to a stable canonical object id or an explicitly provisional sketchpad id.

### B. Lineage layer
Every projected object should retain enough source/provenance information to distinguish authoritative, verified, observed, inferred, proposed, generated, unknown, and failed states.

### C. Relationship layer
The substrate may compute adjacency, neighborhoods, ancestry, descendants, dependencies, vines, trajectories, and semantic groupings, but derived edges must be marked derived unless canonical.

### D. Event layer
Navigation and state-changing interactions are events. Navigation events may remain local/user-specific. Canonical mutations require validation and a write path back to canonical state.

### E. Projection layer
Multiple views may render the same underlying object graph: outline, terrain, network, tree anatomy, timeline, inspector, search results, 2D/3D world. Views are replaceable projections.

### F. Navigation layer
The user has a persistent locus, path history, scale, selected object, camera/view state, and optional saved trails.

## 3. Navigation state

A minimal navigation state should be serializable as:

```json
{
  "locus": "forest",
  "path": ["forest"],
  "selected": null,
  "representation": "atlas",
  "scale": 0,
  "camera": null,
  "filters": {},
  "trail": [],
  "history_cursor": 0
}
```

The URL should encode stable shareable state where practical. Local persistence may remember personal defaults and recent places. Canonical data must not depend on browser-local state.

## 4. Representation invariant

Changing representation must not change semantic location.

If the user switches from outline -> atlas -> network -> 3D world, the same locus and active intent remain selected unless the user deliberately changes them.

## 5. Progressive scale invariant

Zooming deeper should add detail without erasing containment context. Zooming outward should preserve the deeper locus as a visible or recoverable reference.

## 6. Reality-state invariant

The substrate must visibly distinguish canonical/authoritative material from experimental/provisional/unknown material. Persistence alone never upgrades truth status.

## 7. Mutation invariant

Read/navigation operations can be immediate. Any canonical mutation must pass through an explicit mutation boundary that:

1. identifies the canonical object;
2. states the proposed delta;
3. preserves provenance;
4. validates permissions and dependencies;
5. commits to canonical state;
6. rehydrates projections from the new canonical state.

## 8. Offline/stale invariant

When live canonical data cannot be reached, the substrate may display the latest known snapshot with visible freshness state. It must not pretend stale state is current.

## 9. Mobile invariant

Mobile portrait is a first-class surface. The main viewport remains primary. Outline/search/details become drawers or sheets rather than pushing the viewport away. Touch targets, back behavior, keyboard appearance, zoom, pan, and reset must remain predictable.

## 10. Comfort test

The substrate is not successful because it renders a graph. It is successful when repeated use makes the Forest feel like a place the user knows how to move through.

Minimum test sequence:

1. enter at Forest overview;
2. jump to a known tree;
3. drill into an object;
4. follow a relationship to another subsystem;
5. switch representation;
6. inspect provenance/details;
7. go back twice;
8. zoom out to context;
9. save the place;
10. reload and return to the same place.

Every step should preserve orientation.

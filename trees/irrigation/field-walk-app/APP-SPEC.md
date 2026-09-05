# Irrigation Tree — Field Walk App

## Canonical status
- State: proposed/building
- Canonical home: Forest → Irrigation Tree → Field Walk App
- Purpose: interactive in-ChatGPT field workflow for irrigation inspections, diagnosis, watering-plan optimization, and report generation.
- Provenance: derived from the authorized Forest operating session and prior irrigation field-work discussions; not yet deployed or verified as a live ChatGPT app.

## System role
The app is a view/control surface over canonical Forest state. It is not a second source of truth.

## Primary flow
1. Job intake
2. Customer complaint
3. System/source identification
4. Zone-by-zone field walk
5. Water-source / production / distribution / control diagnostics
6. Evidence and observations
7. Diagnosis with confidence/provenance
8. Watering-plan comparison
9. Smart-plan recommendation
10. Report/PDF artifact

## Irrigation diagnostic hierarchy
- Level 0 — Define complaint
- Level 1 — Water source: available GPM, static/dynamic pressure, quality, seasonal variation, reliability, restrictions
- Level 2 — Production: pump curve, TDH, suction, NPSH, cavitation, amperage, voltage, pressure switch/VFD, efficiency
- Level 3 — Distribution: mainline, laterals, valves, filters, regulators, sprays/rotors/drip
- Level 4 — Control: controller, wiring, solenoids, zone valves, flow/pressure sensors, backflow

## Interactive surfaces
- Job header and current system status
- Zone cards with heads, nozzle assumptions, runtime, estimated GPM, observations, evidence state, and priority
- Diagnostic branch controls
- Watering-plan comparison view
- Schedule editor with immediate gallon/week recalculation
- Recommendation panel explaining why a plan wins
- Evidence/provenance indicators
- Export-to-PDF report

## Smart watering logic
The recommendation engine should optimize for effective root-zone irrigation and uniform coverage, not merely maximum runtime or minimum gallons.

Rules currently established:
- Do not increase whole-zone runtime solely because a brown area exists.
- Investigate distribution/coverage before treating symptoms as water-volume deficiency.
- Replace assumed 0.89 GPM/head with measured field flow when available.
- Compare runtime, frequency, cycle/soak structure, estimated volume, coverage evidence, and source/production constraints.
- Keep proposed recommendations distinct from verified field conditions.

## Known Steven example
- Z1: 13 sprays; assumed 0.89 GPM/head; 11.57 GPM calculated demand
- Z2: 8 sprays; 7.12 GPM; brown section
- Z3: 13 sprays; 11.57 GPM; brown spot toward back
- Z4: 7 sprays; 6.23 GPM
- Z5: 13 sprays; 11.57 GPM; two heads very low/almost buried
- Original: 12–20 min/zone, two starts, Mon/Wed/Fri/Sun → ~6,487 gal/week under the stated assumption
- Current: 30 min/zone, two starts on Monday only → ~2,884 gal/week under the stated assumption
- Current plan is lower-volume but not yet validated as the best irrigation plan.

## Deployment boundary
This specification is canonical architecture, not evidence that a custom Apps SDK app is currently deployed. A live in-ChatGPT app requires the supported app/developer runtime, hosting, permissions, and testing/verification.

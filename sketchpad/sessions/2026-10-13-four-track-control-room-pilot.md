# Four-track Forest control-room pilot — 2026-10-13

Status: PROVISIONAL / INCUBATOR RECORD (not promoted; not a canonical architecture rewrite)
Requested by user: "All" — build Forest control room, BTC research pilot, Florida irrigation trainer, Plus setup as one connected experience.
Repository discipline: authoritative source is gulfshobot-source/the-forest; gulfshobot-source/Forest is experimental incubator. Do not conflate UI demos with persisted/live control, proposed work with verified deployment, or prior-chat recollections with fresh repository evidence.

## Evidence recovered / inspected this session

- Canonical `data/forest.json` reports schema_version 0.6, state "operational-prototype", AI, Trading, Irrigation, GitHub/Infrastructure, and proposed Power/Capability. Architecture includes Foundational Substrate, World Engine, Control Surface, Agentic Harness, Capability Frontier, Downstairs Connector Fabric and Forest Chat App.
- Canonical `data/live_state.json` schema 0.4 (meta updated 2026-09-05) records protocol-tested local Forest Chat App, but externally reachable deployment and chat-native persistent connector actuation still pending. It explicitly separates sandboxed AppBlocks from persisted connector actions.
- Canonical `trees/trading/README.md` defines strategy generation, mechanical rules, backtesting, screening, evaluation, execution and optimization.
- Canonical `trees/irrigation/README.md` fixes complaint→source→production→distribution→control diagnostic taxonomy, pump/well GPM diagnostic, field domains.
- Incubator README states strict raw→sketchpad→validation/reconciliation→deliberate canonical promotion process.
- Verified against current OpenAI Help: Plus has GPT-6 Medium/High thinking (subject to rollout); personal Plus cannot create *new* custom GPTs; Projects support files/chats/default-memory; Work is unavailable in projects set to project-only memory. These details may change; current docs override prior examples.
- Coinbase public candles endpoint documented in official Coinbase Advanced Trade Python SDK: `/api/v3/brokerage/market/products/{product_id}/candles`; no trading authorization needed for public candles.
- UF/IFAS AE067: evaluate **flow at measured pressure** under site conditions, preferably multiple discharge/pressure points; never infer site pump capacity from horsepower alone.

## Four modules in one Forest

### A. Control room / world
- Storage authority: canonical registry + versioned evidence; incubator is provisional.
- UI projection: resources/stock, transfer flows, pressure/bottleneck, paths/dependencies, open evidence gates, freshness.
- Work graph: intake→candidate→research→test→verify→governed promotion→observe, with explicit reasons when blocked.
- For each item maintain id, origin, timestamp, observation status, claimed state, current proof, verification level, linked domain, canonical path, and next action.
- Present reality flags: VERIFIED_REPOSITORY, PROPOSED, DEMO_LOCAL, UNVERIFIED_LIVE.
- One chat UI is an interaction surface, not automatic evidence of a deployed application or synchronized backend.

### B. BTC-USD / Coinbase research pilot
- Asset: BTC-USD, preferred test venue Coinbase spot. Exploratory / paper research only. No trade placement authorized.
- Target timeframe lattice: 12M→6M→3M→1M→1W→1D→4H→1H→15M (and smaller as quality allows). Higher bars must be deterministically aggregated from timestamp-normalized lower source bars where supported, with source exchange and epoch explicit. A Coinbase-only historical series does not mean BTC inception history; external pre-listing evidence must remain separately labeled.
- Per candle: open/high/low/close/volume, true start/end timestamp, complete flag, source/provenance, context and parent/child links, known-at-time data cutoff, hypothesis, observed outcome.
- Example testable setups:
  POC Bounce: prior session CLOSED outside prior value area; extend prior-session POC; require later revisit plus directional rejection confirmation. Stop/invalidation beyond agreed structure; log R multiples; no entry without both gates.
  Value Area Reversal: prior session CLOSED inside prior value area; current session trades beyond VAH or VAL then candle CLOSES back inside; short from above VAH or long from below VAL. Record excursion extreme for invalidation.
  ORB: specify session anchor first because BTC spot is 24/7 (proposed NY 09:30–09:45 ET opening range); define what counts as confirmed breakout and re-test; no performance assumptions.
- Pipeline: documented external criteria→source candles→normalize→replay→generate scenarios→paper backtest with fees/slippage→walk-forward check→compare variants by regime→paper screen→review. Include explicit NO_TRADE gate.
- Required reports: raw period count/completeness, lookahead/leak checks, missing data, sample size, net expectancy after costs, max drawdown, uncertainty, strategy correlation, versioned predictions/outcomes.
- Data not fetched or empirically backtested in this note. Prior informal "80 observations" pilot is only a recollection pending physical artifact verification. No profitability claims.

### C. Florida irrigation field-learning pilot
- Main taxonomy: L0 customer complaint; L1 water source (well, pond/lake, municipal, reclaimed, canal/cistern as appropriate); L2 pump/production; L3 distribution; L4 controller/control.
- Module 1: triage tree keyed to symptoms and evidence, not just guesswork.
- Module 2: measured pump capacity: gpm=(measured gallons × 60)/elapsed seconds. Pair measured GPM with gauge PSI and suction/water conditions at same operating point. High shutoff pressure alone is not an adequate capacity measurement. Avoid unsafe dead-heading/dry-running.
- Module 3: zone estimate: nominal zone GPM = sum of nozzle-specific GPM at actual operating pressure; gallons = GPM×actual runtime. Values from a catalog at a different PSI are only estimates.
- Demonstration with prior observed Steven field job: Zone 1 13 sprays × nominal 0.89 GPM/head = nominal 11.57 GPM; at 30 minutes = 347.1 gallons estimated, conditional on rated flow and zone duration. No field meter/GPM verification attached to this computation.
- Training drill: 'Runs manually, fails from controller' → L4 first; 'all zones weak with running pump' → L1/L2 measurements before replacing parts; 'one zone weak while others are normal' → L3 first (verify no source-wide issue).
- Assessment: present symptom, user selects first level; reveal reason, next measurement, and disconfirming evidence. Future safety and field-validation logs.

### D. Plus workflow / environment
- Keep an overarching Forest ChatGPT Project using DEFAULT memory if cross-project memory and Work access are desired. Project-only memory can isolate context and disables Work in that project. Avoid shared-project memory restrictions unless intentional.
- GitHub already connected for this session; read-only repository verification accomplished. Writes to authoritative canonical branch require reconciliation and proof, not casual UI actions.
- Google Drive suggested, not confirmed connected in this session; can hold supporting docs but cannot supersede canonical registry.
- Model: select GPT-6 Medium or High where available on Plus for architecture/research; Instant for routine.
- Deep Research: source discovery, evidence grading, competitor/tested-criteria literature.
- Work: supported multi-step browser/files/app process; Work and inline DIL demo differ in persistence and app execution.
- Files: attach docs and CSVs as input. GitHub still holds authoritative source of truth.
- No claims that custom Plus GPT creation is enabled or that unconfirmed plugins are connected.

## Transition gates / next action

1. Verify and label: canonical architecture confirmed; live Forest Chat external deployment still pending.
2. Surface immediate in-chat demo showing four workflows and working local rule calculations (present turn).
3. BTC: locate/ingest and checksum a real Coinbase BTC-USD dated OHLCV slice; verify timeframe aggregation and closed-candle logic; then compute a first strategy dry-run with costs. No unseen backtest numbers.
4. Irrigation: connect example field input to measurements (PSI at GPM), then turn diagnostic and zone calculations into a tested case record.
5. Only after source-artifact review: deliberate promotion of tested artifacts to appropriate canonical locations, with revision proof and no competing canonical repo.

This is a capture of context and runnable pilot criteria, not a report of live streaming data, automated execution, or production deployment.

import type { ForestSnapshot } from './types';

export const forestSnapshot: ForestSnapshot = {
  sourceRepository: 'gulfshobot-source/the-forest',
  sourceRef: 'main:data/forest.json',
  capturedAt: '2026-09-05',
  canonical: false,
  nodes: [
    {
      id: 'forest',
      name: 'The Forest',
      kind: 'forest',
      state: 'authoritative',
      description: 'Persistent, rebuildable system for knowledge, systems, relationships, capabilities, and reusable infrastructure.'
    },
    {
      id: 'ai',
      name: 'AI',
      kind: 'tree',
      state: 'authoritative',
      parentId: 'forest',
      canonicalPath: 'trees/ai/README.md',
      description: 'AI systems, capabilities, orchestration, memory, evaluation, and experimental ideas.'
    },
    {
      id: 'trading',
      name: 'Trading',
      kind: 'tree',
      state: 'authoritative',
      parentId: 'forest',
      canonicalPath: 'trees/trading/README.md',
      description: 'Systematic generation, testing, screening, refinement, and maintenance of trading strategies.'
    },
    {
      id: 'irrigation',
      name: 'Irrigation',
      kind: 'tree',
      state: 'authoritative',
      parentId: 'forest',
      canonicalPath: 'trees/irrigation/README.md',
      description: 'Practical irrigation knowledge across water source, pumping, distribution, controls, diagnostics, and estimating.'
    },
    {
      id: 'github',
      name: 'GitHub / Infrastructure',
      kind: 'tree',
      state: 'authoritative',
      parentId: 'forest',
      canonicalPath: 'trees/github/README.md',
      description: 'Persistence, versioning, recovery, automation, deployment, and infrastructure for the Forest itself.'
    },
    {
      id: 'power',
      name: 'Power / Capability',
      kind: 'tree',
      state: 'proposed',
      parentId: 'forest',
      description: 'Foundational resource and capability layer awaiting full formalization.'
    },
    {
      id: 'foundational-substrate',
      name: 'Foundational Substrate',
      kind: 'architecture',
      state: 'authoritative',
      parentId: 'forest',
      canonicalPath: 'architecture/FOUNDATIONAL_SUBSTRATE.md',
      description: 'Continuity layer binding canonical identity, provenance, dependency, navigation state, projection continuity, operational boundaries, and recoverable movement.'
    },
    {
      id: 'control-surface-target',
      name: 'Control Surface',
      kind: 'architecture',
      state: 'authoritative',
      parentId: 'forest',
      canonicalPath: 'architecture/FOREST_CONTROL_SURFACE_TARGET.md',
      description: 'Human-facing interactive environment for navigating and operating the Forest.'
    },
    {
      id: 'canonical-data-model',
      name: 'Canonical Data Model',
      kind: 'architecture',
      state: 'authoritative',
      parentId: 'forest',
      canonicalPath: 'architecture/CANONICAL_DATA_MODEL.md'
    },
    {
      id: 'cognitive-visualization',
      name: 'Cognitive Visualization',
      kind: 'architecture',
      state: 'authoritative',
      parentId: 'forest',
      canonicalPath: 'architecture/COGNITIVE_VISUALIZATION.md'
    },
    {
      id: 'world-engine',
      name: 'World Engine',
      kind: 'architecture',
      state: 'authoritative',
      parentId: 'forest',
      canonicalPath: 'architecture/WORLD_ENGINE.md'
    },
    {
      id: 'agentic-harness',
      name: 'Agentic Harness',
      kind: 'architecture',
      state: 'authoritative',
      parentId: 'forest',
      canonicalPath: 'architecture/AGENTIC_HARNESS.md'
    },
    {
      id: 'capability-frontier',
      name: 'Capability Frontier',
      kind: 'architecture',
      state: 'authoritative',
      parentId: 'forest',
      canonicalPath: 'architecture/CAPABILITY_FRONTIER.md'
    },
    {
      id: 'downstairs-connector-fabric',
      name: 'Downstairs Connector Fabric',
      kind: 'architecture',
      state: 'authoritative',
      parentId: 'forest',
      canonicalPath: 'architecture/DOWNSTAIRS_CONNECTOR_FABRIC.md'
    },
    {
      id: 'forest-chat-app',
      name: 'Forest Chat App',
      kind: 'capability',
      state: 'verified',
      parentId: 'forest',
      canonicalPath: 'anatomy/FOREST_CHAT_APP_DRIVER.md'
    }
  ],
  edges: [
    { id: 'contain-ai', from: 'forest', to: 'ai', label: 'contains', kind: 'contains', state: 'authoritative' },
    { id: 'contain-trading', from: 'forest', to: 'trading', label: 'contains', kind: 'contains', state: 'authoritative' },
    { id: 'contain-irrigation', from: 'forest', to: 'irrigation', label: 'contains', kind: 'contains', state: 'authoritative' },
    { id: 'contain-github', from: 'forest', to: 'github', label: 'contains', kind: 'contains', state: 'authoritative' },
    { id: 'contain-power', from: 'forest', to: 'power', label: 'contains', kind: 'contains', state: 'proposed' },
    { id: 'contain-substrate', from: 'forest', to: 'foundational-substrate', label: 'depends on', kind: 'depends-on', state: 'authoritative' },
    { id: 'contain-control', from: 'forest', to: 'control-surface-target', label: 'projects through', kind: 'projects-to', state: 'authoritative' },
    { id: 'contain-canon', from: 'forest', to: 'canonical-data-model', label: 'contains', kind: 'contains', state: 'authoritative' },
    { id: 'contain-viz', from: 'forest', to: 'cognitive-visualization', label: 'contains', kind: 'contains', state: 'authoritative' },
    { id: 'contain-world', from: 'forest', to: 'world-engine', label: 'contains', kind: 'contains', state: 'authoritative' },
    { id: 'contain-harness', from: 'forest', to: 'agentic-harness', label: 'contains', kind: 'contains', state: 'authoritative' },
    { id: 'contain-frontier', from: 'forest', to: 'capability-frontier', label: 'contains', kind: 'contains', state: 'authoritative' },
    { id: 'contain-downstairs', from: 'forest', to: 'downstairs-connector-fabric', label: 'contains', kind: 'contains', state: 'authoritative' },
    { id: 'contain-chat', from: 'forest', to: 'forest-chat-app', label: 'contains', kind: 'contains', state: 'verified' },
    { id: 'substrate-canon', from: 'foundational-substrate', to: 'canonical-data-model', label: 'identity + provenance', kind: 'supports', state: 'authoritative' },
    { id: 'substrate-downstairs', from: 'foundational-substrate', to: 'downstairs-connector-fabric', label: 'operational continuity', kind: 'supports', state: 'authoritative' },
    { id: 'substrate-world', from: 'foundational-substrate', to: 'world-engine', label: 'navigation embodiment', kind: 'projects-to', state: 'authoritative' },
    { id: 'substrate-control', from: 'foundational-substrate', to: 'control-surface-target', label: 'human projection', kind: 'projects-to', state: 'authoritative' },
    { id: 'vine-ai-trading', from: 'ai', to: 'trading', label: 'AI ↔ Trading', kind: 'vine', state: 'authoritative' },
    { id: 'vine-ai-irrigation', from: 'ai', to: 'irrigation', label: 'AI ↔ Irrigation', kind: 'vine', state: 'authoritative' },
    { id: 'vine-harness-canon', from: 'agentic-harness', to: 'canonical-data-model', label: 'Harness ↔ Canonical Data', kind: 'supports', state: 'authoritative' },
    { id: 'vine-harness-viz', from: 'agentic-harness', to: 'cognitive-visualization', label: 'Harness ↔ Visualization', kind: 'supports', state: 'authoritative' },
    { id: 'vine-frontier-harness', from: 'capability-frontier', to: 'agentic-harness', label: 'Frontier ↔ Harness', kind: 'supports', state: 'authoritative' },
    { id: 'vine-world-canon', from: 'world-engine', to: 'canonical-data-model', label: 'World ↔ Canonical Data', kind: 'projects-to', state: 'authoritative' },
    { id: 'vine-world-frontier', from: 'world-engine', to: 'capability-frontier', label: 'World ↔ Frontier', kind: 'supports', state: 'authoritative' },
    { id: 'vine-downstairs-harness', from: 'downstairs-connector-fabric', to: 'agentic-harness', label: 'Downstairs ↔ Harness', kind: 'supports', state: 'authoritative' },
    { id: 'vine-downstairs-world', from: 'downstairs-connector-fabric', to: 'world-engine', label: 'Downstairs ↔ World', kind: 'supports', state: 'authoritative' },
    { id: 'vine-chat-downstairs', from: 'forest-chat-app', to: 'downstairs-connector-fabric', label: 'Chat ↔ Downstairs', kind: 'supports', state: 'verified' },
    { id: 'vine-chat-world', from: 'forest-chat-app', to: 'world-engine', label: 'Chat ↔ World', kind: 'projects-to', state: 'verified' }
  ]
};

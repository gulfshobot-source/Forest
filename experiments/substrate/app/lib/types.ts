export type RealityState =
  | 'authoritative'
  | 'verified'
  | 'observed'
  | 'inferred'
  | 'proposed'
  | 'generated'
  | 'unknown'
  | 'failed';

export type NodeKind =
  | 'forest'
  | 'tree'
  | 'architecture'
  | 'registry'
  | 'capability'
  | 'vine'
  | 'object';

export type ForestNode = {
  id: string;
  name: string;
  kind: NodeKind;
  state: RealityState;
  description?: string;
  parentId?: string | null;
  canonicalPath?: string | null;
  tags?: string[];
};

export type ForestEdge = {
  id: string;
  from: string;
  to: string;
  label: string;
  kind: 'contains' | 'vine' | 'depends-on' | 'projects-to' | 'supports';
  state: RealityState;
};

export type ForestSnapshot = {
  sourceRepository: string;
  sourceRef: string;
  capturedAt: string;
  canonical: boolean;
  nodes: ForestNode[];
  edges: ForestEdge[];
};

export type Representation = 'atlas' | 'outline' | 'network';

export type NavigationState = {
  locus: string;
  selected: string | null;
  representation: Representation;
  scale: number;
  trail: string[];
};

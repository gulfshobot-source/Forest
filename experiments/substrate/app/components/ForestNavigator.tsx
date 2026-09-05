'use client';

import { useCallback, useMemo, useState } from 'react';
import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import type { ForestEdge, ForestNode, Representation } from '../lib/types';
import { forestSnapshot } from '../lib/snapshot';

const stateRank: Record<ForestNode['state'], number> = {
  authoritative: 7,
  verified: 6,
  observed: 5,
  inferred: 4,
  proposed: 3,
  generated: 2,
  unknown: 1,
  failed: 0
};

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}

function nodeById(id: string | null) {
  if (!id) return null;
  return forestSnapshot.nodes.find((node) => node.id === id) ?? null;
}

function ancestry(node: ForestNode | null) {
  const result: ForestNode[] = [];
  let current = node;
  const seen = new Set<string>();

  while (current && !seen.has(current.id)) {
    seen.add(current.id);
    result.unshift(current);
    current = current.parentId ? nodeById(current.parentId) : null;
  }

  return result;
}

function neighborhood(id: string) {
  const edgeList = forestSnapshot.edges.filter((edge) => edge.from === id || edge.to === id);
  const ids = new Set<string>();
  edgeList.forEach((edge) => ids.add(edge.from === id ? edge.to : edge.from));
  return {
    edges: edgeList,
    nodes: forestSnapshot.nodes.filter((node) => ids.has(node.id))
  };
}

function stablePosition(node: ForestNode, index: number, total: number) {
  if (node.id === 'forest') return { x: 50, y: 50 };

  const ring = node.kind === 'tree' ? 28 : node.kind === 'architecture' ? 39 : 44;
  const angle = ((index / Math.max(total, 1)) * Math.PI * 2) - Math.PI / 2;
  return {
    x: 50 + Math.cos(angle) * ring,
    y: 50 + Math.sin(angle) * ring
  };
}

function edgeLabel(edge: ForestEdge, current: string) {
  return edge.from === current ? `→ ${edge.label}` : `← ${edge.label}`;
}

export default function ForestNavigator() {
  const router = useRouter();
  const pathname = usePathname();
  const params = useSearchParams();

  const locusId = params.get('locus') ?? 'forest';
  const representation = (params.get('view') as Representation | null) ?? 'atlas';
  const scale = clamp(Number(params.get('scale') ?? '0'), 0, 4);

  const locus = nodeById(locusId) ?? nodeById('forest')!;
  const crumbs = ancestry(locus);
  const nearby = useMemo(() => neighborhood(locus.id), [locus.id]);
  const [query, setQuery] = useState('');
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [outlineOpen, setOutlineOpen] = useState(false);

  const updateUrl = useCallback((next: { locus?: string; view?: Representation; scale?: number }, push = true) => {
    const search = new URLSearchParams(params.toString());
    if (next.locus) search.set('locus', next.locus);
    if (next.view) search.set('view', next.view);
    if (typeof next.scale === 'number') search.set('scale', String(clamp(next.scale, 0, 4)));
    const href = `${pathname}?${search.toString()}`;
    if (push) router.push(href);
    else router.replace(href);
  }, [params, pathname, router]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return forestSnapshot.nodes;
    return forestSnapshot.nodes.filter((node) =>
      [node.name, node.description, node.kind, node.canonicalPath]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(q))
    );
  }, [query]);

  const sortedNodes = useMemo(() => {
    return [...forestSnapshot.nodes].sort((a, b) => {
      if (a.id === 'forest') return -1;
      if (b.id === 'forest') return 1;
      return stateRank[b.state] - stateRank[a.state] || a.name.localeCompare(b.name);
    });
  }, []);

  const positions = useMemo(() => {
    const nonRoot = sortedNodes.filter((node) => node.id !== 'forest');
    const map = new Map<string, { x: number; y: number }>();
    map.set('forest', { x: 50, y: 50 });
    nonRoot.forEach((node, index) => map.set(node.id, stablePosition(node, index, nonRoot.length)));
    return map;
  }, [sortedNodes]);

  const selectedEdges = new Set(nearby.edges.map((edge) => edge.id));
  const selectedNodes = new Set([locus.id, ...nearby.nodes.map((node) => node.id)]);

  return (
    <main className="shell">
      <header className="topbar">
        <div>
          <div className="eyebrow">FOREST SUBSTRATE · EXPERIMENTAL PROJECTION</div>
          <h1>{locus.name}</h1>
        </div>
        <div className="freshness" title="This prototype uses a captured canonical-compatible snapshot, not a live authoritative feed.">
          <span className="freshness-dot" /> snapshot · {forestSnapshot.capturedAt}
        </div>
      </header>

      <nav className="breadcrumbs" aria-label="Current location">
        {crumbs.map((node, index) => (
          <span key={node.id} className="crumb-wrap">
            {index > 0 && <span className="crumb-sep">/</span>}
            <button className="crumb" onClick={() => updateUrl({ locus: node.id })}>{node.name}</button>
          </span>
        ))}
      </nav>

      <section className="workspace">
        <aside className={`rail outline-rail ${outlineOpen ? 'mobile-open' : ''}`}>
          <div className="rail-head">
            <strong>Outline</strong>
            <button className="mobile-close" onClick={() => setOutlineOpen(false)}>×</button>
          </div>
          <label className="search-box">
            <span>Search</span>
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Find a place…"
            />
          </label>
          <div className="outline-list">
            {filtered.map((node) => (
              <button
                key={node.id}
                className={`outline-item ${node.id === locus.id ? 'active' : ''}`}
                onClick={() => {
                  updateUrl({ locus: node.id });
                  setOutlineOpen(false);
                }}
              >
                <span className={`state-mark state-${node.state}`} />
                <span>
                  <b>{node.name}</b>
                  <small>{node.kind}</small>
                </span>
              </button>
            ))}
          </div>
        </aside>

        <section className="viewport-card">
          <div className="viewport-toolbar">
            <div className="representation-switch" aria-label="Representation">
              {(['atlas', 'outline', 'network'] as Representation[]).map((view) => (
                <button
                  key={view}
                  className={representation === view ? 'active' : ''}
                  onClick={() => updateUrl({ view }, false)}
                >
                  {view}
                </button>
              ))}
            </div>
            <div className="zoom-controls">
              <button onClick={() => updateUrl({ scale: scale - 1 }, false)} aria-label="Zoom out">−</button>
              <span>scale {scale}</span>
              <button onClick={() => updateUrl({ scale: scale + 1 }, false)} aria-label="Zoom in">+</button>
            </div>
          </div>

          <div className={`viewport view-${representation}`}>
            {representation === 'atlas' && (
              <div className="atlas" style={{ ['--scale' as string]: String(1 + scale * 0.08) }}>
                <svg className="edge-layer" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
                  {forestSnapshot.edges.map((edge) => {
                    const from = positions.get(edge.from);
                    const to = positions.get(edge.to);
                    if (!from || !to) return null;
                    const active = selectedEdges.has(edge.id);
                    return (
                      <line
                        key={edge.id}
                        x1={from.x}
                        y1={from.y}
                        x2={to.x}
                        y2={to.y}
                        className={`${active ? 'active-edge' : ''} edge-${edge.kind}`}
                      />
                    );
                  })}
                </svg>
                {sortedNodes.map((node) => {
                  const pos = positions.get(node.id)!;
                  const active = node.id === locus.id;
                  const related = selectedNodes.has(node.id);
                  return (
                    <button
                      key={node.id}
                      className={`atlas-node kind-${node.kind} state-${node.state} ${active ? 'active' : ''} ${related ? 'related' : ''}`}
                      style={{ left: `${pos.x}%`, top: `${pos.y}%` }}
                      onClick={() => updateUrl({ locus: node.id })}
                      title={`${node.name} · ${node.state}`}
                    >
                      <span className="node-core" />
                      <span className="node-label">{node.name}</span>
                    </button>
                  );
                })}
              </div>
            )}

            {representation === 'network' && (
              <div className="network-view">
                <div className="network-center">
                  <span className={`state-mark state-${locus.state}`} />
                  <strong>{locus.name}</strong>
                  <small>{locus.kind} · {locus.state}</small>
                </div>
                <div className="neighbor-grid">
                  {nearby.nodes.length === 0 && <p className="empty">No recorded neighbors in this snapshot.</p>}
                  {nearby.nodes.map((node) => {
                    const edge = nearby.edges.find((candidate) =>
                      (candidate.from === locus.id && candidate.to === node.id) ||
                      (candidate.to === locus.id && candidate.from === node.id)
                    );
                    return (
                      <button key={node.id} className="neighbor-card" onClick={() => updateUrl({ locus: node.id })}>
                        <span className={`state-mark state-${node.state}`} />
                        <b>{node.name}</b>
                        <small>{edge ? edgeLabel(edge, locus.id) : node.kind}</small>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}

            {representation === 'outline' && (
              <div className="focus-outline">
                <section>
                  <span className="section-kicker">You are here</span>
                  <h2>{locus.name}</h2>
                  <p>{locus.description ?? 'No description in this snapshot.'}</p>
                </section>
                <section>
                  <span className="section-kicker">Inside / nearby</span>
                  <div className="neighbor-grid compact">
                    {nearby.nodes.map((node) => (
                      <button key={node.id} className="neighbor-card" onClick={() => updateUrl({ locus: node.id })}>
                        <b>{node.name}</b>
                        <small>{node.kind} · {node.state}</small>
                      </button>
                    ))}
                  </div>
                </section>
              </div>
            )}
          </div>

          <div className="orientation-strip">
            <div>
              <span className="section-kicker">Path</span>
              <strong>{crumbs.map((node) => node.name).join(' → ')}</strong>
            </div>
            <div>
              <span className="section-kicker">Nearby</span>
              <strong>{nearby.nodes.length} places · {nearby.edges.length} paths</strong>
            </div>
            <div>
              <span className="section-kicker">Reality</span>
              <strong>{locus.state}</strong>
            </div>
          </div>
        </section>

        <aside className={`rail inspector-rail ${detailsOpen ? 'mobile-open' : ''}`}>
          <div className="rail-head">
            <strong>Details</strong>
            <button className="mobile-close" onClick={() => setDetailsOpen(false)}>×</button>
          </div>
          <div className="detail-block">
            <span className="section-kicker">Identity</span>
            <h3>{locus.name}</h3>
            <code>{locus.id}</code>
          </div>
          <div className="detail-grid">
            <div><span>Kind</span><b>{locus.kind}</b></div>
            <div><span>Reality</span><b>{locus.state}</b></div>
            <div><span>Scale</span><b>{scale}</b></div>
            <div><span>View</span><b>{representation}</b></div>
          </div>
          <div className="detail-block">
            <span className="section-kicker">Description</span>
            <p>{locus.description ?? 'No description in this snapshot.'}</p>
          </div>
          <div className="detail-block">
            <span className="section-kicker">Canonical home</span>
            <code>{locus.canonicalPath ?? 'none declared'}</code>
          </div>
          <div className="detail-block warning-block">
            <span className="section-kicker">Projection status</span>
            <p>This app is a non-authoritative projection. Source: {forestSnapshot.sourceRepository}/{forestSnapshot.sourceRef}.</p>
          </div>
        </aside>
      </section>

      <div className="mobile-commandbar">
        <button onClick={() => setOutlineOpen(true)}>☰ Outline</button>
        <button onClick={() => router.back()}>← Back</button>
        <button onClick={() => updateUrl({ locus: 'forest', scale: 0 })}>⌾ Home</button>
        <button onClick={() => router.forward()}>Forward →</button>
        <button onClick={() => setDetailsOpen(true)}>Details ⓘ</button>
      </div>
    </main>
  );
}

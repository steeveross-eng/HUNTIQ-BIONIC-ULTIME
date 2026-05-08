/**
 * Visualizer18Page.jsx — P21 · Dashboard interactif 18 couches
 * COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT
 */
import React, { useEffect, useMemo, useState } from 'react';
import {
  LAYER_CATALOG_OMEGA,
  LAYER_GROUPS_OMEGA,
} from '@/components/territoire/registry/layer_catalog_omega';
import {
  layerManualStatus, layerManualCreate, layerManualDownloadUrl,
  visualizerAllLayers,
} from '@/lib/bce4xApi';
import { Search, Download, FileText, Eye, RefreshCw } from 'lucide-react';

const Visualizer18Page = () => {
  const [groupFilter, setGroupFilter] = useState('ALL');
  const [search, setSearch] = useState('');
  const [manualState, setManualState] = useState(null);
  const [manualLoading, setManualLoading] = useState(false);
  const [vizState, setVizState] = useState(null);
  const [error, setError] = useState('');

  const filtered = useMemo(() => {
    return LAYER_CATALOG_OMEGA.filter((l) => {
      if (groupFilter !== 'ALL' && l.group !== groupFilter) return false;
      if (search) {
        const q = search.toLowerCase();
        return (
          l.label.toLowerCase().includes(q) ||
          l.desc.toLowerCase().includes(q) ||
          l.code.toLowerCase().includes(q) ||
          l.id.toLowerCase().includes(q)
        );
      }
      return true;
    });
  }, [groupFilter, search]);

  const refreshAll = async () => {
    setManualLoading(true);
    setError('');
    const [m, v] = await Promise.all([
      layerManualStatus(),
      visualizerAllLayers(),
    ]);
    if (m.ok) setManualState(m.data?.result);
    else setError(`MANUAL_STATUS_FAILED::${m.detail}`);
    if (v.ok) setVizState(v.data);
    setManualLoading(false);
  };

  useEffect(() => {
    refreshAll();
  }, []);

  const onGenerateManual = async () => {
    setManualLoading(true);
    const r = await layerManualCreate({
      include_pdf: true,
      include_html: true,
      persist: true,
    });
    if (r.ok) {
      setManualState({
        ...manualState,
        last_manual_sha256: r.data?.result?.manual_sha256,
        n_manuals_generated: (manualState?.n_manuals_generated || 0) + 1,
      });
    } else {
      setError(`GENERATE_FAILED::${r.detail}`);
    }
    setManualLoading(false);
  };

  return (
    <div data-testid="visualizer18-page" style={{ maxWidth: 1200 }}>
      <header style={{ marginBottom: 20 }}>
        <h1
          style={{
            color: '#D4A017',
            fontSize: 24,
            margin: 0,
            fontWeight: 800,
            letterSpacing: 1,
          }}
        >
          VISUALIZER 18 · DASHBOARD INTERACTIF
        </h1>
        <p style={{ opacity: 0.7, fontSize: 12, marginTop: 4 }}>
          Catalogue doctrinal des 18 couches · filtres groupe + recherche +
          aperçu PDF.
        </p>
      </header>

      {/* Toolbar */}
      <div
        style={{
          display: 'flex',
          gap: 12,
          marginBottom: 16,
          alignItems: 'center',
          flexWrap: 'wrap',
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            background: '#1d2330',
            borderRadius: 6,
            padding: '6px 10px',
            flex: '1 1 240px',
            minWidth: 220,
          }}
        >
          <Search size={14} color="#94A3B8" />
          <input
            data-testid="visualizer18-search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Rechercher couche…"
            style={{
              border: 'none',
              outline: 'none',
              background: 'transparent',
              color: '#E8E4D9',
              fontSize: 12,
              flex: 1,
            }}
          />
        </div>
        <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
          {['ALL', ...Object.keys(LAYER_GROUPS_OMEGA)].map((g) => {
            const meta = LAYER_GROUPS_OMEGA[g];
            const active = groupFilter === g;
            return (
              <button
                key={g}
                data-testid={`visualizer18-filter-${g.toLowerCase()}`}
                onClick={() => setGroupFilter(g)}
                style={{
                  padding: '5px 10px',
                  borderRadius: 4,
                  border: '1px solid rgba(212,160,23,0.3)',
                  background: active
                    ? '#D4A017'
                    : 'rgba(15,23,42,0.7)',
                  color: active ? '#0F1419' : '#E8E4D9',
                  fontSize: 10,
                  fontWeight: 800,
                  letterSpacing: 1,
                  cursor: 'pointer',
                  fontFamily: 'JetBrains Mono, monospace',
                }}
              >
                {g === 'ALL' ? 'TOUS' : `${g} · ${meta?.label || ''}`}
              </button>
            );
          })}
        </div>
        <button
          onClick={refreshAll}
          data-testid="visualizer18-refresh"
          disabled={manualLoading}
          style={{
            padding: '7px 14px',
            background: 'rgba(212,160,23,0.2)',
            border: '1px solid rgba(212,160,23,0.4)',
            borderRadius: 4,
            color: '#D4A017',
            fontSize: 11,
            fontWeight: 700,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: 4,
          }}
        >
          <RefreshCw size={12} /> Refresh
        </button>
      </div>

      {/* Status manual + actions */}
      <div
        data-testid="visualizer18-manual-status"
        style={{
          background: 'rgba(15,23,42,0.6)',
          border: '1px solid rgba(212,160,23,0.3)',
          padding: '10px 14px',
          borderRadius: 8,
          marginBottom: 16,
          fontSize: 11,
          display: 'flex',
          gap: 14,
          alignItems: 'center',
          flexWrap: 'wrap',
        }}
      >
        <span style={{ opacity: 0.7 }}>P18 Manual :</span>
        <code style={{ color: '#7CB518' }}>
          {manualState?.current_status || '—'}
        </code>
        <span>n={manualState?.n_manuals_generated || 0}</span>
        <span>n_layers={manualState?.n_layers || 18}</span>
        {manualState?.last_manual_sha256 && (
          <code style={{ fontSize: 9, opacity: 0.7 }}>
            sha={manualState.last_manual_sha256.slice(0, 16)}…
          </code>
        )}
        <button
          onClick={onGenerateManual}
          disabled={manualLoading}
          data-testid="visualizer18-generate-manual"
          style={{
            marginLeft: 'auto',
            padding: '5px 12px',
            background: '#D4A017',
            color: '#0F1419',
            border: 'none',
            borderRadius: 4,
            fontWeight: 800,
            fontSize: 11,
            cursor: 'pointer',
          }}
        >
          {manualLoading ? '…' : 'Régénérer Manuel PDF'}
        </button>
        {manualState?.last_manual_sha256 && (
          <a
            href={layerManualDownloadUrl(manualState.last_manual_sha256, 'pdf')}
            target="_blank"
            rel="noopener noreferrer"
            data-testid="visualizer18-download-pdf"
            style={{
              padding: '5px 10px',
              background: 'transparent',
              border: '1px solid #7CB518',
              borderRadius: 4,
              color: '#7CB518',
              fontSize: 11,
              fontWeight: 700,
              textDecoration: 'none',
              display: 'flex',
              alignItems: 'center',
              gap: 4,
            }}
          >
            <Download size={11} /> PDF
          </a>
        )}
      </div>

      {error && (
        <div
          data-testid="visualizer18-error"
          style={{
            background: 'rgba(220,38,38,0.15)',
            border: '1px solid rgba(220,38,38,0.4)',
            padding: 10,
            borderRadius: 6,
            marginBottom: 16,
            color: '#FCA5A5',
            fontSize: 12,
          }}
        >
          {error}
        </div>
      )}

      {/* Layers grid */}
      <div
        data-testid="visualizer18-grid"
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
          gap: 10,
        }}
      >
        {filtered.map((l) => {
          const Icon = l.icon;
          return (
            <div
              key={l.id}
              data-testid={`visualizer18-card-${l.id}`}
              style={{
                background: 'rgba(15,23,42,0.7)',
                border: `1px solid ${l.color}55`,
                borderLeft: `4px solid ${l.color}`,
                borderRadius: 6,
                padding: '10px 12px',
                fontSize: 11,
              }}
            >
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                  marginBottom: 4,
                }}
              >
                <Icon size={13} color={l.color} />
                <span
                  style={{
                    fontWeight: 800,
                    color: l.color,
                    flex: 1,
                  }}
                >
                  {l.label}
                </span>
                <code
                  style={{
                    fontSize: 8,
                    opacity: 0.7,
                    fontFamily: 'JetBrains Mono, monospace',
                  }}
                >
                  {l.code}
                </code>
              </div>
              <p
                style={{
                  fontSize: 10,
                  opacity: 0.8,
                  margin: '4px 0',
                  lineHeight: 1.4,
                }}
              >
                {l.desc}
              </p>
              <div
                style={{
                  display: 'flex',
                  gap: 6,
                  marginTop: 6,
                  fontSize: 9,
                  fontFamily: 'JetBrains Mono, monospace',
                  opacity: 0.7,
                }}
              >
                <span>{LAYER_GROUPS_OMEGA[l.group]?.label}</span>
                <span>·</span>
                <span>z{l.zIndex}</span>
                <span>·</span>
                <span>op{l.opacityDefault}%</span>
              </div>
            </div>
          );
        })}
      </div>
      {vizState && (
        <div
          data-testid="visualizer18-backend-meta"
          style={{
            marginTop: 18,
            padding: 10,
            background: 'rgba(15,23,42,0.6)',
            border: '1px solid rgba(124,181,24,0.3)',
            borderRadius: 6,
            fontSize: 10,
            fontFamily: 'JetBrains Mono, monospace',
            opacity: 0.85,
          }}
        >
          Backend visualizer-all-layers · status =
          {' '}
          <code style={{ color: '#7CB518' }}>
            {vizState?.result?.current_status || vizState?.manifest_id || 'OK'}
          </code>
        </div>
      )}
    </div>
  );
};

export default Visualizer18Page;

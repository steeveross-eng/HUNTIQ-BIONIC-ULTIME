/**
 * LayerManualPage.jsx — P21 · UI P18 (manual 18 couches)
 * COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT
 */
import React, { useEffect, useState } from 'react';
import {
  layerManualCreate, layerManualStatus, layerManualDownloadUrl,
} from '@/lib/bce4xApi';
import { Download, BookOpen, AlertTriangle } from 'lucide-react';
import {
  LAYER_CATALOG_OMEGA, LAYER_GROUPS_OMEGA,
} from '@/components/territoire/registry/layer_catalog_omega';

const LayerManualPage = () => {
  const [status, setStatus] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [genResult, setGenResult] = useState(null);

  const refresh = async () => {
    const s = await layerManualStatus();
    if (s.ok) setStatus(s.data?.result);
  };
  useEffect(() => {
    refresh();
  }, []);

  const onGenerate = async () => {
    setBusy(true);
    setError('');
    const r = await layerManualCreate({
      include_pdf: true,
      include_html: true,
      persist: true,
    });
    if (r.ok) {
      setGenResult(r.data?.result);
      await refresh();
    } else {
      setError(`GENERATE_FAILED::${r.detail}`);
    }
    setBusy(false);
  };

  return (
    <div data-testid="layer-manual-page" style={{ maxWidth: 1100 }}>
      <header style={{ marginBottom: 20 }}>
        <h1 style={{ color: '#D4A017', fontSize: 24, margin: 0, fontWeight: 800 }}>
          MANUEL D'INTERPRÉTATION · 18 COUCHES · P18
        </h1>
        <p style={{ opacity: 0.7, fontSize: 12, marginTop: 4 }}>
          Manuel doctrinal complet · définitions, usage, exemples · export PDF paysage A4.
        </p>
      </header>

      <section
        data-testid="layer-manual-actions"
        style={{
          background: 'rgba(15,23,42,0.7)',
          border: '1px solid rgba(212,160,23,0.3)',
          padding: 14,
          borderRadius: 8,
          marginBottom: 16,
          display: 'flex',
          gap: 10,
          alignItems: 'center',
          flexWrap: 'wrap',
        }}
      >
        <button
          onClick={onGenerate}
          disabled={busy}
          data-testid="layer-manual-generate"
          style={{
            padding: '8px 16px',
            background: '#D4A017',
            color: '#0F1419',
            border: 'none',
            borderRadius: 4,
            fontWeight: 800,
            cursor: 'pointer',
          }}
        >
          {busy ? 'Génération…' : 'Générer Manuel'}
        </button>
        {status?.last_manual_sha256 && (
          <>
            <span style={{ fontSize: 11, opacity: 0.8 }}>
              Dernier manuel :
            </span>
            <code style={{ fontSize: 10, color: '#7CB518' }}>
              {status.last_manual_sha256.slice(0, 24)}…
            </code>
            <a
              href={layerManualDownloadUrl(status.last_manual_sha256, 'pdf')}
              target="_blank"
              rel="noopener noreferrer"
              data-testid="layer-manual-dl-pdf"
              style={dlBtn('#D4A017')}
            >
              <Download size={12} /> PDF
            </a>
            <a
              href={layerManualDownloadUrl(status.last_manual_sha256, 'html')}
              target="_blank"
              rel="noopener noreferrer"
              data-testid="layer-manual-dl-html"
              style={dlBtn('#7CB518')}
            >
              <Download size={12} /> HTML
            </a>
          </>
        )}
        <span
          style={{
            marginLeft: 'auto',
            fontSize: 10,
            opacity: 0.6,
            fontFamily: 'JetBrains Mono, monospace',
          }}
        >
          n_manuels = {status?.n_manuals_generated || 0} · n_couches = {status?.n_layers || 18}
        </span>
      </section>

      {error && (
        <div
          data-testid="layer-manual-error"
          style={{
            background: 'rgba(220,38,38,0.15)',
            border: '1px solid rgba(220,38,38,0.4)',
            padding: 10,
            borderRadius: 6,
            marginBottom: 16,
            color: '#FCA5A5',
            fontSize: 12,
            display: 'flex',
            alignItems: 'center',
            gap: 6,
          }}
        >
          <AlertTriangle size={14} /> {error}
        </div>
      )}

      {/* Catalog by group */}
      {Object.values(LAYER_GROUPS_OMEGA).map((group) => {
        const layers = LAYER_CATALOG_OMEGA.filter((l) => l.group === group.id);
        if (layers.length === 0) return null;
        return (
          <section
            key={group.id}
            data-testid={`layer-manual-group-${group.id}`}
            style={{ marginBottom: 14 }}
          >
            <h2
              style={{
                fontSize: 14,
                color: group.color,
                margin: '8px 0 6px',
                fontWeight: 800,
                letterSpacing: 1.5,
                paddingLeft: 8,
                borderLeft: `4px solid ${group.color}`,
              }}
            >
              {group.id} · {group.label} · z{group.zBase}
            </h2>
            <table
              style={{
                width: '100%',
                fontSize: 11,
                borderCollapse: 'collapse',
              }}
            >
              <thead>
                <tr style={{ background: 'rgba(15,23,42,0.6)' }}>
                  <th style={th}>Code</th>
                  <th style={th}>Couche</th>
                  <th style={th}>Définition</th>
                  <th style={th}>Z-index</th>
                  <th style={th}>Source</th>
                </tr>
              </thead>
              <tbody>
                {layers.map((l) => {
                  const Icon = l.icon;
                  return (
                    <tr
                      key={l.id}
                      data-testid={`layer-manual-row-${l.id}`}
                      style={{
                        borderBottom: '1px dashed rgba(255,255,255,0.06)',
                      }}
                    >
                      <td style={td}>
                        <code style={{ color: l.color, fontSize: 10 }}>
                          {l.code}
                        </code>
                      </td>
                      <td style={td}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                          <Icon size={12} color={l.color} />
                          <strong>{l.label}</strong>
                        </div>
                      </td>
                      <td style={td}>{l.desc}</td>
                      <td style={{ ...td, fontFamily: 'JetBrains Mono, monospace', fontSize: 10 }}>
                        z{l.zIndex}
                      </td>
                      <td style={{ ...td, fontFamily: 'JetBrains Mono, monospace', fontSize: 10, opacity: 0.75 }}>
                        {l.source}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </section>
        );
      })}

      {genResult && (
        <div
          data-testid="layer-manual-gen-result"
          style={{
            marginTop: 16,
            padding: 10,
            background: 'rgba(124,181,24,0.10)',
            border: '1px solid rgba(124,181,24,0.4)',
            borderRadius: 6,
            fontSize: 11,
            fontFamily: 'JetBrains Mono, monospace',
            color: '#7CB518',
          }}
        >
          ✓ Manuel généré · sha = {genResult.manual_sha256?.slice(0, 32)}…
        </div>
      )}
    </div>
  );
};

const th = {
  textAlign: 'left',
  padding: '6px 10px',
  fontSize: 10,
  color: '#D4A017',
  fontWeight: 800,
  letterSpacing: 1,
};
const td = { padding: '6px 10px', verticalAlign: 'top' };
const dlBtn = (color) => ({
  padding: '6px 12px',
  background: 'transparent',
  border: `1px solid ${color}`,
  borderRadius: 4,
  color,
  fontSize: 11,
  fontWeight: 700,
  textDecoration: 'none',
  display: 'flex',
  alignItems: 'center',
  gap: 4,
});

export default LayerManualPage;

/**
 * StatutCorridorsOmegaPanel — PHASE_XII_SUPRA_DIAGNOSTIC_V30_STATUS_Ω
 * ═══════════════════════════════════════════════════════════════════════
 * Panneau LECTURE SEULE institutionnel affichant le statut ENGINE
 * CORRIDORS V30 couplé à RenduΩ et P6.
 *
 *   - Taux d'acceptation par espèce
 *   - Corridors visibles vs rejetés
 *   - Score v30_alignment_score (barre + code couleur)
 *   - Aucune action utilisateur — purement institutionnel
 *
 * BCE-4X ULTIME ABSOLU — TOP-ABSOLU.
 * ═══════════════════════════════════════════════════════════════════════
 */

import React, { useEffect, useState } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;
const REFRESH_INTERVAL_MS = 60_000; // 1 min
const OFFICIAL_LAT = 48.206657;
const OFFICIAL_LNG = -68.382422;

function labelColor(label) {
  switch (label) {
    case 'CONFORME_Ω': return '#16a34a';
    case 'CONFORME':   return '#f59e0b';
    case 'NON_CONFORME':
    default:           return '#ef4444';
  }
}

function ScoreBar({ score = 0, label = 'NON_CONFORME' }) {
  const pct = Math.max(0, Math.min(100, score));
  const color = labelColor(label);
  return (
    <div data-testid="v30-score-bar" style={{
      width: '100%', height: 8, background: '#1c2735', borderRadius: 4,
      overflow: 'hidden', marginTop: 6,
    }}>
      <div style={{
        width: `${pct}%`, height: '100%', background: color,
        transition: 'width 450ms ease',
      }} />
    </div>
  );
}

export default function StatutCorridorsOmegaPanel({ lat = OFFICIAL_LAT, lng = OFFICIAL_LNG }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;
    let initialTimer = null;
    async function fetchStatus() {
      try {
        const r = await fetch(
          `${API}/api/v30/corridors/status?lat=${lat}&lon=${lng}`,
          { cache: 'no-store' }
        );
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        const j = await r.json();
        if (mounted) { setData(j); setError(null); }
      } catch (e) {
        const msg = String(e.message || e);
        if (mounted && !msg.includes('DataCloneError') && !msg.includes('postMessage') && !msg.includes('abort')) {
          setError(msg);
        }
      }
    }
    // Retarder pour éviter StrictMode double-mount qui ABORT le 1er fetch
    initialTimer = setTimeout(fetchStatus, 800);
    const t = setInterval(fetchStatus, REFRESH_INTERVAL_MS);
    return () => {
      mounted = false;
      if (initialTimer) clearTimeout(initialTimer);
      clearInterval(t);
    };
  }, [lat, lng]);

  if (error) {
    return (
      <div data-testid="v30-status-error" style={{
        padding: 10, fontSize: 11, color: '#ffc3c3',
        background: '#2a1616', borderRadius: 4,
      }}>
        STATUT CORRIDORS Ω — erreur lecture: {error}
      </div>
    );
  }
  if (!data) {
    return (
      <div data-testid="v30-status-loading" style={{
        padding: 10, fontSize: 11, color: '#9fb0c2',
      }}>
        STATUT CORRIDORS Ω — chargement…
      </div>
    );
  }

  const g = data.global || {};
  const ps = data.per_species || {};
  const color = labelColor(g.alignment_label);

  return (
    <div data-testid="v30-status-panel" style={{
      background: 'rgba(14,20,28,0.94)',
      border: `1px solid ${color}`,
      borderRadius: 6,
      padding: '10px 12px',
      color: '#e8eef5',
      font: '11px/1.5 ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace',
      minWidth: 260, maxWidth: 320,
    }}>
      <div style={{
        color: '#ff8f00', fontWeight: 700, letterSpacing: '0.04em',
        borderBottom: '1px solid #1c2735', paddingBottom: 4, marginBottom: 6,
      }}>STATUT CORRIDORS Ω <span style={{
        fontSize: 9, color: '#9fb0c2', marginLeft: 6,
      }}>V30 · RenduΩ · P6</span></div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
        <span style={{ color: '#9fb0c2' }}>v30_alignment_score</span>
        <span data-testid="v30-score-value" style={{ color, fontWeight: 700, fontSize: 14 }}>
          {g.v30_alignment_score?.toFixed(2) ?? '—'}
        </span>
      </div>
      <ScoreBar score={g.v30_alignment_score ?? 0} label={g.alignment_label} />
      <div data-testid="v30-alignment-label" style={{
        color, fontWeight: 700, marginTop: 4, fontSize: 10,
      }}>{g.alignment_label}</div>

      <div style={{ marginTop: 8, color: '#9fb0c2' }}>
        acceptance rate&nbsp;: <span style={{ color: '#e8eef5' }}>{g.acceptance_rate_pct?.toFixed(1)} %</span>
        &nbsp;·&nbsp;corridors&nbsp;: <span style={{ color: '#e8eef5' }}>{g.accepted ?? 0}/{g.total ?? 0}</span>
      </div>

      <div style={{ marginTop: 8, fontSize: 10, color: '#9fb0c2' }}>
        Par espèce&nbsp;:
      </div>
      <table data-testid="v30-per-species-table" style={{
        width: '100%', marginTop: 2, borderCollapse: 'collapse', fontSize: 10,
      }}>
        <tbody>
          {Object.entries(ps).map(([sp, s]) => (
            <tr key={sp} data-testid={`v30-species-row-${sp}`}>
              <td style={{ color: '#ffc300', width: '30%' }}>{sp}</td>
              <td style={{ color: '#e8eef5', width: '30%' }}>
                {s.accepted}/{s.total}
              </td>
              <td style={{ color: labelColor(s.alignment_label), textAlign: 'right' }}>
                {s.v30_alignment_score?.toFixed(1)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {Array.isArray(g.rejection_top_reasons) && g.rejection_top_reasons.length > 0 && (
        <div data-testid="v30-rejection-top" style={{
          marginTop: 8, fontSize: 9.5, color: '#9fb0c2',
        }}>
          Rejets dominants&nbsp;:{' '}
          {g.rejection_top_reasons.slice(0, 3).map((r, i) => (
            <span key={i} style={{ color: '#e8eef5' }}>
              {r[0]}({r[1]}){i < Math.min(2, g.rejection_top_reasons.length - 1) ? ', ' : ''}
            </span>
          ))}
        </div>
      )}

      <div style={{
        marginTop: 8, paddingTop: 6, borderTop: '1px dashed #1c2735',
        fontSize: 9, color: '#6b7a8c',
      }}>
        seuils&nbsp;: ≥{data.thresholds?.conform_omega_above}&nbsp;CONFORME_Ω · ≥{data.thresholds?.non_conform_below}&nbsp;CONFORME · &lt;{data.thresholds?.non_conform_below}&nbsp;NON_CONFORME<br/>
        V30 LOCKED · lecture seule · refresh 60 s
      </div>
    </div>
  );
}

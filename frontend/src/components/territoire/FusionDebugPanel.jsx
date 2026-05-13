/**
 * FusionDebugPanel.jsx — P22Σ_V3_FUSION_VEINEUSE_DIAGNOSTIC_Ω
 * ════════════════════════════════════════════════════════════════════════
 * COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT
 *
 * Panneau de diagnostic FUSION VEINEUSE — affiche en temps réel par espèce :
 *   - n_corridors_before_fusion / n_after / clusters_fused / absorbed
 *   - distribution des intensity_level (FAIBLE / MODÉRÉ / MOYEN / ÉLEVÉ / EXTRÊME)
 *   - récapitulatif fusion_summary par espèce
 *
 * Activation : URL flag `?fusionDebug=on`
 * Tag global : window.__P22SIGMA_V3_FUSION_DEBUG__
 *
 * V30_LOCK INVIOLÉ · FUSION ADD-ONLY · NEW COMPONENT
 * ════════════════════════════════════════════════════════════════════════
 */

import React, { useCallback, useEffect, useState } from 'react';

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';
const ORGANIC_URL = `${API_BASE}/api/v20/territoire/corridors-organic/generate`;

const SPECIES_LIST = ['orignal', 'chevreuil', 'ours_noir', 'dindon_sauvage', 'wapiti', 'coyote'];
const INTENSITY_LABELS = ['FAIBLE', 'MODÉRÉ', 'MOYEN', 'ÉLEVÉ', 'EXTRÊME'];
const INTENSITY_COLORS = ['#FFE0B2', '#FFCC80', '#FFB74D', '#FF9800', '#E65100'];

const isEnabled = () => {
  try {
    if (typeof window === 'undefined') return false;
    const sp = new URLSearchParams(window.location.search);
    const v = sp.get('fusionDebug');
    return v === 'on' || v === '1' || v === 'true';
  } catch (_e) { return false; }
};

const getCoords = () => {
  try {
    const sp = new URLSearchParams(window.location.search);
    return {
      lat: parseFloat(sp.get('lat')) || 48.206657,
      lon: parseFloat(sp.get('lng') || sp.get('lon')) || -68.382422,
    };
  } catch (_e) {
    return { lat: 48.206657, lon: -68.382422 };
  }
};

/** Probe TERRITORY_CONTINUOUS sur 1 espèce → extrait fusion doctrine.
 *  Timeout dur 30s par espèce (anti-saturation Cloudflare P22J).
 */
const probeFusionForSpecies = async (lat, lon, species, timeoutMs = 30000) => {
  const t0 = Date.now();
  const controller = new AbortController();
  const tid = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const resp = await fetch(ORGANIC_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'omit',
      signal: controller.signal,
      body: JSON.stringify({
        lat, lon, species,
        month: 10, hour: 7, wind_deg: 225, wind_speed: 15,
        anchor_mode: 'TERRITORY_CONTINUOUS',
        anchor_priority: ['saline', 'feeding_zone', 'rut_zone', 'rest_zone', 'waypoint'],
        allow_multi_anchor: true,
        external_entry_exit_radius_m: 600.0,
      }),
    });
    clearTimeout(tid);
    const data = await resp.json();
    const fd = data?.p22sigma_v3_fusion_doctrine || {};
    const fs = fd.fusion_summary || null;
    const corridors = Array.isArray(data?.corridors) ? data.corridors : [];
    const intensityDist = { 0: 0, 1: 0, 2: 0, 3: 0, 4: 0 };
    let nNetwork = 0;
    corridors.forEach((c) => {
      if (typeof c?.intensity_level === 'number') {
        intensityDist[c.intensity_level] = (intensityDist[c.intensity_level] || 0) + 1;
        nNetwork += 1;
      }
    });
    return {
      species,
      ok: resp.ok,
      ms: Date.now() - t0,
      n_corridors_total: corridors.length,
      n_network_corridors: nNetwork,
      fusion_applied: !!fd.fusion_applied,
      summary: fs,
      intensity_dist_live: intensityDist,
    };
  } catch (e) {
    clearTimeout(tid);
    return {
      species,
      ok: false,
      ms: Date.now() - t0,
      error: (e?.name === 'AbortError') ? 'TIMEOUT 30s' : String(e),
    };
  }
};

// ═══ STYLES ═══
const cellStyle = {
  padding: '6px 10px',
  border: '1px solid #444',
  fontSize: '11px',
  fontFamily: 'monospace',
  textAlign: 'left',
};
const headerStyle = {
  ...cellStyle,
  background: '#1a1a1a',
  color: '#FFC300',
  fontWeight: 'bold',
  textTransform: 'uppercase',
  fontSize: '10px',
};

// ═══ TABLEAU SUMMARY GLOBAL ═══
const GlobalSummaryTable = ({ rows }) => {
  const total = rows.reduce((acc, r) => {
    const fs = r.summary || {};
    acc.before += Number(fs.n_corridors_before_fusion || 0);
    acc.after += Number(fs.n_corridors_after_fusion || 0);
    acc.clusters += Number(fs.n_fused_clusters || 0);
    acc.absorbed += Number(fs.n_corridors_absorbed || 0);
    return acc;
  }, { before: 0, after: 0, clusters: 0, absorbed: 0 });
  return (
    <div data-testid="fusion-debug-global-summary" style={{ marginBottom: 16 }}>
      <h4 style={{ color: '#FF6A00', fontSize: 13, fontFamily: 'monospace',
                   marginBottom: 8, fontWeight: 'bold' }}>
        Σ Synthèse globale FUSION VEINEUSE — TERRITORY_CONTINUOUS
      </h4>
      <table style={{ borderCollapse: 'collapse', width: '100%',
                      background: 'rgba(0,0,0,0.45)' }}>
        <thead>
          <tr>
            <th style={headerStyle}>Avant fusion</th>
            <th style={headerStyle}>Après fusion</th>
            <th style={headerStyle}>Clusters fusionnés</th>
            <th style={headerStyle}>Absorbés</th>
            <th style={headerStyle}>Réduction</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td style={cellStyle} data-testid="fd-before">{total.before}</td>
            <td style={cellStyle} data-testid="fd-after">{total.after}</td>
            <td style={cellStyle} data-testid="fd-clusters">{total.clusters}</td>
            <td style={cellStyle} data-testid="fd-absorbed">{total.absorbed}</td>
            <td style={cellStyle}>
              {total.before > 0
                ? `-${(((total.before - total.after) / total.before) * 100).toFixed(1)}%`
                : '—'}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
};

// ═══ TABLEAU PAR ESPÈCE ═══
const PerSpeciesTable = ({ rows }) => (
  <div data-testid="fusion-debug-per-species" style={{ marginBottom: 16 }}>
    <h4 style={{ color: '#FF6A00', fontSize: 13, fontFamily: 'monospace',
                 marginBottom: 8, fontWeight: 'bold' }}>
      Détails par espèce (5 species × TERRITORY_CONTINUOUS)
    </h4>
    <table style={{ borderCollapse: 'collapse', width: '100%',
                    background: 'rgba(0,0,0,0.45)' }}>
      <thead>
        <tr>
          <th style={headerStyle}>Espèce</th>
          <th style={headerStyle}>HTTP</th>
          <th style={headerStyle}>ms</th>
          <th style={headerStyle}>N total</th>
          <th style={headerStyle}>N réseau</th>
          <th style={headerStyle}>Fusion</th>
          <th style={headerStyle}>Avant</th>
          <th style={headerStyle}>Après</th>
          <th style={headerStyle}>Clusters</th>
          <th style={headerStyle}>Absorbés</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((r, i) => {
          const fs = r.summary || {};
          return (
            <tr key={r.species} style={i % 2 ? { background: 'rgba(255,255,255,0.02)' } : null}
                data-testid={`fd-row-${r.species}`}>
              <td style={{ ...cellStyle, color: '#FFC300', fontWeight: 'bold' }}>
                {r.species}
              </td>
              <td style={{ ...cellStyle, color: r.ok ? '#0f0' : (r._pending ? '#FFC300' : '#f55') }}>
                {r._pending ? '...' : (r.ok ? 'OK' : (r.error ? 'ERR' : 'KO'))}
              </td>
              <td style={cellStyle}>{r._pending ? '⟳' : r.ms}</td>
              <td style={cellStyle}>{r.n_corridors_total ?? '—'}</td>
              <td style={cellStyle}>{r.n_network_corridors ?? '—'}</td>
              <td style={{ ...cellStyle, color: r.fusion_applied ? '#0f0' : '#888' }}>
                {r.fusion_applied ? 'ON' : 'OFF'}
              </td>
              <td style={cellStyle}>{fs.n_corridors_before_fusion ?? '—'}</td>
              <td style={cellStyle}>{fs.n_corridors_after_fusion ?? '—'}</td>
              <td style={cellStyle}>{fs.n_fused_clusters ?? '—'}</td>
              <td style={cellStyle}>{fs.n_corridors_absorbed ?? '—'}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  </div>
);

// ═══ DISTRIBUTION INTENSITÉ ═══
const IntensityDistributionTable = ({ rows }) => (
  <div data-testid="fusion-debug-intensity-distribution" style={{ marginBottom: 16 }}>
    <h4 style={{ color: '#FF6A00', fontSize: 13, fontFamily: 'monospace',
                 marginBottom: 8, fontWeight: 'bold' }}>
      Distribution intensity_level par espèce (data live corridors[])
    </h4>
    <table style={{ borderCollapse: 'collapse', width: '100%',
                    background: 'rgba(0,0,0,0.45)' }}>
      <thead>
        <tr>
          <th style={headerStyle}>Espèce</th>
          {INTENSITY_LABELS.map((label, lvl) => (
            <th key={lvl} style={{ ...headerStyle, color: INTENSITY_COLORS[lvl] }}>
              L{lvl} · {label}
            </th>
          ))}
          <th style={headerStyle}>Total</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((r, i) => {
          const dist = r.intensity_dist_live || {};
          const total = Object.values(dist).reduce((a, b) => a + b, 0);
          return (
            <tr key={r.species} style={i % 2 ? { background: 'rgba(255,255,255,0.02)' } : null}>
              <td style={{ ...cellStyle, color: '#FFC300', fontWeight: 'bold' }}>
                {r.species}
              </td>
              {INTENSITY_LABELS.map((_, lvl) => {
                const n = Number(dist[lvl] || 0);
                return (
                  <td key={lvl} style={{
                    ...cellStyle,
                    color: n > 0 ? INTENSITY_COLORS[lvl] : '#555',
                    fontWeight: n > 0 ? 'bold' : 'normal',
                  }}>{n}</td>
                );
              })}
              <td style={cellStyle}>{total}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  </div>
);

// ═══ COMPOSANT PRINCIPAL ═══
const FusionDebugPanel = () => {
  const [enabled] = useState(isEnabled());
  const [coords] = useState(getCoords());
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [lastFetchedAt, setLastFetchedAt] = useState(null);
  const [error, setError] = useState(null);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    setError(null);
    setRows([]);
    // Mode SÉQUENTIEL anti-saturation Cloudflare P22J — affichage progressif
    const accumulated = [];
    try {
      for (const sp of SPECIES_LIST) {
        // Placeholder "in progress"
        accumulated.push({ species: sp, ok: false, ms: 0, _pending: true });
        setRows([...accumulated]);
        const r = await probeFusionForSpecies(coords.lat, coords.lon, sp);
        accumulated[accumulated.length - 1] = r;
        setRows([...accumulated]);
      }
      setLastFetchedAt(new Date().toISOString());
      try {
        if (typeof window !== 'undefined') {
          window.__P22SIGMA_V3_FUSION_DEBUG__ = Object.freeze({
            doctrine: 'P22Σ_V3_FUSION_VEINEUSE_Ω',
            coords: { ...coords },
            rows: accumulated,
            fetched_at: new Date().toISOString(),
          });
        }
      } catch (_) { /* noop */ }
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }, [coords]);

  useEffect(() => {
    if (enabled) fetchAll();
  }, [enabled, fetchAll]);

  if (!enabled) return null;

  return (
    <div
      data-testid="fusion-debug-panel"
      style={{
        position: 'fixed',
        top: 80,
        right: 12,
        width: 'min(680px, 95vw)',
        maxHeight: '85vh',
        overflowY: 'auto',
        background: 'rgba(10, 10, 10, 0.95)',
        border: '2px solid #FF6A00',
        borderRadius: 8,
        padding: 14,
        zIndex: 99999,
        boxShadow: '0 0 24px rgba(255, 106, 0, 0.4)',
        color: '#FFFFFF',
        fontFamily: 'monospace',
      }}
    >
      <div style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        marginBottom: 12, paddingBottom: 8, borderBottom: '1px solid #444',
      }}>
        <h3 style={{
          color: '#FF6A00', fontSize: 14, margin: 0, fontWeight: 'bold',
          letterSpacing: 0.5,
        }}>
          P22Σ_V3 · FUSION VEINEUSE Ω · DIAGNOSTIC
        </h3>
        <button
          data-testid="fusion-debug-refresh"
          onClick={fetchAll}
          disabled={loading}
          style={{
            background: loading ? '#444' : '#FF6A00',
            color: '#000',
            border: 'none',
            padding: '4px 10px',
            fontSize: 11,
            fontFamily: 'monospace',
            fontWeight: 'bold',
            cursor: loading ? 'wait' : 'pointer',
            borderRadius: 4,
          }}
        >
          {loading ? '⟳ ...' : '⟳ REFRESH'}
        </button>
      </div>

      <div style={{ fontSize: 10, color: '#888', marginBottom: 12 }}>
        <div data-testid="fd-coord">
          lat={coords.lat.toFixed(4)} · lon={coords.lon.toFixed(4)} ·
          mode=<span style={{ color: '#0f0' }}>TERRITORY_CONTINUOUS</span>
        </div>
        <div>doctrine=<span style={{ color: '#FFC300' }}>P22Σ_V3_FUSION_VEINEUSE_Ω</span> ·
          fusion_distance=<span style={{ color: '#0f0' }}>18.0m</span> ·
          overlap_ratio_min=<span style={{ color: '#0f0' }}>0.30</span></div>
        {lastFetchedAt && (
          <div data-testid="fd-fetched">fetched_at={lastFetchedAt}</div>
        )}
      </div>

      {error && (
        <div style={{ color: '#f55', marginBottom: 12, fontSize: 11 }}>
          ⚠ {error}
        </div>
      )}

      {rows.length > 0 && (
        <>
          <GlobalSummaryTable rows={rows} />
          <PerSpeciesTable rows={rows} />
          <IntensityDistributionTable rows={rows} />
        </>
      )}

      {loading && rows.length === 0 && (
        <div style={{ color: '#888', fontSize: 11, padding: 20, textAlign: 'center' }}>
          ⟳ Probing 5 espèces × TERRITORY_CONTINUOUS...
        </div>
      )}

      <div style={{
        fontSize: 9, color: '#666', marginTop: 8, paddingTop: 8,
        borderTop: '1px solid #333', textAlign: 'center',
      }}>
        BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT · V30_LOCK INVIOLÉ
      </div>
    </div>
  );
};

export default FusionDebugPanel;

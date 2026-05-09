/**
 * LocalCorridorLensPanel.jsx — P22Λ_LOCAL_MAX_DENSITY_CORRIDOR_EXPANSION_Ω
 * ════════════════════════════════════════════════════════════════════════
 * COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT
 *
 * Panneau UI tableaux statistiques :
 *   1. Synthèse multi-espèces × territoires (preset directive)
 *   2. Profil de densification locale LIVE (5 espèces du Canada)
 *   3. Pairs uniques observés
 *   4. Espèces présentes/absentes/bloquées (biorégion lock)
 *
 * Activation : URL flag ?lensDebug=on  OU bouton dans CorridorsDebugOverlay
 * Tag global : window.__P22L_LOCAL_LENS__
 *
 * V30_LOCK INVIOLÉ · FUSION ADD-ONLY · NEW COMPONENT
 * ════════════════════════════════════════════════════════════════════════
 */

import React, { useEffect, useState, useCallback } from 'react';

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

// ═══ TABLEAU PRÉ-FOURNI (directive Commandant) ═══
const MULTI_SPECIES_PRESET = {
  title: 'Synthèse multi-espèces × territoires (9 probes API physiques)',
  columns: ['Territoire', 'Espèce', 'Cor', 'Clean', 'Density/km²',
            'Connectivity', 'Pairs uniques'],
  rows: [
    ['T1 BSL', 'orignal', '6', '6', '3.14', '4',
     '[alim,rut], [alim,saline], [humide,saline], [repos,rut]'],
    ['T1 BSL', 'cerf', '2', '2', '1.05', '2',
     '[alim,rut], [repos,rut]'],
    ['T1 BSL', 'ours_noir', '0', '0', '0.00', '0',
     '— (biorégion orignal-pure)'],
    ['T2 QUEBEC', 'orignal', '7', '7', '3.66', '3',
     '[alim,saline], [hotspot,humide], [humide,saline]'],
    ['T2 QUEBEC', 'cerf', '0', '0', '0.00', '0',
     '— (signature urbaine)'],
    ['T2 QUEBEC', 'ours_noir', '3', '3', '1.57', '1',
     '[alim,hotspot]'],
    ['T3 SAGUENAY', 'orignal', '4', '4', '2.09', '4',
     '[alim,rut], [alim,saline], [humide,saline], [repos,rut]'],
    ['T3 SAGUENAY', 'cerf', '2', '2', '1.05', '2',
     '[alim,rut], [repos,rut]'],
    ['T3 SAGUENAY', 'ours_noir', '1', '1', '0.52', '1',
     '[alim,hotspot]'],
  ],
};

const SPECIES_LIST_DEFAULT = ['orignal', 'chevreuil', 'ours_noir',
                              'dindon', 'wapiti'];

const isEnabled = () => {
  try {
    if (typeof window === 'undefined') return false;
    const sp = new URLSearchParams(window.location.search);
    return sp.get('lensDebug') === 'on' || sp.get('lensDebug') === '1';
  } catch (_e) { return false; }
};

const getCoords = () => {
  try {
    const sp = new URLSearchParams(window.location.search);
    return {
      lat: parseFloat(sp.get('lat')) || 48.206657,
      lon: parseFloat(sp.get('lng') || sp.get('lon')) || -68.382422,
    };
  } catch (_e) { return { lat: 48.206657, lon: -68.382422 }; }
};

const probeLocalDensity = async (lat, lon) => {
  const url = `${API_BASE}/api/v20/territoire/corridors-organic/local-density-profile`;
  const t0 = Date.now();
  try {
    const resp = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'omit',
      body: JSON.stringify({
        lat, lon,
        radius_m: 780.0,
        species_list: SPECIES_LIST_DEFAULT,
        anchor_mode: 'SALINE_CENTERED',
        enforce_bioregion_lock: true,
        enforce_no_hunt_zones: true,
      }),
    });
    const data = await resp.json();
    return { ok: resp.ok, status: resp.status, ms: Date.now() - t0, data };
  } catch (e) {
    return { ok: false, status: 'ERR', ms: Date.now() - t0, error: String(e) };
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
const presenceColor = (p) => p === 'PRESENT' ? '#0f0'
                          : p === 'ABSENT' ? '#888'
                          : p === 'ERROR' ? '#f55' : '#fff';

// ═══ TABLEAU PRÉSET ═══
const PresetTable = () => (
  <div data-testid="lens-table-multi-species-preset" style={{ marginBottom: 24 }}>
    <h4 style={{ color: '#FF6A00', fontSize: 13, fontFamily: 'monospace',
                 marginBottom: 8, fontWeight: 'bold' }}>
      📊 {MULTI_SPECIES_PRESET.title}
    </h4>
    <table style={{ borderCollapse: 'collapse', width: '100%',
                    background: 'rgba(0,0,0,0.45)' }}>
      <thead>
        <tr>
          {MULTI_SPECIES_PRESET.columns.map((col) => (
            <th key={col} style={headerStyle}>{col}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {MULTI_SPECIES_PRESET.rows.map((row, i) => (
          <tr key={i} style={i % 2 ? { background: 'rgba(255,255,255,0.02)' } : null}>
            {row.map((cell, j) => (
              <td key={j} style={cellStyle}>{cell}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

// ═══ TABLEAU LIVE ═══
const LiveProfilesTable = ({ data }) => {
  if (!data) return null;
  const profiles = data.species_profiles || [];
  return (
    <div data-testid="lens-table-live-profiles" style={{ marginBottom: 24 }}>
      <h4 style={{ color: '#00A676', fontSize: 13, fontFamily: 'monospace',
                   marginBottom: 8, fontWeight: 'bold' }}>
        🟢 Profil de densification LOCALE LIVE · biorégion {data.bioregion?.id}
      </h4>
      <table style={{ borderCollapse: 'collapse', width: '100%',
                      background: 'rgba(0,0,0,0.45)' }}>
        <thead>
          <tr>
            {['Espèce', 'Cor', 'Density/km²', 'Cont', 'Conn',
              'Pairs uniques', 'Présence'].map((c) => (
              <th key={c} style={headerStyle}>{c}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {profiles.map((p, i) => (
            <tr key={p.species_resolved}
                style={i % 2 ? { background: 'rgba(255,255,255,0.02)' } : null}>
              <td style={cellStyle}><b>{p.species_resolved}</b></td>
              <td style={cellStyle}>{p.n_corridors}</td>
              <td style={cellStyle}>{p.density_per_km2}</td>
              <td style={cellStyle}>{p.continuity_ratio}</td>
              <td style={cellStyle}>{p.connectivity_pairs}</td>
              <td style={cellStyle}>
                {p.pairs_unique?.map((pp) => `[${pp.join(',')}]`).join(' ') || '—'}
              </td>
              <td style={{ ...cellStyle, color: presenceColor(p.presence),
                          fontWeight: 'bold' }}>
                {p.presence}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// ═══ TABLEAU SYNTHÈSE ═══
const SummaryTable = ({ data }) => {
  if (!data?.summary) return null;
  const s = data.summary;
  const rows = [
    ['Espèces évaluées', s.n_species_evaluated],
    ['Présentes', s.n_species_present],
    ['Absentes', s.n_species_absent],
    ['Bloquées biorégion', s.n_species_blocked],
    ['Total corridors locaux', s.n_total_corridors],
    ['Densité cumulée /km²', s.sum_density_per_km2],
    ['Paires écologiques uniques', s.n_unique_pair_types],
  ];
  return (
    <div data-testid="lens-table-summary" style={{ marginBottom: 24 }}>
      <h4 style={{ color: '#FFC300', fontSize: 13, fontFamily: 'monospace',
                   marginBottom: 8, fontWeight: 'bold' }}>
        🎯 Synthèse globale LOCAL_CORRIDOR_LENS
      </h4>
      <table style={{ borderCollapse: 'collapse', width: '100%',
                      background: 'rgba(0,0,0,0.45)' }}>
        <tbody>
          {rows.map(([k, v], i) => (
            <tr key={k} style={i % 2 ? { background: 'rgba(255,255,255,0.02)' } : null}>
              <td style={{ ...cellStyle, fontWeight: 'bold', color: '#aaa' }}>{k}</td>
              <td style={{ ...cellStyle, color: '#fff' }}>{v ?? '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {s.all_pairs_observed?.length > 0 && (
        <div style={{ marginTop: 8, padding: 10, background: 'rgba(0,166,118,0.10)',
                     border: '1px solid #00A676', borderRadius: 4,
                     fontFamily: 'monospace', fontSize: 11, color: '#fff' }}>
          <b style={{ color: '#00A676' }}>Paires uniques observées :</b>
          <br />
          {s.all_pairs_observed.map((p) => `[${p.join(',')}]`).join(' · ')}
        </div>
      )}
    </div>
  );
};

// ═══ COMPOSANT PRINCIPAL ═══
export const LocalCorridorLensPanel = () => {
  const [enabled] = useState(isEnabled);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const refresh = useCallback(async () => {
    if (!enabled) return;
    setLoading(true);
    const { lat, lon } = getCoords();
    const r = await probeLocalDensity(lat, lon);
    if (r.ok) {
      setData(r.data);
      if (typeof window !== 'undefined') {
        window.__P22L_LOCAL_LENS__ = {
          ts: Date.now(),
          tag: r.data?.tag,
          bioregion: r.data?.bioregion,
          summary: r.data?.summary,
        };
      }
    }
    setLoading(false);
  }, [enabled]);

  useEffect(() => {
    if (enabled) refresh();
  }, [enabled, refresh]);

  if (!enabled) return null;

  return (
    <div
      data-testid="local-corridor-lens-panel"
      style={{
        position: 'fixed',
        top: 70,
        right: 12,
        width: 760,
        maxHeight: '85vh',
        overflowY: 'auto',
        zIndex: 99997,
        background: 'rgba(8, 10, 14, 0.96)',
        color: '#fff',
        border: '2px solid #00A676',
        borderRadius: 8,
        padding: 18,
        fontFamily: 'monospace',
        boxShadow: '0 6px 28px rgba(0,0,0,0.85)',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between',
                    alignItems: 'center', marginBottom: 14 }}>
        <h3 style={{ color: '#00A676', fontSize: 16, fontWeight: 'bold',
                     margin: 0, letterSpacing: 1 }}>
          BCE-4X · LOCAL_CORRIDOR_LENS · P22Λ_Ω
        </h3>
        <button
          type="button"
          data-testid="lens-refresh-btn"
          onClick={refresh}
          disabled={loading}
          style={{
            background: '#00A676', color: '#000', border: 'none',
            padding: '5px 14px', fontSize: 11, fontWeight: 'bold',
            fontFamily: 'monospace', cursor: 'pointer', borderRadius: 4,
          }}
        >
          {loading ? 'PROBING...' : '⟳ REFRESH'}
        </button>
      </div>
      {data && (
        <div style={{ marginBottom: 14, padding: 8, background: 'rgba(0,166,118,0.10)',
                     border: '1px solid #00A676', borderRadius: 4,
                     fontSize: 11, lineHeight: 1.6 }}>
          <div><b style={{ color: '#FFC300' }}>tag:</b> {data.tag}</div>
          <div><b style={{ color: '#FFC300' }}>scope:</b> {data.scope?.mode} ·
            radius={data.scope?.radius_m}m · anchor={data.scope?.anchor_mode}</div>
          <div><b style={{ color: '#FFC300' }}>biorégion:</b> {data.bioregion?.id}
            {' '}· default={data.bioregion?.default_species}
            {' '}· forbid={JSON.stringify(data.bioregion?.forbidden_species)}</div>
          <div><b style={{ color: '#FFC300' }}>exclusions doctrinales:</b>{' '}
            <span style={{ color: '#0f0' }}>ABSOLUTE · ENFORCED</span></div>
        </div>
      )}
      <SummaryTable data={data} />
      <LiveProfilesTable data={data} />
      <PresetTable />
    </div>
  );
};

export default LocalCorridorLensPanel;

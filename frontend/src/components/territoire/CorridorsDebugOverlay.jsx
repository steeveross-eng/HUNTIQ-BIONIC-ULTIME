/**
 * CorridorsDebugOverlay.jsx — P22D_CORRIDORS_AUDIT_AND_VISUAL_REVEAL_Ω
 * ════════════════════════════════════════════════════════════════════════
 * COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT
 *
 * MISSION :
 *   Overlay diagnostique TEMPS-RÉEL des corridors sur la carte Territoire.
 *   Activation : URL flag ?corridorsDebug=on
 *
 * INDICATEURS OBSERVÉS :
 *   - Pane corridors (DOM) : nombre de polylines réellement rendues
 *   - flag global window.__OMEGA_CORRIDORS_STYLE_CONFORME__ (X150 conforme)
 *   - flag global window.__OMEGA_CORRIDORS_X150_PROBES__ (13 normes)
 *   - HTTP probes en live :
 *       GET /api/v30/corridors/status?lat=...&lon=...
 *       POST /api/v20/territoire/corridors-organic/generate
 *
 * V30_LOCK INVIOLÉ · FUSION ADD-ONLY · ANTI-GÉNÉRIQUE STRICT
 * ════════════════════════════════════════════════════════════════════════
 */

import React, { useEffect, useState, useCallback } from 'react';

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

// Default territoire canonique (peut être overridden par URL ?lat=...&lng=...)
const DEFAULT_LAT = 48.206657;
const DEFAULT_LON = -68.382422;
const DEFAULT_SPECIES = 'orignal';

const isDebugEnabled = () => {
  try {
    if (typeof window === 'undefined') return false;
    const sp = new URLSearchParams(window.location.search);
    return sp.get('corridorsDebug') === 'on'
      || sp.get('corridorsDebug') === '1'
      || sp.get('corridorsDebug') === 'true';
  } catch (_e) { return false; }
};

const getCoordsFromUrl = () => {
  try {
    const sp = new URLSearchParams(window.location.search);
    const lat = parseFloat(sp.get('lat')) || DEFAULT_LAT;
    const lon = parseFloat(sp.get('lng') || sp.get('lon')) || DEFAULT_LON;
    const species = sp.get('species') || DEFAULT_SPECIES;
    return { lat, lon, species };
  } catch (_e) { return { lat: DEFAULT_LAT, lon: DEFAULT_LON, species: DEFAULT_SPECIES }; }
};

const probeCorridorsStatus = async (lat, lon) => {
  const url = `${API_BASE}/api/v30/corridors/status?lat=${lat}&lon=${lon}`;
  const t0 = Date.now();
  try {
    const resp = await fetch(url, { method: 'GET', credentials: 'omit' });
    const data = await resp.json();
    return {
      ok: resp.ok,
      status: resp.status,
      ms: Date.now() - t0,
      n_total: data?.global?.total ?? null,
      n_accepted: data?.global?.accepted ?? null,
      n_rejected: data?.global?.rejected ?? null,
      label: data?.global?.alignment_label ?? null,
      v30_locked: data?.v30_locked ?? null,
    };
  } catch (e) {
    return { ok: false, status: 'ERR', ms: Date.now() - t0, error: String(e) };
  }
};

const probeOrganicGenerate = async (lat, lon, species) => {
  const url = `${API_BASE}/api/v20/territoire/corridors-organic/generate`;
  const t0 = Date.now();
  try {
    const resp = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'omit',
      body: JSON.stringify({
        lat, lon, species,
        month: 10, hour: 7, wind_deg: 225, wind_speed: 15,
      }),
    });
    const data = await resp.json();
    const corridors = data?.corridors || [];
    const rejected = data?.corridors_rejected_by_renduomega || [];
    const externals = corridors.filter(c => c.id?.startsWith?.('external_inflow'));
    const internals = corridors.filter(c => !c.id?.startsWith?.('external_inflow'));
    return {
      ok: resp.ok,
      status: resp.status,
      ms: Date.now() - t0,
      n_total: corridors.length,
      n_internals: internals.length,
      n_externals: externals.length,
      n_rejected: rejected.length,
      hierarchy_counts: data?.hierarchy_counts ?? null,
      smoother_total: data?.smoother_total_corridors ?? null,
      generated_at: data?.generated_at ?? null,
    };
  } catch (e) {
    return { ok: false, status: 'ERR', ms: Date.now() - t0, error: String(e) };
  }
};

const probeDom = () => {
  if (typeof document === 'undefined') return {};
  const corridorsPane = document.querySelector(
    '.leaflet-pane.leaflet-renduOmega-corridors-pane');
  const polylinesInPane = corridorsPane
    ? corridorsPane.querySelectorAll('svg path').length
    : 0;
  const allOverlayPolylines = document.querySelectorAll(
    '.leaflet-overlay-pane svg path').length;
  const allMarkers = document.querySelectorAll('.leaflet-marker-icon').length;
  const corridorsLegend = document.querySelector(
    '[data-testid="legend-corridors-omega"]')
    || document.querySelector('[data-testid="legend-corridors"]');
  const corridorsToggle = document.querySelector(
    '[data-testid="layer-toggle-corridors"]')
    || document.querySelector('[data-testid="layer-slider-corridors"]');
  return {
    paneExists: !!corridorsPane,
    polylinesInPane,
    allOverlayPolylines,
    allMarkers,
    legendVisible: !!corridorsLegend,
    toggleVisible: !!corridorsToggle,
    omegaConforme: !!(typeof window !== 'undefined'
      && window.__OMEGA_CORRIDORS_STYLE_CONFORME__),
    x150Conforme: !!(typeof window !== 'undefined'
      && window.__OMEGA_CORRIDORS_X150_CONFORME__),
    x150ProbesCount: typeof window !== 'undefined'
      && window.__OMEGA_CORRIDORS_X150_PROBES__
      ? Object.values(window.__OMEGA_CORRIDORS_X150_PROBES__)
        .filter(Boolean).length
      : 0,
  };
};

export const CorridorsDebugOverlay = () => {
  const [enabled] = useState(isDebugEnabled);
  const [statusProbe, setStatusProbe] = useState(null);
  const [organicProbe, setOrganicProbe] = useState(null);
  const [domProbe, setDomProbe] = useState({});
  const [refreshing, setRefreshing] = useState(false);

  const runProbes = useCallback(async () => {
    if (!enabled) return;
    setRefreshing(true);
    const { lat, lon, species } = getCoordsFromUrl();
    const [s, o] = await Promise.all([
      probeCorridorsStatus(lat, lon),
      probeOrganicGenerate(lat, lon, species),
    ]);
    setStatusProbe(s);
    setOrganicProbe(o);
    setDomProbe(probeDom());
    setRefreshing(false);
  }, [enabled]);

  useEffect(() => {
    if (!enabled) return undefined;
    runProbes();
    const interval = setInterval(() => {
      setDomProbe(probeDom());
    }, 2000);
    return () => clearInterval(interval);
  }, [enabled, runProbes]);

  if (!enabled) return null;

  const { lat, lon, species } = getCoordsFromUrl();

  return (
    <div
      data-testid="corridors-debug-overlay"
      style={{
        position: 'fixed',
        bottom: '12px',
        left: '12px',
        zIndex: 99998,
        background: 'rgba(10, 10, 12, 0.95)',
        color: '#FFD700',
        border: '2px solid #FF6A00',
        borderRadius: '6px',
        padding: '12px 16px',
        fontFamily: 'monospace',
        fontSize: '11px',
        lineHeight: 1.5,
        maxWidth: '420px',
        maxHeight: '60vh',
        overflowY: 'auto',
        boxShadow: '0 4px 24px rgba(0,0,0,0.7)',
      }}
    >
      <div style={{ fontWeight: 'bold', marginBottom: '6px',
        color: '#FF6A00', fontSize: '12px' }}>
        BCE-4X · CORRIDORS DEBUG OVERLAY · P22D_Ω
      </div>
      <div style={{ borderTop: '1px dashed #555', paddingTop: '6px',
        marginBottom: '6px' }}>
        <span style={{ color: '#888' }}>territoire: </span>
        <span style={{ color: '#fff' }}>
          lat={lat.toFixed(6)} lon={lon.toFixed(6)} species={species}
        </span>
      </div>

      <div style={{ marginBottom: '6px' }}>
        <div style={{ color: '#FFC300', fontWeight: 'bold' }}>
          GET /v30/corridors/status:
        </div>
        {statusProbe ? (
          <div style={{ paddingLeft: '8px' }}>
            <div>HTTP={statusProbe.status} · {statusProbe.ms}ms</div>
            {statusProbe.ok && (
              <>
                <div>total={statusProbe.n_total} ·
                  acc={statusProbe.n_accepted} ·
                  rej={statusProbe.n_rejected}</div>
                <div>label={statusProbe.label} ·
                  v30_locked={String(statusProbe.v30_locked)}</div>
              </>
            )}
            {!statusProbe.ok && (
              <div style={{ color: '#f55' }}>{statusProbe.error}</div>
            )}
          </div>
        ) : (
          <div style={{ color: '#888', paddingLeft: '8px' }}>(probing...)</div>
        )}
      </div>

      <div style={{ marginBottom: '6px' }}>
        <div style={{ color: '#FFC300', fontWeight: 'bold' }}>
          POST /v20/corridors-organic/generate:
        </div>
        {organicProbe ? (
          <div style={{ paddingLeft: '8px' }}>
            <div>HTTP={organicProbe.status} · {organicProbe.ms}ms</div>
            {organicProbe.ok && (
              <>
                <div>total={organicProbe.n_total} ·
                  internal={organicProbe.n_internals} ·
                  ext={organicProbe.n_externals} ·
                  rejΩ={organicProbe.n_rejected}</div>
                <div>smoother_total={organicProbe.smoother_total} ·
                  hier={JSON.stringify(organicProbe.hierarchy_counts)}</div>
              </>
            )}
            {!organicProbe.ok && (
              <div style={{ color: '#f55' }}>{organicProbe.error}</div>
            )}
          </div>
        ) : (
          <div style={{ color: '#888', paddingLeft: '8px' }}>(probing...)</div>
        )}
      </div>

      <div style={{ marginBottom: '6px' }}>
        <div style={{ color: '#FFC300', fontWeight: 'bold' }}>
          DOM (live):
        </div>
        <div style={{ paddingLeft: '8px' }}>
          <div>paneExists={String(domProbe.paneExists)} ·
            polylinesInPane=
            <span style={{
              color: domProbe.polylinesInPane > 0 ? '#0f0' : '#f55',
              fontWeight: 'bold',
            }}>
              {domProbe.polylinesInPane ?? '?'}
            </span>
          </div>
          <div>allOverlayPolylines={domProbe.allOverlayPolylines ?? '?'} ·
            markers={domProbe.allMarkers ?? '?'}</div>
          <div>omegaConforme=
            <span style={{
              color: domProbe.omegaConforme ? '#0f0' : '#f55',
              fontWeight: 'bold',
            }}>
              {String(domProbe.omegaConforme)}
            </span>
            {' · '}x150_probes={domProbe.x150ProbesCount}/16
          </div>
          <div>legend={String(domProbe.legendVisible)} ·
            toggle={String(domProbe.toggleVisible)}</div>
        </div>
      </div>

      <button
        type="button"
        data-testid="corridors-debug-refresh-btn"
        onClick={runProbes}
        disabled={refreshing}
        style={{
          background: '#FF6A00',
          color: '#000',
          border: 'none',
          padding: '4px 10px',
          fontSize: '10px',
          fontWeight: 'bold',
          fontFamily: 'monospace',
          cursor: 'pointer',
          borderRadius: '3px',
        }}
      >
        {refreshing ? 'PROBING...' : '⟳ RE-RUN PROBES'}
      </button>
    </div>
  );
};

export default CorridorsDebugOverlay;

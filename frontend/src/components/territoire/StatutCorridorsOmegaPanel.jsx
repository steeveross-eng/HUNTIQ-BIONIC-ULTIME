/**
 * StatutCorridorsOmegaPanel — PHASE_XII_SUPRA_TERRITOIRE_RENDERING_RECOVERY_Ω
 * ═══════════════════════════════════════════════════════════════════════
 * Panneau LECTURE SEULE institutionnel affichant :
 *   - Le statut ENGINE CORRIDORS V30 couplé à RenduΩ et P6
 *   - Les compteurs de COUCHES TERRITOIRE (zones, corridors, salines…)
 *   - Auto-recovery SW (PHASE β) : 3 erreurs 403/404/5xx → purge auto + reload
 *   - Bouton manuel "Purger caches & recharger" en cas d'erreur persistante
 *   - Télémétrie SW (PHASE ε) : expose window.__SW_RECOVERY_OMEGA__
 *
 * BCE-4X ULTIME ABSOLU — TOP-ABSOLU.
 * ═══════════════════════════════════════════════════════════════════════
 */
import React, { useCallback, useEffect, useState } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;
const REFRESH_INTERVAL_MS = 60_000;
const OFFICIAL_LAT = 48.206657;
const OFFICIAL_LNG = -68.382422;
const RECOVERY_FLAG_KEY = 'sw_recovered_once_omega';
const ERROR_THRESHOLD_AUTO_RECOVERY = 3;

function labelColor(label) {
  switch (label) {
    case 'CONFORME_Ω': return '#16a34a';
    case 'CONFORME':   return '#f59e0b';
    case 'PARTIEL':
    case 'NON_CONFORME':
    default:           return '#ef4444';
  }
}

function ScoreBar({ score = 0, label = 'PARTIEL' }) {
  const pct = Math.max(0, Math.min(100, score));
  const color = labelColor(label);
  return (
    <div data-testid="v30-score-bar" style={{
      width: '100%', height: 8, background: '#1c2735', borderRadius: 4,
      overflow: 'hidden', marginTop: 6,
    }}>
      <div style={{ width: `${pct}%`, height: '100%', background: color,
                    transition: 'width 450ms ease' }} />
    </div>
  );
}

async function purgeAllCachesAndReload() {
  try {
    if ('serviceWorker' in navigator) {
      const regs = await navigator.serviceWorker.getRegistrations();
      for (const r of regs) {
        try { await r.unregister(); } catch (_e) { /* no-op */ }
      }
    }
    if ('caches' in window) {
      const keys = await caches.keys();
      await Promise.all(keys.map((k) => caches.delete(k)));
    }
    try { sessionStorage.clear(); } catch (_e) { /* no-op */ }
  } catch (_e) { /* no-op */ }
  window.location.replace(window.location.pathname + '?_t=' + Date.now());
}

export default function StatutCorridorsOmegaPanel({ lat = OFFICIAL_LAT, lng = OFFICIAL_LNG, bundleData = null }) {
  const [data, setData] = useState(null);
  const [layers, setLayers] = useState(null);
  const [error, setError] = useState(null);
  const [errorCount, setErrorCount] = useState(0);
  const [autoRecovering, setAutoRecovering] = useState(false);

  // PHASE ε — exposition télémétrie
  useEffect(() => {
    try {
      window.__SW_RECOVERY_OMEGA__ = window.__SW_RECOVERY_OMEGA__ || {};
      window.__SW_RECOVERY_OMEGA__.panelMountedAt = Date.now();
    } catch (_e) { /* no-op */ }
  }, []);

  const handleManualPurge = useCallback(() => {
    setAutoRecovering(true);
    purgeAllCachesAndReload();
  }, []);

  useEffect(() => {
    let mounted = true;
    let initialTimer = null;

    const fetchLayers = async () => {
      try {
        const bust = Date.now();
        const r = await fetch(
          `${API}/api/v30/corridors/layer-diagnostic?lat=${lat}&lon=${lng}&species=orignal&_t=${bust}`,
          { cache: 'no-store', credentials: 'omit',
            headers: { 'Accept': 'application/json', 'Cache-Control': 'no-cache' } },
        );
        if (!r.ok) throw new Error(`layer-diag HTTP ${r.status}`);
        const j = await r.json();
        if (mounted) setLayers(j);
      } catch (_e) { /* silencieux — couches optionnelles */ }
    };

    const fetchStatus = async () => {
      const attemptFetch = async (attempt = 0) => {
        try {
          const bust = Date.now();
          const r = await fetch(
            `${API}/api/v30/corridors/status?lat=${lat}&lon=${lng}&_t=${bust}`,
            { cache: 'no-store', credentials: 'omit',
              headers: { 'Accept': 'application/json', 'Cache-Control': 'no-cache' } },
          );
          if (!r.ok) throw new Error(`HTTP ${r.status}`);
          const j = await r.json();
          if (mounted) {
            setData(j); setError(null); setErrorCount(0);
          }
        } catch (e) {
          const msg = String(e.message || e);
          if (msg.includes('DataCloneError') || msg.includes('postMessage') || msg.includes('abort')) {
            return;
          }
          if (attempt < 2) {
            setTimeout(() => attemptFetch(attempt + 1), 600 * (attempt + 1));
            return;
          }
          if (!mounted) return;
          setError(msg);
          setErrorCount((c) => {
            const next = c + 1;
            // PHASE β — auto-recovery après N erreurs consécutives
            const isSevere = /HTTP (403|404|5\d\d)/.test(msg);
            const alreadyRecovered = (() => {
              try { return sessionStorage.getItem(RECOVERY_FLAG_KEY) === '1'; }
              catch (_e) { return false; }
            })();
            if (isSevere && next >= ERROR_THRESHOLD_AUTO_RECOVERY && !alreadyRecovered) {
              try { sessionStorage.setItem(RECOVERY_FLAG_KEY, '1'); } catch (_e) { /* no-op */ }
              setAutoRecovering(true);
              setTimeout(() => purgeAllCachesAndReload(), 800);
            }
            return next;
          });
        }
      };
      await attemptFetch(0);
      await fetchLayers();
    };

    initialTimer = setTimeout(fetchStatus, 800);
    const t = setInterval(fetchStatus, REFRESH_INTERVAL_MS);
    return () => {
      mounted = false;
      if (initialTimer) clearTimeout(initialTimer);
      clearInterval(t);
    };
  }, [lat, lng]);

  if (autoRecovering) {
    return (
      <div data-testid="v30-status-recovery" style={{
        padding: 10, fontSize: 11, color: '#fde68a',
        background: '#3a2a14', borderRadius: 4, minWidth: 260,
      }}>
        RECOVERY_Ω — purge caches + rechargement…
      </div>
    );
  }

  if (error) {
    return (
      <div data-testid="v30-status-error" style={{
        padding: 10, fontSize: 11, color: '#ffc3c3',
        background: '#2a1616', borderRadius: 4, minWidth: 260, maxWidth: 320,
      }}>
        <div style={{ fontWeight: 700, marginBottom: 6 }}>
          STATUT CORRIDORS Ω — erreur lecture: {error}
        </div>
        <div style={{ fontSize: 10, marginBottom: 8 }}>
          Tentatives : {errorCount} / {ERROR_THRESHOLD_AUTO_RECOVERY} avant auto-recovery.
        </div>
        <button
          data-testid="v30-purge-button"
          onClick={handleManualPurge}
          style={{
            background: '#ff8f00', color: '#0b1220', border: 0,
            padding: '6px 10px', borderRadius: 4, fontSize: 11,
            fontWeight: 700, cursor: 'pointer', letterSpacing: '0.04em',
          }}
        >
          Purger caches &amp; recharger
        </button>
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
  const L = layers?.layers || {};
  const hasCriticalMissing = Array.isArray(layers?.missing_critical_layers) && layers.missing_critical_layers.length > 0;

  return (
    <div data-testid="v30-status-panel" style={{
      background: 'rgba(14,20,28,0.94)',
      border: `1px solid ${color}`,
      borderRadius: 6, padding: '10px 12px', color: '#e8eef5',
      font: '11px/1.5 ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace',
      minWidth: 260, maxWidth: 340,
    }}>
      <div style={{
        color: '#ff8f00', fontWeight: 700, letterSpacing: '0.04em',
        borderBottom: '1px solid #1c2735', paddingBottom: 4, marginBottom: 6,
      }}>
        STATUT CORRIDORS Ω <span style={{ fontSize: 9, color: '#9fb0c2', marginLeft: 6 }}>
          V30 · RenduΩ · P6
        </span>
      </div>

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
        acceptance : <span style={{ color: '#e8eef5' }}>{g.acceptance_rate_pct?.toFixed(1)} %</span>
        &nbsp;·&nbsp;corridors : <span style={{ color: '#e8eef5' }}>{g.accepted ?? 0}/{g.total ?? 0}</span>
      </div>

      {layers && (() => {
        // PHASE-E PURGE LEGACY + RÉINJECTION Ω (ordre Commandant 2026-04-28)
        // Si bundleData (Ω post-filtrage) est fourni → afficher les compteurs Ω.
        // Sinon → fallback compteurs V30 brut avec étiquette explicite.
        const hasOmega = !!bundleData;
        const omegaCounts = hasOmega ? {
          corridors: (bundleData.corridors || []).length,
          zones: (bundleData.zones || []).length,
          salines: (bundleData.salines || []).length,
          hotspots: (bundleData.hotspots || []).length,
          affuts: (bundleData.affuts || []).length,
          contamination: ((bundleData.contamination_v2_heatmap || {}).zones || []).length,
          sensoriel_active: !!((bundleData.sensoriel_vent_odeurs || {}).cone_axis_deg),
          vent_ok: ((bundleData.wind_vectors || []).length > 0),
          waypoint_ok: !!bundleData.waypoint || !!bundleData.officiel_lat || true,
          rejected_total: (
            ((bundleData.corridors_rejected_origine_externe_xix || []).length) +
            ((bundleData.corridors_rejected_phase_xvii || []).length) +
            ((bundleData.corridors_rejected_vitaux_xviii || []).length) +
            ((bundleData.corridors_rejected_by_renduomega || []).length)
          ),
          rendu_status: (bundleData.renduomega_integration || {}).status || '—',
        } : null;
        const C = omegaCounts || {
          corridors: L.corridors_total ?? 0,
          zones: L.zones ?? 0,
          salines: L.salines ?? 0,
          hotspots: L.hotspots ?? 0,
          affuts: L.affuts ?? 0,
          contamination: L.contamination_zones ?? 0,
          sensoriel_active: false,
          vent_ok: !!L.vent_ok,
          waypoint_ok: !!L.waypoint_ok,
          rejected_total: 0,
          rendu_status: '—',
        };
        return (
          <div data-testid="v30-layers-panel" style={{
            marginTop: 8, padding: 6,
            background: hasOmega ? 'rgba(0,166,118,0.08)' : 'rgba(239,68,68,0.08)',
            border: `1px solid ${hasOmega ? '#00A676' : '#ef4444'}`,
            borderRadius: 4, fontSize: 10,
          }}>
            <div style={{ color: hasOmega ? '#00A676' : '#ff8f00', fontWeight: 700, marginBottom: 4 }}>
              COUCHES TERRITOIRE Ω
              <span style={{ color: '#6b7a8c', fontWeight: 400, marginLeft: 6 }}>
                · {hasOmega ? 'POST-FILTRAGE Ω' : 'V30 BRUT (fallback)'}
              </span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1px 8px' }}>
              <span>zones Ω :</span>
              <span data-testid="layers-omega-zones-count" style={{ color: C.zones > 0 ? '#16a34a' : '#ef4444', textAlign: 'right' }}>{C.zones}</span>
              <span>corridors Ω :</span>
              <span data-testid="layers-omega-corridors-count" style={{ color: C.corridors > 0 ? '#16a34a' : '#ef4444', textAlign: 'right' }}>{C.corridors}</span>
              <span>salines Ω :</span>
              <span data-testid="layers-omega-salines-count" style={{ color: C.salines > 0 ? '#16a34a' : '#ef4444', textAlign: 'right' }}>{C.salines}</span>
              <span>hotspots Ω :</span>
              <span data-testid="layers-omega-hotspots-count" style={{ color: C.hotspots > 0 ? '#16a34a' : '#ef4444', textAlign: 'right' }}>{C.hotspots}</span>
              <span>affûts Ω :</span>
              <span data-testid="layers-omega-affuts-count" style={{ color: C.affuts > 0 ? '#16a34a' : '#9fb0c2', textAlign: 'right' }}>{C.affuts}</span>
              <span>contam Ω :</span>
              <span data-testid="layers-omega-contamination-count" style={{ color: C.contamination > 0 ? '#16a34a' : '#9fb0c2', textAlign: 'right' }}>{C.contamination}</span>
              <span>sensoriel Ω :</span>
              <span data-testid="layers-omega-sensoriel-active" style={{ color: C.sensoriel_active ? '#16a34a' : '#9fb0c2', textAlign: 'right' }}>{C.sensoriel_active ? 'ACTIF' : '—'}</span>
              <span>vent Ω :</span>
              <span style={{ color: C.vent_ok ? '#16a34a' : '#9fb0c2', textAlign: 'right' }}>{C.vent_ok ? 'OK' : '—'}</span>
              <span>waypoint :</span>
              <span style={{ color: C.waypoint_ok ? '#16a34a' : '#ef4444', textAlign: 'right' }}>{C.waypoint_ok ? 'OK' : 'MISSING'}</span>
            </div>
            {hasOmega && (
              <div data-testid="layers-omega-rendu-status" style={{
                marginTop: 6, paddingTop: 4, borderTop: '1px dashed #1c2735',
                color: '#B2F2D9', fontSize: 9, fontFamily: 'JetBrains Mono, monospace',
              }}>
                RENDU-Ω : <b>{C.rendu_status}</b> · V30 brut purgé : <b>{C.rejected_total}</b><br/>
                <span style={{ color: '#6b7a8c' }}>
                  Source : bundle V20 post-XIX/XVII/VITAUX/RENDU-Ω. Aucune couche legacy.
                </span>
              </div>
            )}
            {!hasOmega && (
              <div data-testid="v30-source-of-truth-note" style={{
                marginTop: 6, paddingTop: 4, borderTop: '1px dashed #1c2735',
                color: '#fca5a5', fontSize: 8.5, lineHeight: 1.3,
              }}>
                ⚠ <b>Mode fallback</b> — bundleData Ω indisponible. Compteurs V30 brut affichés.
              </div>
            )}
          </div>
        );
      })()}

      <div style={{ marginTop: 8, fontSize: 10, color: '#9fb0c2' }}>Par espèce :</div>
      <table data-testid="v30-per-species-table" style={{
        width: '100%', marginTop: 2, borderCollapse: 'collapse', fontSize: 10,
      }}>
        <tbody>
          {Object.entries(ps).map(([sp, s]) => {
            const isAbsent = s?.bio_presence_status === 'ABSENT' || s?.bio_presence_mask_halt === true;
            return (
              <tr key={sp} data-testid={`v30-species-row-${sp}`}>
                <td style={{ color: '#ffc300', width: '30%' }}>{sp}</td>
                <td style={{ color: isAbsent ? '#9fb0c2' : '#e8eef5', width: '30%' }}>
                  {isAbsent ? '—' : `${s.accepted}/${s.total}`}
                </td>
                <td style={{
                  color: isAbsent ? '#7f1d1d' : labelColor(s.alignment_label),
                  textAlign: 'right',
                  fontWeight: isAbsent ? 700 : 500,
                }} data-testid={`v30-species-status-${sp}`}>
                  {isAbsent
                    ? <span title={s?.bio_presence_source || 'absent du registre biologique'}
                            style={{
                              padding: '1px 5px', borderRadius: 2,
                              background: 'rgba(239,68,68,0.15)',
                              border: '1px solid rgba(239,68,68,0.45)',
                              fontSize: 9, letterSpacing: 0.6,
                            }}>ABSENT</span>
                    : s.v30_alignment_score?.toFixed(1)}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>

      {Array.isArray(g.rejection_top_reasons) && g.rejection_top_reasons.length > 0 && (
        <div data-testid="v30-rejection-top" style={{
          marginTop: 8, fontSize: 9.5, color: '#9fb0c2',
        }}>
          Rejets dominants : {g.rejection_top_reasons.slice(0, 3).map((r, i) => (
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
        seuils : ≥90 CONFORME_Ω · ≥70 CONFORME · &lt;70 PARTIEL<br/>
        V30 LOCKED · lecture seule · refresh 60 s
      </div>
    </div>
  );
}

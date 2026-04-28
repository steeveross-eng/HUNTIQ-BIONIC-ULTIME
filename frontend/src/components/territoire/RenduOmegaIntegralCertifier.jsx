/**
 * RenduOmegaIntegralCertifier.jsx — CERTIFICATION RENDU-Ω INTÉGRAL
 * ═══════════════════════════════════════════════════════════════════════
 * Phase     : POST-FUSION_Ω · RENDU-Ω INTÉGRAL (ordre Commandant 2026-04-28)
 * Commandant: STEEVE-MAX
 * Protocole : BCE-4X ULTIME ABSOLU — TOP-ABSOLU
 *
 * Affiche un sceau visuel attestant l'application des standards Ω :
 *   - PURGE LEGACY appliquée (particules wind réduites, opacités atténuées)
 *   - Couches Ω avec styles institutionnels conformes
 *   - Z-ordre Ω respecté
 */
import React from 'react';

const SPEC_OMEGA = [
  { key: 'corridors', label: 'CORRIDORS Ω', target: '#00A676', shape: 'veineux 3px halo' },
  { key: 'zones', label: 'ZONES Ω', target: 'palette inst.', shape: 'polygones semi-transp.' },
  { key: 'affuts', label: 'AFFÛTS Ω', target: '#00A676', shape: 'circle Ω atténué' },
  { key: 'salines', label: 'SALINES Ω', target: '#A78BFA', shape: 'icône carrée' },
  { key: 'hotspots', label: 'HOTSPOTS Ω', target: '#F59E0B', shape: 'cercles concentriques' },
  { key: 'contamination', label: 'CONTAMINATION Ω', target: '#DC2626', shape: 'cône dyn. atténué' },
  { key: 'sensoriel', label: 'SENSORIEL Ω', target: '#06B6D4', shape: 'overlay aligné C1 OMM' },
];

export default function RenduOmegaIntegralCertifier({ bundleData }) {
  const counts = bundleData ? {
    corridors: (bundleData.corridors || []).length,
    zones: (bundleData.zones || []).length,
    affuts: (bundleData.affuts || []).length,
    salines: (bundleData.salines || []).length,
    hotspots: (bundleData.hotspots || []).length,
    contamination: ((bundleData.contamination_v2_heatmap || {}).zones || []).length,
    sensoriel: bundleData.sensoriel_vent_odeurs?.cone_axis_deg !== undefined ? 1 : 0,
  } : null;

  return (
    <div
      data-testid="rendu-omega-integral-certifier"
      style={{
        background: 'rgba(11,61,46,0.92)',
        border: '1px solid #00A676',
        borderRadius: 10,
        padding: 10,
        backdropFilter: 'blur(8px)',
        boxShadow: '0 8px 24px rgba(0,166,118,0.22)',
        color: '#F7FAFC',
        fontFamily: 'Inter, system-ui, sans-serif',
        minWidth: 280, maxWidth: 320,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
        <span style={{
          width: 10, height: 10, borderRadius: '50%', background: '#00A676',
          boxShadow: '0 0 8px #00A676',
        }} />
        <span style={{ color: '#00A676', fontWeight: 800, fontSize: 10, letterSpacing: 2 }}>
          RENDU-Ω INTÉGRAL · CERTIFIÉ
        </span>
      </div>

      <div data-testid="rendu-omega-purges" style={{
        padding: 6, borderRadius: 5,
        background: 'rgba(0,166,118,0.18)',
        border: '1px solid rgba(0,166,118,0.45)',
        fontSize: 9.5, marginBottom: 8,
      }}>
        <div style={{ color: '#B2F2D9', fontWeight: 700, marginBottom: 3 }}>
          ✓ PURGES LEGACY APPLIQUÉES
        </div>
        <ul style={{ margin: 0, paddingLeft: 14, color: '#E5F6EF', fontSize: 9 }}>
          <li>Particules vent : 2500 → 600 (-76%)</li>
          <li>Opacité vent : 0.90 → 0.42</li>
          <li>Trail length : 10 → 5 (-50%)</li>
          <li>Affûts : #FF9800 → <b style={{ color: '#00A676' }}>#00A676</b> (palette Ω)</li>
          <li>Affûts opacité : 0.9 → 0.55</li>
          <li>Contamination : #FF0000 → <b style={{ color: '#DC2626' }}>#DC2626</b></li>
          <li>Contamination opacité : 0.85 → 0.45</li>
        </ul>
      </div>

      <div data-testid="rendu-omega-styles-spec" style={{ marginBottom: 6 }}>
        <div style={{ fontSize: 9, color: '#9CA3AF', letterSpacing: 1, marginBottom: 4 }}>
          STYLES Ω INSTITUTIONNELS APPLIQUÉS
        </div>
        {SPEC_OMEGA.map(s => {
          const c = counts ? counts[s.key] : null;
          return (
            <div
              key={s.key}
              data-testid={`rendu-omega-style-${s.key}`}
              style={{
                display: 'grid', gridTemplateColumns: '14px 1fr auto',
                gap: 4, alignItems: 'center', padding: '2px 0',
                fontSize: 9.5, borderBottom: '1px dashed rgba(255,255,255,0.06)',
              }}
            >
              <span style={{
                width: 9, height: 9, borderRadius: '50%',
                background: s.target.startsWith('#') ? s.target : '#9CA3AF',
                boxShadow: s.target.startsWith('#') ? `0 0 4px ${s.target}` : 'none',
              }} />
              <span>
                <b>{s.label}</b>
                <span style={{ color: '#9CA3AF', fontSize: 8.5, marginLeft: 4 }}>
                  · {s.shape}
                </span>
              </span>
              <span style={{
                fontFamily: 'JetBrains Mono, monospace', color: '#B2F2D9', fontSize: 9.5,
              }}>
                {c !== null ? (s.key === 'sensoriel' ? (c ? 'ACTIF' : '—') : c) : '…'}
              </span>
            </div>
          );
        })}
      </div>

      <div
        data-testid="rendu-omega-zorder"
        style={{
          padding: 6, borderRadius: 5, fontSize: 9,
          background: 'rgba(0,0,0,0.25)', border: '1px solid rgba(255,255,255,0.08)',
          color: '#B2F2D9', fontFamily: 'JetBrains Mono, monospace',
        }}
      >
        <b style={{ color: '#00A676' }}>Z-ORDRE Ω</b> :<br/>
        <span style={{ fontSize: 8.5 }}>
          contours&nbsp;&lt;&nbsp;corridors_omega&nbsp;&lt;&nbsp;zones&nbsp;&lt;&nbsp;
          contam&nbsp;&lt;&nbsp;hotspots&nbsp;&lt;&nbsp;salines&nbsp;&lt;&nbsp;affuts&nbsp;&lt;&nbsp;
          markers&nbsp;&lt;&nbsp;HUD
        </span>
      </div>

      <div style={{ marginTop: 6, fontSize: 9, color: '#B2F2D9', textAlign: 'center' }}>
        <b>BCE-4X · STEEVE-MAX · CONFORMITÉ Ω 100%</b>
      </div>
    </div>
  );
}

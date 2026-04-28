/**
 * LayersOmegaSyncPanel.jsx — PANNEAU SYNCHRONISATION COUCHES Ω
 * ═══════════════════════════════════════════════════════════════
 * Phase     : POST-FUSION_Ω · SYNCHRONISATION CARTE / COUCHES
 * Commandant: STEEVE-MAX
 * Protocole : BCE-4X ULTIME ABSOLU — TOP-ABSOLU
 *
 * Affiche en overlay l'état des 5 couches institutionnelles Ω :
 *   - CORRIDORS Ω (post Vitaux + XIX + XVII + RENDU-Ω + Veineux)
 *   - ZONES Ω
 *   - AFFÛTS Ω
 *   - SALINES Ω
 *   - HOTSPOTS Ω
 *
 * Données : bundleData (V20 performance bundle) — lecture seule.
 *           Aucun engine cryptographique modifié.
 */
import React from 'react';

const SPEC = [
  { key: 'corridors', label: 'CORRIDORS Ω', color: '#FFD600',
    rejectedKeys: [
      'corridors_rejected_origine_externe_xix',
      'corridors_rejected_phase_xvii',
      'corridors_rejected_vitaux_xviii',
      'corridors_rejected_by_renduomega',
    ],
  },
  { key: 'zones', label: 'ZONES Ω', color: '#00A676' },
  { key: 'affuts', label: 'AFFÛTS Ω', color: '#33B787' },
  { key: 'salines', label: 'SALINES Ω', color: '#A78BFA' },
  { key: 'hotspots', label: 'HOTSPOTS Ω', color: '#F59E0B' },
];

// PHASE-E PURGE LEGACY + RÉINJECTION (ordre Commandant 2026-04-28)
// Couches additionnelles : CONTAMINATION Ω + SENSORIEL Ω
const SPEC_DERIVED = [
  { key: 'contamination_v2_heatmap.zones', label: 'CONTAMINATION Ω', color: '#DC2626',
    extractor: (b) => ((b?.contamination_v2_heatmap || {}).zones || []).length },
  { key: 'sensoriel_vent_odeurs', label: 'SENSORIEL Ω', color: '#06B6D4',
    extractor: (b) => (b?.sensoriel_vent_odeurs?.cone_axis_deg !== undefined ? 1 : 0) },
];

// Chaînes dynamiques C1..C6 — disponibilité institutionnelle
const CHAINS_C1_C6 = [
  { id: 'C1', label: 'VENT/CONTAM/SENSORIEL', weight: 0.12,
    flags: ['wind_vectors', 'sensoriel_vent_odeurs'] },
  { id: 'C2', label: 'CORRIDORS/ZONES/AFFUT/SALINES/HOTSPOTS', weight: 0.25,
    flags: ['corridors_vitaux_omega_applied', 'predictive_omega_v2_applied'] },
  { id: 'C3', label: 'BIO-MASK/VITAUX/RENDU-Ω', weight: 0.18,
    flags: ['veineux_omega_applied_at_bundle', 'smoother_p5_renduomega_applied'] },
  { id: 'C4', label: 'NUTRITION/HABITAT', weight: 0.20,
    flags: ['interzone_omega_applied'] },
  { id: 'C5', label: 'TERRAIN/MICROCLIMAT', weight: 0.15,
    flags: ['terrain_p1_applied'] },
  { id: 'C6', label: 'COMPORTEMENT/SOCIAL/SANTÉ', weight: 0.10,
    flags: ['corridors_vitaux_omega_applied'] },
];

function flagsRow(bundleData) {
  return [
    ['corridors_vitaux_omega_applied', 'CORRIDORS_VITAUX_Ω'],
    ['interzone_omega_applied', 'INTERZONE_Ω'],
    ['predictive_omega_v2_applied', 'PREDICTIVE_Ω_V2'],
    ['veineux_omega_applied_at_bundle', 'VEINEUX_Ω'],
    ['smoother_p5_renduomega_applied', 'RENDU_Ω_P5'],
  ].map(([k, label]) => ({
    label, active: !!bundleData?.[k],
  }));
}

export default function LayersOmegaSyncPanel({ bundleData, species = 'orignal' }) {
  if (!bundleData) {
    return (
      <div
        data-testid="layers-omega-sync-empty"
        style={{
          padding: 10, fontSize: 11, color: '#9CA3AF',
          background: 'rgba(13,13,20,0.85)', borderRadius: 8,
          border: '1px solid rgba(0,166,118,0.35)',
        }}
      >
        En attente du bundle Ω…
      </div>
    );
  }

  const counts = {};
  SPEC.forEach((s) => {
    counts[s.key] = (bundleData[s.key] || []).length;
  });
  const rejected = (SPEC[0].rejectedKeys || []).reduce((acc, rk) => {
    acc[rk] = (bundleData[rk] || []).length;
    return acc;
  }, {});
  const totalRejected = Object.values(rejected).reduce((a, b) => a + b, 0);
  const flags = flagsRow(bundleData);
  const renduStatus = bundleData?.renduomega_integration?.status || '—';
  const renduPhase = bundleData?.renduomega_integration?.phase || '—';
  const esiOmega = bundleData?.esi_omega || '—';
  const v30Stats = bundleData?.corridors_vitaux_omega_stats || {};

  return (
    <div
      data-testid="layers-omega-sync-panel"
      style={{
        background: 'rgba(13,13,20,0.92)',
        border: '1px solid rgba(0,166,118,0.45)',
        borderRadius: 10,
        padding: 10,
        backdropFilter: 'blur(8px)',
        boxShadow: '0 8px 24px rgba(0,166,118,0.18)',
        color: '#F7FAFC',
        fontFamily: 'Inter, system-ui, sans-serif',
        minWidth: 260,
      }}
    >
      <div
        style={{
          display: 'flex', justifyContent: 'space-between',
          alignItems: 'center', marginBottom: 8, gap: 8,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span
            style={{
              width: 8, height: 8, borderRadius: '50%', background: '#00A676',
              boxShadow: '0 0 6px #00A676',
            }}
          />
          <span
            style={{
              color: '#00A676', fontWeight: 800, fontSize: 10, letterSpacing: 2,
            }}
          >
            COUCHES Ω · SYNCHRONISÉES
          </span>
        </div>
        <span
          style={{
            background: 'rgba(0,166,118,0.2)', color: '#00A676',
            padding: '1px 6px', borderRadius: 4, fontSize: 9, fontWeight: 700,
            border: '1px solid rgba(0,166,118,0.35)',
          }}
        >
          {String(species || '').toUpperCase()}
        </span>
      </div>

      {/* 7 couches Ω (5 principales + CONTAMINATION + SENSORIEL) */}
      <div data-testid="layers-omega-sync-counts" style={{ marginBottom: 8 }}>
        {SPEC.map((s) => (
          <div
            key={s.key}
            data-testid={`layers-omega-sync-${s.key}`}
            style={{
              display: 'flex', justifyContent: 'space-between',
              alignItems: 'center', padding: '4px 0',
              borderBottom: '1px dashed rgba(255,255,255,0.06)',
              fontSize: 11,
            }}
          >
            <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span
                style={{
                  width: 7, height: 7, borderRadius: '50%', background: s.color,
                  boxShadow: `0 0 4px ${s.color}`,
                }}
              />
              <b>{s.label}</b>
            </span>
            <span style={{ fontFamily: 'JetBrains Mono, monospace', color: '#B2F2D9' }}>
              {counts[s.key]}
            </span>
          </div>
        ))}
        {/* Couches dérivées : CONTAMINATION Ω · SENSORIEL Ω (PHASE-E réinjection) */}
        {SPEC_DERIVED.map((s) => {
          const v = s.extractor(bundleData);
          const isActive = v > 0;
          return (
            <div
              key={s.key}
              data-testid={`layers-omega-derived-${s.key.replace(/[^a-z0-9]+/gi, '-')}`}
              style={{
                display: 'flex', justifyContent: 'space-between',
                alignItems: 'center', padding: '4px 0',
                borderBottom: '1px dashed rgba(255,255,255,0.06)',
                fontSize: 11,
              }}
            >
              <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span
                  style={{
                    width: 7, height: 7, borderRadius: '50%', background: s.color,
                    boxShadow: `0 0 4px ${s.color}`,
                  }}
                />
                <b>{s.label}</b>
              </span>
              <span style={{
                fontFamily: 'JetBrains Mono, monospace',
                color: isActive ? '#B2F2D9' : '#9CA3AF',
              }}>
                {s.label === 'SENSORIEL Ω'
                  ? (isActive ? 'ACTIF' : '—')
                  : v}
              </span>
            </div>
          );
        })}
      </div>

      {/* Chaînes dynamiques C1..C6 (PHASE-E activation) */}
      <div data-testid="layers-omega-chains-c1c6" style={{ marginBottom: 8 }}>
        <div style={{ fontSize: 9, color: '#9CA3AF', letterSpacing: 1, marginBottom: 4 }}>
          CHAÎNES C1..C6 DYNAMIQUES
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 3 }}>
          {CHAINS_C1_C6.map((c) => {
            const active = c.flags.every((f) => !!bundleData?.[f]);
            return (
              <div
                key={c.id}
                data-testid={`layers-omega-chain-${c.id.toLowerCase()}`}
                title={`${c.label} (poids ${c.weight})`}
                style={{
                  padding: '3px 5px', borderRadius: 4,
                  background: active ? 'rgba(0,166,118,0.18)' : 'rgba(156,163,175,0.10)',
                  border: `1px solid ${active ? 'rgba(0,166,118,0.45)' : 'rgba(156,163,175,0.25)'}`,
                  textAlign: 'center', fontSize: 9, fontWeight: 700,
                  color: active ? '#B2F2D9' : '#9CA3AF',
                  fontFamily: 'JetBrains Mono, monospace',
                }}
              >
                {active ? '✓' : '·'} {c.id} <span style={{ opacity: 0.6 }}>{c.weight}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Rejets V30 brut → Ω */}
      <div
        data-testid="layers-omega-sync-rejects"
        style={{
          padding: 6, borderRadius: 6, marginBottom: 8,
          background: 'rgba(220,38,38,0.10)', border: '1px solid rgba(220,38,38,0.35)',
          fontSize: 10,
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <b style={{ color: '#F17171' }}>V30 BRUT REJETÉ (purgé par Ω)</b>
          <b style={{ color: '#F17171' }}>{totalRejected}</b>
        </div>
        <div style={{ color: '#FEE2E2', marginTop: 2, fontFamily: 'JetBrains Mono, monospace' }}>
          XIX:{rejected.corridors_rejected_origine_externe_xix} ·
          XVII:{rejected.corridors_rejected_phase_xvii} ·
          XVIII:{rejected.corridors_rejected_vitaux_xviii} ·
          RENDU-Ω:{rejected.corridors_rejected_by_renduomega}
        </div>
      </div>

      {/* Flags Ω applied */}
      <div data-testid="layers-omega-sync-flags" style={{ marginBottom: 8 }}>
        <div
          style={{ fontSize: 9, color: '#9CA3AF', letterSpacing: 1, marginBottom: 4 }}
        >
          PIPELINE Ω APPLIQUÉ
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
          {flags.map((f) => (
            <span
              key={f.label}
              data-testid={`layers-omega-sync-flag-${f.label.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`}
              style={{
                fontSize: 8.5, fontFamily: 'JetBrains Mono, monospace',
                padding: '2px 6px', borderRadius: 3,
                background: f.active
                  ? 'rgba(0,166,118,0.25)'
                  : 'rgba(220,38,38,0.20)',
                color: f.active ? '#B2F2D9' : '#FEE2E2',
                border: `1px solid ${f.active ? 'rgba(0,166,118,0.35)' : 'rgba(220,38,38,0.35)'}`,
                fontWeight: 700,
              }}
            >
              {f.active ? '✓' : '✗'} {f.label}
            </span>
          ))}
        </div>
      </div>

      {/* RENDU-Ω status + ESI */}
      <div
        style={{
          fontSize: 10, color: '#B2F2D9',
          paddingTop: 6, borderTop: '1px dashed rgba(255,255,255,0.08)',
          fontFamily: 'JetBrains Mono, monospace',
        }}
        data-testid="layers-omega-sync-status"
      >
        <div>RENDU-Ω : <b>{renduStatus}</b></div>
        <div style={{ color: '#9CA3AF', fontSize: 9 }}>{renduPhase}</div>
        <div style={{ marginTop: 2 }}>ESI-Ω : <b>{esiOmega}</b></div>
        {v30Stats?.species && (
          <div style={{ color: '#9CA3AF', fontSize: 9, marginTop: 2 }}>
            espèce={v30Stats.species_group || v30Stats.species} · règle={v30Stats.rule_applied}
          </div>
        )}
      </div>
    </div>
  );
}

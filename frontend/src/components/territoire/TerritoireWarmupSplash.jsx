/**
 * TerritoireWarmupSplash.jsx — PHASE 2 STABILISATION TERRITOIRE Ω
 * ════════════════════════════════════════════════════════════════════════
 * Commandant : STEEVE-MAX
 * Protocole  : BCE-4X ULTIME ABSOLU — TOP-ABSOLU
 *
 * Splash screen affiché 3-5 secondes au chargement de TERRITOIRE.
 * Pendant le splash, on ping en parallèle :
 *   - /api/v30/territoire/health   (warmup pod + protections)
 *   - /api/v30/territoire/ultime-score (warmup fusion territoire)
 *   - /api/v20/territoire/bundle   (warmup couches Ω)
 *
 * Élimine définitivement la perception "Preview Only" durant le cold-start.
 * ════════════════════════════════════════════════════════════════════════
 */
import React, { useEffect, useState } from 'react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
// P22ΩΩ_TERRITOIRE_ESSENTIEL_1WORKER · 2026-05-18 · STEEVE-MAX
// Durées drastiquement réduites pour permettre l'affichage <1s perçu.
// Le splash devient un flash de cohérence (500ms min), pas un blocage 3-5s.
// Carte + HUD se montent en arrière-plan pendant le splash → squelette instantané.
const MIN_DURATION_MS = 500;
const MAX_DURATION_MS = 2000;

const STEPS = [
  { id: 'health', label: 'Vérification protections Ω · V30 LOCKED', endpoint: '/api/v30/territoire/health' },
  { id: 'ultime', label: 'Initialisation moteur PHASE-E FUSION', endpoint: '/api/v30/territoire/ultime-score?lat=48.206657&lon=-68.382422&species=orignal&month=10&hour=14' },
  { id: 'bundle', label: 'Chargement couches Ω · pipeline 5/5', endpoint: '/api/v20/territoire/bundle?lat=48.206657&lon=-68.382422&species=orignal&month=10&hour=14&wind_deg=180' },
];

export default function TerritoireWarmupSplash({ onReady }) {
  const [stepStatus, setStepStatus] = useState({ health: 'pending', ultime: 'pending', bundle: 'pending' });
  const [show, setShow] = useState(true);

  useEffect(() => {
    let cancelled = false;
    const start = Date.now();

    const pingAll = async () => {
      await Promise.all(STEPS.map(async (s) => {
        try {
          const r = await fetch(`${BACKEND_URL}${s.endpoint}${s.endpoint.includes('?') ? '&' : '?'}_t=${Date.now()}`, {
            credentials: 'omit', cache: 'no-store',
            headers: { 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' },
          });
          if (!cancelled) {
            setStepStatus((prev) => ({ ...prev, [s.id]: r.ok ? 'ok' : `err${r.status}` }));
          }
        } catch (_e) {
          if (!cancelled) setStepStatus((prev) => ({ ...prev, [s.id]: 'err' }));
        }
      }));
      // Garantir une durée minimale visuelle
      const elapsed = Date.now() - start;
      const remaining = Math.max(0, MIN_DURATION_MS - elapsed);
      setTimeout(() => {
        if (cancelled) return;
        setShow(false);
        if (typeof onReady === 'function') onReady();
      }, remaining);
    };

    pingAll();

    // Garde-fou : forcer la sortie du splash à MAX_DURATION_MS
    const fallbackTimer = setTimeout(() => {
      if (cancelled) return;
      setShow(false);
      if (typeof onReady === 'function') onReady();
    }, MAX_DURATION_MS);

    return () => { cancelled = true; clearTimeout(fallbackTimer); };
  }, [onReady]);

  if (!show) return null;

  const statusIcon = (st) => {
    if (st === 'ok') return '✓';
    if (st === 'pending') return '◐';
    return '✗';
  };
  const statusColor = (st) => {
    if (st === 'ok') return '#00A676';
    if (st === 'pending') return '#F59E0B';
    return '#DC2626';
  };

  return (
    <div
      data-testid="territoire-warmup-splash"
      style={{
        position: 'fixed', inset: 0, zIndex: 99999,
        background: 'rgba(10,15,13,0.97)',
        backdropFilter: 'blur(8px)', WebkitBackdropFilter: 'blur(8px)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        flexDirection: 'column', gap: 24, color: '#E5F6EF',
        fontFamily: 'Inter, system-ui, sans-serif', letterSpacing: '0.5px',
      }}
    >
      <div style={{
        fontSize: 28, fontWeight: 800, color: '#00A676',
        letterSpacing: '2px', textTransform: 'uppercase',
        textShadow: '0 0 16px rgba(0,166,118,0.45)',
      }}>
        TERRITOIRE Ω — Initialisation du pipeline…
      </div>
      <div style={{
        fontSize: 11, color: '#9fb0c2', letterSpacing: '1.5px',
        marginTop: -16, marginBottom: 8,
      }}>
        BCE-4X · STEEVE-MAX · CONFORMITÉ Ω 100% · V30 LOCKED
      </div>
      <div style={{
        display: 'flex', flexDirection: 'column', gap: 10,
        background: 'rgba(0,0,0,0.30)',
        border: '1px solid rgba(0,166,118,0.40)',
        borderRadius: 8, padding: '14px 22px',
        minWidth: 420,
      }}>
        {STEPS.map((s) => (
          <div key={s.id} data-testid={`splash-step-${s.id}`}
            style={{ display: 'flex', alignItems: 'center', gap: 12, fontSize: 12 }}>
            <span style={{
              color: statusColor(stepStatus[s.id]), fontWeight: 800,
              fontSize: 16, width: 20, textAlign: 'center',
              animation: stepStatus[s.id] === 'pending' ? 'splash-pulse 0.9s linear infinite' : 'none',
            }}>{statusIcon(stepStatus[s.id])}</span>
            <span style={{ color: '#B2F2D9' }}>{s.label}</span>
          </div>
        ))}
      </div>
      <div style={{ fontSize: 10, color: '#6b9c87', marginTop: 12 }}>
        PHASE_2_STABILISATION_TERRITOIRE_Ω · WATCHDOG-Ω 600s
      </div>
      <style>{`
        @keyframes splash-pulse {
          0% { opacity: 0.4; }
          50% { opacity: 1; }
          100% { opacity: 0.4; }
        }
      `}</style>
    </div>
  );
}

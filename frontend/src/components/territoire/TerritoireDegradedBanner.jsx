/**
 * TerritoireDegradedBanner.jsx — Doctrine NEVER BLANK Ω
 * ============================================================
 * P22ΩΩ_ZEROCOST_ENGINE_ET_TERRITOIRE_NEVER_BLANK_Ω · 2026-02-XX
 * COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU
 *
 * Affiche une bande discrète mais explicite quand le backend retourne un
 * payload `status === "DEGRADED"` (cf. middleware FastAPI). Empêche la carte
 * de paraître silencieusement vide en cas de panne backend.
 *
 * Props :
 *   - bundleData       : payload V20 (peut contenir status === "DEGRADED")
 *   - retryAt          : timestamp ms du prochain retry programmé (optionnel)
 *   - onRetry          : callback retry manuel (optionnel)
 */
import React from 'react';

const STYLE = {
  container: {
    position: 'absolute',
    top: 12,
    left: '50%',
    transform: 'translateX(-50%)',
    zIndex: 1500,
    backgroundColor: 'rgba(220, 38, 38, 0.95)',
    color: '#FFFFFF',
    padding: '8px 16px',
    borderRadius: 8,
    border: '1.5px solid #991B1B',
    boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
    fontFamily: 'system-ui, -apple-system, sans-serif',
    fontSize: 12,
    fontWeight: 600,
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    letterSpacing: '0.02em',
  },
  badge: {
    backgroundColor: '#991B1B',
    padding: '2px 8px',
    borderRadius: 4,
    fontSize: 11,
    fontWeight: 800,
  },
  reason: {
    opacity: 0.92,
    fontWeight: 500,
  },
  button: {
    backgroundColor: 'rgba(255,255,255,0.18)',
    color: '#FFFFFF',
    border: '1px solid rgba(255,255,255,0.32)',
    padding: '3px 10px',
    borderRadius: 4,
    cursor: 'pointer',
    fontWeight: 700,
    fontSize: 11,
  },
};

export const TerritoireDegradedBanner = ({ bundleData, onRetry }) => {
  const isDegraded = bundleData
    && (bundleData.status === 'DEGRADED' || bundleData.doctrine === 'P22ΩΩ_NEVER_BLANK_Ω');
  // P22ΩΩ_ZEROCOST_PHASE1_SHADOW_ET_LKG_Ω : badge LKG distinct
  const isLkg = bundleData && bundleData._lkg && bundleData._lkg.served_from_lkg;

  if (!isDegraded && !isLkg) return null;

  if (isLkg) {
    const ageMin = Math.round((bundleData._lkg.age_ms || 0) / 60000);
    return (
      <div
        role="status"
        data-testid="territoire-lkg-banner"
        style={{
          ...STYLE.container,
          backgroundColor: 'rgba(217, 119, 6, 0.95)',
          borderColor: '#92400E',
        }}
      >
        <span style={{ ...STYLE.badge, backgroundColor: '#92400E' }}>📦 LKG Ω</span>
        <span style={STYLE.reason}>
          Mode hors-ligne · dernier bundle valide (
          {ageMin === 0 ? 'à l’instant' : `il y a ${ageMin} min`})
        </span>
        {onRetry && (
          <button type="button" onClick={onRetry} style={STYLE.button} data-testid="territoire-lkg-retry">
            Actualiser
          </button>
        )}
      </div>
    );
  }

  const reason = bundleData.reason || 'backend_temporairement_indisponible';
  const reasonHuman = (() => {
    if (reason.includes('endpoint_unavailable')) return "Endpoint backend temporairement absent — données dégradées en cours.";
    if (reason.includes('backend_overloaded')) return "Backend surchargé — bundle dégradé en cours d'enrichissement.";
    if (reason.includes('unsupported_species')) return "Espèce non supportée par ce service.";
    return reason;
  })();

  return (
    <div
      role="alert"
      data-testid="territoire-degraded-banner"
      style={STYLE.container}
    >
      <span style={STYLE.badge}>⚠ DÉGRADÉ Ω</span>
      <span style={STYLE.reason}>{reasonHuman}</span>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          style={STYLE.button}
          data-testid="territoire-degraded-retry"
        >
          Réessayer
        </button>
      )}
    </div>
  );
};

export default TerritoireDegradedBanner;

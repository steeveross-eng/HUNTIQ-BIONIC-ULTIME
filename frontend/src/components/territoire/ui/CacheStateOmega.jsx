/**
 * CacheStateOmega — Overlay CACHE-STATE-Ω bas-droite (ADMIN uniquement)
 * =====================================================================
 * PHASE-PERFORMANCE-Omega V11-SUPRA
 *
 * Dimensions: 60x18px (compact)
 * Halo: #2E7D32 (vert institutionnel)
 * Opacite: 0.92
 * Texte dynamique: "CACHE HIT XXms" / "COMPUTE XXms"
 * Source: headers X-Cache + X-Compute-Ms via bundle response
 * Activation: adminArchitecteMode === true
 */
import React from 'react';

export default function CacheStateOmega({ visible, cacheState, servedMs, computeMs }) {
  if (!visible) return null;
  if (!cacheState) return null;

  const isHit = cacheState === 'HIT';
  const ms = isHit ? (servedMs != null ? Math.round(servedMs) : '?') : (computeMs != null ? Math.round(computeMs) : '?');
  const label = isHit ? `CACHE HIT ${ms}ms` : `COMPUTE ${ms}ms`;
  const color = '#2E7D32';

  return (
    <div
      data-testid="cache-state-omega"
      style={{
        position: 'absolute',
        bottom: 8,
        right: 8,
        width: 'auto',
        minWidth: 60,
        height: 18,
        padding: '0 8px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: 9,
        fontWeight: 800,
        letterSpacing: '0.5px',
        fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace',
        color: color,
        backgroundColor: 'rgba(6, 10, 6, 0.92)',
        border: `1px solid ${color}`,
        borderRadius: 3,
        boxShadow: `0 0 6px ${color}55, inset 0 0 0 1px ${color}22`,
        textShadow: `0 0 4px ${color}88`,
        zIndex: 1001,
        pointerEvents: 'none',
        userSelect: 'none',
      }}
    >
      {label}
    </div>
  );
}

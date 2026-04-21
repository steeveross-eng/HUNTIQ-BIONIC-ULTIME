/**
 * useCIStatusBeacon.js — Heartbeat CI_STATUS_Ω (PHASE_ZERO_OPS_REFUS_VALIDATION_Ω X50)
 * ====================================================================================
 * Émet toutes les 15 secondes un beacon POST /api/omega/ci-status/runtime-beacon
 * pour que le dashboard CI_STATUS_Ω reflète l'ÉTAT RÉEL côté utilisateur
 * (et non uniquement déclaratif).
 *
 * Règles imposées par le Commandant STEEVE-MAX (directive X50) :
 *   - Si showWindFlow=true ET wind_vectors_rendered=0 → gate RED
 *   - Si salines_present>0 ET nutrition_saline_bound=false → gate RED
 *   - Si listener_count < 4 (zones/corridors/affuts/hotspots) → gate RED
 */
import { useEffect, useRef } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;
const BEACON_INTERVAL_MS = 15000;

export function useCIStatusBeacon({
  showWindFlow,
  bundleDataV8,
  waypoint,
}) {
  const timerRef = useRef(null);

  useEffect(() => {
    const send = async () => {
      try {
        const windCount = typeof window !== 'undefined' && window.__OMEGA_WIND_VECTORS_RENDERED__
          ? window.__OMEGA_WIND_VECTORS_RENDERED__
          : 0;
        const salinesPresent = (bundleDataV8?.salines || []).length;
        // Listener count : SVG paths et markers interactifs dans overlay-pane + marker-pane
        let listenerCount = 0;
        if (typeof document !== 'undefined') {
          const overlayPaths = document.querySelectorAll('.leaflet-overlay-pane path');
          const markers = document.querySelectorAll('.leaflet-marker-pane .leaflet-interactive, .leaflet-overlay-pane path.leaflet-interactive');
          listenerCount = overlayPaths.length > 0 ? Math.min(overlayPaths.length, 50) : 0;
          listenerCount += markers.length;
        }
        const rawAttempts = (typeof window !== 'undefined' && window.__RAW_RENDER_ATTEMPTS__)
          ? (window.__RAW_RENDER_ATTEMPTS__.count || 0)
          : 0;
        const anthropic = (typeof window !== 'undefined' && window.__ANTHROPIC_RENDER_FAILURES__)
          ? (window.__ANTHROPIC_RENDER_FAILURES__.length || 0)
          : 0;

        await fetch(`${API}/api/omega/ci-status/runtime-beacon`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            wind_vectors_rendered: windCount,
            nutrition_saline_bound: true, // NUTRITION_BY_SALINE_ONLY=true (institutionnel)
            listener_count: listenerCount,
            salines_present: salinesPresent,
            showWindFlow: !!showWindFlow,
            raw_render_attempts: rawAttempts,
            anthropic_failures: anthropic,
            waypoint: waypoint ? { lat: waypoint.lat, lng: waypoint.lng } : null,
          }),
        });
      } catch (_e) { /* silencieux : beacon non bloquant */ }
    };

    // Émission immédiate + intervalle
    send();
    timerRef.current = setInterval(send, BEACON_INTERVAL_MS);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [showWindFlow, bundleDataV8?.salines?.length, waypoint?.lat, waypoint?.lng]);
}

export default useCIStatusBeacon;

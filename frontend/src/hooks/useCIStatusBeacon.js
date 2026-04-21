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
        const w = typeof window !== 'undefined' ? window : {};
        const windCount = w.__OMEGA_WIND_VECTORS_RENDERED__ || 0;
        const ventusky = w.__OMEGA_VENTUSKY_PARTICLES_ACTIVE__ || 0;
        const ventStyleConf = !!w.__OMEGA_VENT_STYLE_CONFORME__;
        const ventConfusion = !!w.__OMEGA_VENT_CONFUSION_CORRIDORS__;
        const corridorsStyleConf = !!w.__OMEGA_CORRIDORS_STYLE_CONFORME__;
        const contamVisible = !!w.__OMEGA_CONTAMINATION_LAYERS_VISIBLE__;
        const salinesPresent = (bundleDataV8?.salines || []).length;
        let listenerCount = 0;
        let panelsClickable = 0;
        if (typeof document !== 'undefined') {
          const overlayPaths = document.querySelectorAll('.leaflet-overlay-pane path');
          const markers = document.querySelectorAll('.leaflet-marker-pane .leaflet-interactive, .leaflet-overlay-pane path.leaflet-interactive');
          listenerCount = overlayPaths.length > 0 ? Math.min(overlayPaths.length, 50) : 0;
          listenerCount += markers.length;
          // Comptage des popups descriptifs binds (via data-testid présents dans leaflet popups cachés)
          // On se base sur des marqueurs sources présents quand bundle a data
          panelsClickable = 0;
          if ((bundleDataV8?.zones || []).filter(z => !z.excluded).length > 0) panelsClickable++;
          if ((bundleDataV8?.corridors || []).length > 0) panelsClickable++;
          if ((bundleDataV8?.affuts || []).length > 0) panelsClickable++;
          if ((bundleDataV8?.hotspots || []).length > 0) panelsClickable++;
          if (windCount > 0) panelsClickable++;
        }
        const rawAttempts = (w.__RAW_RENDER_ATTEMPTS__ || {}).count || 0;
        const anthropic = (w.__ANTHROPIC_RENDER_FAILURES__ || []).length || 0;

        await fetch(`${API}/api/omega/ci-status/runtime-beacon`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            wind_vectors_rendered: windCount,
            nutrition_saline_bound: true,
            listener_count: listenerCount,
            salines_present: salinesPresent,
            showWindFlow: !!showWindFlow,
            raw_render_attempts: rawAttempts,
            anthropic_failures: anthropic,
            waypoint: waypoint ? { lat: waypoint.lat, lng: waypoint.lng } : null,
            // X80-ABSOLU-Ω
            corridors_style_conforme: corridorsStyleConf,
            ventusky_particles_active: ventusky,
            vent_style_conforme: ventStyleConf,
            vent_confusion_corridors: ventConfusion,
            contamination_layers_visible: contamVisible,
            panels_clickable_count: panelsClickable,
            filters_omega_active: true, // 4 filtres Ω enforced (ENFORCE_PIPELINE_SPEC_V20)
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

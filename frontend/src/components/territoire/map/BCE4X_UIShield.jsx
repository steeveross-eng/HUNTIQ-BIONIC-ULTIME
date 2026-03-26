/**
 * BCE-4X-UI Shield — Protection Leaflet/Map Rendering
 * 
 * GOUVERNANCE: STEEVE-MAX / BCE-4X
 * OBJECTIF: Empecher toute regression du rendu cartographique
 * par des tests automatises, des re-renders excessifs,
 * ou des modifications accidentelles de z-index.
 * 
 * USAGE:
 *   import { LeafletShield, useRenderGuard } from './BCE4X_UIShield';
 *   <LeafletShield><MapContent /></LeafletShield>
 */
import React, { useRef, useCallback, memo } from 'react';

// ============================================================
// 1. LEAFLET SHIELD HOC
// Empeche les re-renders de remonter dans l'arbre React
// au-dela du composant carte.
// ============================================================
const LeafletShieldInner = ({ children }) => {
  const shieldRef = useRef(null);
  const renderCountRef = useRef(0);
  
  renderCountRef.current += 1;
  
  // Log excessif re-render (seuil: >20 renders en session)
  if (renderCountRef.current > 20 && renderCountRef.current % 10 === 0) {
    console.warn(
      `[BCE-4X-UI] LeafletShield: ${renderCountRef.current} renders detectes. ` +
      `Verifier les dependances du composant parent.`
    );
  }
  
  return (
    <div 
      ref={shieldRef}
      data-testid="bce4x-leaflet-shield"
      data-bce4x-protected="true"
      className="bce4x-shield-container"
      style={{
        position: 'relative',
        width: '100%',
        height: '100%',
        isolation: 'isolate',  // Cree un nouveau contexte d'empilement
      }}
    >
      {children}
    </div>
  );
};

export const LeafletShield = memo(LeafletShieldInner);

// ============================================================
// 2. Z-INDEX GUARD
// Protege les z-index critiques de la carte
// contre les modifications non autorisees.
// ============================================================
const Z_INDEX_MAP = {
  'map-base': 1,
  'map-tiles': 10,
  'map-zones': 100,
  'map-corridors': 200,
  'map-markers': 300,
  'map-overlays': 400,
  'ui-toolbar': 1000,
  'ui-panels': 1100,
  'ui-modals': 1500,
  'ui-toasts': 2000,
};

export const getProtectedZIndex = (layer) => {
  const z = Z_INDEX_MAP[layer];
  if (z === undefined) {
    console.warn(`[BCE-4X-UI] Z-index non defini pour: ${layer}`);
    return 500; // Fallback securise
  }
  return z;
};

// ============================================================
// 3. RENDER GUARD HOOK
// Hook qui detecte et limite les re-renders excessifs
// sur les composants Leaflet.
// ============================================================
export const useRenderGuard = (componentName, maxRenders = 50) => {
  const renderCountRef = useRef(0);
  const lastRenderTimeRef = useRef(Date.now());
  
  renderCountRef.current += 1;
  const now = Date.now();
  const elapsed = now - lastRenderTimeRef.current;
  lastRenderTimeRef.current = now;
  
  // Detection de render storm (>5 renders en <100ms)
  if (elapsed < 100 && renderCountRef.current > 5) {
    console.error(
      `[BCE-4X-UI] RENDER STORM detecte sur ${componentName}: ` +
      `${renderCountRef.current} renders, dernier intervalle: ${elapsed}ms`
    );
  }
  
  return {
    renderCount: renderCountRef.current,
    isExcessive: renderCountRef.current > maxRenders,
    reset: useCallback(() => { renderCountRef.current = 0; }, []),
  };
};

// ============================================================
// 4. LAYER WEIGHT GUARD
// Mesure le poids des donnees GeoJSON et alerte
// si le seuil est depasse.
// ============================================================
export const checkLayerWeight = (geojsonData, layerName, maxSizeKB = 500) => {
  if (!geojsonData) return { ok: true, sizeKB: 0 };
  
  const sizeBytes = new Blob([JSON.stringify(geojsonData)]).size;
  const sizeKB = Math.round(sizeBytes / 1024);
  
  if (sizeKB > maxSizeKB) {
    console.warn(
      `[BCE-4X-UI] Layer ${layerName}: ${sizeKB}KB depasse le seuil de ${maxSizeKB}KB`
    );
    return { ok: false, sizeKB };
  }
  
  return { ok: true, sizeKB };
};

// ============================================================
// 5. MAP LOAD TIMER
// Mesure le temps de chargement de la carte et alerte
// si le seuil est depasse.
// ============================================================
export const createLoadTimer = (operationName, thresholdMs = 5000) => {
  const start = performance.now();
  
  return {
    stop: () => {
      const elapsed = performance.now() - start;
      if (elapsed > thresholdMs) {
        console.warn(
          `[BCE-4X-UI] ${operationName}: ${Math.round(elapsed)}ms ` +
          `(seuil: ${thresholdMs}ms)`
        );
      }
      return Math.round(elapsed);
    },
  };
};

// ============================================================
// 6. OVERLAY DUPLICATION GUARD
// Verifie que les overlays Leaflet ne sont pas dupliques
// (cause connue de regression).
// ============================================================
export const checkOverlayDuplication = (mapRef) => {
  if (!mapRef?.current) return { ok: true, count: 0 };
  
  const map = mapRef.current;
  let layerCount = 0;
  const layerTypes = {};
  
  map.eachLayer((layer) => {
    layerCount++;
    const type = layer.constructor?.name || 'unknown';
    layerTypes[type] = (layerTypes[type] || 0) + 1;
  });
  
  // Detection de duplication (>500 layers est suspect)
  const hasDuplication = layerCount > 500;
  if (hasDuplication) {
    console.error(
      `[BCE-4X-UI] OVERLAY DUPLICATION SUSPECTE: ${layerCount} layers. ` +
      `Types: ${JSON.stringify(layerTypes)}`
    );
  }
  
  return { ok: !hasDuplication, count: layerCount, types: layerTypes };
};

// ============================================================
// 7. TEST AGENT ROUTE GUARD
// Liste des routes PROTEGEES que le testing agent
// ne doit JAMAIS naviguer.
// ============================================================
export const BCE4X_PROTECTED_ROUTES = [
  '/mon-territoire-bionic',
  '/territoire',
  '/territory',
];

export const isProtectedRoute = (pathname) => {
  return BCE4X_PROTECTED_ROUTES.some(route => 
    pathname.toLowerCase().includes(route.toLowerCase())
  );
};

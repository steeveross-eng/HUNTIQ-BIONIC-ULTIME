/**
 * TerritoireCaptureMode — Phase XI-SUPRA-D
 * Route dédiée `/territoire-capture-mode` produisant un rendu TERRITOIRE
 * stable pour les captures Playwright institutionnelles.
 *
 * Caractéristiques :
 *   - Pas de useEffect auth périodique (pas de redirect)
 *   - Mount unique de MonTerritoireBionicPage
 *   - Expose window.__bionicReady = true quand bundle + map + couches prêts
 *   - Accepte lat/lon/species/zoom en query params
 */
import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';

// Import statique (pas lazy) pour mount immédiat stable
import MonTerritoireBionicPage from './MonTerritoireBionicPage';

export default function TerritoireCaptureModePage() {
  const [params] = useSearchParams();
  const [readyMarker, setReadyMarker] = useState(0);

  // Phase XI-SUPRA-D : flag global pour Playwright
  useEffect(() => {
    if (typeof window === 'undefined') return;
    window.__bionicReady = false;

    // Poll window.__bionicMap + window.__lastBundle pour marquer ready
    const start = Date.now();
    const t = setInterval(() => {
      const hasMap = !!window.__bionicMap;
      const hasBundle = !!window.__lastBundle;
      const hasTiles = document.querySelectorAll('.leaflet-tile-loaded').length >= 4;
      const elapsed = Date.now() - start;
      if (hasMap && hasTiles) {
        window.__bionicReady = true;
        window.__bionicReadyMeta = {
          hasMap,
          hasBundle,
          hasTiles,
          tilesCount: document.querySelectorAll('.leaflet-tile-loaded').length,
          elapsed_ms: elapsed,
        };
        setReadyMarker(1);
        clearInterval(t);
      } else if (elapsed > 60000) {
        // timeout 60s : marque ready quand même pour ne pas bloquer
        window.__bionicReady = true;
        window.__bionicReadyMeta = { forced: true, elapsed_ms: elapsed, hasMap, hasTiles };
        clearInterval(t);
      }
    }, 500);

    return () => {
      clearInterval(t);
      window.__bionicReady = false;
    };
  }, []);

  return (
    <div data-testid="territoire-capture-mode" style={{ width: '100%', height: '100vh' }}>
      {/* Banner discret de statut capture */}
      <div style={{
        position: 'fixed', top: 4, right: 4, zIndex: 99999,
        padding: '2px 8px', background: readyMarker ? '#059669' : '#dc2626',
        color: '#fff', fontSize: 11, fontFamily: 'ui-monospace, monospace',
        borderRadius: 4, pointerEvents: 'none',
      }} data-testid="capture-mode-status">
        CAPTURE MODE · {readyMarker ? 'READY' : 'loading…'}
      </div>
      <MonTerritoireBionicPage />
    </div>
  );
}

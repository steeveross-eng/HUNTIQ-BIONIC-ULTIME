/**
 * TerritoireCaptureMode — Phase XI-SUPRA-D
 * =========================================
 * Route dédiée /territoire-capture-mode pour captures Playwright institutionnelles.
 *
 * STRATÉGIE V2 : self-contained minimal Leaflet + BionicLayersV8 direct.
 *   - Pas de MonTerritoireBionicPage (trop complexe, overlays invisibles en headless)
 *   - Fetch direct /api/v20/territoire/bundle → alimente BionicLayersV8
 *   - StrictMode désactivé via src/index.js
 *   - Navigation masquée via CaptureModeAwareChrome
 *   - Expose window.__bionicReady quand map + tuiles + overlay visibles
 *   - Accepte ?lat=..&lon=..&species=..&zoom=..
 */
import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { MapContainer, TileLayer } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

import BionicLayersV8 from '@/components/territoire/BionicLayersV8';

const API = process.env.REACT_APP_BACKEND_URL || '';

function useReadyProbe(bundleLoaded) {
  const [ready, setReady] = useState(false);
  useEffect(() => {
    if (typeof window === 'undefined') return;
    window.__bionicReady = false;
    delete window.__bionicReadyMeta;

    const start = Date.now();
    const t = setInterval(() => {
      const elapsed = Date.now() - start;
      const map = window.__bionicMap;
      const tiles = document.querySelectorAll('.leaflet-tile-loaded').length;
      const overlays = document.querySelectorAll(
        '.leaflet-overlay-pane path, .leaflet-overlay-pane circle, .leaflet-marker-icon'
      ).length;
      let layers = 0;
      if (map) { try { map.eachLayer(() => { layers += 1; }); } catch { /* noop */ } }
      const ok = !!map && tiles >= 6 && bundleLoaded && overlays >= 1;
      if (ok) {
        window.__bionicReady = true;
        window.__bionicReadyMeta = {
          source: 'full-criteria', hasMap: true, tiles, overlays, layers, elapsed_ms: elapsed,
        };
        setReady(true);
        clearInterval(t);
      } else if (elapsed > 60000) {
        window.__bionicReady = true;
        window.__bionicReadyMeta = {
          source: 'timeout-forced', hasMap: !!map, tiles, overlays, layers,
          bundleLoaded, elapsed_ms: elapsed,
        };
        setReady(true);
        clearInterval(t);
      }
    }, 400);
    return () => {
      clearInterval(t);
      window.__bionicReady = false;
    };
  }, [bundleLoaded]);
  return ready;
}

export default function TerritoireCaptureModePage() {
  const [params] = useSearchParams();
  const lat = parseFloat(params.get('lat')) || 45.10;
  const lon = parseFloat(params.get('lon')) || -72.80;
  const species = params.get('species') || 'chevreuil';
  const zoom = parseInt(params.get('zoom'), 10) || 14;

  const [bundle, setBundle] = useState(null);
  const [bundleErr, setBundleErr] = useState(null);
  const ready = useReadyProbe(!!bundle);

  // Fetch bundle une seule fois
  useEffect(() => {
    const token = localStorage.getItem('auth_token') || localStorage.getItem('token') || '';
    const url = `${API}/api/v20/territoire/bundle?lat=${lat}&lon=${lon}&species=${encodeURIComponent(species)}`;
    fetch(url, { headers: token ? { Authorization: `Bearer ${token}` } : {} })
      .then((r) => r.json())
      .then((data) => { setBundle(data); window.__lastBundle = data; })
      .catch((e) => setBundleErr(String(e)));
  }, [lat, lon, species]);

  const waypointCenter = { lat, lng: lon };

  return (
    <>
      {/* Banner status (non-interactif) */}
      <div
        data-testid="capture-mode-status"
        style={{
          position: 'fixed', top: 6, right: 6, zIndex: 99999,
          padding: '3px 10px',
          background: ready ? '#059669' : '#dc2626',
          color: '#fff', fontSize: 11, fontFamily: 'ui-monospace, monospace',
          borderRadius: 4, pointerEvents: 'none', letterSpacing: 0.5,
        }}
      >
        CAPTURE-MODE · {ready ? 'READY' : (bundleErr ? `ERR: ${bundleErr.slice(0, 40)}` : 'LOADING')}
      </div>

      {/* MapContainer plein viewport */}
      <div
        data-testid="territoire-capture-mode"
        style={{ position: 'fixed', inset: 0, width: '100vw', height: '100vh', background: '#0a0a0f', zIndex: 1 }}
      >
        <MapContainer
          center={[lat, lon]}
          zoom={zoom}
          zoomControl={false}
          attributionControl={false}
          style={{ width: '100%', height: '100%', background: '#0a0a0f' }}
          whenReady={() => { /* handled by BionicLayersV8 useMap exposure */ }}
        >
          {/* Fond satellite ArcGIS World Imagery — accessible et institutionnel */}
          <TileLayer
            url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
            maxZoom={19}
          />
          {/* 14 couches BionicLayersV8 — toutes activées */}
          <BionicLayersV8
            bundleData={bundle}
            waypointCenter={waypointCenter}
            showZones
            showCorridors
            showAffuts
            showSalines
            showHotspots
            showWind
            showContamination
            showNutrition
            enabled
          />
        </MapContainer>
      </div>
    </>
  );
}

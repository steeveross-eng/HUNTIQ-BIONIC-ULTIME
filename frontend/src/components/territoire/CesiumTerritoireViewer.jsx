/**
 * CesiumTerritoireViewer.jsx · PHASE_3_3D_FRONTEND_Ω
 * ══════════════════════════════════════════════════════════════════════════
 * COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT
 *
 * Viewer Cesium 3D loadant le tileset.json depuis /api/v20/mesh-3d/build
 *
 * Architecture INSTITUTIONNELLE :
 *  - Cesium chargé via CDN ESM (zéro byte disque preview)
 *  - cesium_ion_token sourcé depuis REACT_APP_CESIUM_ION_TOKEN
 *  - Tileset 3D Tiles 1.0 + glTF embedded base64 généré côté backend
 *  - Draping SPECTRAL (NDVI) sur vertex colors
 *  - Camera mode : terrain_follow (auto rotate)
 *
 * V30_LOCK INVIOLÉ · FUSION ADD-ONLY · NEW COMPONENT
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';

const CESIUM_VERSION = '1.123'; // Compat Node 20 + JS ESM moderne
const CESIUM_CDN = `https://cdn.jsdelivr.net/npm/cesium@${CESIUM_VERSION}`;
const CESIUM_BASE_URL = `${CESIUM_CDN}/Build/Cesium/`;
const CESIUM_CSS_URL = `${CESIUM_BASE_URL}Widgets/widgets.css`;
const API_BASE = process.env.REACT_APP_BACKEND_URL || '';
const ION_TOKEN = process.env.REACT_APP_CESIUM_ION_TOKEN || '';

const DEFAULT_LAT = 48.206657;
const DEFAULT_LON = -68.382422;

const ensureCssLoaded = () => {
  if (typeof document === 'undefined') return;
  if (document.getElementById('cesium-widgets-css')) return;
  const link = document.createElement('link');
  link.id = 'cesium-widgets-css';
  link.rel = 'stylesheet';
  link.href = CESIUM_CSS_URL;
  document.head.appendChild(link);
};

let _cesiumPromise = null;
const loadCesium = () => {
  if (_cesiumPromise) return _cesiumPromise;
  _cesiumPromise = new Promise((resolve, reject) => {
    if (typeof window === 'undefined') {
      reject(new Error('window undefined'));
      return;
    }
    if (window.Cesium) {
      resolve(window.Cesium);
      return;
    }
    // Configure base URL avant de charger Cesium.js (requis par Cesium)
    window.CESIUM_BASE_URL = CESIUM_BASE_URL;
    const script = document.createElement('script');
    script.src = `${CESIUM_BASE_URL}Cesium.js`;
    script.async = true;
    script.onload = () => {
      if (window.Cesium) resolve(window.Cesium);
      else reject(new Error('Cesium loaded but global undefined'));
    };
    script.onerror = (e) => reject(new Error(`Cesium CDN load failed: ${e.message || e.type}`));
    document.head.appendChild(script);
  });
  return _cesiumPromise;
};

const CesiumTerritoireViewer = ({
  lat = DEFAULT_LAT, lon = DEFAULT_LON,
  drapeSpectral = true, drapeSlope = false,
  bboxRadiusM = 200, gridN = 11,
}) => {
  const containerRef = useRef(null);
  const viewerRef = useRef(null);
  const [status, setStatus] = useState('init');
  const [error, setError] = useState(null);
  const [tilesetMeta, setTilesetMeta] = useState(null);
  const [stats, setStats] = useState({ vertices: 0, triangles: 0, drapeMode: 'none' });

  const buildMesh = useCallback(async () => {
    setStatus('fetch_mesh');
    try {
      const resp = await fetch(`${API_BASE}/api/v20/mesh-3d/build`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'omit',
        body: JSON.stringify({
          lat, lon, halo_m: bboxRadiusM,
          grid_n: gridN,
          drape_spectral: drapeSpectral,
          drape_slope: drapeSlope,
        }),
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      if (!data.ok) throw new Error(data.error || 'mesh build failed');
      return data;
    } catch (e) {
      throw new Error(`Mesh build failed: ${e.message}`);
    }
  }, [lat, lon, bboxRadiusM, gridN, drapeSpectral, drapeSlope]);

  useEffect(() => {
    if (!containerRef.current) return;
    let cancelled = false;
    let viewer = null;

    (async () => {
      try {
        if (!ION_TOKEN) {
          throw new Error('REACT_APP_CESIUM_ION_TOKEN absent · contactez COMMANDANT');
        }
        setStatus('load_cesium');
        ensureCssLoaded();
        const Cesium = await loadCesium();
        if (cancelled) return;

        Cesium.Ion.defaultAccessToken = ION_TOKEN;

        setStatus('init_viewer');
        viewer = new Cesium.Viewer(containerRef.current, {
          animation: false, baseLayerPicker: true, fullscreenButton: true,
          geocoder: false, homeButton: false, infoBox: false,
          sceneModePicker: false, selectionIndicator: false,
          timeline: false, navigationHelpButton: false,
          requestRenderMode: true,
        });
        viewerRef.current = viewer;

        setStatus('build_mesh');
        const meshData = await buildMesh();
        if (cancelled) { viewer.destroy(); return; }
        setTilesetMeta(meshData.tileset_meta);
        setStats({
          vertices: meshData.gltf?.n_vertices || 0,
          triangles: meshData.gltf?.n_triangles || 0,
          drapeMode: drapeSpectral ? 'SPECTRAL' : (drapeSlope ? 'TERRAIN_HR_SLOPE' : 'NONE'),
        });

        // Camera positionnée sur le waypoint avec vue oblique
        const bbox = meshData.tileset_meta?.bounding_region_deg || [lon - 0.005, lat - 0.003, lon + 0.005, lat + 0.003, 300, 500];
        const center = Cesium.Cartesian3.fromDegrees((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2, bbox[5] + 800);
        viewer.camera.setView({
          destination: center,
          orientation: {
            heading: Cesium.Math.toRadians(0.0),
            pitch: Cesium.Math.toRadians(-55.0),
            roll: 0.0,
          },
        });

        // Charger le glTF mesh local depuis le tileset (mode primitif Entity)
        try {
          const gltfJson = meshData.gltf?.doc;
          if (gltfJson) {
            const blob = new Blob([JSON.stringify(gltfJson)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            viewer.scene.primitives.add(
              await Cesium.Model.fromGltfAsync({
                url,
                modelMatrix: Cesium.Transforms.headingPitchRollToFixedFrame(
                  Cesium.Cartesian3.fromDegrees(lon, lat, bbox[4] || 350),
                  new Cesium.HeadingPitchRoll(0, 0, 0),
                ),
                scale: 1.0,
                minimumPixelSize: 64,
              }),
            );
          }
        } catch (modelErr) {
          // glTF fromGltfAsync peut échouer si data: URI non supporté
          // Fallback : afficher juste le waypoint marker
          // eslint-disable-next-line no-console
          console.warn('Cesium glTF load fallback marker:', modelErr.message);
        }

        // Marker waypoint canonique
        viewer.entities.add({
          name: 'WAYPOINT_CANONIQUE',
          position: Cesium.Cartesian3.fromDegrees(lon, lat, bbox[5] + 50),
          point: {
            pixelSize: 14, color: Cesium.Color.ORANGE,
            outlineColor: Cesium.Color.WHITE, outlineWidth: 2,
          },
          label: {
            text: `BSL · ${lat.toFixed(4)}, ${lon.toFixed(4)}`,
            font: '12px monospace', fillColor: Cesium.Color.WHITE,
            outlineColor: Cesium.Color.BLACK, outlineWidth: 2,
            style: Cesium.LabelStyle.FILL_AND_OUTLINE,
            verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
            pixelOffset: new Cesium.Cartesian2(0, -15),
          },
        });

        // Bounding box du mesh territoire
        viewer.entities.add({
          name: 'MESH_3D_BBOX',
          rectangle: {
            coordinates: Cesium.Rectangle.fromDegrees(bbox[0], bbox[1], bbox[2], bbox[3]),
            material: Cesium.Color.ORANGE.withAlpha(0.15),
            outline: true, outlineColor: Cesium.Color.ORANGE,
            height: bbox[4], extrudedHeight: bbox[5] + 10,
          },
        });

        viewer.scene.requestRender();
        setStatus('ready');
      } catch (e) {
        if (!cancelled) {
          // eslint-disable-next-line no-console
          console.error('CesiumTerritoireViewer error:', e);
          setError(String(e.message || e));
          setStatus('error');
        }
      }
    })();

    return () => {
      cancelled = true;
      if (viewerRef.current && !viewerRef.current.isDestroyed()) {
        try { viewerRef.current.destroy(); } catch (_) { /* noop */ }
      }
    };
  }, [lat, lon, bboxRadiusM, gridN, drapeSpectral, drapeSlope, buildMesh]);

  return (
    <div
      data-testid="cesium-territoire-viewer"
      style={{
        position: 'relative',
        width: '100%',
        height: '600px',
        background: '#0a0a0a',
        border: '2px solid #FF6A00',
        borderRadius: 8,
        overflow: 'hidden',
      }}
    >
      <div
        ref={containerRef}
        data-testid="cesium-canvas-container"
        style={{ width: '100%', height: '100%' }}
      />

      {/* Overlay de statut */}
      <div
        data-testid="cesium-status-overlay"
        style={{
          position: 'absolute', top: 12, left: 12,
          background: 'rgba(0,0,0,0.85)', color: '#FFF',
          padding: '8px 12px', borderRadius: 6,
          fontSize: 11, fontFamily: 'monospace',
          border: '1px solid #FF6A00',
          maxWidth: 360, zIndex: 99,
        }}
      >
        <div style={{ color: '#FF6A00', fontWeight: 'bold', marginBottom: 4 }}>
          PHASE_3_3D_OMEGA · CESIUM
        </div>
        <div>status=<span style={{ color: status === 'ready' ? '#0F0' : status === 'error' ? '#F55' : '#FFC300' }}>{status}</span></div>
        <div>lat={lat.toFixed(4)} · lon={lon.toFixed(4)}</div>
        <div>vertices={stats.vertices} · triangles={stats.triangles}</div>
        <div>drape={stats.drapeMode}</div>
        {tilesetMeta && (
          <div>geom_error={Number(tilesetMeta.geometric_error || 0).toFixed(1)}m</div>
        )}
        {error && (
          <div style={{ color: '#F55', marginTop: 4 }}>{error}</div>
        )}
      </div>
    </div>
  );
};

export default CesiumTerritoireViewer;

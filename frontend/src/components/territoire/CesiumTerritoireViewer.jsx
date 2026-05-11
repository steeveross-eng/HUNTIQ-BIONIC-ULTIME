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
  // CARTE_3D_INTEGRATION_SOUS_HEADER_Ω (2026-05-11 · STEEVE-MAX)
  species = 'orignal',
  month = 10,
  hour = 7,
  windDeg = 225,
  windSpeed = 15,
  fullScreen = false,
  loadOverlays = false,
}) => {
  const containerRef = useRef(null);
  const viewerRef = useRef(null);
  const [status, setStatus] = useState('init');
  const [error, setError] = useState(null);
  const [tilesetMeta, setTilesetMeta] = useState(null);
  const [stats, setStats] = useState({ vertices: 0, triangles: 0, drapeMode: 'none' });
  const [overlayStats, setOverlayStats] = useState({ corridors: 0, zones: 0, poi: 0, buffer: false });

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

  // CARTE_3D_INTEGRATION_SOUS_HEADER_Ω — Fetch des 4 overlays réels
  const fetchOverlays = useCallback(async () => {
    if (!loadOverlays) return null;
    const qs = new URLSearchParams({
      lat: String(lat), lon: String(lon),
      species, month: String(month), hour: String(hour),
      wind_deg: String(windDeg), wind_speed: String(windSpeed),
    }).toString();
    const buffQs = new URLSearchParams({
      lat: String(lat), lon: String(lon), radius_m: '600', n_points: '64',
    }).toString();
    try {
      const [corrR, zonesR, poiR, buffR] = await Promise.all([
        fetch(`${API_BASE}/api/v20/corridors/active?${qs}`, { credentials: 'omit' }).then(r => r.json()).catch(() => null),
        fetch(`${API_BASE}/api/v20/zones/active?${qs}`, { credentials: 'omit' }).then(r => r.json()).catch(() => null),
        fetch(`${API_BASE}/api/v20/points-interet/active?${qs}`, { credentials: 'omit' }).then(r => r.json()).catch(() => null),
        fetch(`${API_BASE}/api/v20/territoire/buffer-600m?${buffQs}`, { credentials: 'omit' }).then(r => r.json()).catch(() => null),
      ]);
      return {
        corridors: corrR?.corridors || [],
        zones: zonesR?.zones || [],
        poi: poiR?.points_interet || [],
        buffer: buffR?.feature || null,
      };
    } catch (e) {
      // eslint-disable-next-line no-console
      console.warn('[Cesium overlays] fetch failed:', e.message);
      return { corridors: [], zones: [], poi: [], buffer: null };
    }
  }, [loadOverlays, lat, lon, species, month, hour, windDeg, windSpeed]);

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
        // CARTE_3D_INTEGRATION_SOUS_HEADER_Ω : parallélisation mesh + overlays
        // Les overlays (corridors/zones/POI/buffer) sont indépendants du mesh 3D.
        // On lance les deux en parallèle pour réduire le TTFOverlay.
        const meshPromise = buildMesh();
        const overlayPromise = loadOverlays ? fetchOverlays() : Promise.resolve(null);

        const meshData = await meshPromise;
        if (cancelled) { viewer.destroy(); return; }
        setTilesetMeta(meshData.tileset_meta);
        setStats({
          vertices: meshData.gltf?.n_vertices || 0,
          triangles: meshData.gltf?.n_triangles || 0,
          drapeMode: drapeSpectral ? 'SPECTRAL' : (drapeSlope ? 'TERRAIN_HR_SLOPE' : 'NONE'),
        });

        // Camera CARTE_3D_INTEGRATION_SOUS_HEADER_Ω :
        //  - center_on_active_waypoint
        //  - visible_radius = 600m  → altitude ~ radius / tan(35°) ≈ 857m
        //  - terrain_follow + tilt = 55° (pitch = -55°)
        const VISIBLE_RADIUS_M = 600;
        const TILT_DEG = 55;
        const cameraAltM = VISIBLE_RADIUS_M / Math.tan((90 - TILT_DEG) * Math.PI / 180); // ≈ 857m
        viewer.camera.setView({
          destination: Cesium.Cartesian3.fromDegrees(lon, lat, cameraAltM),
          orientation: {
            heading: Cesium.Math.toRadians(0.0),
            pitch: Cesium.Math.toRadians(-TILT_DEG),
            roll: 0.0,
          },
        });

        // Activer terrain_follow (terrain Cesium World Terrain via Ion)
        try {
          const terrainProv = await Cesium.createWorldTerrainAsync({
            requestVertexNormals: true,
          });
          viewer.terrainProvider = terrainProv;
          viewer.scene.globe.depthTestAgainstTerrain = true;
        } catch (terrErr) {
          // eslint-disable-next-line no-console
          console.warn('[Cesium] terrain_follow indisponible:', terrErr.message);
        }

        // Bounding box du mesh territoire (pour glTF positioning + bbox overlay)
        const bbox = meshData.tileset_meta?.bounding_region_deg
          || [lon - 0.005, lat - 0.003, lon + 0.005, lat + 0.003, 300, 500];

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
          position: Cesium.Cartesian3.fromDegrees(lon, lat, (bbox[5] || 500) + 50),
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
            height: bbox[4], extrudedHeight: (bbox[5] || 500) + 10,
          },
        });

        // ══ CARTE_3D_INTEGRATION_SOUS_HEADER_Ω · OVERLAYS RÉELS ══
        if (loadOverlays && !cancelled) {
          setStatus('fetch_overlays');
          const ov = await overlayPromise;
          if (cancelled) return;

          const ovStats = { corridors: 0, zones: 0, poi: 0, buffer: false };

          // Buffer 600m → cercle au sol
          if (ov?.buffer?.geometry?.coordinates?.[0]) {
            const ring = ov.buffer.geometry.coordinates[0];
            const positions = ring.flatMap(([lng2, lat2]) => [lng2, lat2]);
            viewer.entities.add({
              name: 'BUFFER_600M',
              polygon: {
                hierarchy: Cesium.Cartesian3.fromDegreesArray(positions),
                material: Cesium.Color.fromCssColorString('#FFC300').withAlpha(0.10),
                outline: true,
                outlineColor: Cesium.Color.fromCssColorString('#FFC300'),
                outlineWidth: 2,
                heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
              },
            });
            ovStats.buffer = true;
          }

          // Zones vitales → polygones colorés (clampés au sol)
          const ZONE_COLORS = {
            alimentation: '#7CB518', rut: '#FF6A00', repos: '#00B5C5',
            salines: '#FDD835', eau: '#42A5F5', affuts: '#9E9E9E',
            corridors: '#FF9800', hydro: '#4A8AFF',
          };
          for (const z of (ov?.zones || [])) {
            // API V20 renvoie `polygon` (liste de [lat,lng]) ; fallback `positions`
            const raw = z?.polygon || z?.positions;
            if (!Array.isArray(raw)) continue;
            try {
              const flat = (raw.flat ? raw.flat() : raw);
              // Filtre points valides
              const points = flat
                .map(p => Array.isArray(p) && p.length >= 2
                  ? [Number(p[0]), Number(p[1])]
                  : (p && p.lat !== undefined ? [p.lat, (p.lng ?? p.lon)] : null))
                .filter(p => p && Number.isFinite(p[0]) && Number.isFinite(p[1]));
              if (points.length < 3) continue;
              const arr = points.flatMap(([la, ln]) => [ln, la]); // Cesium: [lng, lat]
              const layerKey = z.layerId || z.type || 'rut';
              const color = ZONE_COLORS[layerKey] || '#7CB518';
              viewer.entities.add({
                name: `ZONE_${layerKey}_${z.id || ''}`,
                polygon: {
                  hierarchy: Cesium.Cartesian3.fromDegreesArray(arr),
                  material: Cesium.Color.fromCssColorString(color).withAlpha(0.35),
                  outline: true,
                  outlineColor: Cesium.Color.fromCssColorString(color),
                  heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
                },
              });
              ovStats.zones += 1;
            } catch (_e) { /* skip malformed */ }
          }

          // Corridors → polylignes orangées avec hauteur extrudée (+25m)
          for (const c of (ov?.corridors || [])) {
            const path = c?.path || c?.coordinates || c?.points;
            if (!Array.isArray(path) || path.length < 2) continue;
            try {
              // Path : [[lat,lng], ...] → flat [lng, lat, +25, lng, lat, +25, ...]
              const lonLatH = [];
              for (const p of path) {
                let la, ln;
                if (Array.isArray(p) && p.length >= 2) { la = p[0]; ln = p[1]; }
                else if (p && p.lng !== undefined) { la = p.lat; ln = p.lng; }
                else if (p && p.lon !== undefined) { la = p.lat; ln = p.lon; }
                else continue;
                if (!Number.isFinite(la) || !Number.isFinite(ln)) continue;
                lonLatH.push(ln, la, 25);
              }
              if (lonLatH.length < 6) continue;
              viewer.entities.add({
                name: `CORRIDOR_${c.id || ''}`,
                polyline: {
                  positions: Cesium.Cartesian3.fromDegreesArrayHeights(lonLatH),
                  width: 5,
                  material: Cesium.Color.fromCssColorString('#FF6A00').withAlpha(0.85),
                  clampToGround: false,
                },
              });
              ovStats.corridors += 1;
            } catch (_e) { /* skip */ }
          }

          // Points d'intérêt → markers
          for (const p of (ov?.poi || [])) {
            if (!Number.isFinite(p?.lat) || !Number.isFinite(p?.lng)) continue;
            const isAffut = p.category === 'affut';
            viewer.entities.add({
              name: `POI_${p.category}_${p.id || ''}`,
              position: Cesium.Cartesian3.fromDegrees(p.lng, p.lat, (bbox[5] || 500) + 5),
              point: {
                pixelSize: isAffut ? 10 : 9,
                color: Cesium.Color.fromCssColorString(isAffut ? '#9E9E9E' : '#FDD835'),
                outlineColor: Cesium.Color.WHITE, outlineWidth: 1,
                heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
              },
            });
            ovStats.poi += 1;
          }

          setOverlayStats(ovStats);
        }

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
  }, [lat, lon, bboxRadiusM, gridN, drapeSpectral, drapeSlope, buildMesh, fetchOverlays, loadOverlays]);

  return (
    <div
      data-testid="cesium-territoire-viewer"
      style={{
        position: 'relative',
        width: '100%',
        height: fullScreen ? '100%' : '600px',
        background: '#0a0a0a',
        border: fullScreen ? 'none' : '2px solid #FF6A00',
        borderRadius: fullScreen ? 0 : 8,
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
        {loadOverlays && (
          <div style={{ marginTop: 4, paddingTop: 4, borderTop: '1px dashed #FF6A00' }}>
            <div style={{ color: '#FFC300', fontWeight: 'bold' }}>OVERLAYS_Ω · réels</div>
            <div>corridors={overlayStats.corridors} · zones={overlayStats.zones} · poi={overlayStats.poi}</div>
            <div>buffer_600m={overlayStats.buffer ? 'OK' : '—'}</div>
          </div>
        )}
        {error && (
          <div style={{ color: '#F55', marginTop: 4 }}>{error}</div>
        )}
      </div>
    </div>
  );
};

export default CesiumTerritoireViewer;

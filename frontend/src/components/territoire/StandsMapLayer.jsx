/**
 * StandsMapLayer.jsx — Couche cartographique Affûts Professionnels
 * STEEVE-MAX x2280/x2310/x2320
 *
 * Affiche sur la carte Leaflet:
 * - Marqueurs d'affûts (icônes par type, score visible)
 * - Chemins d'approche en lignes pointillées (#4ECDC4)
 * - Popup justification professionnelle au clic
 */
import { useEffect, useRef, useCallback } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

const STAND_COLORS = {
  tree_stand: '#E74C3C',
  ground_blind: '#9B59B6',
  elevated_blind: '#F39C12',
  natural_hide: '#2ECC71',
  saddle_platform: '#3498DB',
};

const StandsMapLayer = ({
  center,
  windDirection = 'NE',
  windSpeed = 12,
  species = 'orignal',
  enabled = true,
  onStandClick = null,
}) => {
  const map = useMap();
  const layerRef = useRef(null);
  const cacheRef = useRef(null);
  const lastKeyRef = useRef('');
  const abortRef = useRef(null);

  const centerLat = center?.lat;
  const centerLng = center?.lng;

  const clearLayers = useCallback(() => {
    if (layerRef.current) {
      map.removeLayer(layerRef.current);
      layerRef.current = null;
    }
  }, [map]);

  const renderStands = useCallback((data) => {
    clearLayers();
    if (!data?.stands?.length) return;

    const group = L.featureGroup();

    for (const stand of data.stands) {
      const color = STAND_COLORS[stand.type_key] || '#E74C3C';

      // Approach path — dotted polyline
      if (stand.approach_path?.length >= 2) {
        const pathCoords = stand.approach_path.map(p => [p.lat, p.lng]);
        const approachLine = L.polyline(pathCoords, {
          color: '#4ECDC4',
          weight: 2.5,
          dashArray: '8, 5',
          opacity: 0.75,
          lineCap: 'round',
          pane: 'overlayPane',
        });
        group.addLayer(approachLine);

        // Start dot (entry point)
        const startPt = stand.approach_path[0];
        const startDot = L.circleMarker([startPt.lat, startPt.lng], {
          radius: 4, fillColor: '#2ECC71', color: '#1a1a2e', weight: 1.5,
          fillOpacity: 0.9, pane: 'markerPane',
        });
        startDot.bindTooltip('Point d\'entrée', { direction: 'top', offset: [0, -8] });
        group.addLayer(startDot);
      }

      // Stand marker (crosshair icon)
      const standIcon = L.divIcon({
        className: 'bionic-stand-marker',
        html: `<div style="
          width:28px;height:28px;border-radius:50%;
          background:${color}33;border:2.5px solid ${color};
          display:flex;align-items:center;justify-content:center;
          box-shadow:0 0 8px ${color}66;position:relative;
        ">
          <div style="width:12px;height:2px;background:${color};position:absolute"></div>
          <div style="width:2px;height:12px;background:${color};position:absolute"></div>
          <div style="
            position:absolute;top:-16px;left:50%;transform:translateX(-50%);
            background:#0d1117;border:1px solid ${color}88;border-radius:4px;
            padding:1px 5px;white-space:nowrap;
            font-size:9px;font-weight:700;color:${color};
          ">${stand.score}</div>
        </div>`,
        iconSize: [28, 28],
        iconAnchor: [14, 14],
      });

      const marker = L.marker([stand.lat, stand.lng], { icon: standIcon, pane: 'markerPane' });

      // x4520-E: Emit stand click event to open PinnablePanel V2 instead of Leaflet popup
      if (onStandClick) {
        marker.on('click', () => onStandClick(stand));
      } else {
        // Fallback: Leaflet popup (legacy)
        const j = stand.justification || {};
        const sections = [
          ['Analyse du vent', j.analyse_vent, '#3498DB'],
          ['Lecture corridor', j.lecture_corridor, '#9B59B6'],
          ['Zones 600m', j.lecture_zones_600m, '#FF6B35'],
          ['Topographie', j.lecture_topographie, '#27AE60'],
          ['Hydrographie', j.lecture_hydrographie, '#3498DB'],
          ['Zones fraîcheur', j.lecture_zones_fraicheur, '#1ABC9C'],
          ['Pression', j.analyse_pression, '#E67E22'],
          ['Type d\'affût', j.justification_type_affut, '#E74C3C'],
          ['Orientation', j.justification_orientation, '#2ECC71'],
          ['Score', j.justification_score, '#F39C12'],
          ['Recommandations', j.recommandations_pratiques, '#FF6B35'],
        ];

        const sectionsHtml = sections.filter(s => s[1]).map(([title, text, col]) =>
          `<div style="margin-bottom:6px;padding:4px 6px;background:rgba(255,255,255,0.03);border-left:2px solid ${col};border-radius:0 4px 4px 0">
            <div style="font-size:9px;font-weight:600;color:${col};margin-bottom:2px">${title}</div>
            <div style="font-size:8px;color:#aaa;line-height:1.4;white-space:pre-line">${text}</div>
          </div>`
        ).join('');

        const factorBars = ['wind', 'corridor', 'topography', 'cover', 'hydrology', 'pressure', 'coolzone'].map(k => {
          const score = stand.factors?.[k]?.score ?? 0;
          const labels = { wind: 'Vent', corridor: 'Corridor', topography: 'Topo', cover: 'Couvert', hydrology: 'Hydro', pressure: 'Pression', coolzone: 'Fraîcheur' };
          const col = score > 70 ? '#2ECC71' : score > 50 ? '#F39C12' : '#E74C3C';
          return `<div style="display:flex;align-items:center;gap:3px;margin:1px 0">
            <span style="width:48px;font-size:8px;color:#999">${labels[k] || k}</span>
            <div style="flex:1;height:3px;background:rgba(255,255,255,0.08);border-radius:2px">
              <div style="width:${score}%;height:100%;background:${col};border-radius:2px"></div>
            </div>
            <span style="width:22px;font-size:7px;color:${col};text-align:right;font-weight:700">${Math.round(score)}</span>
          </div>`;
        }).join('');

        const popupContent = `
          <div style="min-width:280px;max-width:340px;max-height:400px;overflow-y:auto;padding:4px;font-family:system-ui">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;padding-bottom:6px;border-bottom:1px solid rgba(255,255,255,0.1)">
              <div>
                <div style="font-size:13px;font-weight:700;color:#fff">${stand.type_name}</div>
                <div style="font-size:10px;color:#888">Rang #${stand.rank} | ${stand.orientation_label} (${stand.orientation_deg}°) | ${stand.height_m}m</div>
              </div>
              <div style="width:44px;height:44px;border-radius:50%;border:3px solid ${stand.score > 75 ? '#2ECC71' : stand.score > 55 ? '#F39C12' : '#E74C3C'};display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:800;color:${stand.score > 75 ? '#2ECC71' : stand.score > 55 ? '#F39C12' : '#E74C3C'}">${stand.score}</div>
            </div>
            <div style="font-size:9px;font-weight:600;color:#f5a623;margin-bottom:4px">Facteurs (7)</div>
            ${factorBars}
            <div style="font-size:9px;font-weight:600;color:#f5a623;margin:8px 0 4px">Justification professionnelle</div>
            ${sectionsHtml}
          </div>`;

        marker.bindPopup(popupContent, {
          maxWidth: 360,
          maxHeight: 420,
          className: 'bionic-stand-popup',
          autoPanPadding: [20, 20],
        });
      }

      group.addLayer(marker);
    }

    group.addTo(map);
    layerRef.current = group;
  }, [map, clearLayers]);

  const renderRef = useRef(renderStands);
  renderRef.current = renderStands;

  const fetchData = useCallback(async () => {
    if (centerLat == null || centerLng == null || !enabled) {
      clearLayers();
      return;
    }

    const key = `${centerLat.toFixed(6)}:${centerLng.toFixed(6)}:${species}:${windDirection}:${windSpeed}`;
    if (lastKeyRef.current === key && layerRef.current) return;
    if (lastKeyRef.current === key && cacheRef.current) {
      renderRef.current(cacheRef.current);
      return;
    }
    lastKeyRef.current = key;

    if (abortRef.current) abortRef.current.abort();
    abortRef.current = new AbortController();

    try {
      const apiUrl = process.env.REACT_APP_BACKEND_URL;
      const res = await fetch(
        `${apiUrl}/api/v1/stand-recommendation/recommend?lat=${centerLat}&lng=${centerLng}&wind_direction=${windDirection}&wind_speed_kmh=${windSpeed}&species=${species}`,
        { signal: abortRef.current.signal }
      );
      if (!res.ok) return;
      const data = await res.json();
      cacheRef.current = data;
      if (lastKeyRef.current === key) renderRef.current(data);
    } catch (err) {
      if (err.name !== 'AbortError') console.error('[STANDS-LAYER]', err);
    }
  }, [centerLat, centerLng, species, windDirection, windSpeed, enabled, clearLayers]);

  useEffect(() => {
    fetchData();
    return () => {
      if (abortRef.current) abortRef.current.abort();
      // x4600-R4: UNMOUNT CLEANUP — supprimer les layers Leaflet au démontage
      clearLayers();
    };
  }, [fetchData, clearLayers]);

  useEffect(() => {
    if (cacheRef.current) renderStands(cacheRef.current);
  }, [renderStands]);

  useEffect(() => {
    if (!enabled) clearLayers();
  }, [enabled, clearLayers]);

  return null;
};

export default StandsMapLayer;

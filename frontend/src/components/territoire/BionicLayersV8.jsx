/**
 * BionicLayersV8.jsx — RENDERING V8-INSTITUTIONNEL EXCLUSIF
 * ===========================================================
 * PHASE-4B: Source UNIQUE /api/v8/institutional/territoire
 *
 * ZONES:    polygones organiques terrain-aware, 14-20 vertices
 *           contours 100% opaques, interieurs 100% transparents
 *           ZERO smoothing, ZERO arrondi, ZERO interpolation
 *
 * CORRIDORS: veines animales directionnelles, angulaires
 *            couleur UNIQUE #FF8F00, ZERO glow, ZERO halo
 *            lineCap butt, lineJoin miter, smoothFactor 0
 *
 * AFFUTS:   cercle gris #9E9E9E + X central #424242
 *           ZERO halo, ZERO glow
 *
 * SALINES:  cercle organique #FDD835, opacite 100%
 *
 * HOTSPOTS: marqueur rouge #E53935
 *
 * Z-ORDER:  zones < corridors < salines < hotspots < affuts
 */
import { useEffect, useRef, useCallback } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

// COULEURS EXACTES BCE-4X — DOCUMENT MAITRE
const ZONE_COLORS = {
  rut:          { stroke: '#C62828', weight: 2.5 },
  alimentation: { stroke: '#2E7D32', weight: 2.0 },
  repos:        { stroke: '#1565C0', weight: 1.8 },
  eau:          { stroke: '#29B6F6', weight: 1.5 },
  affuts:       { stroke: '#C62828', weight: 2.0 },
};

// CORRIDOR: COULEUR UNIQUE #FF8F00 — ZERO multicolore
const CORRIDOR_COLOR = '#FF8F00';
const CORRIDOR_WEIGHT = { faible: 1.2, modere: 2.0, fort: 3.0, majeur: 3.0, critique: 3.0 };

// AFFUT: cercle gris + X central
const AFFUT_COLOR = '#9E9E9E';
const AFFUT_X_COLOR = '#424242';
const AFFUT_SIZE = { optimal: 8, bon: 7, acceptable: 6 };

// SALINE: cercle organique jaune
const SALINE_COLOR = '#FDD835';

// HOTSPOT: rouge
const HOTSPOT_COLOR = '#E53935';

const BionicLayersV8 = ({
  bundleData,
  showZones = true,
  showCorridors = true,
  showAffuts = true,
  showSalines = true,
  showHotspots = true,
  enabled = true,
  onDataLoaded = null,
}) => {
  const map = useMap();
  const groupRef = useRef(null);
  const onDataLoadedRef = useRef(onDataLoaded);
  onDataLoadedRef.current = onDataLoaded;

  const clearOwnLayers = useCallback(() => {
    if (groupRef.current && map) {
      try { map.removeLayer(groupRef.current); } catch (e) { /* */ }
      groupRef.current = null;
    }
  }, [map]);

  const renderLayers = useCallback(() => {
    if (!map || !enabled || !bundleData) return;
    clearOwnLayers();

    const group = L.featureGroup();
    const zones = bundleData.zones || [];
    const corridors = bundleData.corridors || [];
    const affuts = bundleData.affuts || [];
    const salines = bundleData.salines || [];
    const hotspots = bundleData.hotspots || [];

    // Z-ORDER 1: ZONES (dessous)
    // Polygones organiques, contours opaques, interieurs transparents
    // ZERO smoothing, ZERO arrondi
    if (showZones && zones.length > 0) {
      zones.forEach(z => {
        const cfg = ZONE_COLORS[z.type] || ZONE_COLORS.alimentation;
        if (!z.polygon || z.polygon.length < 4) return;

        const poly = L.polygon(z.polygon, {
          color: cfg.stroke,
          weight: cfg.weight,
          opacity: 1.0,
          fillColor: cfg.stroke,
          fillOpacity: 0,
          lineCap: 'butt',
          lineJoin: 'miter',
          smoothFactor: 0,
          interactive: true,
        });

        const t = z.terrain || {};
        const terrain = t.canopy !== undefined
          ? `<br><span style="font-size:9px;color:#888">Canopy ${Math.round(t.canopy*100)}% | Pente ${t.pente_deg}deg | Eau ${t.distance_eau_m}m</span>`
          : '';
        const excl = z.excluded
          ? `<br><span style="font-size:9px;color:#EF4444;font-weight:700">EXCLU: ${z.exclusion_reason}</span>`
          : '';

        poly.bindTooltip(
          `<b style="color:${cfg.stroke}">${z.type}</b> ${z.score}/100${terrain}${excl}`,
          { sticky: true, opacity: 0.95 }
        );
        group.addLayer(poly);
      });
    }

    // Z-ORDER 2: CORRIDORS (milieu)
    // Veines animales directionnelles, angulaires
    // lineCap BUTT, lineJoin MITER, smoothFactor 0
    // ZERO glow, ZERO halo, ZERO multicolore
    if (showCorridors && corridors.length > 0) {
      corridors.forEach(c => {
        const path = c.path || [[c.start.lat, c.start.lng], [c.end.lat, c.end.lng]];
        const w = CORRIDOR_WEIGHT[c.type] || 2.0;

        const line = L.polyline(path, {
          color: CORRIDOR_COLOR,
          weight: w,
          opacity: 1.0,
          lineCap: 'butt',
          lineJoin: 'miter',
          smoothFactor: 0,
          interactive: true,
        });

        line.bindTooltip(
          `<b style="color:${CORRIDOR_COLOR}">${c.type}</b> int:${c.intensity}`,
          { sticky: true, opacity: 0.95 }
        );
        group.addLayer(line);
      });
    }

    // Z-ORDER 3: SALINES
    // Cercle organique jaune, opacite 100%
    if (showSalines && salines.length > 0) {
      salines.forEach((s, idx) => {
        const lat = s.lat || s.center?.lat;
        const lon = s.lng || s.lon || s.center?.lng;
        if (!lat || !lon) return;

        const circle = L.circleMarker([lat, lon], {
          radius: 7,
          color: SALINE_COLOR,
          fillColor: SALINE_COLOR,
          fillOpacity: 0.4,
          weight: 2,
          opacity: 1.0,
          interactive: true,
        });

        circle.bindTooltip(
          `<b style="color:${SALINE_COLOR}">Saline</b> ${s.score || ''}/100`,
          { sticky: true, opacity: 0.95 }
        );
        group.addLayer(circle);
      });
    }

    // Z-ORDER 4: HOTSPOTS
    // Marqueur rouge
    if (showHotspots && hotspots.length > 0) {
      hotspots.forEach(h => {
        const lat = h.lat || h.center?.lat;
        const lon = h.lng || h.lon || h.center?.lng;
        if (!lat || !lon) return;

        const circle = L.circleMarker([lat, lon], {
          radius: 5,
          color: HOTSPOT_COLOR,
          fillColor: HOTSPOT_COLOR,
          fillOpacity: 0.6,
          weight: 2,
          opacity: 1.0,
          interactive: true,
        });

        circle.bindTooltip(
          `<b style="color:${HOTSPOT_COLOR}">Hotspot</b> ${h.score || ''}/100`,
          { sticky: true, opacity: 0.95 }
        );
        group.addLayer(circle);
      });
    }

    // Z-ORDER 5: AFFUTS (dessus)
    // DOCUMENT MAITRE: cercle gris + X central, opacite 100%, ZERO halo
    if (showAffuts && affuts.length > 0) {
      affuts.forEach(a => {
        const sz_px = AFFUT_SIZE[a.quality] || 6;

        // Cercle gris
        const circle = L.circleMarker([a.lat, a.lng], {
          radius: sz_px,
          color: AFFUT_COLOR,
          fillColor: AFFUT_COLOR,
          fillOpacity: 0.3,
          weight: 2,
          opacity: 1.0,
          interactive: true,
        });

        // X central via divIcon
        const xIcon = L.divIcon({
          className: 'affut-x-v8',
          html: `<div style="width:${sz_px*2}px;height:${sz_px*2}px;display:flex;align-items:center;justify-content:center;font-size:${sz_px+2}px;font-weight:900;color:${AFFUT_X_COLOR};line-height:1;">X</div>`,
          iconSize: [sz_px*2, sz_px*2],
          iconAnchor: [sz_px, sz_px],
        });
        L.marker([a.lat, a.lng], { icon: xIcon, interactive: false }).addTo(group);

        const score = a.score !== undefined ? a.score : a.zone_score;
        circle.bindTooltip(
          `<b style="color:${AFFUT_COLOR}">Affut</b> ${a.quality} ${score}/100 ${a.orientation_deg}deg`,
          { sticky: true, opacity: 0.95 }
        );
        group.addLayer(circle);
      });
    }

    group.addTo(map);
    groupRef.current = group;

    if (onDataLoadedRef.current) {
      onDataLoadedRef.current({
        zones_count: zones.length,
        corridors_count: corridors.length,
        affuts_count: affuts.length,
        salines_count: salines.length,
        hotspots_count: hotspots.length,
        engine: 'V8-INSTITUTIONNEL-EXCLUSIF',
        esi_omega: bundleData.esi_omega,
      });
    }
  }, [map, bundleData, enabled, showZones, showCorridors, showAffuts, showSalines, showHotspots, clearOwnLayers]);

  useEffect(() => {
    renderLayers();
    return () => clearOwnLayers();
  }, [renderLayers, clearOwnLayers]);

  return null;
};

export default BionicLayersV8;

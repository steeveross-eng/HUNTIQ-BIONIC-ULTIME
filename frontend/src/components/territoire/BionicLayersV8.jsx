/**
 * BionicLayersV8.jsx — PROTOCOLE V6 ABSOLU
 * ==========================================
 * V8-ULTIME-PROTOCOLE-V6-ABSOLU-Omega-FINAL
 *
 * RENDU IDENTIQUE V6. ZERO DEVIATION.
 *
 * ZONES:    contours 100% opaques, interieurs 100% transparents
 *           couleurs EXACTES V6, epaisseurs EXACTES V6
 *           formes organiques irregulieres, ZERO smoothing
 *
 * CORRIDORS: couleur UNIQUE #FF8F00, epaisseurs 1.2/2.0/3.0 px
 *            opacite 100%, ZERO glow, ZERO halo, ZERO multicolore
 *
 * AFFUTS:   jaune #FDD835, 6-8px, opacite 100%, ZERO halo
 *
 * Z-ORDER:  zones DESSOUS > corridors MILIEU > affuts DESSUS
 */
import { useEffect, useRef, useCallback } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

// ═══ PROTOCOLE V6 ABSOLU — COULEURS EXACTES ═══
const ZONE_COLORS = {
  rut:          { stroke: '#C62828', weight: 2.5 },
  alimentation: { stroke: '#2E7D32', weight: 2.0 },
  repos:        { stroke: '#1565C0', weight: 1.8 },
  eau:          { stroke: '#29B6F6', weight: 1.5 },
  affuts:       { stroke: '#C62828', weight: 2.0 },
};

// ═══ PROTOCOLE V6 ABSOLU — CORRIDOR COULEUR UNIQUE #FF8F00 ═══
const CORRIDOR_WEIGHT = { faible: 1.2, modere: 2.0, fort: 3.0, majeur: 3.0, critique: 3.0 };
const CORRIDOR_COLOR = '#FF8F00';

// ═══ DOCUMENT MAITRE ULTIME MAX — AFFUT: cercle gris + X central ═══
const AFFUT_COLOR = '#9E9E9E';
const AFFUT_X_COLOR = '#424242';
const AFFUT_SIZE = { optimal: 8, bon: 7, acceptable: 6 };

const BionicLayersV8 = ({
  bundleData,
  showZones = true,
  showCorridors = true,
  showAffuts = true,
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

    // ═══ Z-ORDER 1: ZONES (dessous) ═══
    // Contours 100% opaques, interieurs 100% transparents
    // Formes organiques, ZERO smoothing, ZERO arrondi
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
          ? `<br><span style="font-size:9px;color:#888">Canopy ${Math.round(t.canopy*100)}% | Pente ${t.pente_deg}° | Eau ${t.distance_eau_m}m | Route ${t.distance_route_m}m</span>`
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

    // ═══ Z-ORDER 2: CORRIDORS (milieu) ═══
    // Couleur UNIQUE #FF8F00, epaisseur selon intensite
    // ZERO glow, ZERO halo, ZERO multicolore
    if (showCorridors && corridors.length > 0) {
      corridors.forEach(c => {
        const path = c.path || [[c.start.lat, c.start.lng], [c.end.lat, c.end.lng]];
        const w = CORRIDOR_WEIGHT[c.type] || 2.0;

        const line = L.polyline(path, {
          color: CORRIDOR_COLOR,
          weight: w,
          opacity: 1.0,
          lineCap: 'round',
          lineJoin: 'round',
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

    // ═══ Z-ORDER 3: AFFUTS (dessus) ═══
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
          `<b style="color:${AFFUT_COLOR}">Affut</b> ${a.quality} ${score}/100 ${a.orientation_deg}°`,
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
        engine: 'V8-PROTOCOLE-V6-ABSOLU',
      });
    }
  }, [map, bundleData, enabled, showZones, showCorridors, showAffuts, clearOwnLayers]);

  useEffect(() => {
    renderLayers();
    return () => clearOwnLayers();
  }, [renderLayers, clearOwnLayers]);

  return null;
};

export default BionicLayersV8;

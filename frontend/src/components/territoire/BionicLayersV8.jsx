/**
 * BionicLayersV8.jsx — RENDERING V8-INSTITUTIONNEL COMPLET
 * ==========================================================
 * PHASE-4E: TOUS ENGINES TERRITOIRE RÉINTRODUITS
 *
 * ZONES:       polygones organiques ultra-précis (24-36 vertices Catmull-Rom)
 *              courbes douces, zéro angle, contours opaques, fill transparent
 * CORRIDORS:   veines animales continues (Bézier cubique, 8-12 pts)
 *              #FF8F00, rayon 600m, extension ±30%
 * AFFUTS:      cercle gris #9E9E9E + X central #424242
 * SALINES:     cercle organique #FDD835
 * HOTSPOTS:    marqueur multi-intensité 1-5 (rouge gradué)
 * VENT:        flèches directionnelles #90CAF9 (direction+intensité+turbulence)
 * CONTAMINATION: cône directionnel décroissant #FF7043→transparent
 * PRESSION:    gradient intensité zone humaine #EF5350
 *
 * Z-ORDER: pression < zones < corridors < vent < contamination < salines < hotspots < affûts
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

const CORRIDOR_COLOR = '#FF8F00';
const CORRIDOR_COLORS = {
  critique: '#FF0000',
  majeur: '#D32F2F',
  fort: '#FF8F00',
  modere: '#FFEB3B',
  faible: '#FFFFFF',
};
const CORRIDOR_WEIGHT = { faible: 1.4, modere: 1.8, fort: 2.2, majeur: 2.4, critique: 2.6 };
const CORRIDOR_OPACITY = { faible: 0.65, modere: 0.75, fort: 0.85, majeur: 0.90, critique: 0.95 };

const AFFUT_COLOR = '#9E9E9E';
const AFFUT_X_COLOR = '#424242';
const AFFUT_SIZE = { optimal: 8, bon: 7, acceptable: 6 };

const SALINE_COLOR = '#FDD835';
const WIND_COLOR = '#90CAF9';
const CONTAM_COLOR = '#FF7043';
const PRESSION_COLOR = '#EF5350';

// Hotspot intensité 1-5
const HOTSPOT_COLORS = ['#FFCDD2', '#EF9A9A', '#EF5350', '#E53935', '#B71C1C'];
const HOTSPOT_SIZES = [4, 5, 6, 7, 8];

const BionicLayersV8 = ({
  bundleData,
  showZones = true,
  showCorridors = true,
  showAffuts = true,
  showSalines = true,
  showHotspots = true,
  showWind = true,       // Delegue a WindFlowLayer
  showContamination = true,
  showPression = true,
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
    const windVectors = bundleData.wind_vectors || [];
    const contamination = bundleData.contamination || null;
    const pression = bundleData.pression || null;

    // ═══ Z-ORDER 1: PRESSION HUMAINE (gradient) ═══
    if (showPression && pression && pression.pression_score !== undefined) {
      const score = pression.pression_score;
      if (score > 10) {
        const center = map.getCenter();
        const opacity = Math.min(0.35, score / 200);
        const radius = 300 + score * 3;
        const circle = L.circle([center.lat, center.lng], {
          radius: radius,
          color: PRESSION_COLOR,
          fillColor: PRESSION_COLOR,
          fillOpacity: opacity,
          weight: 1,
          opacity: 0.4,
          dashArray: '4,4',
          interactive: true,
        });
        circle.bindTooltip(
          `<b style="color:${PRESSION_COLOR}">Pression humaine</b> ${score}/100`,
          { sticky: true, opacity: 0.95 }
        );
        group.addLayer(circle);
      }
    }

    // ═══ Z-ORDER 2: ZONES (polygones organiques ultra-précis) ═══
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
          lineCap: 'round',
          lineJoin: 'round',
          smoothFactor: 1,
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

    // ═══ Z-ORDER 3: CORRIDORS (veines animales Catmull-Rom V9-x20) ═══
    if (showCorridors && corridors.length > 0) {
      corridors.forEach(c => {
        const path = c.path || [[c.start.lat, c.start.lng], [c.end.lat, c.end.lng]];
        const w = CORRIDOR_WEIGHT[c.type] || 2.0;
        const color = CORRIDOR_COLORS[c.type] || CORRIDOR_COLOR;
        const opacity = CORRIDOR_OPACITY[c.type] || 0.85;

        const line = L.polyline(path, {
          color: color,
          weight: w,
          opacity: opacity,
          lineCap: 'round',
          lineJoin: 'round',
          smoothFactor: 1,
          interactive: true,
        });

        line.bindTooltip(
          `<b style="color:${color}">${c.type}</b> int:${c.intensity} | ${c.species_profile || ''}`,
          { sticky: true, opacity: 0.95 }
        );
        group.addLayer(line);
      });
    }

    // Z-ORDER 4: VENT — DELEGUEE A WindFlowLayer (VENTUSKY-STEEVE-MAX dynamique)
    // Les vecteurs statiques sont remplaces par les streamlines temps reel

    // ═══ Z-ORDER 5: CONTAMINATION OLFACTIVE (cône directionnel) ═══
    if (showContamination && contamination && contamination.polygon) {
      const cone = L.polygon(contamination.polygon, {
        color: CONTAM_COLOR,
        weight: 1.5,
        opacity: 0.7,
        fillColor: CONTAM_COLOR,
        fillOpacity: 0.15,
        dashArray: '4,4',
        interactive: true,
      });

      cone.bindTooltip(
        `<b style="color:${CONTAM_COLOR}">Contamination olfactive</b><br>Direction: ${contamination.direction_deg}deg | Portee: ${contamination.reach_m}m`,
        { sticky: true, opacity: 0.95 }
      );
      group.addLayer(cone);
    }

    // ═══ Z-ORDER 6: SALINES ═══
    if (showSalines && salines.length > 0) {
      salines.forEach(s => {
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

    // ═══ Z-ORDER 7: HOTSPOTS (intensité 1-5) ═══
    if (showHotspots && hotspots.length > 0) {
      hotspots.forEach(h => {
        const lat = h.lat || h.center?.lat;
        const lon = h.lng || h.lon || h.center?.lng;
        if (!lat || !lon) return;

        // Intensité 1-5 basée sur le score
        const intensity = h.intensity || 50;
        const level = Math.min(4, Math.max(0, Math.floor(intensity / 20)));
        const color = HOTSPOT_COLORS[level];
        const size = HOTSPOT_SIZES[level];

        const circle = L.circleMarker([lat, lon], {
          radius: size,
          color: color,
          fillColor: color,
          fillOpacity: 0.6,
          weight: 2,
          opacity: 1.0,
          interactive: true,
        });

        circle.bindTooltip(
          `<b style="color:${color}">Hotspot</b> intensite:${level+1}/5 (${Math.round(intensity)})`,
          { sticky: true, opacity: 0.95 }
        );
        group.addLayer(circle);
      });
    }

    // ═══ Z-ORDER 8: AFFUTS (dessus — cercle gris + X) ═══
    if (showAffuts && affuts.length > 0) {
      affuts.forEach(a => {
        const sz_px = AFFUT_SIZE[a.quality] || 6;

        const circle = L.circleMarker([a.lat, a.lng], {
          radius: sz_px,
          color: AFFUT_COLOR,
          fillColor: AFFUT_COLOR,
          fillOpacity: 0.3,
          weight: 2,
          opacity: 1.0,
          interactive: true,
        });

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
        wind_count: windVectors.length,
        contamination: !!contamination,
        pression: !!(pression && pression.pression_score > 0),
        engine: 'V8-INSTITUTIONNEL-COMPLET',
        esi_omega: bundleData.esi_omega,
      });
    }
  }, [map, bundleData, enabled, showZones, showCorridors, showAffuts, showSalines, showHotspots, showWind, showContamination, showPression, clearOwnLayers]);

  useEffect(() => {
    renderLayers();
    return () => clearOwnLayers();
  }, [renderLayers, clearOwnLayers]);

  return null;
};

export default BionicLayersV8;

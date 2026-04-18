/**
 * BionicLayersV8.jsx — RENDERER V20-INSTITUTIONNEL
 * ==================================================
 * PHASE-INSTITUTIONNELLE-Omega V20
 *
 * CONTOUR:     L.circle 600m, #9E9E9E, 2.2px, pointilles, 0.85
 * CORRIDORS:   4 niveaux (EXTREME/INTENSE/SAISONNIER/NORMAL) + RESEAU
 *              Catmull-Rom, smoothFactor=0
 * ZONES:       Catmull-Rom 22-40 vertices, terrain reel + IA
 * CONTAMINATION: Multi-cones SOURCE=AFFUTS, 3 intensites
 * SALINES:     VALIDEE jaune / A-REPOSITIONNER rouge + suggestion
 * HOTSPOTS:    intensite 1-5
 * AFFUTS:      cercle gris #9E9E9E + X #424242
 * VENT:        delegue a WindFlowLayer (Ventusky)
 *
 * Z-ORDER: contour < zones < corridors < contamination < salines < hotspots < affuts
 * ZERO pression. ZERO buffer. ZERO Bezier. ZERO smoothing. ZERO fallback.
 */
import { useEffect, useRef, useCallback } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

// ═══ PALETTE BCE-4X V9-INSTITUTIONNEL ═══
const ZONE_COLORS = {
  rut:          { stroke: '#C62828', weight: 2.5 },
  alimentation: { stroke: '#2E7D32', weight: 2.0 },
  repos:        { stroke: '#1565C0', weight: 1.8 },
  eau:          { stroke: '#29B6F6', weight: 1.5 },
  affuts:       { stroke: '#C62828', weight: 2.0 },
};

// CORRIDORS Omega: 4 niveaux
const CORRIDOR_STYLES = {
  extreme:    { color: '#D32F2F', weight: 4.2, opacity: 0.95 },
  intense:    { color: '#FF9800', weight: 3.0, opacity: 0.90 },
  saisonnier: { color: '#4CAF50', weight: 2.4, opacity: 0.90 },
  normal:     { color: '#FFFFFF', weight: 1.6, opacity: 0.85 },
};

const AFFUT_COLOR = '#9E9E9E';
const AFFUT_X_COLOR = '#424242';
const AFFUT_SIZE = { optimal: 8, bon: 7, acceptable: 6 };

const SALINE_COLOR = '#FDD835';
const CONTAM_COLOR = '#FF7043';

const HOTSPOT_COLORS = ['#FFCDD2', '#EF9A9A', '#EF5350', '#E53935', '#B71C1C'];
const HOTSPOT_SIZES = [4, 5, 6, 7, 8];

// CONTOUR-TERRITOIRE 600m
const CONTOUR_COLOR = '#9E9E9E';

const BionicLayersV8 = ({
  bundleData,
  waypointCenter = null,
  showZones = true,
  showCorridors = true,
  showAffuts = true,
  showSalines = true,
  showHotspots = true,
  showWind = true,
  showContamination = true,
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
    const contamination = bundleData.contamination || null;

    // ═══ Z-0: CONTOUR-TERRITOIRE-Omega 600m ═══
    // Cercle institutionnel centre sur waypoint. Rayon 600m exact.
    // Element visuel AUTONOME. ZERO interaction avec aucun engine.
    if (waypointCenter) {
      const contour = L.circle([waypointCenter.lat, waypointCenter.lng], {
        radius: 600,
        color: CONTOUR_COLOR,
        weight: 2.2,
        opacity: 0.85,
        fillOpacity: 0,
        dashArray: '4,4',
        interactive: false,
      });
      group.addLayer(contour);
    }

    // ═══ Z-2: ZONES (Catmull-Rom V9, smoothFactor=0, ZERO interpolation) ═══
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

    // ═══ Z-2: CORRIDORS-Omega (4 niveaux: NORMAL/INTENSE/EXTREME/SAISONNIER) ═══
    if (showCorridors && corridors.length > 0) {
      corridors.forEach(c => {
        const path = c.path || [[c.start.lat, c.start.lng], [c.end.lat, c.end.lng]];
        const style = CORRIDOR_STYLES[c.type] || CORRIDOR_STYLES.normal;
        const color = c.color || style.color;
        const weight = c.weight || style.weight;
        const opacity = c.opacity || style.opacity;

        const line = L.polyline(path, {
          color: color,
          weight: weight,
          opacity: opacity,
          lineCap: 'round',
          lineJoin: 'round',
          smoothFactor: 0,
          interactive: true,
        });

        // Fleche directionnelle
        if (path.length >= 3) {
          const midIdx = Math.floor(path.length / 2);
          const prev = path[midIdx - 1] || path[0];
          const mid = path[midIdx];
          const next = path[midIdx + 1] || path[path.length - 1];
          const dx = next[1] - prev[1];
          const dy = next[0] - prev[0];
          const len = Math.sqrt(dx * dx + dy * dy);
          if (len > 0.0001) {
            const arrowSize = 0.0008;
            const nx = dx / len;
            const ny = dy / len;
            const arrow = L.polygon([
              [mid[0] + ny * arrowSize, mid[1] + nx * arrowSize],
              [mid[0] - ny * arrowSize * 0.5 + nx * arrowSize * 0.4, mid[1] - nx * arrowSize * 0.5 - ny * arrowSize * 0.4],
              [mid[0] - ny * arrowSize * 0.5 - nx * arrowSize * 0.4, mid[1] - nx * arrowSize * 0.5 + ny * arrowSize * 0.4],
            ], { color, fillColor: color, fillOpacity: opacity, weight: 1, opacity, smoothFactor: 0, interactive: false });
            group.addLayer(arrow);
          }
        }

        const costStr = c.cost_surface !== undefined ? ` | cost:${c.cost_surface}` : '';
        const netStr = c.is_network_link ? ' [RESEAU]' : '';
        line.bindTooltip(
          `<b style="color:${color}">${c.type.toUpperCase()}</b> int:${Math.round(c.intensity)}${costStr} | ${c.species_profile || ''}${netStr}`,
          { sticky: true, opacity: 0.95 }
        );
        group.addLayer(line);
      });
    }

    // ═══ Z-4: CONTAMINATION-Omega (multi-cones depuis AFFUTS) ═══
    // SOURCE = AFFUTS OPTIMAUX. ZERO waypoint. 3 intensites par affut.
    if (showContamination && contamination) {
      const cones = Array.isArray(contamination) ? contamination : [contamination];
      cones.forEach(cone => {
        if (!cone.polygon || cone.polygon.length < 3) return;

        const color = cone.color || '#FF7043';
        const opacity = cone.opacity || 0.2;
        const fillOpacity = cone.fill_opacity || 0.1;

        const poly = L.polygon(cone.polygon, {
          color: color,
          weight: 1.2,
          opacity: opacity,
          fillColor: color,
          fillOpacity: fillOpacity,
          dashArray: cone.intensity === 'faible' ? '3,3' : cone.intensity === 'moyen' ? '5,3' : null,
          smoothFactor: 0,
          interactive: true,
        });

        const src = cone.affut_source || {};
        poly.bindTooltip(
          `<b style="color:${color}">Contamination ${cone.intensity}</b><br>` +
          `Portee: ${cone.reach_m}m | Angle: ${cone.cone_angle_deg}deg<br>` +
          `<span style="font-size:9px">Source: Affut ${src.quality || ''} (${src.score || ''})</span>`,
          { sticky: true, opacity: 0.95 }
        );
        group.addLayer(poly);
      });
    }

    // ═══ Z-5: SALINES-Omega (VALIDEE vs A-REPOSITIONNER) ═══
    if (showSalines && salines.length > 0) {
      salines.forEach(s => {
        const lat = s.lat || s.center?.lat;
        const lon = s.lng || s.lon || s.center?.lng;
        if (!lat || !lon) return;

        const isValidee = s.status === 'SALINE-VALIDEE-Omega';
        const color = isValidee ? SALINE_COLOR : '#EF5350';
        const dashArray = isValidee ? null : '3,3';

        const circle = L.circleMarker([lat, lon], {
          radius: isValidee ? 8 : 6,
          color: color,
          fillColor: color,
          fillOpacity: isValidee ? 0.5 : 0.2,
          weight: 2,
          opacity: 1.0,
          dashArray: dashArray,
          interactive: true,
        });

        let tooltipHtml = `<b style="color:${color}">${isValidee ? 'Saline VALIDEE' : 'Saline A REPOSITIONNER'}</b> ${s.score || ''}/100`;
        tooltipHtml += `<br><span style="font-size:9px">Eau: ${s.eau_distance_m || '?'}m ${s.eau_conforme ? 'OK' : 'HORS'}`;
        tooltipHtml += ` | Corridor: ${s.corridor_distance_m || '?'}m ${s.corridor_conforme ? 'OK' : 'HORS'}</span>`;
        if (s.suggestion) {
          tooltipHtml += `<br><span style="font-size:9px;color:#4CAF50">Suggestion: lat=${s.suggestion.lat} lon=${s.suggestion.lon} (score ${s.suggestion.score})</span>`;
        }

        circle.bindTooltip(tooltipHtml, { sticky: true, opacity: 0.95 });
        group.addLayer(circle);

        // Afficher suggestion de repositionnement
        if (s.suggestion && !isValidee) {
          const sg = s.suggestion;
          const sugMarker = L.circleMarker([sg.lat, sg.lon], {
            radius: 5,
            color: '#4CAF50',
            fillColor: '#4CAF50',
            fillOpacity: 0.4,
            weight: 1.5,
            opacity: 0.8,
            dashArray: '2,2',
            interactive: true,
          });
          sugMarker.bindTooltip(
            `<b style="color:#4CAF50">Position suggeree</b><br>Eau: ${sg.eau_distance_m}m | Corridor: ${sg.corridor_distance_m}m`,
            { sticky: true, opacity: 0.95 }
          );
          group.addLayer(sugMarker);

          // Ligne pointillee saline → suggestion
          const line = L.polyline([[lat, lon], [sg.lat, sg.lon]], {
            color: '#4CAF50',
            weight: 1,
            opacity: 0.5,
            dashArray: '3,5',
            interactive: false,
          });
          group.addLayer(line);
        }
      });
    }

    // ═══ Z-6: HOTSPOTS (intensite 1-5) ═══
    if (showHotspots && hotspots.length > 0) {
      hotspots.forEach(h => {
        const lat = h.lat || h.center?.lat;
        const lon = h.lng || h.lon || h.center?.lng;
        if (!lat || !lon) return;

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

    // ═══ Z-7: AFFUTS (cercle gris + X) ═══
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
          className: 'affut-x-v9',
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
        contamination: Array.isArray(contamination) ? contamination.length : 0,
        engine: 'V20-INSTITUTIONNEL',
        esi_omega: bundleData.esi_omega,
      });
    }
  }, [map, bundleData, waypointCenter, enabled, showZones, showCorridors, showAffuts, showSalines, showHotspots, showContamination, clearOwnLayers]);

  useEffect(() => {
    renderLayers();
    return () => clearOwnLayers();
  }, [renderLayers, clearOwnLayers]);

  return null;
};

export default BionicLayersV8;

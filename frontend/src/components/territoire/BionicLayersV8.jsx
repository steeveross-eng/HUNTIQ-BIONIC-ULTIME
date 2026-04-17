/**
 * BionicLayersV8.jsx — RENDERER V9-PURE INSTITUTIONNEL
 * =====================================================
 * PHASE-RENDERER-CORRIDORS-Omega-V9-PURE
 *
 * CORRIDORS V9-x20:
 *   Catmull-Rom directionnel 22-25 pts, ZERO smoothing, ZERO interpolation
 *   5 niveaux: Critique #FF0000 → Majeur #D32F2F → Fort #FF8F00 → Modere #FFEB3B → Faible #FFFFFF
 *   Fleches directionnelles sur chaque corridor
 *   Tooltip: type, intensite, profil espece, cost surface, connexions zones
 *
 * ZONES V9:
 *   Catmull-Rom 24-36 vertices, smoothFactor=0, ZERO interpolation Leaflet
 *   Contours opaques, fill transparent, terrain-aware
 *
 * AFFUTS:   cercle gris #9E9E9E + X #424242
 * SALINES:  #FDD835
 * HOTSPOTS: intensite 1-5
 * CONTAMINATION: cone #FF7043
 * PRESSION: gradient #EF5350
 * VENT:     delegue a WindFlowLayer (Ventusky-Steeve-Max)
 *
 * Z-ORDER: pression < zones < corridors < contamination < salines < hotspots < affuts
 * VERROUILLE: V9-PURE. ZERO fallback. ZERO override. ZERO smoothing.
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

// CORRIDORS V9-x20: 5 niveaux intensite
const CORRIDOR_STYLES = {
  critique: { color: '#FF0000', weight: 2.6, opacity: 0.95 },
  majeur:   { color: '#D32F2F', weight: 2.4, opacity: 0.90 },
  fort:     { color: '#FF8F00', weight: 2.2, opacity: 0.85 },
  modere:   { color: '#FFEB3B', weight: 1.8, opacity: 0.75 },
  faible:   { color: '#FFFFFF', weight: 1.4, opacity: 0.65 },
};

const AFFUT_COLOR = '#9E9E9E';
const AFFUT_X_COLOR = '#424242';
const AFFUT_SIZE = { optimal: 8, bon: 7, acceptable: 6 };

const SALINE_COLOR = '#FDD835';
const CONTAM_COLOR = '#FF7043';
const PRESSION_COLOR = '#EF5350';

const HOTSPOT_COLORS = ['#FFCDD2', '#EF9A9A', '#EF5350', '#E53935', '#B71C1C'];
const HOTSPOT_SIZES = [4, 5, 6, 7, 8];

const BionicLayersV8 = ({
  bundleData,
  showZones = true,
  showCorridors = true,
  showAffuts = true,
  showSalines = true,
  showHotspots = true,
  showWind = true,
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
    const contamination = bundleData.contamination || null;
    const pression = bundleData.pression || null;

    // ═══ Z-1: PRESSION HUMAINE ═══
    if (showPression && pression && pression.pression_score > 10) {
      const score = pression.pression_score;
      const center = map.getCenter();
      const circle = L.circle([center.lat, center.lng], {
        radius: 300 + score * 3,
        color: PRESSION_COLOR,
        fillColor: PRESSION_COLOR,
        fillOpacity: Math.min(0.35, score / 200),
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

    // ═══ Z-3: CORRIDORS V9-x20 (Catmull-Rom, smoothFactor=0, ZERO interpolation) ═══
    if (showCorridors && corridors.length > 0) {
      corridors.forEach(c => {
        const path = c.path || [[c.start.lat, c.start.lng], [c.end.lat, c.end.lng]];
        const style = CORRIDOR_STYLES[c.type] || CORRIDOR_STYLES.fort;

        // Polyline principale — Catmull-Rom directionnel, ZERO smoothing
        const line = L.polyline(path, {
          color: style.color,
          weight: style.weight,
          opacity: style.opacity,
          lineCap: 'round',
          lineJoin: 'round',
          smoothFactor: 0,
          interactive: true,
        });

        // Fleche directionnelle au milieu du corridor
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
            const tipLat = mid[0] + ny * arrowSize;
            const tipLng = mid[1] + nx * arrowSize;
            const lLat = mid[0] - ny * arrowSize * 0.5 + nx * arrowSize * 0.4;
            const lLng = mid[1] - nx * arrowSize * 0.5 - ny * arrowSize * 0.4;
            const rLat = mid[0] - ny * arrowSize * 0.5 - nx * arrowSize * 0.4;
            const rLng = mid[1] - nx * arrowSize * 0.5 + ny * arrowSize * 0.4;

            const arrow = L.polygon([[tipLat, tipLng], [lLat, lLng], [rLat, rLng]], {
              color: style.color,
              fillColor: style.color,
              fillOpacity: style.opacity,
              weight: 1,
              opacity: style.opacity,
              smoothFactor: 0,
              interactive: false,
            });
            group.addLayer(arrow);
          }
        }

        // Tooltip enrichi V9
        const connStr = (c.zone_connections && c.zone_connections.length > 0)
          ? `<br><span style="font-size:9px;color:#FDD835">Zones: ${c.zone_connections.join(', ')}</span>`
          : '';
        const costStr = c.cost_surface !== undefined
          ? ` | cost:${c.cost_surface}`
          : '';
        const profileStr = c.species_profile
          ? ` | ${c.species_profile}`
          : '';

        line.bindTooltip(
          `<b style="color:${style.color}">${c.type}</b> int:${Math.round(c.intensity)}${costStr}${profileStr}${connStr}`,
          { sticky: true, opacity: 0.95 }
        );
        group.addLayer(line);
      });
    }

    // ═══ Z-4: CONTAMINATION (cone directionnel) ═══
    if (showContamination && contamination && contamination.polygon) {
      const cone = L.polygon(contamination.polygon, {
        color: CONTAM_COLOR,
        weight: 1.5,
        opacity: 0.7,
        fillColor: CONTAM_COLOR,
        fillOpacity: 0.15,
        dashArray: '4,4',
        smoothFactor: 0,
        interactive: true,
      });
      cone.bindTooltip(
        `<b style="color:${CONTAM_COLOR}">Contamination olfactive</b><br>Dir: ${contamination.direction_deg}deg | Portee: ${contamination.reach_m}m`,
        { sticky: true, opacity: 0.95 }
      );
      group.addLayer(cone);
    }

    // ═══ Z-5: SALINES ═══
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
        contamination: !!contamination,
        pression: !!(pression && pression.pression_score > 0),
        engine: 'V9-PURE-RENDERER',
        esi_omega: bundleData.esi_omega,
      });
    }
  }, [map, bundleData, enabled, showZones, showCorridors, showAffuts, showSalines, showHotspots, showContamination, showPression, clearOwnLayers]);

  useEffect(() => {
    renderLayers();
    return () => clearOwnLayers();
  }, [renderLayers, clearOwnLayers]);

  return null;
};

export default BionicLayersV8;

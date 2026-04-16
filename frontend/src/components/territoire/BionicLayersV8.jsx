/**
 * BionicLayersV8.jsx — Rendu V8 ORGANIQUE conforme STEEVE-MAX
 * =============================================================
 * V8-VISUAL-STEVE-MAX-Omega:
 * - Zones: polygones organiques, contours opaques 2.5px, interieur TRANSPARENT
 * - Corridors: courbes Bezier, largeur variable intensite, opacite 0.85
 * - Affuts: icones vectorielles, orientation vent, halo discret
 * - ZERO micro-points, ZERO artefacts, ZERO rectangles
 */
import { useEffect, useRef, useCallback } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

// V8-ULTIME-ALIGNEMENT-V6: Couleurs institutionnelles V6
const ZONE_COLORS = {
  alimentation: { stroke: '#2E7D32', label: 'Alimentation', weight: 2.0 },
  repos:        { stroke: '#1565C0', label: 'Repos', weight: 1.8 },
  rut:          { stroke: '#C62828', label: 'Rut', weight: 2.5 },
  affuts:       { stroke: '#F44336', label: 'Affuts', weight: 2.0 },
  eau:          { stroke: '#29B6F6', label: 'Eau', weight: 1.5 },
};

// V8-ULTIME-ALIGNEMENT-V6: Corridors style "veines animales" (opacite 100%, poids V6)
const CORRIDOR_STYLES = {
  critique: { color: '#FF0000', weight: 3.0, opacity: 1.0, label: 'Critique' },
  majeur:   { color: '#CC0000', weight: 2.5, opacity: 1.0, label: 'Majeur' },
  fort:     { color: '#FF8C00', weight: 2.0, opacity: 1.0, label: 'Fort' },
  modere:   { color: '#FFD700', weight: 1.5, opacity: 1.0, label: 'Modere' },
  faible:   { color: '#9E9E9E', weight: 1.2, opacity: 1.0, label: 'Faible' },
};

// V8-ULTIME-ALIGNEMENT-V6: Affuts jaune institutionnel #FDD835, ZERO halo
const AFFUT_QUALITY = {
  optimal:    { color: '#FDD835', radius: 8 },
  bon:        { color: '#FDD835', radius: 7 },
  acceptable: { color: '#FDD835', radius: 6 },
};

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

    // ═══ ZONES ORGANIQUES (contour opaque, interieur TRANSPARENT) ═══
    if (showZones && zones.length > 0) {
      zones.forEach(z => {
        const colors = ZONE_COLORS[z.type] || ZONE_COLORS.alimentation;
        if (z.polygon && z.polygon.length >= 4) {
          const poly = L.polygon(z.polygon, {
            color: colors.stroke,
            weight: colors.weight || 2.0,
            opacity: 1.0,
            fillColor: colors.stroke,
            fillOpacity: z.excluded ? 0.15 : 0,
            lineCap: 'round',
            lineJoin: 'round',
            interactive: true,
            dashArray: z.excluded ? '6,4' : null,
          });
          const t = z.terrain || {};
          const terrainInfo = t.canopy !== undefined
            ? `<br><span style="font-size:9px;color:#888">Canopy: ${Math.round(t.canopy*100)}% | Pente: ${t.pente_deg}° | Eau: ${t.distance_eau_m}m</span>`
            + `<br><span style="font-size:9px;color:#888">Strate: ${Math.round(t.strate_1_3m*100)}% | Feuillus: ${Math.round(t.feuillus_ratio*100)}% | Route: ${t.distance_route_m}m</span>`
            : '';
          const exclInfo = z.excluded
            ? `<br><span style="font-size:9px;color:#EF4444;font-weight:700">EXCLU: ${z.exclusion_reason || 'terrain'}</span>`
            : '';
          poly.bindTooltip(
            `<b style="color:${colors.stroke}">${colors.label}</b><br><span style="font-size:10px">Score: ${z.score}/100</span>${terrainInfo}${exclInfo}`,
            { sticky: true, opacity: 0.92 }
          );
          poly.on('mouseover', function () { this.setStyle({ weight: (colors.weight || 2.0) + 1.5, fillOpacity: 0.08 }); });
          poly.on('mouseout', function () { this.setStyle({ weight: colors.weight || 2.0, fillOpacity: z.excluded ? 0.15 : 0 }); });
          group.addLayer(poly);
        }
      });
    }

    // ═══ CORRIDORS COURBES (intensite variable) ═══
    if (showCorridors && corridors.length > 0) {
      const order = { faible: 0, modere: 1, fort: 2, majeur: 3, critique: 4 };
      const sorted = [...corridors].sort((a, b) => (order[a.type] || 0) - (order[b.type] || 0));

      sorted.forEach(c => {
        const style = CORRIDOR_STYLES[c.type] || CORRIDOR_STYLES.faible;
        const path = c.path || [[c.start.lat, c.start.lng], [c.end.lat, c.end.lng]];

        // V8-ALIGNEMENT-V6: ZERO glow, ZERO halo — style "veines animales" pur

        const line = L.polyline(path, {
          color: style.color,
          weight: style.weight,
          opacity: style.opacity,
          lineCap: 'round',
          lineJoin: 'round',
          interactive: true,
        });
        const costInfo = c.cost_surface !== undefined
          ? `<br><span style="font-size:9px;color:#888">Cost surface: ${c.cost_surface}</span>`
          : '';
        const tStart = c.terrain_start || {};
        const terrainCorr = tStart.pente_deg !== undefined
          ? `<br><span style="font-size:9px;color:#888">Pente: ${tStart.pente_deg}° | Canopy: ${Math.round(tStart.canopy*100)}%</span>`
          : '';
        line.bindTooltip(
          `<b style="color:${style.color}">${style.label}</b><br><span style="font-size:10px">Intensite: ${c.intensity}</span>${costInfo}${terrainCorr}`,
          { sticky: true }
        );
        line.on('mouseover', function () { this.setStyle({ weight: style.weight + 2 }); });
        line.on('mouseout', function () { this.setStyle({ weight: style.weight }); });
        group.addLayer(line);
      });
    }

    // ═══ AFFUTS V6 INSTITUTIONNEL (jaune #FDD835, ZERO halo) ═══
    if (showAffuts && affuts.length > 0) {
      affuts.forEach(a => {
        const q = AFFUT_QUALITY[a.quality] || AFFUT_QUALITY.acceptable;

        // V8-ALIGNEMENT-V6: ZERO halo — affut direct

        // Affut marker (triangle oriented by wind)
        const orientRad = (a.orientation_deg || 0) * Math.PI / 180;
        const sz = 0.00015;
        const cos_lat = Math.max(0.5, Math.cos(a.lat * Math.PI / 180));
        const tip = [a.lat + Math.cos(orientRad) * sz * 2, a.lng + Math.sin(orientRad) * sz * 2 / cos_lat];
        const left = [a.lat + Math.cos(orientRad + 2.3) * sz, a.lng + Math.sin(orientRad + 2.3) * sz / cos_lat];
        const right = [a.lat + Math.cos(orientRad - 2.3) * sz, a.lng + Math.sin(orientRad - 2.3) * sz / cos_lat];
        const triangle = L.polygon([tip, left, right], {
          color: q.color,
          fillColor: q.color,
          fillOpacity: 0.85,
          weight: 1.5,
          opacity: 1.0,
          interactive: true,
        });
        const affutScore = a.score !== undefined ? a.score : a.zone_score;
        const corrBonus = a.corridor_proximity_bonus !== undefined
          ? `<br><span style="font-size:9px;color:#888">Corridor bonus: +${a.corridor_proximity_bonus}</span>`
          : '';
        triangle.bindTooltip(
          `<b style="color:${q.color}">Affut ${a.quality}</b><br>` +
          `<span style="font-size:10px">Score: ${affutScore} | Zone: ${a.zone_type}</span>` +
          `<br><span style="font-size:10px">Orient: ${a.orientation_deg}&deg;</span>${corrBonus}`,
          { sticky: true }
        );
        group.addLayer(triangle);
      });
    }

    group.addTo(map);
    groupRef.current = group;

    if (onDataLoadedRef.current) {
      onDataLoadedRef.current({
        zones_count: zones.length,
        corridors_count: corridors.length,
        affuts_count: affuts.length,
        engine: 'V8-MAP-BUNDLE',
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

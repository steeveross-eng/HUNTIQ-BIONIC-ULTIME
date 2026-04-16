/**
 * BionicLayersV8.jsx — Rendu PRINCIPAL V8 unifie
 * ================================================
 * TERRITOIRE-V8-FIX-Omega: Source PRINCIPALE zones/corridors/heatmap.
 * - Polygones dimensionnes ~300m (identique V6)
 * - clearLayers ISOLE (ne touche jamais les layers V6)
 * - Retry + loading state si bundle null
 * - GOVERNANCE-INDEPENDENT
 */
import { useEffect, useRef, useCallback, useState } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

const ZONE_COLORS = {
  alimentation: { fill: '#4CAF50', stroke: '#2E7D32', label: 'Alimentation' },
  repos:        { fill: '#2196F3', stroke: '#1565C0', label: 'Repos' },
  rut:          { fill: '#FF9800', stroke: '#E65100', label: 'Rut' },
  affuts:       { fill: '#F44336', stroke: '#B71C1C', label: 'Affuts' },
  eau:          { fill: '#00BCD4', stroke: '#00838F', label: 'Eau' },
};

const CORRIDOR_STYLES = {
  extreme:     { color: '#FF4500', weight: 4.5, opacity: 0.75, dashArray: null, glow: true },
  intense:     { color: '#FF8C00', weight: 3.5, opacity: 0.60, dashArray: null, glow: false },
  saisonnier:  { color: '#FFA500', weight: 2.5, opacity: 0.55, dashArray: '8,5', glow: false },
  normal:      { color: '#FFD27F', weight: 2,   opacity: 0.55, dashArray: '5,7', glow: false },
};

const HEATMAP_COLORS = [
  { min: 0.7, color: '#FF4500', radius: 5, opacity: 0.50 },
  { min: 0.4, color: '#FF8C00', radius: 4, opacity: 0.40 },
  { min: 0.2, color: '#FFD700', radius: 3, opacity: 0.30 },
  { min: 0.0, color: '#9E9E9E', radius: 2, opacity: 0.20 },
];

const BionicLayersV8 = ({
  bundleData,
  center,
  showZones = true,
  showCorridors = true,
  showHeatmap = true,
  showPoints = true,
  enabled = true,
  onDataLoaded = null,
}) => {
  const map = useMap();
  const groupRef = useRef(null);
  const [rendered, setRendered] = useState(false);
  const onDataLoadedRef = useRef(onDataLoaded);
  onDataLoadedRef.current = onDataLoaded;

  const clearOwnLayers = useCallback(() => {
    if (groupRef.current && map) {
      try { map.removeLayer(groupRef.current); } catch (e) { /* map destroyed */ }
      groupRef.current = null;
    }
  }, [map]);

  const renderLayers = useCallback(() => {
    if (!map || !enabled || !bundleData) {
      setRendered(false);
      return;
    }

    clearOwnLayers();

    const group = L.featureGroup();
    const zones = bundleData.zones || [];
    const corridors = bundleData.corridors || [];
    const heatmap = bundleData.heatmap || [];
    let layerCount = 0;

    // ═══ HEATMAP (Z-index bas — rendu en premier, sous les zones) ═══
    if (showHeatmap && heatmap.length > 0) {
      heatmap.forEach(pt => {
        const prob = pt.probability || 0;
        const style = HEATMAP_COLORS.find(h => prob >= h.min) || HEATMAP_COLORS[3];
        L.circleMarker([pt.lat, pt.lng], {
          radius: style.radius,
          color: 'transparent',
          fillColor: style.color,
          fillOpacity: style.opacity,
          weight: 0,
          interactive: false,
          pane: 'overlayPane',
        }).addTo(group);
        layerCount++;
      });
    }

    // ═══ ZONES POLYGONES (Z-index moyen — au-dessus du heatmap) ═══
    if (showZones && zones.length > 0) {
      zones.forEach(z => {
        const colors = ZONE_COLORS[z.type] || ZONE_COLORS.alimentation;
        if (z.polygon && z.polygon.length >= 3) {
          const polygon = L.polygon(z.polygon, {
            color: colors.stroke,
            fillColor: colors.fill,
            fillOpacity: 0.25,
            weight: 3,
            opacity: 1.0,
            lineCap: 'round',
            lineJoin: 'round',
            interactive: true,
          });
          polygon.bindTooltip(
            `<div style="font-size:12px;font-weight:700;color:${colors.stroke}">${colors.label}</div>` +
            `<div style="font-size:10px;color:#666">Score: ${z.score}/100</div>`,
            { sticky: true, opacity: 0.95 }
          );
          polygon.on('mouseover', function() { this.setStyle({ weight: 5, fillOpacity: 0.35 }); });
          polygon.on('mouseout', function() { this.setStyle({ weight: 3, fillOpacity: 0.25 }); });
          group.addLayer(polygon);
          layerCount++;
        }
        // Centre point marker
        if (showPoints && z.center) {
          L.circleMarker([z.center.lat, z.center.lng], {
            radius: 6,
            color: colors.stroke,
            fillColor: colors.fill,
            fillOpacity: 0.9,
            weight: 2,
          }).bindTooltip(colors.label, { direction: 'top' }).addTo(group);
          layerCount++;
        }
      });
    }

    // ═══ CORRIDORS (Z-index haut — au-dessus des zones) ═══
    if (showCorridors && corridors.length > 0) {
      // Sort: normal < saisonnier < intense < extreme
      const order = { normal: 0, saisonnier: 1, intense: 2, extreme: 3 };
      const sorted = [...corridors].sort((a, b) => (order[a.type] || 0) - (order[b.type] || 0));

      sorted.forEach(c => {
        const style = CORRIDOR_STYLES[c.type] || CORRIDOR_STYLES.normal;
        if (c.start && c.end) {
          const coords = [[c.start.lat, c.start.lng], [c.end.lat, c.end.lng]];

          // Glow for extreme corridors
          if (style.glow) {
            L.polyline(coords, {
              color: style.color, weight: style.weight + 6, opacity: 0.15,
              lineCap: 'round', lineJoin: 'round', interactive: false,
            }).addTo(group);
            L.polyline(coords, {
              color: style.color, weight: style.weight + 3, opacity: 0.30,
              lineCap: 'round', lineJoin: 'round', interactive: false,
            }).addTo(group);
          }

          const line = L.polyline(coords, {
            color: style.color,
            weight: style.weight,
            opacity: style.opacity,
            dashArray: style.dashArray,
            lineCap: 'round',
            lineJoin: 'round',
            interactive: true,
          });
          line.bindTooltip(
            `<div style="font-size:11px;font-weight:600;color:${style.color}">${c.type.toUpperCase()}</div>` +
            `<div style="font-size:10px;color:#666">Intensite: ${c.intensity}</div>`,
            { sticky: true }
          );
          line.on('mouseover', function() { this.setStyle({ weight: style.weight + 2, opacity: Math.min(1, style.opacity + 0.2) }); });
          line.on('mouseout', function() { this.setStyle({ weight: style.weight, opacity: style.opacity }); });
          group.addLayer(line);
          layerCount++;
        }
      });
    }

    if (layerCount > 0) {
      group.addTo(map);
      groupRef.current = group;
      setRendered(true);
    }

    // Callback
    if (onDataLoadedRef.current) {
      const scoreAvg = heatmap.length > 0
        ? Math.round(heatmap.reduce((s, p) => s + (p.probability || 0) * 100, 0) / heatmap.length)
        : 0;
      onDataLoadedRef.current({
        zones_count: zones.length,
        corridors_count: corridors.length,
        heatmap_count: heatmap.length,
        total_layers: layerCount,
        score_avg: scoreAvg,
        engine: 'V8-MAP-BUNDLE',
      });
    }
  }, [map, bundleData, enabled, showZones, showCorridors, showHeatmap, showPoints, clearOwnLayers]);

  useEffect(() => {
    renderLayers();
    return () => clearOwnLayers();
  }, [renderLayers, clearOwnLayers]);

  // Pas de rendu HTML dans un contexte Leaflet
  return null;
};

export default BionicLayersV8;

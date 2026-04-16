/**
 * BionicLayersV8.jsx — Rendu unifie V8 (zones+corridors+heatmap)
 * ================================================================
 * UI-V8-FORCE-Omega: Consomme EXCLUSIVEMENT le bundle V8.
 * ZERO source V7. GOVERNANCE-INDEPENDENT.
 * Rend zones, corridors, heatmap depuis bundleData.
 */
import { useEffect, useRef, useCallback } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

const ZONE_COLORS = {
  alimentation: { fill: '#4CAF50', stroke: '#2E7D32' },
  repos: { fill: '#2196F3', stroke: '#1565C0' },
  rut: { fill: '#FF9800', stroke: '#E65100' },
  affuts: { fill: '#F44336', stroke: '#B71C1C' },
  eau: { fill: '#00BCD4', stroke: '#00838F' },
};

const CORRIDOR_COLORS = {
  extreme: { color: '#FF4500', weight: 4, dashArray: null },
  intense: { color: '#FF8C00', weight: 3, dashArray: null },
  saisonnier: { color: '#FFA500', weight: 2, dashArray: '6,4' },
  normal: { color: '#FFD27F', weight: 1.5, dashArray: '4,6' },
};

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
  const onDataLoadedRef = useRef(onDataLoaded);
  onDataLoadedRef.current = onDataLoaded;

  const renderLayers = useCallback(() => {
    if (!map || !enabled) return;

    // Clear previous
    if (groupRef.current) {
      map.removeLayer(groupRef.current);
      groupRef.current = null;
    }

    if (!bundleData) return;

    const group = L.featureGroup();
    const zones = bundleData.zones || [];
    const corridors = bundleData.corridors || [];
    const heatmap = bundleData.heatmap || [];

    // ═══ ZONES ═══
    if (showZones && zones.length > 0) {
      zones.forEach(z => {
        const colors = ZONE_COLORS[z.type] || ZONE_COLORS.alimentation;
        if (z.polygon && z.polygon.length >= 3) {
          L.polygon(z.polygon, {
            color: colors.stroke,
            fillColor: colors.fill,
            fillOpacity: 0.12,
            weight: 2.5,
            interactive: true,
          }).bindTooltip(`${z.type} (${z.score})`, { direction: 'top', className: 'bionic-tooltip-v8' })
            .addTo(group);
        }
        // Center point
        if (showPoints && z.center) {
          L.circleMarker([z.center.lat, z.center.lng], {
            radius: 5,
            color: colors.stroke,
            fillColor: colors.fill,
            fillOpacity: 0.8,
            weight: 1.5,
          }).addTo(group);
        }
      });
    }

    // ═══ CORRIDORS ═══
    if (showCorridors && corridors.length > 0) {
      corridors.forEach(c => {
        const style = CORRIDOR_COLORS[c.type] || CORRIDOR_COLORS.normal;
        if (c.start && c.end) {
          const line = L.polyline(
            [[c.start.lat, c.start.lng], [c.end.lat, c.end.lng]],
            {
              color: style.color,
              weight: style.weight,
              opacity: 0.7,
              dashArray: style.dashArray,
              interactive: false,
            }
          );
          line.addTo(group);
        }
      });
    }

    // ═══ HEATMAP ═══
    if (showHeatmap && heatmap.length > 0) {
      heatmap.forEach(pt => {
        const prob = pt.probability || 0;
        const color = prob >= 0.7 ? '#FF4500' : prob >= 0.4 ? '#FF8C00' : prob >= 0.2 ? '#FFD700' : '#9E9E9E';
        const radius = Math.max(2, prob * 6);
        L.circleMarker([pt.lat, pt.lng], {
          radius,
          color: 'transparent',
          fillColor: color,
          fillOpacity: Math.max(0.15, prob * 0.6),
          weight: 0,
          interactive: false,
        }).addTo(group);
      });
    }

    group.addTo(map);
    groupRef.current = group;

    // Callback data loaded
    if (onDataLoadedRef.current) {
      const scoreAvg = heatmap.length > 0
        ? Math.round(heatmap.reduce((s, p) => s + (p.probability || 0) * 100, 0) / heatmap.length)
        : 0;
      onDataLoadedRef.current({
        zones_count: zones.length,
        corridors_count: corridors.length,
        heatmap_count: heatmap.length,
        score_avg: scoreAvg,
        governance_mode: bundleData.governance_mode,
        engine: 'V8-MAP-BUNDLE',
        dataVersion: 'V8',
      });
    }
  }, [map, bundleData, enabled, showZones, showCorridors, showHeatmap, showPoints]);

  useEffect(() => {
    renderLayers();
    return () => {
      if (groupRef.current && map) {
        try { map.removeLayer(groupRef.current); } catch (e) { /* map destroyed */ }
        groupRef.current = null;
      }
    };
  }, [renderLayers]);

  return null;
};

export default BionicLayersV8;

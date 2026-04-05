/**
 * W5 — Predictive Heatmap Layer (Leaflet)
 * Directive x7000-M3-DASHBOARD | BCE-4X GOLDEN V6+
 * COEXISTE avec HeatmapLayer.jsx V5 (ZERO modification)
 */
import { useEffect } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet.heat';

export const PredictiveHeatmapLayer = ({ data, visible = true }) => {
  const map = useMap();

  useEffect(() => {
    if (!visible || !data?.points?.length) return;

    const heatData = data.points.map(p => [p.lat, p.lng, p.probability || 0.3]);

    const layer = L.heatLayer(heatData, {
      radius: 40,
      blur: 25,
      maxZoom: 17,
      max: 1.0,
      gradient: {
        0.0: '#3b82f6',
        0.3: '#22c55e',
        0.5: '#eab308',
        0.7: '#f97316',
        1.0: '#ef4444',
      },
    });

    layer.addTo(map);
    return () => { map.removeLayer(layer); };
  }, [data, visible, map]);

  return null;
};

export default PredictiveHeatmapLayer;

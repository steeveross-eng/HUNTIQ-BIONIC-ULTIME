/**
 * RoutePlannerLayer — Tactical Route Visualization on Leaflet Map
 * BIONIC V6 GOLDEN — RoutePlannerLayer_v1
 *
 * Displays optimal tactical route between hotspots using polylines.
 * Color-coded by habitat score along path segments.
 * Shows waypoint markers with distance/time info.
 *
 * 0 impact on existing layers.
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

function scoreToLineColor(score) {
  if (score < 40) return '#ef4444';
  if (score < 55) return '#f97316';
  if (score < 65) return '#eab308';
  if (score < 75) return '#84cc16';
  return '#22c55e';
}

export default function RoutePlannerLayer({ species = 'moose', anchorWaypoints = [] }) {
  const map = useMap();
  const layerGroupRef = useRef(null);
  const [routeData, setRouteData] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchRoute = useCallback(async () => {
    const b = map.getBounds();
    setLoading(true);
    try {
      const body = {
        bounds: { north: b.getNorth(), south: b.getSouth(), east: b.getEast(), west: b.getWest() },
        species,
        resolution: 30,
        hotspot_threshold: 70,
      };
      if (anchorWaypoints.length > 0) {
        body.anchor_waypoints = anchorWaypoints.map(wp => ({
          lat: wp.lat || wp.latitude,
          lng: wp.lng || wp.longitude,
          name: wp.name || 'Waypoint',
        }));
      }
      const res = await fetch(`${API}/v1/bionic/route-planner/compute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!res.ok) return;
      const data = await res.json();
      setRouteData(data);
    } catch (err) {
      console.warn('RoutePlanner: fetch error', err);
    } finally {
      setLoading(false);
    }
  }, [map, species, anchorWaypoints]);

  useEffect(() => {
    fetchRoute();
    map.on('moveend', fetchRoute);
    return () => { map.off('moveend', fetchRoute); };
  }, [map, fetchRoute]);

  useEffect(() => {
    if (layerGroupRef.current) {
      layerGroupRef.current.clearLayers();
      map.removeLayer(layerGroupRef.current);
    }

    if (!routeData || !routeData.route) return;

    const group = L.layerGroup();
    layerGroupRef.current = group;
    const route = routeData.route;

    // Draw path segments colored by score
    route.segments.forEach((seg) => {
      if (!seg.path || seg.path.length < 2) return;
      const latlngs = seg.path.map(p => [p.lat, p.lng]);
      const color = scoreToLineColor(seg.avg_score_along_path);
      const line = L.polyline(latlngs, {
        color,
        weight: 4,
        opacity: 0.8,
        dashArray: null,
        lineCap: 'round',
        lineJoin: 'round',
      });
      line.bindPopup(`
        <div style="font-size:12px; line-height:1.5;">
          <b style="color:${color}">Score moyen: ${seg.avg_score_along_path}%</b><br/>
          Distance: ${seg.path_distance_km.toFixed(2)} km<br/>
          Temps: ${seg.estimated_time_min.toFixed(0)} min
        </div>
      `);
      group.addLayer(line);
    });

    // Draw waypoint markers
    route.points.forEach((pt, idx) => {
      const isFirst = idx === 0;
      const isLast = idx === route.points.length - 1;
      const isAnchor = pt.is_anchor;

      const size = isAnchor ? 14 : 10;
      const borderColor = isAnchor ? '#60a5fa' : (pt.score >= 80 ? '#22c55e' : pt.score >= 70 ? '#84cc16' : '#eab308');
      const bgColor = isFirst ? '#3b82f6' : isLast ? '#ef4444' : (isAnchor ? '#1e40af' : scoreToLineColor(pt.score));

      const icon = L.divIcon({
        className: 'route-point-icon',
        html: `<div style="
          width:${size}px; height:${size}px; border-radius:50%;
          background:${bgColor}; border:2px solid ${borderColor};
          box-shadow: 0 0 6px ${bgColor}80;
          display:flex; align-items:center; justify-content:center;
          font-size:7px; color:white; font-weight:700;
        ">${isFirst ? 'D' : isLast ? 'F' : ''}</div>`,
        iconSize: [size + 4, size + 4],
        iconAnchor: [(size + 4) / 2, (size + 4) / 2],
      });

      const marker = L.marker([pt.lat, pt.lng], { icon });
      marker.bindPopup(`
        <div style="font-size:12px; line-height:1.5; min-width:120px;">
          <b>${pt.name}</b><br/>
          Score: <span style="color:${scoreToLineColor(pt.score)}; font-weight:700;">${pt.score}%</span><br/>
          ${pt.lat.toFixed(5)}, ${pt.lng.toFixed(5)}
          ${isAnchor ? '<br/><i style="color:#60a5fa;">Point d\'ancrage</i>' : ''}
        </div>
      `);
      group.addLayer(marker);
    });

    group.addTo(map);

    return () => {
      if (layerGroupRef.current) {
        layerGroupRef.current.clearLayers();
        map.removeLayer(layerGroupRef.current);
      }
    };
  }, [routeData, map]);

  return (
    <>
      {loading && (
        <div style={{
          position: 'absolute', top: '70px', left: '50%', transform: 'translateX(-50%)',
          zIndex: 1100, background: 'rgba(10,15,25,0.85)', color: '#93c5fd',
          padding: '6px 16px', borderRadius: '8px', fontSize: '12px',
          border: '1px solid rgba(59,130,246,0.3)', backdropFilter: 'blur(8px)',
        }}>
          Calcul du parcours tactique...
        </div>
      )}
      {/* BCE-4X ORDONNANCE STEEVE-MAX: LEGENDE PARCOURS SUPPRIMEE — BionicLegend SEULE AUTORISEE */}
    </>
  );
}

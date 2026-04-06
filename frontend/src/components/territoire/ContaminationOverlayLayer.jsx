/**
 * ContaminationOverlayLayer.jsx — BCE-4X BLOC 2: BDRE PEDAGOGIQUE
 * ================================================================
 * ORDONNANCE STEEVE-MAX 2026-04-06 | Branche BIONIC_REWRITE_P0
 *
 * Affichage PERMANENT des zones de contamination olfactive BDRE
 * pour 100% des salines actives, INDEPENDAMMENT des affuts.
 *
 * Consomme: POST /api/v1/hunt/contamination-zones
 */
import { useEffect, useRef, useCallback, useState } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const HUNTER_ZONE_COLOR = '#FF4444';
const SALINE_ZONE_COLOR = '#FF8800';

export default function ContaminationOverlayLayer({
  center,
  feedingSites = [],
  windDirectionDeg = 315,
  windSpeed = 12,
  session = 'matin',
  enabled = true,
}) {
  const map = useMap();
  const layerGroupRef = useRef(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const lastKeyRef = useRef('');

  const fetchZones = useCallback(async () => {
    if (!center || !enabled) return;

    const key = `${center.lat.toFixed(5)}_${center.lng.toFixed(5)}_${windDirectionDeg}_${windSpeed}_${feedingSites.length}`;
    if (key === lastKeyRef.current && data) return;
    lastKeyRef.current = key;

    setLoading(true);
    try {
      const body = {
        center_lat: center.lat,
        center_lng: center.lng,
        wind_direction_deg: windDirectionDeg,
        wind_speed_kmh: windSpeed,
        session,
        feeding_sites: feedingSites.map((fs, i) => ({
          lat: fs.lat,
          lng: fs.lng,
          name: fs.name || `Saline-${i + 1}`,
        })),
      };

      const res = await fetch(`${API}/v1/hunt/contamination-zones`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        console.warn('[CONTAMINATION] API error:', res.status);
        return;
      }

      setData(await res.json());
    } catch (err) {
      console.warn('[CONTAMINATION] fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, [center, feedingSites, windDirectionDeg, windSpeed, session, enabled, data]);

  useEffect(() => {
    if (center && enabled && feedingSites.length > 0) {
      fetchZones();
    }
  }, [center, enabled, feedingSites.length, windDirectionDeg, windSpeed, fetchZones]);

  // Render contamination zones on the map
  useEffect(() => {
    if (layerGroupRef.current) {
      layerGroupRef.current.clearLayers();
      map.removeLayer(layerGroupRef.current);
    }

    if (!data || !enabled) return;

    const group = L.layerGroup();
    layerGroupRef.current = group;

    const zones = data.zones || [];

    for (const zone of zones) {
      const polygon = zone.polygon;
      if (!polygon || polygon.length < 3) continue;

      const coords = polygon.map(p => [p.lat, p.lng]);
      const isHunter = zone.source === 'hunter_center';
      const color = isHunter ? HUNTER_ZONE_COLOR : SALINE_ZONE_COLOR;
      const opacity = isHunter ? 0.12 : 0.08;

      const poly = L.polygon(coords, {
        color: color,
        fillColor: color,
        fillOpacity: opacity,
        weight: 1,
        opacity: 0.3,
        dashArray: '6, 4',
        interactive: true,
      });

      const riskBadge = zone.risk_level === 'HIGH'
        ? '<span style="color:#ff4444;font-weight:700">RISQUE ELEVE</span>'
        : zone.risk_level === 'MODERATE'
        ? '<span style="color:#ff8800;font-weight:700">RISQUE MODERE</span>'
        : '<span style="color:#66bb6a;font-weight:700">RISQUE FAIBLE</span>';

      poly.bindPopup(`
        <div style="font-size:11px;line-height:1.5;min-width:180px;background:#0f1525;color:#e0e8f0;padding:10px;border-radius:8px;">
          <div style="font-weight:700;font-size:12px;margin-bottom:4px;color:${color}">
            ${zone.label || 'Zone de contamination'}
          </div>
          <div style="margin-bottom:4px">${riskBadge}</div>
          <div style="font-size:10px;color:#9ca3af">
            Vent ${zone.bearing_deg || 0}° | Portee ${zone.range_m || 0}m
          </div>
        </div>
      `, { className: 'bionic-popup' });

      group.addLayer(poly);
    }

    // Pedagogy label
    const pedagogy = data.pedagogy;
    if (pedagogy && center) {
      const pedagogyIcon = L.divIcon({
        className: 'contamination-pedagogy',
        html: `<div data-testid="contamination-pedagogy" style="
          background:rgba(15,21,37,0.92);backdrop-filter:blur(8px);
          border:1px solid rgba(255,136,0,0.3);border-radius:8px;
          padding:6px 10px;color:#e0e8f0;font-size:10px;line-height:1.4;
          max-width:220px;white-space:normal;pointer-events:auto;
        ">
          <div style="font-weight:700;font-size:10px;color:#FF8800;margin-bottom:2px">BDRE PEDAGOGIQUE</div>
          <div style="font-size:9px;color:#9ca3af">${pedagogy.conseil || ''}</div>
        </div>`,
        iconSize: [220, 60],
        iconAnchor: [110, -10],
      });

      const marker = L.marker([center.lat, center.lng], {
        icon: pedagogyIcon,
        interactive: false,
        zIndexOffset: -100,
      });
      group.addLayer(marker);
    }

    group.addTo(map);

    return () => {
      if (layerGroupRef.current) {
        layerGroupRef.current.clearLayers();
        map.removeLayer(layerGroupRef.current);
      }
    };
  }, [data, map, enabled, center]);

  return null;
}

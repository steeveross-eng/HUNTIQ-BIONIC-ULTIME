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
  const [pedagogyVisible, setPedagogyVisible] = useState(true);
  const lastKeyRef = useRef('');
  const pedagogyMarkerRef = useRef(null);

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
        <div style="font-size:18px;line-height:1.6;min-width:260px;background:#0f1525;color:#e0e8f0;padding:16px;border-radius:10px;">
          <div style="font-weight:700;font-size:20px;margin-bottom:6px;color:${color}">
            ${zone.label || 'Zone de contamination'}
          </div>
          <div style="margin-bottom:6px;font-size:18px">${riskBadge}</div>
          <div style="font-size:16px;color:#9ca3af">
            Vent ${zone.bearing_deg || 0}° | Portee ${zone.range_m || 0}m
          </div>
        </div>
      `, { className: 'bionic-popup' });

      group.addLayer(poly);
    }

    // Pedagogy label — TYPOGRAPHIE x2 + BOUTON FERMER (ORDONNANCE STEEVE-MAX)
    const pedagogy = data.pedagogy;
    if (pedagogy && center && pedagogyVisible) {
      const closeFnName = '__bdre_pedagogy_close';
      window[closeFnName] = () => {
        if (pedagogyMarkerRef.current && layerGroupRef.current) {
          layerGroupRef.current.removeLayer(pedagogyMarkerRef.current);
          pedagogyMarkerRef.current = null;
        }
        setPedagogyVisible(false);
      };

      const pedagogyIcon = L.divIcon({
        className: 'contamination-pedagogy',
        html: `<div data-testid="contamination-pedagogy" style="
          background:rgba(15,21,37,0.95);backdrop-filter:blur(12px);
          border:2px solid rgba(255,136,0,0.5);border-radius:12px;
          padding:16px 20px;color:#e0e8f0;font-size:20px;line-height:1.5;
          max-width:420px;min-width:280px;white-space:normal;pointer-events:auto;
          box-shadow:0 4px 24px rgba(0,0,0,0.5);
          position:relative;
        ">
          <button data-testid="bdre-pedagogy-close-btn" onclick="window.${closeFnName}()" style="
            position:absolute;top:8px;right:10px;
            background:rgba(255,68,68,0.15);border:2px solid rgba(255,68,68,0.5);
            color:#ff6666;font-size:22px;font-weight:700;
            width:36px;height:36px;border-radius:8px;
            cursor:pointer;display:flex;align-items:center;justify-content:center;
            transition:background 0.2s;line-height:1;
          " onmouseover="this.style.background='rgba(255,68,68,0.35)'"
             onmouseout="this.style.background='rgba(255,68,68,0.15)'"
          >X</button>
          <div style="font-weight:700;font-size:22px;color:#FF8800;margin-bottom:8px;padding-right:40px;">
            BDRE PEDAGOGIQUE
          </div>
          <div style="font-size:18px;color:#c8d0dc;line-height:1.5;">${pedagogy.conseil || ''}</div>
        </div>`,
        iconSize: [420, 120],
        iconAnchor: [210, -10],
      });

      const marker = L.marker([center.lat, center.lng], {
        icon: pedagogyIcon,
        interactive: true,
        zIndexOffset: 1000,
      });

      pedagogyMarkerRef.current = marker;
      group.addLayer(marker);
    }

    group.addTo(map);

    return () => {
      if (layerGroupRef.current) {
        layerGroupRef.current.clearLayers();
        map.removeLayer(layerGroupRef.current);
      }
    };
  }, [data, map, enabled, center, pedagogyVisible]);

  return null;
}

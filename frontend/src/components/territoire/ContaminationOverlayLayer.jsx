/**
 * ContaminationOverlayLayer.jsx — BCE-4X BLOC 2: GUIDE PRO
 * ================================================================
 * ORDONNANCE STEEVE-MAX 2026-04-07 | Branche BIONIC_REWRITE_P0
 *
 * Affichage PERMANENT des zones de contamination olfactive BDRE
 * pour 100% des salines actives, INDEPENDAMMENT des affuts.
 *
 * GUIDE PRO: Fenetre pedagogique positionnee en overlay React fixe
 * (JAMAIS sous les controles zoom/layers/navigation)
 *
 * Consomme: POST /api/v1/hunt/contamination-zones
 */
import { useEffect, useRef, useCallback, useState } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import { X, BookOpen } from 'lucide-react';

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

  // Render contamination zones on the map (polygons only — pedagogy is now React overlay)
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
        <div style="font-size:12px;line-height:1.5;min-width:200px;background:#0f1525;color:#e0e8f0;padding:10px;border-radius:8px;">
          <div style="font-weight:700;font-size:13px;margin-bottom:4px;color:${color}">
            ${zone.label || 'Zone de contamination'}
          </div>
          <div style="margin-bottom:4px;font-size:12px">${riskBadge}</div>
          <div style="font-size:11px;color:#9ca3af">
            Vent ${zone.bearing_deg || 0}° | Portee ${zone.range_m || 0}m
          </div>
        </div>
      `, { className: 'bionic-popup' });

      group.addLayer(poly);
    }

    group.addTo(map);

    return () => {
      if (layerGroupRef.current) {
        layerGroupRef.current.clearLayers();
        map.removeLayer(layerGroupRef.current);
      }
    };
  }, [data, map, enabled, center, pedagogyVisible]);

  // BCE-4X GUIDE PRO — Overlay React fixe (JAMAIS sous les controles)
  const pedagogy = data?.pedagogy;
  const showGuide = pedagogy && pedagogyVisible && enabled;

  return showGuide ? (
    <div
      data-testid="guide-pro-overlay"
      style={{
        position: 'absolute',
        top: '16px',
        right: '16px',
        zIndex: 900,
        pointerEvents: 'auto',
      }}
      onMouseDown={(e) => e.stopPropagation()}
      onClick={(e) => e.stopPropagation()}
      onDoubleClick={(e) => e.stopPropagation()}
    >
      <div
        data-testid="guide-pro-window"
        className="bg-[#0c0c14]/95 border border-gray-700/50 rounded-lg shadow-2xl backdrop-blur-sm"
        style={{ maxWidth: 280, minWidth: 220 }}
      >
        {/* Header — Typographie BionicLegend */}
        <div className="flex items-center justify-between px-3 py-2 border-b border-gray-800/60">
          <div className="flex items-center gap-2">
            <BookOpen className="w-3.5 h-3.5 text-[#F5A623]" />
            <span className="text-[10px] font-bold tracking-wider text-gray-100 uppercase">GUIDE PRO</span>
          </div>
          <button
            data-testid="guide-pro-close-btn"
            onClick={() => setPedagogyVisible(false)}
            className="w-6 h-6 rounded flex items-center justify-center hover:bg-white/10 transition-colors"
          >
            <X className="w-3.5 h-3.5 text-gray-400 hover:text-red-400" />
          </button>
        </div>

        {/* Contenu pedagogique */}
        <div className="px-3 py-2.5">
          <p className="text-[10px] text-gray-300 leading-relaxed">
            {pedagogy.conseil || ''}
          </p>
        </div>

        {/* Footer BCE-4X */}
        <div className="px-3 py-1.5 border-t border-gray-800/40 flex items-center justify-between">
          <span className="text-[8px] text-gray-600 tracking-wide">BCE-4X + Steeve-MAX</span>
          <span className="text-[8px] text-gray-600">GUIDE PRO</span>
        </div>
      </div>
    </div>
  ) : null;
}

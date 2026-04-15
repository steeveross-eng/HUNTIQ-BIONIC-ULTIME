/**
 * Carte2027Page — CARTE-2027-REBUILD-Omega-FULL-DEPLOY
 * Carte terrain V7 interactive Leaflet.
 * Architecture: TERRITOIRE (L1) -> INTELLIGENCE (L2) -> CARTE 2027 (L3)
 *
 * Integrations: 87 moteurs, heatmaps comportementales V7, cameras, POI,
 * GPS, vent, corridors, zones legales, solunaire, prevision 24h.
 */
import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, Polyline, Rectangle, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet.heat';
import axios from 'axios';
import { useAuth } from '@/components/GlobalAuth';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import {
  Map, Brain, Clock, Moon, TreePine, Wind, Camera, MapPin,
  Crosshair, Loader2, RefreshCw, ChevronDown, ChevronUp,
  LocateFixed, Layers, Eye, EyeOff, Navigation, Shield,
  Thermometer, Target, Compass
} from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const SPECIES = [
  { value: 'cerf', label: 'Chevreuil' },
  { value: 'orignal', label: 'Orignal' },
  { value: 'ours_noir', label: 'Ours noir' },
  { value: 'wapiti', label: 'Wapiti' },
  { value: 'dindon_sauvage', label: 'Dindon sauvage' },
];

const PROVINCES = [
  { value: 'qc', label: 'Quebec' }, { value: 'on', label: 'Ontario' },
  { value: 'nb', label: 'N.-Brunswick' }, { value: 'ns', label: 'N.-Ecosse' },
  { value: 'mb', label: 'Manitoba' }, { value: 'sk', label: 'Saskatchewan' },
  { value: 'ab', label: 'Alberta' }, { value: 'bc', label: 'C.-Britannique' },
  { value: 'yt', label: 'Yukon' }, { value: 'nt', label: 'T.N.-O.' },
  { value: 'pei', label: 'I.-P.-E.' },
];

const TILE_LAYERS = {
  dark: {
    url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    attribution: '&copy; CartoDB',
    label: 'Tactique',
  },
  satellite: {
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution: '&copy; Esri',
    label: 'Satellite',
  },
  topo: {
    url: 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
    attribution: '&copy; OpenTopoMap',
    label: 'Topographique',
  },
};

/* ═══ MAP SUB-COMPONENTS ═══ */

const HeatmapLayer = ({ data, visible }) => {
  const map = useMap();
  const layerRef = useRef(null);

  useEffect(() => {
    if (layerRef.current) {
      map.removeLayer(layerRef.current);
      layerRef.current = null;
    }
    if (!visible || !data?.length) return;

    const heatData = data.map(p => [p.lat, p.lng, p.probability || 0.3]);
    const layer = L.heatLayer(heatData, {
      radius: 45,
      blur: 30,
      maxZoom: 17,
      max: 1.0,
      gradient: {
        0.0: '#1e3a5f',
        0.2: '#3b82f6',
        0.4: '#22c55e',
        0.6: '#eab308',
        0.8: '#f97316',
        1.0: '#ef4444',
      },
    });
    layer.addTo(map);
    layerRef.current = layer;

    return () => {
      if (layerRef.current) {
        map.removeLayer(layerRef.current);
        layerRef.current = null;
      }
    };
  }, [data, visible, map]);

  return null;
};

const UserPositionMarker = ({ position }) => {
  const map = useMap();
  const markerRef = useRef(null);

  useEffect(() => {
    if (markerRef.current) {
      map.removeLayer(markerRef.current);
      markerRef.current = null;
    }
    if (!position) return;

    const icon = L.divIcon({
      className: 'user-position-marker',
      html: `<div style="width:18px;height:18px;border-radius:50%;background:#3b82f6;border:3px solid white;box-shadow:0 0 12px rgba(59,130,246,0.6);"></div>`,
      iconSize: [18, 18],
      iconAnchor: [9, 9],
    });
    const marker = L.marker([position.lat, position.lng], { icon, zIndexOffset: 1000 }).addTo(map);
    marker.bindPopup('<b>Ma position</b>');
    markerRef.current = marker;

    return () => {
      if (markerRef.current) map.removeLayer(markerRef.current);
    };
  }, [position, map]);

  return null;
};

const WindIndicator = ({ windData, center }) => {
  const map = useMap();
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!windData || !center) return;
    const container = map.getContainer();
    let canvas = container.querySelector('canvas[data-carte2027wind]');
    if (!canvas) {
      canvas = document.createElement('canvas');
      canvas.setAttribute('data-carte2027wind', 'true');
      canvas.style.position = 'absolute';
      canvas.style.top = '0';
      canvas.style.left = '0';
      canvas.style.pointerEvents = 'none';
      canvas.style.zIndex = '450';
      container.appendChild(canvas);
    }
    canvasRef.current = canvas;

    const draw = () => {
      const size = map.getSize();
      canvas.width = size.x;
      canvas.height = size.y;
      const ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const rad = (windData.direction_deg - 90) * Math.PI / 180;
      const cx = canvas.width - 60;
      const cy = 80;
      const len = 28;

      ctx.save();
      ctx.globalAlpha = 0.7;
      ctx.strokeStyle = '#60a5fa';
      ctx.lineWidth = 2;
      ctx.fillStyle = '#60a5fa';

      ctx.beginPath();
      ctx.arc(cx, cy, 32, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(96,165,250,0.3)';
      ctx.stroke();

      const ex = cx + Math.cos(rad) * len;
      const ey = cy + Math.sin(rad) * len;
      ctx.strokeStyle = '#60a5fa';
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(ex, ey);
      ctx.stroke();

      const arrowSize = 8;
      const angle = Math.atan2(ey - cy, ex - cx);
      ctx.beginPath();
      ctx.moveTo(ex, ey);
      ctx.lineTo(ex - arrowSize * Math.cos(angle - 0.4), ey - arrowSize * Math.sin(angle - 0.4));
      ctx.lineTo(ex - arrowSize * Math.cos(angle + 0.4), ey - arrowSize * Math.sin(angle + 0.4));
      ctx.closePath();
      ctx.fill();

      ctx.fillStyle = '#94a3b8';
      ctx.font = '9px monospace';
      ctx.textAlign = 'center';
      ctx.fillText(`${windData.speed_kmh} km/h`, cx, cy + 48);
      ctx.fillText(windData.compass, cx, cy + 58);
      ctx.restore();
    };

    draw();
    map.on('move zoom', draw);
    return () => {
      map.off('move zoom', draw);
      if (canvasRef.current) canvasRef.current.remove();
    };
  }, [windData, center, map]);

  return null;
};

const MapRefCapture = ({ mapRef }) => {
  const map = useMap();
  useEffect(() => { mapRef.current = map; }, [map, mapRef]);
  return null;
};

const MapEvents = ({ onMoveEnd }) => {
  useMapEvents({
    moveend: (e) => {
      const c = e.target.getCenter();
      onMoveEnd({ lat: c.lat, lng: c.lng }, e.target.getZoom());
    },
  });
  return null;
};

/* ═══ POI ICONS ═══ */
const createPOIIcon = (type) => {
  const colors = { camera: '#F59E0B', waypoint: '#3B82F6', saline: '#10B981' };
  const svgs = {
    camera: '<path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/><circle cx="12" cy="13" r="3"/>',
    waypoint: '<circle cx="12" cy="10" r="3"/><path d="M12 21.7C17.3 17 20 13 20 10a8 8 0 1 0-16 0c0 3 2.7 7 8 11.7z"/>',
    saline: '<path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>',
  };
  const color = colors[type] || '#9CA3AF';
  const svg = svgs[type] || svgs.waypoint;
  return L.divIcon({
    className: 'carte2027-poi',
    html: `<div style="background:${color};border-radius:50%;width:24px;height:24px;display:flex;align-items:center;justify-content:center;border:2px solid rgba(255,255,255,0.8);box-shadow:0 2px 6px rgba(0,0,0,0.4)"><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${svg}</svg></div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
    popupAnchor: [0, -14],
  });
};

const POIMarkers = ({ pois, visible }) => {
  const map = useMap();
  const markersRef = useRef([]);

  useEffect(() => {
    markersRef.current.forEach(m => map.removeLayer(m));
    markersRef.current = [];
    if (!visible || !pois?.length) return;

    pois.forEach(poi => {
      const icon = createPOIIcon(poi.type);
      const marker = L.marker([poi.lat, poi.lng], { icon }).addTo(map);
      const popupHtml = `<div style="min-width:120px"><b style="color:#F5A623">${poi.name}</b><br/><span style="color:#9CA3AF;font-size:10px;text-transform:uppercase">${poi.type}</span></div>`;
      marker.bindPopup(popupHtml);
      markersRef.current.push(marker);
    });

    return () => {
      markersRef.current.forEach(m => map.removeLayer(m));
      markersRef.current = [];
    };
  }, [pois, visible, map]);

  return null;
};

const CorridorLines = ({ corridors, visible }) => {
  if (!visible || !corridors?.length) return null;
  return corridors.map((c) => (
    <Polyline
      key={c.id}
      positions={[[c.start.lat, c.start.lng], [c.end.lat, c.end.lng]]}
      pathOptions={{
        color: c.intensity > 0.6 ? '#F59E0B' : '#6B7280',
        weight: c.intensity > 0.6 ? 3 : 2,
        opacity: Math.max(0.3, c.intensity),
        dashArray: c.type === 'secondary' ? '8 4' : null,
      }}
    />
  ));
};

const ZoneRectangles = ({ zones, visible }) => {
  if (!visible || !zones?.length) return null;
  return zones.map((z) => (
    <Rectangle
      key={z.id}
      bounds={z.bounds}
      pathOptions={{
        color: z.status === 'ouverte' ? '#22C55E' : '#EF4444',
        weight: 1,
        opacity: 0.5,
        fillOpacity: 0.08,
        fillColor: z.status === 'ouverte' ? '#22C55E' : '#EF4444',
      }}
    >
      <Popup>
        <div style={{ minWidth: 150 }}>
          <b style={{ color: '#F5A623' }}>{z.name}</b><br />
          <span style={{ color: z.status === 'ouverte' ? '#22C55E' : '#EF4444', fontWeight: 'bold', textTransform: 'uppercase', fontSize: 10 }}>
            {z.status}
          </span>
          {z.quota && <span style={{ color: '#9CA3AF', fontSize: 10, marginLeft: 6 }}>{z.quota}</span>}
        </div>
      </Popup>
    </Rectangle>
  ));
};


/* ═══ INTELLIGENCE PANEL (floating) ═══ */

const IntelPanel = ({ v7Score, hourlyForecast, solunar, lunar, windData, hour }) => {
  const [open, setOpen] = useState(true);
  const predLabel = v7Score?.prediction || '--';
  const predColor = predLabel === 'excellent' ? '#10B981' : predLabel === 'bon' ? '#22D3EE' : predLabel === 'moyen' ? '#F59E0B' : '#EF4444';

  return (
    <div className="absolute top-2 right-2 z-[500] w-64" data-testid="carte2027-intel-panel">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-3 py-2 bg-gray-950/90 backdrop-blur-md border border-gray-700/50 rounded-t-lg text-white text-xs font-bold"
        data-testid="carte2027-intel-toggle"
      >
        <span className="flex items-center gap-1.5">
          <Brain className="h-3.5 w-3.5 text-emerald-400" />
          INTELLIGENCE V7
        </span>
        {open ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
      </button>

      {open && (
        <div className="bg-gray-950/90 backdrop-blur-md border border-t-0 border-gray-700/50 rounded-b-lg p-3 space-y-3 max-h-[calc(100vh-200px)] overflow-y-auto">
          {/* V7 Score */}
          {v7Score && (
            <div data-testid="carte2027-v7-score">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] text-gray-500 uppercase tracking-wider">Score Global</span>
                <Badge className="text-[9px] font-bold px-1.5 py-0" style={{ backgroundColor: `${predColor}20`, color: predColor }}>
                  {predLabel}
                </Badge>
              </div>
              <div className="text-center mb-2">
                <div className="text-3xl font-black" style={{ color: predColor }}>{Math.round(v7Score.v7_score)}</div>
                <div className="text-[9px] text-gray-500">/100</div>
              </div>
              <div className="grid grid-cols-3 gap-1.5 text-center">
                {[
                  { k: 'temporal', l: 'Temporel', c: '#F59E0B' },
                  { k: 'meteo', l: 'Meteo', c: '#3B82F6' },
                  { k: 'rut', l: 'Rut', c: '#EC4899' },
                ].map(s => (
                  <div key={s.k} className="bg-gray-900/60 rounded px-1 py-1">
                    <div className="text-sm font-bold" style={{ color: s.c }}>{Math.round(v7Score.scores_detail?.[s.k] || 0)}</div>
                    <div className="text-[8px] text-gray-500">{s.l}</div>
                  </div>
                ))}
              </div>
              {v7Score.optimal_windows && (
                <div className="mt-2 flex items-center gap-1 text-[9px] text-gray-400">
                  <Clock className="h-2.5 w-2.5 text-amber-400" />
                  <span>{v7Score.optimal_windows.join(' | ')}</span>
                </div>
              )}
            </div>
          )}

          {/* Hourly Forecast mini */}
          {hourlyForecast?.forecast && (
            <div data-testid="carte2027-hourly">
              <div className="text-[9px] text-gray-500 uppercase tracking-wider mb-1">Prevision 24h</div>
              <div className="flex gap-px items-end h-10">
                {hourlyForecast.forecast.map(f => {
                  const h = Math.max(8, f.score * 0.4);
                  const c = f.score >= 70 ? '#10B981' : f.score >= 40 ? '#F59E0B' : '#374151';
                  const isNow = f.hour === hour;
                  return (
                    <div key={f.hour} className="flex-1 flex flex-col items-center gap-px" title={`${f.hour}h: ${f.score}`}>
                      <div className="w-full rounded-sm" style={{ height: `${h}%`, backgroundColor: c, border: isNow ? '1px solid #fff' : 'none' }} />
                    </div>
                  );
                })}
              </div>
              <div className="text-[8px] text-gray-600 mt-0.5">
                Pic: {hourlyForecast.peak_hours?.slice(0, 3).join('h, ')}h
              </div>
            </div>
          )}

          {/* Solunar */}
          {lunar && (
            <div data-testid="carte2027-solunar">
              <div className="text-[9px] text-gray-500 uppercase tracking-wider mb-1">Solunaire</div>
              <div className="grid grid-cols-2 gap-2 text-[10px]">
                <div>
                  <div className="text-gray-500">Phase</div>
                  <div className="text-white font-bold text-xs">{lunar.phase_name}</div>
                </div>
                <div>
                  <div className="text-gray-500">Chasse</div>
                  <div className="font-bold text-xs" style={{ color: lunar.hunting_rating === 'excellent' ? '#10B981' : lunar.hunting_rating === 'bon' ? '#F59E0B' : '#EF4444' }}>
                    {lunar.hunting_rating}
                  </div>
                </div>
              </div>
              {solunar?.windows && (
                <div className="mt-1.5 space-y-0.5">
                  {Object.entries(solunar.windows).map(([k, v]) => (
                    <div key={k} className="flex justify-between text-[9px]">
                      <span className="text-gray-500">{k.includes('major') ? 'Majeur' : 'Mineur'}</span>
                      <span className="text-white font-mono font-bold">{v}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Wind */}
          {windData && (
            <div data-testid="carte2027-wind-info">
              <div className="text-[9px] text-gray-500 uppercase tracking-wider mb-1">Vent</div>
              <div className="flex items-center justify-between text-[10px]">
                <span className="text-gray-400">{windData.compass} {windData.direction_deg}&deg;</span>
                <span className="text-white font-bold">{windData.speed_kmh} km/h</span>
                <Badge className="text-[8px] px-1" style={{
                  backgroundColor: windData.hunting_impact === 'favorable' ? '#10B98120' : windData.hunting_impact === 'moderee' ? '#F59E0B20' : '#EF444420',
                  color: windData.hunting_impact === 'favorable' ? '#10B981' : windData.hunting_impact === 'moderee' ? '#F59E0B' : '#EF4444',
                }}>
                  {windData.hunting_impact}
                </Badge>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};


/* ═══ LAYER CONTROLS (floating left) ═══ */

const LayerControls = ({ layers, toggleLayer, tileKey, setTileKey }) => {
  const [open, setOpen] = useState(false);

  const layerDefs = [
    { key: 'heatmap', label: 'Heatmap V7', icon: Target, color: '#EF4444' },
    { key: 'pois', label: 'Points interet', icon: MapPin, color: '#3B82F6' },
    { key: 'corridors', label: 'Corridors', icon: Navigation, color: '#F59E0B' },
    { key: 'zones', label: 'Zones legales', icon: Shield, color: '#22C55E' },
    { key: 'wind', label: 'Vent', icon: Wind, color: '#60A5FA' },
  ];

  return (
    <div className="absolute top-2 left-2 z-[500]" data-testid="carte2027-layer-controls">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1.5 px-2.5 py-1.5 bg-gray-950/90 backdrop-blur-md border border-gray-700/50 rounded-lg text-white text-xs font-bold"
        data-testid="carte2027-layers-toggle"
      >
        <Layers className="h-3.5 w-3.5 text-emerald-400" />
        Couches
        {open ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
      </button>

      {open && (
        <div className="mt-1 bg-gray-950/90 backdrop-blur-md border border-gray-700/50 rounded-lg p-2.5 space-y-2 w-52">
          {/* Tile selector */}
          <div className="text-[9px] text-gray-500 uppercase tracking-wider mb-1">Fond de carte</div>
          <div className="flex gap-1">
            {Object.entries(TILE_LAYERS).map(([k, v]) => (
              <button
                key={k}
                onClick={() => setTileKey(k)}
                className={`flex-1 px-1.5 py-1 text-[9px] rounded font-bold transition-colors ${tileKey === k ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40' : 'bg-gray-800/50 text-gray-400 border border-gray-700/30 hover:border-gray-600'}`}
                data-testid={`carte2027-tile-${k}`}
              >
                {v.label}
              </button>
            ))}
          </div>

          <div className="border-t border-gray-800/50 my-1.5" />
          <div className="text-[9px] text-gray-500 uppercase tracking-wider mb-1">Couches V7</div>

          {layerDefs.map(ld => (
            <div key={ld.key} className="flex items-center justify-between">
              <div className="flex items-center gap-1.5">
                <ld.icon className="h-3 w-3" style={{ color: ld.color }} />
                <span className="text-[10px] text-gray-300">{ld.label}</span>
              </div>
              <Switch
                checked={layers[ld.key]}
                onCheckedChange={() => toggleLayer(ld.key)}
                className="h-4 w-7 data-[state=checked]:bg-emerald-500"
                data-testid={`carte2027-toggle-${ld.key}`}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
};


/* ═══ MAIN PAGE COMPONENT ═══ */

export default function Carte2027Page() {
  const { token } = useAuth();
  const mapRef = useRef(null);

  // State
  const [species, setSpecies] = useState('cerf');
  const [province, setProvince] = useState('qc');
  const [loading, setLoading] = useState(false);
  const [tileKey, setTileKey] = useState('dark');
  const [mapCenter, setMapCenter] = useState({ lat: 47.5, lng: -71.8 });
  const [mapZoom, setMapZoom] = useState(10);
  const [userPosition, setUserPosition] = useState(null);
  const [gpsLoading, setGpsLoading] = useState(false);

  // Layer visibility
  const [layers, setLayers] = useState({
    heatmap: true, pois: true, corridors: true, zones: false, wind: true,
  });

  // Data
  const [v7Score, setV7Score] = useState(null);
  const [hourlyForecast, setHourlyForecast] = useState(null);
  const [solunar, setSolunar] = useState(null);
  const [lunar, setLunar] = useState(null);
  const [heatmapData, setHeatmapData] = useState(null);
  const [poisData, setPoisData] = useState(null);
  const [windData, setWindData] = useState(null);
  const [corridorsData, setCorridorsData] = useState(null);
  const [zonesData, setZonesData] = useState(null);

  const headers = useMemo(() => token ? { Authorization: `Bearer ${token}` } : {}, [token]);
  const now = new Date();
  const month = now.getMonth() + 1;
  const day = now.getDate();
  const hour = now.getHours();

  const toggleLayer = useCallback((key) => {
    setLayers(prev => ({ ...prev, [key]: !prev[key] }));
  }, []);

  // Load all data
  const loadAll = useCallback(async (center) => {
    if (!token) return;
    setLoading(true);
    const lat = center?.lat || mapCenter.lat;
    const lon = center?.lng || mapCenter.lng;

    try {
      const [v7, forecast, sol, lun, heat, pois, wind, corr, zones] = await Promise.all([
        axios.get(`${API}/v1/v51/intelligence/v7/score?lat=${lat}&lon=${lon}&species=${species}&month=${month}&day=${day}&hour=${hour}&province=${province}&temp_c=8&wind_kmh=12`, { headers }).catch(() => null),
        axios.get(`${API}/v1/v51/intelligence/v7/hourly-forecast?lat=${lat}&lon=${lon}&species=${species}&month=${month}&day=${day}`, { headers }).catch(() => null),
        axios.get(`${API}/v1/v51/solunar/windows?month=${month}&day=${day}&lat=${lat}`).catch(() => null),
        axios.get(`${API}/v1/v51/lunar/activity?month=${month}&day=${day}&species=${species}`).catch(() => null),
        axios.get(`${API}/v1/carte2027/heatmap-grid?lat=${lat}&lon=${lon}&species=${species}&month=${month}&day=${day}&hour=${hour}&grid_size=14&radius_km=20`, { headers }).catch(() => null),
        axios.get(`${API}/v1/carte2027/poi?lat=${lat}&lon=${lon}`, { headers }).catch(() => null),
        axios.get(`${API}/v1/carte2027/wind?lat=${lat}&lon=${lon}`, { headers }).catch(() => null),
        axios.get(`${API}/v1/carte2027/corridors-overlay?lat=${lat}&lon=${lon}&species=${species}`, { headers }).catch(() => null),
        axios.get(`${API}/v1/carte2027/zones-legales?province=${province}&species=${species}`, { headers }).catch(() => null),
      ]);

      if (v7) setV7Score(v7.data);
      if (forecast) setHourlyForecast(forecast.data);
      if (sol) setSolunar(sol.data);
      if (lun) setLunar(lun.data);
      if (heat) setHeatmapData(heat.data?.points);
      if (pois) setPoisData(pois.data?.pois);
      if (wind) setWindData(wind.data);
      if (corr) setCorridorsData(corr.data?.corridors);
      if (zones) setZonesData(zones.data?.zones);
    } catch (err) {
      console.error('Carte2027 load error:', err);
    } finally {
      setLoading(false);
    }
  }, [token, species, province, month, day, hour, headers, mapCenter]);

  useEffect(() => { loadAll(); }, [loadAll]);

  // GPS
  const handleGPS = useCallback(() => {
    if (!navigator.geolocation) return;
    setGpsLoading(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const loc = { lat: pos.coords.latitude, lng: pos.coords.longitude };
        setUserPosition(loc);
        setMapCenter(loc);
        if (mapRef.current) {
          mapRef.current.flyTo([loc.lat, loc.lng], 13, { duration: 1.5 });
        }
        loadAll(loc);
        setGpsLoading(false);
      },
      () => setGpsLoading(false),
      { enableHighAccuracy: true, timeout: 10000 }
    );
  }, [loadAll]);

  // Map move handler (reload data on significant moves)
  const handleMapMoveEnd = useCallback((center, zoom) => {
    setMapZoom(zoom);
    const dist = Math.sqrt(
      Math.pow(center.lat - mapCenter.lat, 2) + Math.pow(center.lng - mapCenter.lng, 2)
    );
    if (dist > 0.05) {
      setMapCenter(center);
    }
  }, [mapCenter]);

  const tile = TILE_LAYERS[tileKey];

  return (
    <div className="fixed inset-0 bg-gray-950" style={{ paddingTop: '136px' }} data-testid="carte-2027-page">
      {/* COMPACT HEADER */}
      <div className="absolute top-[136px] left-0 right-0 z-[600] flex items-center gap-2 px-3 py-1.5 bg-gray-950/80 backdrop-blur-md border-b border-gray-800/30">
        <Map className="h-4 w-4 text-emerald-400 flex-shrink-0" />
        <span className="text-xs font-bold text-white tracking-wider flex-shrink-0">CARTE TERRAIN V7</span>
        <Badge className="bg-emerald-500/20 text-emerald-400 text-[8px] flex-shrink-0">2027</Badge>

        <div className="flex items-center gap-1.5 ml-auto">
          <Select value={species} onValueChange={setSpecies}>
            <SelectTrigger className="h-6 w-28 text-[10px] bg-gray-900/60 border-gray-800/50" data-testid="carte2027-species"><SelectValue /></SelectTrigger>
            <SelectContent>{SPECIES.map(s => <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>)}</SelectContent>
          </Select>
          <Select value={province} onValueChange={setProvince}>
            <SelectTrigger className="h-6 w-24 text-[10px] bg-gray-900/60 border-gray-800/50" data-testid="carte2027-province"><SelectValue /></SelectTrigger>
            <SelectContent>{PROVINCES.map(p => <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>)}</SelectContent>
          </Select>

          <Button size="sm" variant="ghost" onClick={handleGPS} disabled={gpsLoading}
            className="h-6 w-6 p-0 text-blue-400 hover:text-blue-300 hover:bg-blue-500/10"
            data-testid="carte2027-gps-btn"
            title="Ma position GPS"
          >
            {gpsLoading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <LocateFixed className="h-3.5 w-3.5" />}
          </Button>

          <Button size="sm" variant="ghost" onClick={() => loadAll()} disabled={loading}
            className="h-6 w-6 p-0 text-gray-400 hover:text-white"
            data-testid="carte2027-refresh"
          >
            {loading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <RefreshCw className="h-3.5 w-3.5" />}
          </Button>
        </div>
      </div>

      {/* MAP */}
      <div className="absolute inset-0" style={{ top: '136px' }}>
        {loading && !v7Score && (
          <div className="absolute inset-0 z-[1000] flex items-center justify-center bg-gray-950/60">
            <div className="flex flex-col items-center gap-2">
              <Loader2 className="h-8 w-8 animate-spin text-emerald-400" />
              <span className="text-xs text-gray-400">Chargement moteurs V7...</span>
            </div>
          </div>
        )}

        <MapContainer
          center={[mapCenter.lat, mapCenter.lng]}
          zoom={mapZoom}
          className="absolute inset-0 w-full h-full"
          zoomControl={false}
          style={{ background: '#0a0a0f', top: '32px' }}
          data-testid="carte2027-map"
        >
          <MapRefCapture mapRef={mapRef} />
          <MapEvents onMoveEnd={handleMapMoveEnd} />

          {/* Tile Layer */}
          <TileLayer
            url={tile.url}
            attribution={tile.attribution}
            maxZoom={19}
          />

          {/* Satellite labels overlay */}
          {tileKey === 'satellite' && (
            <TileLayer
              url="https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}{r}.png"
              maxZoom={19}
              pane="overlayPane"
            />
          )}

          {/* V7 Behavioral Heatmap */}
          <HeatmapLayer data={heatmapData} visible={layers.heatmap} />

          {/* POI Markers */}
          <POIMarkers pois={poisData} visible={layers.pois} />

          {/* Corridors */}
          <CorridorLines corridors={corridorsData} visible={layers.corridors} />

          {/* Zones legales */}
          <ZoneRectangles zones={zonesData} visible={layers.zones} />

          {/* Wind indicator */}
          {layers.wind && <WindIndicator windData={windData} center={mapCenter} />}

          {/* User GPS position */}
          <UserPositionMarker position={userPosition} />
        </MapContainer>

        {/* FLOATING PANELS */}
        <LayerControls
          layers={layers}
          toggleLayer={toggleLayer}
          tileKey={tileKey}
          setTileKey={setTileKey}
        />

        <IntelPanel
          v7Score={v7Score}
          hourlyForecast={hourlyForecast}
          solunar={solunar}
          lunar={lunar}
          windData={windData}
          hour={hour}
        />

        {/* Coordinates display */}
        <div className="absolute bottom-2 left-2 z-[500] px-2 py-1 bg-gray-950/80 backdrop-blur-sm rounded text-[9px] text-gray-500 font-mono" data-testid="carte2027-coords">
          {mapCenter.lat.toFixed(4)}, {mapCenter.lng.toFixed(4)} | z{mapZoom}
        </div>

        {/* Engine badge */}
        <div className="absolute bottom-2 right-2 z-[500] px-2 py-1 bg-gray-950/80 backdrop-blur-sm rounded text-[8px] text-emerald-500/60 font-mono" data-testid="carte2027-engine-badge">
          87 MOTEURS | CARTE-2027-V7
        </div>
      </div>
    </div>
  );
}

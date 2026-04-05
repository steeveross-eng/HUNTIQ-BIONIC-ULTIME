/**
 * AdminHotspots V7.2 — SOURCE DE VERITE ADMIN PREMIUM
 * Carte Leaflet + Tableau enrichi + Filtres + Export + Scheduler + Gestionnaire
 * V7.2: Gradient BIONIC + Ecologie + Terrain-aware + Dispersion 1.5km
 * Directive x7200 — UNIFICATION HOTSPOTS ADMIN PREMIUM
 */
import React, { useState, useCallback, useRef, useEffect } from 'react';
import { MapPin, Download, RefreshCw, Filter, ChevronDown, Shield, BarChart3, Clock, MapIcon, List, Phone, Globe, Mail, ExternalLink, Mountain, Navigation, Map, Leaf, TreePine, Droplets, Gauge } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

const API = process.env.REACT_APP_BACKEND_URL;
const HOTSPOT_API = `${API}/api/v1/admin/bionic-hotspots`;

// V7.2 — Gradient BIONIC officiel (directive x7200)
const BIONIC_GRADIENT = {
  GREEN: { min: 80, bg: 'bg-emerald-500/20', text: 'text-emerald-400', border: 'border-emerald-500/30', color: '#10b981', label: '80-100%' },
  YELLOW: { min: 60, bg: 'bg-yellow-500/20', text: 'text-yellow-400', border: 'border-yellow-500/30', color: '#eab308', label: '60-80%' },
  ORANGE: { min: 40, bg: 'bg-orange-500/20', text: 'text-orange-400', border: 'border-orange-500/30', color: '#f97316', label: '40-60%' },
  RED: { min: 0, bg: 'bg-red-500/20', text: 'text-red-400', border: 'border-red-500/30', color: '#ef4444', label: '<40%' },
};

const getGradientStyle = (score) => {
  if (score >= 80) return BIONIC_GRADIENT.GREEN;
  if (score >= 60) return BIONIC_GRADIENT.YELLOW;
  if (score >= 40) return BIONIC_GRADIENT.ORANGE;
  return BIONIC_GRADIENT.RED;
};

const getGradientColor = (score) => getGradientStyle(score).color;

const TT_BADGES = {
  'ZEC': 'bg-emerald-500/20 text-emerald-400',
  'Pourvoirie': 'bg-blue-500/20 text-blue-400',
  'Reserve faunique': 'bg-purple-500/20 text-purple-400',
  'Gouvernemental': 'bg-cyan-500/20 text-cyan-400',
  'Public': 'bg-gray-500/20 text-gray-400',
  'Prive': 'bg-amber-500/20 text-amber-400',
  'Territoire autochtone': 'bg-rose-500/20 text-rose-400',
};

/* ═══════════════════════════════════════════
   SATELLITE PREVIEW (300×180) — Au survol du bouton Carte
   ═══════════════════════════════════════════ */
const SatellitePreview = ({ lat, lng, visible, anchorRef }) => {
  const containerRef = useRef(null);
  const miniMapRef = useRef(null);

  useEffect(() => {
    if (!visible || !containerRef.current) {
      if (miniMapRef.current) { miniMapRef.current.remove(); miniMapRef.current = null; }
      return;
    }
    if (miniMapRef.current) return;

    const map = L.map(containerRef.current, {
      zoomControl: false,
      attributionControl: false,
      dragging: false,
      scrollWheelZoom: false,
      doubleClickZoom: false,
      touchZoom: false,
      boxZoom: false,
      keyboard: false,
    }).setView([lat, lng], 14);

    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 19,
    }).addTo(map);

    // Cercle V6 officiel 600m (directive STEEVE-MAX)
    L.circle([lat, lng], {
      radius: 600,
      color: '#f5a623',
      fillColor: '#f5a623',
      fillOpacity: 0.15,
      weight: 2,
      dashArray: '6,4',
    }).addTo(map);

    // Point central
    L.circleMarker([lat, lng], {
      radius: 5,
      color: '#fff',
      fillColor: '#f5a623',
      fillOpacity: 1,
      weight: 2,
    }).addTo(map);

    miniMapRef.current = map;

    return () => {
      if (miniMapRef.current) { miniMapRef.current.remove(); miniMapRef.current = null; }
    };
  }, [visible, lat, lng]);

  if (!visible) return null;

  return (
    <div
      className="absolute z-[9999] rounded-lg overflow-hidden border-2 border-[#f5a623]/60 shadow-2xl shadow-black/60"
      style={{ width: 300, height: 180, bottom: '100%', left: '50%', transform: 'translateX(-50%)', marginBottom: 8 }}
      data-testid="satellite-preview"
    >
      <div ref={containerRef} style={{ width: 300, height: 180 }} />
      <div className="absolute bottom-0 left-0 right-0 bg-black/70 backdrop-blur-sm px-2 py-1 flex items-center justify-between">
        <span className="text-[9px] text-gray-300 font-mono">{lat.toFixed(4)}, {lng.toFixed(4)}</span>
        <span className="text-[9px] text-[#f5a623] font-bold">Satellite</span>
      </div>
    </div>
  );
};

/* ═══════════════════════════════════════════
   BOUTON CARTE — Ouvre Mon Territoire dans un nouvel onglet
   ═══════════════════════════════════════════ */
const CarteButton = ({ hotspot }) => {
  const [showPreview, setShowPreview] = useState(false);
  const timerRef = useRef(null);
  const btnRef = useRef(null);

  const lat = hotspot.center?.[0];
  const lng = hotspot.center?.[1];
  const hotspotId = hotspot.id;

  const link = `/mon-territoire?lat=${lat}&lng=${lng}&zoom=15&layer=satellite&hotspot=${encodeURIComponent(hotspotId)}`;

  const handleMouseEnter = () => {
    timerRef.current = setTimeout(() => setShowPreview(true), 250);
  };
  const handleMouseLeave = () => {
    clearTimeout(timerRef.current);
    setShowPreview(false);
  };

  useEffect(() => () => clearTimeout(timerRef.current), []);

  if (!lat || !lng) return null;

  return (
    <div className="relative inline-block" onMouseEnter={handleMouseEnter} onMouseLeave={handleMouseLeave} ref={btnRef}>
      <SatellitePreview lat={lat} lng={lng} visible={showPreview} anchorRef={btnRef} />
      <a
        href={link}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-flex items-center gap-1 px-2 py-1 rounded-md text-[10px] font-bold
                   bg-[#1E88E5]/15 text-[#42A5F5] border border-[#1E88E5]/30
                   hover:bg-[#1E88E5]/25 hover:text-[#90CAF9] hover:shadow-[0_0_8px_rgba(30,136,229,0.3)]
                   transition-all duration-200"
        data-testid={`carte-btn-${hotspotId}`}
      >
        <Map className="h-3 w-3" />
        Carte
      </a>
    </div>
  );
};

/* ═══════════════════════════════════════════
   LEAFLET MAP COMPONENT
   ═══════════════════════════════════════════ */
const HotspotMap = ({ hotspots, selectedRegion }) => {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const layerRef = useRef(null);

  useEffect(() => {
    if (!mapRef.current || mapInstanceRef.current) return;
    const map = L.map(mapRef.current, { zoomControl: true }).setView([47.5, -72.0], 6);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: 'BIONIC V6 | GOLDEN-BCE-4X',
      maxZoom: 18,
    }).addTo(map);
    mapInstanceRef.current = map;
    layerRef.current = L.layerGroup().addTo(map);
    return () => { map.remove(); mapInstanceRef.current = null; };
  }, []);

  useEffect(() => {
    if (!mapInstanceRef.current || !layerRef.current) return;
    layerRef.current.clearLayers();
    if (!hotspots?.length) return;

    const bounds = [];
    hotspots.forEach(h => {
      if (!h.polygon?.length) return;
      const coords = h.polygon.map(p => [p[0], p[1]]);
      const score = h.score || 0;
      const color = getGradientColor(score);
      const gradientStyle = getGradientStyle(score);

      const poly = L.polygon(coords, {
        color, fillColor: color, fillOpacity: 0.35, weight: 2,
      });

      poly.bindPopup(`
        <div style="font-family:system-ui;min-width:240px;color:#e5e5e5;background:#1a1a2e;padding:10px;border-radius:8px;">
          <div style="font-weight:800;font-size:14px;color:${color};margin-bottom:6px;">${h.id} — ${h.classification}</div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;font-size:11px;">
            <span style="color:#888;">Score</span><span style="font-weight:700;color:${color};">${h.score}/100</span>
            <span style="color:#888;">Espece</span><span style="color:#f5a623;">${h.dominant_species}</span>
            <span style="color:#888;">Habitat</span><span>${h.habitat_type || '—'}</span>
            <span style="color:#888;">Intensite</span><span>${h.intensity || '—'}</span>
            <span style="color:#888;">Territoire</span><span>${h.territory_type || '—'}</span>
            <span style="color:#888;">Acces</span><span>${h.access_status || '—'}</span>
            <span style="color:#888;">Ville</span><span>${h.ville || '—'}</span>
            <span style="color:#888;">Altitude</span><span>${h.altitude_m || '—'}m</span>
            <span style="color:#888;">GPS</span><span style="font-size:10px;">${h.center[0].toFixed(4)}, ${h.center[1].toFixed(4)}</span>
            <span style="color:#888;">Eau prox.</span><span>${h.water_proximity != null ? (h.water_proximity * 100).toFixed(0) + '%' : '—'}</span>
          </div>
          <div style="margin-top:6px;font-size:10px;color:#666;">
            ${(h.justification || []).slice(0, 3).join('<br/>')}
          </div>
        </div>
      `, { className: 'bionic-popup', maxWidth: 300 });

      poly.addTo(layerRef.current);
      bounds.push(...coords);

      // V7.2: Point central colore selon gradient BIONIC
      L.circleMarker([h.center[0], h.center[1]], {
        radius: 5,
        color: '#fff',
        fillColor: color,
        fillOpacity: 1,
        weight: 1.5,
      }).addTo(layerRef.current);
    });

    if (bounds.length > 0) {
      mapInstanceRef.current.fitBounds(bounds, { padding: [30, 30], maxZoom: 10 });
    }
  }, [hotspots, selectedRegion]);

  return <div ref={mapRef} className="w-full h-[450px] rounded-xl border border-gray-700/30 z-0" data-testid="hotspot-leaflet-map" />;
};

/* ═══════════════════════════════════════════
   GESTIONNAIRE PANEL
   ═══════════════════════════════════════════ */
const GestionnairePanel = ({ hotspot, onClose }) => {
  if (!hotspot) return null;
  const g = hotspot.gestionnaire || {};
  const lot = hotspot.lot_info;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="bg-gray-950 border border-gray-700/60 rounded-xl max-w-lg w-full p-5 space-y-4" onClick={e => e.stopPropagation()} data-testid="gestionnaire-panel">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold text-white">{hotspot.id} — Gestionnaire</h3>
          <button onClick={onClose} className="text-gray-500 hover:text-white">&times;</button>
        </div>

        {/* Territory info */}
        <div className="grid grid-cols-2 gap-3 text-xs">
          <div className="bg-gray-900/50 rounded-lg p-3">
            <div className="text-gray-500 text-[10px] uppercase mb-1">Type territoire</div>
            <Badge className={TT_BADGES[hotspot.territory_type] || 'bg-gray-500/20 text-gray-400'}>{hotspot.territory_type}</Badge>
          </div>
          <div className="bg-gray-900/50 rounded-lg p-3">
            <div className="text-gray-500 text-[10px] uppercase mb-1">Statut d'acces</div>
            <span className="text-white font-bold">{hotspot.access_status}</span>
          </div>
          <div className="bg-gray-900/50 rounded-lg p-3">
            <div className="text-gray-500 text-[10px] uppercase mb-1">Ville</div>
            <span className="text-white">{hotspot.ville}</span>
          </div>
          <div className="bg-gray-900/50 rounded-lg p-3">
            <div className="text-gray-500 text-[10px] uppercase mb-1">Code postal</div>
            <span className="text-white font-mono">{hotspot.code_postal}</span>
          </div>
        </div>

        {/* Gestionnaire info */}
        <div className="bg-gray-900/50 rounded-lg p-3 space-y-2">
          <div className="text-[10px] text-gray-500 uppercase font-bold">Gestionnaire du territoire</div>
          <div className="text-sm text-white font-bold">{g.nom || g.type || '—'}</div>
          {g.tel && <div className="flex items-center gap-2 text-xs text-gray-300"><Phone className="h-3 w-3 text-cyan-400" />{g.tel}</div>}
          {g.courriel && <div className="flex items-center gap-2 text-xs text-gray-300"><Mail className="h-3 w-3 text-cyan-400" />{g.courriel}</div>}
          {g.web && <div className="flex items-center gap-2 text-xs"><Globe className="h-3 w-3 text-cyan-400" /><a href={`https://${g.web}`} target="_blank" rel="noopener noreferrer" className="text-cyan-400 hover:underline">{g.web}</a></div>}
          {g.reglements && <div className="text-[10px] text-gray-400 mt-1">{g.reglements}</div>}
        </div>

        {/* Lot info for private lands */}
        {lot && (
          <div className="bg-gray-900/50 rounded-lg p-3 space-y-2">
            <div className="text-[10px] text-gray-500 uppercase font-bold">Information fonciere</div>
            <div className="text-xs text-gray-300">Lot: <span className="text-white font-mono">{lot.numero_lot}</span></div>
            <div className="text-xs text-gray-300">Cadastre: {lot.cadastre}</div>
            <a href={lot.registre_foncier} target="_blank" rel="noopener noreferrer" className="text-xs text-cyan-400 hover:underline flex items-center gap-1">
              <ExternalLink className="h-3 w-3" /> Registre foncier
            </a>
            <div className="text-xs text-amber-400 italic">{lot.proprietaire}</div>
          </div>
        )}

        <Button className="w-full bg-[#f5a623] text-black font-bold" data-testid="contact-gestionnaire-btn">
          <Phone className="h-4 w-4 mr-2" /> Contacter le gestionnaire du territoire
        </Button>
      </div>
    </div>
  );
};

/* ═══════════════════════════════════════════
   MAIN ADMIN HOTSPOTS COMPONENT
   ═══════════════════════════════════════════ */
const AdminHotspots = () => {
  const [hotspots, setHotspots] = useState([]);
  const [stats, setStats] = useState(null);
  const [bceReport, setBceReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [extractionSummary, setExtractionSummary] = useState(null);
  const [schedulerInfo, setSchedulerInfo] = useState(null);
  const [filters, setFilters] = useState({ region_id: '', species: '', category: '', classification: '', territory_type: '', access_status: '' });
  const [showFilters, setShowFilters] = useState(false);
  const [viewMode, setViewMode] = useState('map'); // 'map' or 'table'
  const [selectedHotspot, setSelectedHotspot] = useState(null);

  const fetchList = useCallback(async () => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => { if (v) params.set(k, v); });
    params.set('limit', '300');
    try {
      const res = await fetch(`${HOTSPOT_API}/list?${params}`);
      const data = await res.json();
      setHotspots(data.hotspots || []);
    } catch (e) { console.error(e); }
  }, [filters]);

  const fetchStats = useCallback(async () => {
    try {
      const res = await fetch(`${HOTSPOT_API}/stats`);
      const data = await res.json();
      setStats(data);
    } catch (e) { console.error(e); }
  }, []);

  const runScheduler = useCallback(async () => {
    setLoading(true);
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 180000); // 3 min timeout
      const res = await fetch(`${HOTSPOT_API}/scheduler/run`, { 
        method: 'POST',
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      const data = await res.json();
      setExtractionSummary(data);
      setSchedulerInfo({ last_run: data.extracted_at, next_run: data.next_scheduled, run: data.scheduler_run });
      setBceReport(data.bce4x_report);
      await fetchList();
      await fetchStats();
    } catch (e) {
      // Si timeout proxy, re-fetch les donnees (extraction a probablement reussi cote serveur)
      console.warn('Extraction timeout, fetching results...', e);
      setTimeout(async () => {
        await fetchList();
        await fetchStats();
        setLoading(false);
      }, 5000);
      return;
    }
    finally { setLoading(false); }
  }, [fetchList, fetchStats]);

  const fetchBceReport = useCallback(async () => {
    try { const r = await fetch(`${HOTSPOT_API}/report/bce4x`); setBceReport(await r.json()); } catch (e) { console.error(e); }
  }, []);

  const exportFile = useCallback(async (type) => {
    try {
      const res = await fetch(`${HOTSPOT_API}/export/${type}`);
      const data = await res.json();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a'); a.href = url;
      a.download = `hotspots_bionic_v6_${new Date().toISOString().slice(0, 10)}.${type === 'geojson' ? 'geojson' : 'json'}`;
      a.click(); URL.revokeObjectURL(url);
    } catch (e) { console.error(e); }
  }, []);

  /* Chargement automatique au montage */
  useEffect(() => {
    fetchList();
    fetchStats();
    fetchBceReport();
  }, [fetchList, fetchStats, fetchBceReport]);

  return (
    <div className="space-y-5" data-testid="admin-hotspots-section">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <MapPin className="h-5 w-5 text-[#f5a623]" /> Hotspots BIONIC V7.2 — Source de Verite
          </h2>
          <p className="text-sm text-gray-400 mt-1">Terrain-aware + Ecologie + Dispersion 1.5km + Exclusion eau embarquee</p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          {/* V7.2: Legende gradient BIONIC */}
          <div className="flex items-center gap-1 mr-2 bg-gray-900/50 rounded-lg px-2 py-1 border border-gray-700/30" data-testid="bionic-gradient-legend">
            <span className="text-[9px] text-gray-500 mr-1">GRADIENT:</span>
            <span className="w-3 h-3 rounded-full bg-emerald-500" title="80-100%" />
            <span className="w-3 h-3 rounded-full bg-yellow-500" title="60-80%" />
            <span className="w-3 h-3 rounded-full bg-orange-500" title="40-60%" />
            <span className="w-3 h-3 rounded-full bg-red-500" title="<40%" />
          </div>
          <Button onClick={runScheduler} disabled={loading} className="bg-[#f5a623] hover:bg-[#f5a623]/90 text-black font-bold" data-testid="extract-all-btn">
            {loading ? <RefreshCw className="h-4 w-4 animate-spin mr-2" /> : <RefreshCw className="h-4 w-4 mr-2" />}
            {loading ? 'Extraction...' : 'Extraction annuelle'}
          </Button>
        </div>
      </div>

      {/* Scheduler + BCE Status */}
      {(schedulerInfo || bceReport) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {schedulerInfo && (
            <div className="bg-gray-900/50 border border-gray-700/30 rounded-lg p-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-[#f5a623]" />
                <span className="text-xs text-gray-300">Scheduler annuel — Run #{schedulerInfo.run}</span>
              </div>
              <span className="text-[10px] text-gray-500 font-mono" data-testid="scheduler-next-run">Prochain: {schedulerInfo.next_run?.slice(0, 10)}</span>
            </div>
          )}
          {bceReport && (
            <div className={`border rounded-lg p-3 flex items-center justify-between ${bceReport.overall === 'PASS' ? 'border-green-500/30 bg-green-500/5' : 'border-red-500/30 bg-red-500/5'}`} data-testid="bce-report-panel">
              <div className="flex items-center gap-2">
                <Shield className={`h-4 w-4 ${bceReport.overall === 'PASS' ? 'text-green-400' : 'text-red-400'}`} />
                <span className="text-xs text-gray-300">BCE-4X</span>
              </div>
              <Badge className={bceReport.overall === 'PASS' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'}>
                {bceReport.overall} — {bceReport.passed}/{bceReport.total_checks}
              </Badge>
            </div>
          )}
        </div>
      )}

      {/* Extraction Summary Cards */}
      {extractionSummary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3" data-testid="extraction-summary">
          <div className="bg-gray-900/50 border border-gray-700/30 rounded-lg p-3 text-center">
            <div className="text-2xl font-black text-white" data-testid="total-hotspots">{extractionSummary.total_hotspots}</div>
            <div className="text-[10px] text-gray-400">Hotspots totaux</div>
          </div>
          <div className="bg-gray-900/50 border border-gray-700/30 rounded-lg p-3 text-center">
            <div className="text-2xl font-black text-[#f5a623]">{extractionSummary.total_regions}</div>
            <div className="text-[10px] text-gray-400">Regions</div>
          </div>
          <div className="bg-gray-900/50 border border-gray-700/30 rounded-lg p-3 text-center">
            <div className="text-2xl font-black text-red-400">{extractionSummary.regions_summary?.reduce((a, r) => a + (r.majeur || 0), 0)}</div>
            <div className="text-[10px] text-gray-400">MAJEUR</div>
          </div>
          <div className="bg-gray-900/50 border border-gray-700/30 rounded-lg p-3 text-center">
            <div className="text-2xl font-black text-orange-400">{extractionSummary.regions_summary?.reduce((a, r) => a + (r.fort || 0), 0)}</div>
            <div className="text-[10px] text-gray-400">FORT</div>
          </div>
        </div>
      )}

      {/* Actions Bar */}
      <div className="flex items-center gap-2 flex-wrap">
        <div className="flex rounded-lg border border-gray-700 overflow-hidden mr-2">
          <button onClick={() => setViewMode('map')} className={`px-3 py-1.5 text-xs font-bold flex items-center gap-1.5 ${viewMode === 'map' ? 'bg-[#f5a623] text-black' : 'text-gray-400 hover:text-white'}`} data-testid="view-map-btn">
            <MapIcon className="h-3.5 w-3.5" /> Carte
          </button>
          <button onClick={() => setViewMode('table')} className={`px-3 py-1.5 text-xs font-bold flex items-center gap-1.5 ${viewMode === 'table' ? 'bg-[#f5a623] text-black' : 'text-gray-400 hover:text-white'}`} data-testid="view-table-btn">
            <List className="h-3.5 w-3.5" /> Tableau
          </button>
        </div>
        <Button variant="outline" size="sm" onClick={() => setShowFilters(!showFilters)} className="border-gray-700 text-gray-300" data-testid="toggle-filters-btn">
          <Filter className="h-3.5 w-3.5 mr-1.5" /> Filtres <ChevronDown className={`h-3 w-3 ml-1 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
        </Button>
        <Button variant="outline" size="sm" onClick={() => exportFile('geojson')} className="border-gray-700 text-gray-300" data-testid="export-geojson-btn">
          <Download className="h-3.5 w-3.5 mr-1.5" /> GeoJSON
        </Button>
        <Button variant="outline" size="sm" onClick={() => exportFile('json')} className="border-gray-700 text-gray-300" data-testid="export-json-btn">
          <Download className="h-3.5 w-3.5 mr-1.5" /> JSON
        </Button>
        <Button variant="outline" size="sm" onClick={fetchBceReport} className="border-gray-700 text-gray-300" data-testid="bce-report-btn">
          <Shield className="h-3.5 w-3.5 mr-1.5" /> BCE-4X
        </Button>
        <Button variant="outline" size="sm" onClick={fetchStats} className="border-gray-700 text-gray-300">
          <BarChart3 className="h-3.5 w-3.5 mr-1.5" /> Stats
        </Button>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="bg-gray-900/50 border border-gray-700/30 rounded-lg p-4 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3" data-testid="filters-panel">
          <div>
            <label className="text-[10px] text-gray-500 uppercase block mb-1">Region</label>
            <select value={filters.region_id} onChange={e => setFilters(p => ({ ...p, region_id: e.target.value }))} className="w-full bg-black border border-gray-700 rounded px-2 py-1.5 text-xs text-white">
              <option value="">Toutes</option>
              {['laurentides','outaouais','lanaudiere','mauricie','estrie','saguenay','capitale_nationale','chaudiere_appalaches','bas_saint_laurent','abitibi','cote_nord','gaspesie'].map(r => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>
          <div>
            <label className="text-[10px] text-gray-500 uppercase block mb-1">Espece</label>
            <select value={filters.species} onChange={e => setFilters(p => ({ ...p, species: e.target.value }))} className="w-full bg-black border border-gray-700 rounded px-2 py-1.5 text-xs text-white">
              <option value="">Toutes</option>
              <option value="orignal">Orignal</option><option value="chevreuil">Chevreuil</option><option value="ours_noir">Ours noir</option><option value="dindon_sauvage">Dindon sauvage</option>
            </select>
          </div>
          <div>
            <label className="text-[10px] text-gray-500 uppercase block mb-1">Classification</label>
            <select value={filters.classification} onChange={e => setFilters(p => ({ ...p, classification: e.target.value }))} className="w-full bg-black border border-gray-700 rounded px-2 py-1.5 text-xs text-white">
              <option value="">Toutes</option><option value="MAJEUR">MAJEUR (80+)</option><option value="FORT">FORT (60-79)</option>
            </select>
          </div>
          <div>
            <label className="text-[10px] text-gray-500 uppercase block mb-1">Type territoire</label>
            <select value={filters.territory_type} onChange={e => setFilters(p => ({ ...p, territory_type: e.target.value }))} className="w-full bg-black border border-gray-700 rounded px-2 py-1.5 text-xs text-white">
              <option value="">Tous</option>
              {['Prive','Public','Gouvernemental','ZEC','Pourvoirie','Reserve faunique','Territoire autochtone'].map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div>
            <label className="text-[10px] text-gray-500 uppercase block mb-1">Acces</label>
            <select value={filters.access_status} onChange={e => setFilters(p => ({ ...p, access_status: e.target.value }))} className="w-full bg-black border border-gray-700 rounded px-2 py-1.5 text-xs text-white">
              <option value="">Tous</option>
              {['Libre','Restreint','Payant','Permission requise'].map(a => <option key={a} value={a}>{a}</option>)}
            </select>
          </div>
          <div>
            <label className="text-[10px] text-gray-500 uppercase block mb-1">Categorie</label>
            <select value={filters.category} onChange={e => setFilters(p => ({ ...p, category: e.target.value }))} className="w-full bg-black border border-gray-700 rounded px-2 py-1.5 text-xs text-white">
              <option value="">Toutes</option>
              {['alimentation','repos','rut','deplacement','corridors','multi_engines','pression_faible'].map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <Button size="sm" onClick={fetchList} className="bg-[#f5a623] text-black font-bold col-span-2 md:col-span-3 lg:col-span-6" data-testid="apply-filters-btn">Appliquer</Button>
        </div>
      )}

      {/* Stats row */}
      {stats && stats.total_hotspots > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3" data-testid="hotspot-stats">
          <div className="bg-gray-900/50 border border-gray-700/30 rounded-lg p-3">
            <div className="text-[10px] text-gray-500 uppercase mb-1">Score moyen</div>
            <div className="text-xl font-bold text-white">{stats.score_avg}</div>
          </div>
          <div className="bg-gray-900/50 border border-gray-700/30 rounded-lg p-3">
            <div className="text-[10px] text-gray-500 uppercase mb-1">Score max</div>
            <div className="text-xl font-bold text-green-400">{stats.score_max}</div>
          </div>
          <div className="bg-gray-900/50 border border-gray-700/30 rounded-lg p-3">
            <div className="text-[10px] text-gray-500 uppercase mb-1">Par espece</div>
            <div className="space-y-0.5">{Object.entries(stats.by_species || {}).slice(0, 4).map(([sp, c]) => <div key={sp} className="flex justify-between text-[10px]"><span className="text-gray-400">{sp}</span><span className="text-white font-bold">{c}</span></div>)}</div>
          </div>
          <div className="bg-gray-900/50 border border-gray-700/30 rounded-lg p-3">
            <div className="text-[10px] text-gray-500 uppercase mb-1">Par categorie</div>
            <div className="space-y-0.5">{Object.entries(stats.by_category || {}).slice(0, 4).map(([cat, c]) => <div key={cat} className="flex justify-between text-[10px]"><span className="text-gray-400">{cat}</span><span className="text-white font-bold">{c}</span></div>)}</div>
          </div>
        </div>
      )}

      {/* MAP VIEW */}
      {viewMode === 'map' && hotspots.length > 0 && (
        <HotspotMap hotspots={hotspots} selectedRegion={filters.region_id} />
      )}

      {/* TABLE VIEW */}
      {viewMode === 'table' && hotspots.length > 0 && (
        <div className="bg-gray-900/50 border border-gray-700/30 rounded-xl overflow-hidden" data-testid="hotspots-table">
          <div className="px-4 py-3 border-b border-gray-800 flex items-center justify-between">
            <span className="text-sm font-bold text-white">{hotspots.length} hotspots</span>
          </div>
          <div className="overflow-x-auto max-h-[500px] overflow-y-auto">
            <table className="w-full text-xs">
              <thead className="bg-black/50 sticky top-0">
                <tr className="text-gray-500 uppercase tracking-wider text-[9px]">
                  <th className="px-2 py-2 text-left">ID</th>
                  <th className="px-2 py-2 text-left">Region</th>
                  <th className="px-2 py-2 text-left">Ville</th>
                  <th className="px-2 py-2 text-center">Score</th>
                  <th className="px-2 py-2 text-center">Gradient</th>
                  <th className="px-2 py-2 text-left">Espece</th>
                  <th className="px-2 py-2 text-left">Habitat</th>
                  <th className="px-2 py-2 text-left">Territoire</th>
                  <th className="px-2 py-2 text-left">Acces</th>
                  <th className="px-2 py-2 text-center">Alt.</th>
                  <th className="px-2 py-2 text-center">Intensite</th>
                  <th className="px-2 py-2 text-left">GPS</th>
                  <th className="px-2 py-2 text-center">Action</th>
                </tr>
              </thead>
              <tbody>
                {hotspots.map(h => {
                  const gradient = getGradientStyle(h.score);
                  return (
                    <tr key={h.id} className="border-t border-gray-800/50 hover:bg-white/5 transition-colors">
                      <td className="px-2 py-2 font-mono text-gray-400 text-[10px]">{h.id}</td>
                      <td className="px-2 py-2 text-gray-300">{h.region_name}</td>
                      <td className="px-2 py-2 text-gray-300">{h.ville || '—'}</td>
                      <td className="px-2 py-2 text-center"><span className="text-white font-bold">{h.score}</span></td>
                      <td className="px-2 py-2 text-center">
                        <div className="flex items-center justify-center gap-1">
                          <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: gradient.color }} />
                          <Badge className={`${gradient.bg} ${gradient.text} border ${gradient.border} text-[9px]`}>{h.classification}</Badge>
                        </div>
                      </td>
                      <td className="px-2 py-2 text-amber-400">{h.dominant_species}</td>
                      <td className="px-2 py-2 text-gray-300 text-[10px]">{h.habitat_type || '—'}</td>
                      <td className="px-2 py-2"><Badge className={`${TT_BADGES[h.territory_type] || 'bg-gray-500/20 text-gray-400'} text-[9px]`}>{h.territory_type || '—'}</Badge></td>
                      <td className="px-2 py-2 text-gray-300">{h.access_status || '—'}</td>
                      <td className="px-2 py-2 text-center text-gray-400">{h.altitude_m || '—'}m</td>
                      <td className="px-2 py-2 text-center">
                        <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold ${
                          h.intensity === 'EXTREME' ? 'bg-red-500/20 text-red-400' :
                          h.intensity === 'INTENSE' ? 'bg-orange-500/20 text-orange-400' :
                          h.intensity === 'MODERE' ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-gray-500/20 text-gray-400'
                        }`}>{h.intensity || '—'}</span>
                      </td>
                      <td className="px-2 py-2 font-mono text-[9px] text-gray-500">{h.center?.[0]?.toFixed(4)}, {h.center?.[1]?.toFixed(4)}</td>
                      <td className="px-2 py-2 text-center">
                        <div className="flex items-center justify-center gap-1.5">
                          <button onClick={() => setSelectedHotspot(h)} className="text-[10px] text-cyan-400 hover:text-cyan-300 underline" data-testid={`contact-btn-${h.id}`}>
                            Contact
                          </button>
                          <CarteButton hotspot={h} />
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Both views: show map + table below if on table mode */}
      {viewMode === 'map' && hotspots.length > 0 && (
        <div className="bg-gray-900/50 border border-gray-700/30 rounded-xl overflow-hidden" data-testid="hotspots-table-below-map">
          <div className="px-4 py-3 border-b border-gray-800">
            <span className="text-sm font-bold text-white">{hotspots.length} hotspots — Donnees territoriales V7.2</span>
          </div>
          <div className="overflow-x-auto max-h-[350px] overflow-y-auto">
            <table className="w-full text-xs">
              <thead className="bg-black/50 sticky top-0">
                <tr className="text-gray-500 uppercase tracking-wider text-[9px]">
                  <th className="px-2 py-2 text-left">ID</th>
                  <th className="px-2 py-2 text-left">Ville</th>
                  <th className="px-2 py-2 text-center">Score</th>
                  <th className="px-2 py-2 text-left">Espece</th>
                  <th className="px-2 py-2 text-left">Habitat</th>
                  <th className="px-2 py-2 text-left">Territoire</th>
                  <th className="px-2 py-2 text-left">Gestionnaire</th>
                  <th className="px-2 py-2 text-center">Intensite</th>
                  <th className="px-2 py-2 text-center">Action</th>
                </tr>
              </thead>
              <tbody>
                {hotspots.slice(0, 50).map(h => {
                  const gradient = getGradientStyle(h.score);
                  return (
                    <tr key={h.id} className="border-t border-gray-800/50 hover:bg-white/5">
                      <td className="px-2 py-1.5 font-mono text-gray-400 text-[10px]">{h.id}</td>
                      <td className="px-2 py-1.5 text-gray-300">{h.ville || '—'}</td>
                      <td className="px-2 py-1.5 text-center">
                        <span className="font-bold" style={{ color: gradient.color }}>{h.score}</span>
                      </td>
                      <td className="px-2 py-1.5 text-amber-400">{h.dominant_species}</td>
                      <td className="px-2 py-1.5 text-gray-300 text-[10px]">{h.habitat_type || '—'}</td>
                      <td className="px-2 py-1.5"><Badge className={`${TT_BADGES[h.territory_type] || 'bg-gray-500/20'} text-[9px]`}>{h.territory_type || '—'}</Badge></td>
                      <td className="px-2 py-1.5 text-gray-300 text-[10px]">{h.gestionnaire?.nom || '—'}</td>
                      <td className="px-2 py-1.5 text-center">
                        <span className={`text-[9px] px-1 py-0.5 rounded font-bold ${
                          h.intensity === 'EXTREME' ? 'bg-red-500/20 text-red-400' :
                          h.intensity === 'INTENSE' ? 'bg-orange-500/20 text-orange-400' :
                          'bg-gray-500/20 text-gray-400'
                        }`}>{h.intensity || '—'}</span>
                      </td>
                      <td className="px-2 py-1.5 text-center">
                        <div className="flex items-center justify-center gap-1.5">
                          <button onClick={() => setSelectedHotspot(h)} className="text-[10px] text-cyan-400 hover:underline">Contacter</button>
                          <CarteButton hotspot={h} />
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Empty state */}
      {hotspots.length === 0 && !loading && (
        <div className="text-center py-12 text-gray-500" data-testid="empty-state">
          <MapPin className="h-12 w-12 mx-auto mb-3 text-gray-700" />
          <p className="text-sm">Aucun hotspot extrait. Cliquez sur "Extraction annuelle" pour commencer.</p>
        </div>
      )}

      {/* Gestionnaire Panel Modal */}
      {selectedHotspot && <GestionnairePanel hotspot={selectedHotspot} onClose={() => setSelectedHotspot(null)} />}
    </div>
  );
};

export default AdminHotspots;

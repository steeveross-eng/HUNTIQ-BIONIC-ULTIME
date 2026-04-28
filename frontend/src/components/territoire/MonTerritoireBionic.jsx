/**
 * MonTerritoireBionic - Section principale pour la page d'accueil
 * BIONIC Design System compliant - No emojis
 * Affiche une carte BIONIC interactive avec aperçu des scores
 */

import React, { useState, useCallback, useMemo, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap, Polygon } from 'react-leaflet';
import { Brain, Map, Crosshair, Wind, Thermometer, Droplets, TrendingUp, 
         ChevronRight, Layers, Activity, Target, Navigation, 
         Sun, Moon, ArrowRight, Zap, Eye, EyeOff, Home, Heart, Leaf, Footprints } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import useBionicLayers from '@/hooks/useBionicLayers';
import useBionicWeather from '@/hooks/useBionicWeather';
import { BIONIC_LAYERS, getScoresForWaypoint, adaptWaypointData } from '@/core/bionic';
import { MapInteractionLayer } from '@/modules/map_interaction';
import L from 'leaflet';
import HudTerritoireUltime from './HudTerritoireUltime';

// Fix for default markers
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// BCE-4X — Affuts de demonstration pour Mon Territoire
const DEMO_AFFUTS_TYPES = {
  actuel:    { color: '#3498DB', border: '#2980B9', label: 'Affut actuel' },
  alt:       { color: '#2ECC71', border: '#27AE60', label: 'ALT' },
  a_eviter:  { color: '#E74C3C', border: '#C0392B', label: 'A EVITER' },
  propose:   { color: '#F39C12', border: '#E67E22', label: 'Propose' },
  historique:{ color: '#95A5A6', border: '#7F8C8D', label: 'Historique' },
};

const generateDemoAffuts = (centerLat, centerLng) => {
  const affuts = [];
  const types = Object.keys(DEMO_AFFUTS_TYPES);
  for (let i = 0; i < types.length; i++) {
    const angle = ((i * 72) + 15) * Math.PI / 180;
    const dist = 0.018 + i * 0.004;
    affuts.push({
      id: `affut-${types[i]}`,
      lat: centerLat + Math.sin(angle) * dist,
      lng: centerLng + Math.cos(angle) * dist,
      type: types[i],
      score: types[i] === 'a_eviter' ? 28 : types[i] === 'historique' ? 55 : 65 + i * 5,
      ...DEMO_AFFUTS_TYPES[types[i]],
    });
  }
  return affuts;
};

// BCE-4X Legend for Mon Territoire map
const MonTerritoireLegend = () => {
  const map = useMap();
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    const container = map.getContainer();
    const existing = container.querySelector('.mt-bce4x-legend');
    if (existing) existing.remove();

    const legendDiv = document.createElement('div');
    legendDiv.className = 'mt-bce4x-legend';
    legendDiv.setAttribute('data-testid', 'mon-territoire-legend');
    legendDiv.style.cssText = [
      'position:absolute', 'bottom:60px', 'left:10px', 'z-index:1000',
      'background:rgba(13,17,23,0.95)', 'border:2px solid #333', 'border-radius:10px',
      'padding:12px 14px', 'font-family:system-ui', 'font-size:13px', 'color:#ccc',
      'min-width:200px', 'max-width:240px', 'pointer-events:auto',
      'backdrop-filter:blur(12px)', 'box-shadow:0 4px 20px rgba(0,0,0,0.4)',
    ].join(';');

    const itemStyle = 'display:flex;align-items:center;gap:8px;margin:3px 0;font-size:12px;line-height:1.4';
    const sectionStyle = 'font-weight:700;font-size:10px;color:#888;margin:8px 0 3px;text-transform:uppercase;letter-spacing:0.5px';

    const contentHtml = `
      <div style="${sectionStyle}">Exclusions BCE-4X</div>
      <div style="${itemStyle}"><span style="width:12px;height:12px;background:#FF444433;border:2px solid #FF4444;display:inline-block;border-radius:3px"></span><span style="color:#FF4444;font-weight:600">Zone A EVITER</span></div>
      <div style="${itemStyle}"><span style="width:12px;height:12px;background:#FF880033;border:2px solid #FF8800;display:inline-block;border-radius:3px"></span><span style="color:#FF8800;font-weight:600">Contamination saline</span></div>
      <div style="${itemStyle}"><span style="width:12px;height:12px;background:#FFD70033;border:2px solid #FFD700;display:inline-block;border-radius:3px"></span><span style="color:#FFD700;font-weight:600">Contamination chasseur</span></div>
      <div style="${sectionStyle}">Affuts</div>
      <div style="${itemStyle}"><span style="width:12px;height:12px;border-radius:50%;background:#3498DB33;border:2px solid #3498DB;display:inline-block"></span><span style="color:#3498DB;font-weight:600">Affut actuel</span></div>
      <div style="${itemStyle}"><span style="width:12px;height:12px;border-radius:50%;background:#2ECC7133;border:2px solid #2ECC71;display:inline-block"></span><span style="color:#2ECC71;font-weight:600">Affut ALT</span></div>
      <div style="${itemStyle}"><span style="width:12px;height:12px;border-radius:50%;background:#E74C3C33;border:2px solid #E74C3C;display:inline-block"></span><span style="color:#E74C3C;font-weight:600">A eviter</span></div>
      <div style="${itemStyle}"><span style="width:12px;height:12px;border-radius:50%;background:#F39C1233;border:2px solid #F39C12;display:inline-block"></span><span style="color:#F39C12;font-weight:600">Propose</span></div>
      <div style="${itemStyle}"><span style="width:12px;height:12px;border-radius:50%;background:#95A5A633;border:2px solid #95A5A6;display:inline-block"></span><span style="color:#95A5A6;">Historique</span></div>
      <div style="${sectionStyle}">Zones</div>
      <div style="${itemStyle}"><span style="width:12px;height:12px;background:#22c55e33;border:2px solid #22c55e;display:inline-block;border-radius:3px"></span> Habitat</div>
      <div style="${itemStyle}"><span style="width:12px;height:12px;background:#e91e6333;border:2px solid #e91e63;display:inline-block;border-radius:3px"></span> Rut</div>
      <div style="${itemStyle}"><span style="width:12px;height:12px;background:#ff572233;border:2px solid #ff5722;display:inline-block;border-radius:3px"></span> Corridor</div>
      <div style="margin-top:8px;font-size:10px;color:#555;border-top:1px solid #333;padding-top:6px">BCE-4X GOLDEN V6+ | STEEVE-MAX</div>
    `;

    legendDiv.innerHTML = `
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;border-bottom:2px solid #333;padding-bottom:5px;">
        <span style="font-weight:700;font-size:14px;color:#fff">BCE-4X — Legende</span>
        <button data-testid="mt-legend-toggle-btn" class="mt-legend-toggle" style="
          background:rgba(255,255,255,0.08);border:1px solid #555;color:#aaa;
          font-size:14px;font-weight:700;width:26px;height:26px;border-radius:6px;
          cursor:pointer;display:flex;align-items:center;justify-content:center;line-height:1;
        ">—</button>
      </div>
      <div class="mt-legend-content">${contentHtml}</div>
    `;

    setTimeout(() => {
      const toggleBtn = legendDiv.querySelector('.mt-legend-toggle');
      const contentDiv = legendDiv.querySelector('.mt-legend-content');
      if (toggleBtn && contentDiv) {
        toggleBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          const isHidden = contentDiv.style.display === 'none';
          contentDiv.style.display = isHidden ? 'block' : 'none';
          toggleBtn.textContent = isHidden ? '—' : '+';
        });
      }
    }, 50);

    container.appendChild(legendDiv);
    return () => {
      try { container.removeChild(legendDiv); } catch (_) {}
    };
  }, [map]);

  return null;
};

// Composant pour centrer la carte
const MapController = ({ center }) => {
  const map = useMap();
  useEffect(() => {
    if (center) {
      map.setView(center, 11);
    }
  }, [center, map]);
  return null;
};

// Génère des zones de démonstration
const generateDemoZones = (centerLat, centerLng) => {
  const zones = [];
  const categories = ['habitat', 'rut', 'affut', 'corridor'];
  const colors = {
    habitat: '#22c55e',
    rut: '#e91e63',
    affut: '#9c27b0',
    corridor: '#ff5722'
  };
  
  // Générer quelques zones hexagonales
  for (let i = 0; i < 12; i++) {
    const angle = (i * 30) * Math.PI / 180;
    const distance = 0.02 + (i * 0.0025);
    const lat = centerLat + Math.sin(angle) * distance;
    const lng = centerLng + Math.cos(angle) * distance;
    const category = categories[i % 4];
    const score = 55 + (i * 3);
    
    // Créer un hexagone
    const hexPoints = [];
    for (let j = 0; j < 6; j++) {
      const hexAngle = (j * 60 - 30) * Math.PI / 180;
      const size = 0.008;
      hexPoints.push([
        lat + Math.sin(hexAngle) * size,
        lng + Math.cos(hexAngle) * size * 1.2
      ]);
    }
    
    zones.push({
      id: `zone-${i}`,
      positions: hexPoints,
      category,
      color: colors[category],
      score,
      label: category === 'habitat' ? 'Habitat optimal' :
             category === 'rut' ? 'Zone de rut' :
             category === 'affut' ? 'Affût potentiel' : 'Corridor'
    });
  }
  
  return zones;
};

const MonTerritoireBionic = ({ onNavigateToTerritory }) => {
  // Position par défaut (Québec)
  const [mapCenter] = useState([46.8139, -71.2080]);
  const [selectedZone, setSelectedZone] = useState(null);
  const [showLayers, setShowLayers] = useState(true);
  
  // Hooks BIONIC
  const { 
    layersVisible, 
    toggleLayer, 
    showAllLayers, 
    hideAllLayers,
    activeCount 
  } = useBionicLayers({ habitats: true, affuts: true, corridors: true });
  
  const { 
    weather, 
    isLoading: weatherLoading,
    temperature,
    windInfo,
    huntingScore,
    nextOptimalWindow
  } = useBionicWeather(mapCenter[0], mapCenter[1], { autoFetch: true });
  
  // Zones de démonstration
  const demoZones = useMemo(() => generateDemoZones(mapCenter[0], mapCenter[1]), [mapCenter]);
  
  // Affuts de demonstration BCE-4X
  const demoAffuts = useMemo(() => generateDemoAffuts(mapCenter[0], mapCenter[1]), [mapCenter]);
  
  // Score global — BCE-4X P0 FIX: source V3 deterministe (plus de Math.random())
  const globalScore = useMemo(() => {
    if (huntingScore && huntingScore > 0) return Math.round(huntingScore);
    return 0;
  }, [huntingScore]);
  
  // Obtenir la classification du score
  const getScoreRating = (score) => {
    if (!score || score === 0) return { label: 'En attente', color: 'bg-gray-500' };
    if (score >= 80) return { label: 'Excellent', color: 'bg-green-500' };
    if (score >= 65) return { label: 'Très bon', color: 'bg-lime-500' };
    if (score >= 50) return { label: 'Bon', color: 'bg-yellow-500' };
    return { label: 'Modéré', color: 'bg-orange-500' };
  };
  
  const rating = getScoreRating(globalScore);
  
  return (
    <section 
      className="relative py-16 bg-gradient-to-b from-black via-gray-900 to-black overflow-hidden"
      data-testid="mon-territoire-bionic-section"
    >
      {/* Background effects */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmNWE2MjMiIGZpbGwtb3BhY2l0eT0iMC4wMyI+PHBhdGggZD0iTTM2IDM0djItSDI0di0yaDEyek0zNiAyNHYySDI0di0yaDEyeiIvPjwvZz48L2c+PC9zdmc+')] opacity-30"></div>
      
      <div className="container mx-auto px-4 relative z-10">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 bg-[#f5a623]/10 border border-[#f5a623]/30 rounded-full px-4 py-2 mb-4">
            <Brain className="h-5 w-5 text-[#f5a623]" />
            <span className="text-[#f5a623] font-medium text-sm">BIONIC™ Territory Engine</span>
            <Badge variant="outline" className="text-[10px] border-green-500/50 text-green-400">LIVE</Badge>
          </div>
          
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-3">
            Mon territoire <span className="text-[#f5a623]">BIONIC™</span>
          </h2>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Analyse multi-couches ultra précise de votre territoire de chasse avec données météo en temps réel
          </p>
        </div>
        
        {/* Main Content Grid */}
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Carte BIONIC */}
          <div className="lg:col-span-2 bg-gray-900/50 rounded-2xl border border-[#f5a623]/20 overflow-hidden backdrop-blur-sm">
            {/* Carte Header */}
            <div className="p-4 border-b border-gray-800 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Map className="h-5 w-5 text-[#f5a623]" />
                <span className="text-white font-semibold">Carte BIONIC™</span>
                <Badge className="bg-[#f5a623]/20 text-[#f5a623] text-[10px]">
                  {activeCount} couches actives
                </Badge>
              </div>
              
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowLayers(!showLayers)}
                  className="text-gray-400 hover:text-white"
                >
                  {showLayers ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={showAllLayers}
                  className="text-gray-400 hover:text-white text-xs"
                >
                  Tout
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={hideAllLayers}
                  className="text-gray-400 hover:text-white text-xs"
                >
                  Aucun
                </Button>
              </div>
            </div>
            
            {/* Map Container */}
            <div className="h-[400px] relative">
              <MapContainer
                center={mapCenter}
                zoom={11}
                className="h-full w-full"
                zoomControl={false}
              >
                <TileLayer
                  url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
                />
                <MapController center={mapCenter} />
                
                {/* Zones BIONIC */}
                {showLayers && demoZones.map(zone => (
                  <Polygon
                    key={zone.id}
                    positions={zone.positions}
                    pathOptions={{
                      color: zone.color,
                      fillColor: zone.color,
                      fillOpacity: selectedZone?.id === zone.id ? 0.5 : 0.25,
                      weight: selectedZone?.id === zone.id ? 3 : 1.5,
                      opacity: 0.8
                    }}
                    eventHandlers={{
                      click: () => setSelectedZone(zone),
                      mouseover: (e) => {
                        e.target.setStyle({ fillOpacity: 0.4, weight: 2 });
                      },
                      mouseout: (e) => {
                        e.target.setStyle({ 
                          fillOpacity: selectedZone?.id === zone.id ? 0.5 : 0.25, 
                          weight: selectedZone?.id === zone.id ? 3 : 1.5 
                        });
                      }
                    }}
                  >
                    <Popup>
                      <div className="text-center p-2">
                        <div className="font-bold text-sm">{zone.label}</div>
                        <div className="text-lg font-bold text-[#f5a623]">{zone.score}%</div>
                      </div>
                    </Popup>
                  </Polygon>
                ))}
                
                {/* Map Interaction Layer - Coordonnées GPS + Waypoints */}
                {/* BCE-4X PURGE V1-V5: GPS overlay uniquement */}
                <MapInteractionLayer showCoordinates={true} />
                
                {/* BCE-4X P0-K: Affuts de demonstration */}
                {showLayers && demoAffuts.map(affut => {
                  const icon = L.divIcon({
                    className: `affut-marker-${affut.type}`,
                    html: `<div data-testid="affut-marker-${affut.type}" style="
                      width:22px;height:22px;border-radius:50%;
                      background:${affut.color}33;border:2.5px solid ${affut.border};
                      display:flex;align-items:center;justify-content:center;
                      box-shadow:0 0 8px ${affut.color}66;
                    ">
                      <div style="width:7px;height:7px;border-radius:50%;background:${affut.color}"></div>
                      <div style="position:absolute;top:-18px;left:50%;transform:translateX(-50%);
                        background:#0d1117;border:1px solid ${affut.border};border-radius:3px;
                        padding:1px 5px;white-space:nowrap;font-size:11px;font-weight:700;color:${affut.color};
                      ">${affut.label} ${affut.score}</div>
                    </div>`,
                    iconSize: [22, 22],
                    iconAnchor: [11, 11],
                  });
                  return (
                    <Marker key={affut.id} position={[affut.lat, affut.lng]} icon={icon}>
                      <Popup>
                        <div className="text-center p-2" data-testid={`affut-popup-${affut.type}`}>
                          <div className="font-bold text-sm" style={{ color: affut.color }}>{affut.label}</div>
                          <div className="text-lg font-bold" style={{ color: affut.color }}>{affut.score}/100</div>
                          <div className="text-xs text-gray-500 mt-1">
                            {affut.type === 'a_eviter' ? 'Site non-conforme BCE-4X' :
                             affut.type === 'alt' ? 'Alternative SAL-ALT proposee' :
                             affut.type === 'historique' ? 'Position historique archivee' :
                             affut.type === 'propose' ? 'Recommandation SUPRA/BDRE' :
                             'Position active validee BCE-4X'}
                          </div>
                        </div>
                      </Popup>
                    </Marker>
                  );
                })}
                
                {/* BCE-4X P0-K: Legende dynamique */}
                <MonTerritoireLegend />
              </MapContainer>
              
              {/* Score Overlay */}
              <div className="absolute top-4 left-4 bg-black/80 backdrop-blur-sm rounded-xl p-3 border border-[#f5a623]/30 z-[1000]">
                <div className="text-[10px] text-gray-400 uppercase tracking-wider mb-1">Score Global</div>
                <div className="flex items-center gap-2">
                  <span className="text-2xl font-bold text-white">{globalScore}</span>
                  <span className="text-gray-400">/100</span>
                  <Badge className={`${rating.color} text-white text-[10px]`}>{rating.label}</Badge>
                </div>
              </div>
              
              {/* Weather Mini Banner */}
              {weather && (
                <div className="absolute bottom-4 left-4 right-4 bg-black/80 backdrop-blur-sm rounded-lg p-2 border border-gray-700 z-[1000]">
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-1.5">
                        <Thermometer className="h-3.5 w-3.5 text-blue-400" />
                        <span className="text-white">{Math.round(temperature)}°C</span>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <Wind className="h-3.5 w-3.5 text-gray-400" />
                        <span className="text-white">{windInfo?.direction} {Math.round(windInfo?.speed)} km/h</span>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <Activity className="h-3.5 w-3.5 text-green-400" />
                        <span className="text-white">Chasse: {huntingScore}/100</span>
                      </div>
                    </div>
                    <Badge className="bg-green-500/20 text-green-400 text-[10px]">
                      <Zap className="h-3 w-3 mr-1" /> LIVE
                    </Badge>
                  </div>
                </div>
              )}
            </div>
            
            {/* Couches Toggle */}
            <div className="p-3 border-t border-gray-800">
              <div className="flex flex-wrap gap-2">
                {BIONIC_LAYERS.slice(0, 8).map(layer => (
                  <button
                    key={layer.id}
                    onClick={() => toggleLayer(layer.id)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
                      layersVisible[layer.id]
                        ? 'bg-[#f5a623]/20 text-[#f5a623] border border-[#f5a623]/30'
                        : 'bg-gray-800 text-gray-400 border border-gray-700 hover:border-gray-600'
                    }`}
                  >
                    <span>{layer.icon}</span>
                    <span>{layer.name.replace(' potentiels', '').replace(' optimaux', '')}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
          
          {/* Panneau latéral */}
          <div className="space-y-4">
            {/* PHASE-E ACTIVATION : HUD TERRITOIRE ULTIME (production) */}
            <div data-testid="hud-ultime-prod-wrapper" className="bg-gray-900/50 rounded-2xl border border-[#00A676]/30 p-3 backdrop-blur-sm">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="inline-block w-2 h-2 bg-[#00A676] rounded-full animate-pulse"></span>
                  <span className="text-[#00A676] font-bold text-xs tracking-widest">TERRITOIRE Ω · ACTIF</span>
                </div>
                <Badge className="bg-[#00A676]/20 text-[#00A676] text-[9px] border-[#00A676]/40">
                  PHASE-E LIVE
                </Badge>
              </div>
              <HudTerritoireUltime
                lat={48.206657}
                lng={-68.382422}
                defaultSpecies="orignal"
                month={10}
                hour={14}
              />
            </div>

            {/* Score Breakdown */}
            <div className="bg-gray-900/50 rounded-2xl border border-[#f5a623]/20 p-4 backdrop-blur-sm">
              <div className="flex items-center gap-2 mb-4">
                <Target className="h-5 w-5 text-[#f5a623]" />
                <span className="text-white font-semibold">Analyse BIONIC™</span>
              </div>
              
              <div className="space-y-3">
                {[
                  { label: 'Habitat', score: 78, Icon: Home, color: 'bg-green-500' },
                  { label: 'Rut', score: 72, Icon: Heart, color: 'bg-pink-500' },
                  { label: 'Affûts', score: 85, Icon: Target, color: 'bg-purple-500' },
                  { label: 'Corridors', score: 68, Icon: Footprints, color: 'bg-orange-500' },
                  { label: 'Alimentation', score: 74, Icon: Leaf, color: 'bg-lime-500' },
                ].map((item, idx) => (
                  <div key={idx} className="flex items-center gap-3">
                    <item.Icon className="w-5 h-5 text-slate-400" />
                    <div className="flex-1">
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-gray-400">{item.label}</span>
                        <span className="text-white font-medium">{item.score}%</span>
                      </div>
                      <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
                        <div 
                          className={`h-full ${item.color} rounded-full transition-all duration-500`}
                          style={{ width: `${item.score}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            {/* Prochaine fenêtre optimale */}
            {nextOptimalWindow && (
              <div className="bg-gradient-to-br from-green-900/30 to-green-800/20 rounded-2xl border border-green-500/30 p-4">
                <div className="flex items-center gap-2 mb-3">
                  <Sun className="h-5 w-5 text-green-400" />
                  <span className="text-green-400 font-semibold text-sm">Prochaine fenêtre optimale</span>
                </div>
                <div className="text-white">
                  <div className="text-lg font-bold">
                    {new Date(nextOptimalWindow.start).toLocaleTimeString('fr-CA', { hour: '2-digit', minute: '2-digit' })}
                    {' - '}
                    {new Date(nextOptimalWindow.end).toLocaleTimeString('fr-CA', { hour: '2-digit', minute: '2-digit' })}
                  </div>
                  <div className="text-xs text-green-300 mt-1">
                    Score moyen: {Math.round(nextOptimalWindow.avgScore)}/100
                  </div>
                </div>
              </div>
            )}
            
            {/* Selected Zone Info */}
            {selectedZone && (
              <div className="bg-gray-900/50 rounded-2xl border border-[#f5a623]/20 p-4 backdrop-blur-sm">
                <div className="flex items-center gap-2 mb-3">
                  <div 
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: selectedZone.color }}
                  />
                  <span className="text-white font-semibold">{selectedZone.label}</span>
                </div>
                <div className="text-3xl font-bold text-[#f5a623] mb-2">{selectedZone.score}%</div>
                <p className="text-gray-400 text-sm mb-3">
                  Zone à fort potentiel identifiée par l'analyse multi-couches BIONIC™
                </p>
                <Button 
                  className="w-full bg-[#f5a623] hover:bg-[#f5a623]/90 text-black font-medium"
                  onClick={onNavigateToTerritory}
                >
                  <Navigation className="h-4 w-4 mr-2" />
                  Analyser en détail
                </Button>
              </div>
            )}
            
            {/* CTA */}
            <div className="bg-gradient-to-br from-[#f5a623]/20 to-orange-600/10 rounded-2xl border border-[#f5a623]/30 p-4">
              <div className="text-white font-semibold mb-2">Accéder à la Carte BIONIC™ complète</div>
              <p className="text-gray-400 text-sm mb-4">
                15 couches d'analyse • Météo LIVE • Stratégie temps réel • IA prédictive
              </p>
              <Button 
                className="w-full bg-[#f5a623] hover:bg-[#f5a623]/90 text-black font-medium group"
                onClick={onNavigateToTerritory}
              >
                Explorer mon territoire
                <ChevronRight className="h-4 w-4 ml-2 group-hover:translate-x-1 transition-transform" />
              </Button>
            </div>
          </div>
        </div>
        
        {/* Features Grid */}
        <div className="grid md:grid-cols-4 gap-4 mt-8">
          {[
            { icon: Layers, label: '15 couches', desc: 'Analyse multi-critères' },
            { icon: Wind, label: 'Météo LIVE', desc: 'Données en temps réel' },
            { icon: Brain, label: 'IA Hybride', desc: 'Règles + Machine Learning' },
            { icon: Target, label: 'Stratégie', desc: 'Recommandations tactiques' },
          ].map((feature, idx) => (
            <div 
              key={idx}
              className="bg-gray-900/30 rounded-xl border border-gray-800 p-4 text-center hover:border-[#f5a623]/30 transition-colors"
            >
              <feature.icon className="h-8 w-8 text-[#f5a623] mx-auto mb-2" />
              <div className="text-white font-semibold text-sm">{feature.label}</div>
              <div className="text-gray-500 text-xs">{feature.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default MonTerritoireBionic;

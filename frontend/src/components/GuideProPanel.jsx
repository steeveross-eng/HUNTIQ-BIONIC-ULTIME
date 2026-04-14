/**
 * GuideProPanel — GUIDE-PRO-Omega UI Integration
 * Panneau lateral GUIDE PRO pour CARTE.
 * Modes: LIVE (secteur visible), POINT (point selectionne), ZONE (analyse secteur), ESPECE ACTIVE
 * Connecte aux 15 endpoints /api/v1/guide-pro + P1 engines.
 */
import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useAuth } from '@/components/GlobalAuth';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Compass, MapPin, Crosshair, Radar, X, Loader2, ChevronDown, ChevronUp,
  Target, Eye, Thermometer, Wind, TreePine, Camera, Brain, Shield
} from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const MODES = [
  { id: 'live', label: 'LIVE', icon: Radar, color: '#10B981', desc: 'Analyse continue du secteur' },
  { id: 'point', label: 'POINT', icon: MapPin, color: '#F59E0B', desc: 'Analyse du point selectionne' },
  { id: 'zone', label: 'ZONE', icon: Target, color: '#8B5CF6', desc: 'Analyse de zone elargie' },
  { id: 'espece', label: 'ESPECE', icon: Eye, color: '#3B82F6', desc: 'Multi-especes actif' },
];

const GuideProPanel = ({ isOpen, onClose, mapCenter, selectedSpecies }) => {
  const { token } = useAuth();
  const [activeMode, setActiveMode] = useState('live');
  const [loading, setLoading] = useState(false);
  const [guideData, setGuideData] = useState(null);
  const [optimData, setOptimData] = useState(null);
  const [terrainData, setTerrainData] = useState(null);
  const [predictData, setPredictData] = useState(null);
  const [ecoData, setEcoData] = useState(null);
  const [expandedSection, setExpandedSection] = useState('overview');

  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const lat = mapCenter?.lat || 47.5;
  const lon = mapCenter?.lng || -71.8;
  const species = selectedSpecies || 'cerf';

  const loadGuideData = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const [optimRes, terrainRes, predictRes, ecoRes] = await Promise.all([
        axios.get(`${API}/v1/p1/optimization/score?lat=${lat}&lon=${lon}&species=${species}&season=pre_rut`, { headers }).catch(() => null),
        axios.get(`${API}/v1/critical/lidar-fusion/analyze?lat=${lat}&lon=${lon}&species=${species}`, { headers }).catch(() => null),
        axios.get(`${API}/v1/p1/predict/behavior?species=${species}&season=pre_rut&hour=${new Date().getHours()}&month=${new Date().getMonth() + 1}`, { headers }).catch(() => null),
        axios.get(`${API}/v1/p1/eco-dynamics/status?lat=${lat}&lon=${lon}&species=${species}&month=${new Date().getMonth() + 1}`, { headers }).catch(() => null),
      ]);

      if (optimRes) setOptimData(optimRes.data);
      if (terrainRes) setTerrainData(terrainRes.data);
      if (predictRes) setPredictData(predictRes.data);
      if (ecoRes) setEcoData(ecoRes.data);

      // Guide-Pro health
      const guideRes = await axios.get(`${API}/v1/guide-pro/health`).catch(() => null);
      if (guideRes) setGuideData(guideRes.data);
    } catch (err) {
      console.error('Guide Pro data error:', err);
    } finally {
      setLoading(false);
    }
  }, [token, lat, lon, species, headers]);

  useEffect(() => {
    if (isOpen) loadGuideData();
  }, [isOpen, loadGuideData]);

  if (!isOpen) return null;

  const toggleSection = (s) => setExpandedSection(expandedSection === s ? null : s);
  const scoreColor = (s) => s >= 70 ? '#10B981' : s >= 40 ? '#F59E0B' : '#EF4444';

  return (
    <div className="absolute top-4 left-4 z-[1000] w-72 bg-gray-950/95 backdrop-blur-md rounded-xl border border-emerald-500/30 shadow-2xl overflow-hidden"
      data-testid="guide-pro-panel">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 bg-emerald-500/10 border-b border-emerald-500/20">
        <div className="flex items-center gap-2">
          <Compass className="h-4 w-4 text-emerald-400" />
          <span className="text-xs font-bold text-white">GUIDE PRO</span>
          <Badge className="bg-emerald-500/20 text-emerald-400 text-[8px] px-1">LIVE</Badge>
        </div>
        <button onClick={onClose} className="text-gray-400 hover:text-white" data-testid="guide-pro-close">
          <X className="h-3.5 w-3.5" />
        </button>
      </div>

      {/* Mode selector */}
      <div className="flex gap-1 p-2 border-b border-gray-800">
        {MODES.map(mode => (
          <button key={mode.id}
            onClick={() => setActiveMode(mode.id)}
            className={`flex-1 flex flex-col items-center gap-0.5 py-1.5 rounded text-[9px] font-bold transition-all ${
              activeMode === mode.id
                ? 'text-white' : 'text-gray-500 hover:text-gray-300'
            }`}
            style={{ backgroundColor: activeMode === mode.id ? `${mode.color}20` : 'transparent' }}
            data-testid={`guide-mode-${mode.id}`}
          >
            <mode.icon className="h-3 w-3" style={{ color: activeMode === mode.id ? mode.color : undefined }} />
            {mode.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="p-2 space-y-2 max-h-[55vh] overflow-y-auto">
        {loading ? (
          <div className="flex justify-center py-6">
            <Loader2 className="h-5 w-5 animate-spin text-emerald-400" />
          </div>
        ) : (
          <>
            {/* OVERVIEW SECTION */}
            <div className="rounded-lg overflow-hidden" data-testid="guide-section-overview">
              <button onClick={() => toggleSection('overview')}
                className="w-full flex items-center justify-between px-2 py-1.5 bg-gray-900/50 hover:bg-gray-800/50">
                <div className="flex items-center gap-1.5">
                  <Brain className="h-3 w-3 text-emerald-400" />
                  <span className="text-[10px] font-bold text-white">Score Optimisation</span>
                </div>
                {expandedSection === 'overview' ? <ChevronUp className="h-3 w-3 text-gray-500" /> : <ChevronDown className="h-3 w-3 text-gray-500" />}
              </button>
              {expandedSection === 'overview' && optimData && (
                <div className="p-2 bg-gray-900/30 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] text-gray-400">Score global</span>
                    <span className="text-lg font-black" style={{ color: scoreColor(optimData.global_score) }}>
                      {optimData.global_score}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-1">
                    {Object.entries(optimData.scores_detail || {}).slice(0, 6).map(([k, v]) => (
                      <div key={k} className="flex items-center justify-between text-[9px] px-1 py-0.5 rounded bg-gray-800/30">
                        <span className="text-gray-500 truncate">{k.replace(/_/g, ' ')}</span>
                        <span className="font-bold" style={{ color: scoreColor(v) }}>{v}</span>
                      </div>
                    ))}
                  </div>
                  {optimData.data_sources && (
                    <div className="text-[9px] text-gray-500 mt-1">
                      Sources: {optimData.data_sources.cameras} cam, {optimData.data_sources.hotspots} hotspots, {optimData.data_sources.affuts_ia} affuts
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* TERRAIN SECTION */}
            <div className="rounded-lg overflow-hidden" data-testid="guide-section-terrain">
              <button onClick={() => toggleSection('terrain')}
                className="w-full flex items-center justify-between px-2 py-1.5 bg-gray-900/50 hover:bg-gray-800/50">
                <div className="flex items-center gap-1.5">
                  <TreePine className="h-3 w-3 text-amber-400" />
                  <span className="text-[10px] font-bold text-white">Terrain & Habitat</span>
                </div>
                {expandedSection === 'terrain' ? <ChevronUp className="h-3 w-3 text-gray-500" /> : <ChevronDown className="h-3 w-3 text-gray-500" />}
              </button>
              {expandedSection === 'terrain' && terrainData && (
                <div className="p-2 bg-gray-900/30 space-y-1">
                  <div className="grid grid-cols-2 gap-1">
                    <div className="text-[9px] px-1 py-0.5 rounded bg-gray-800/30">
                      <span className="text-gray-500">Elevation</span>
                      <div className="font-bold text-white">{terrainData.terrain_fusion?.elevation_m}m</div>
                    </div>
                    <div className="text-[9px] px-1 py-0.5 rounded bg-gray-800/30">
                      <span className="text-gray-500">Pente</span>
                      <div className="font-bold text-white">{terrainData.terrain_fusion?.slope_deg} deg</div>
                    </div>
                    <div className="text-[9px] px-1 py-0.5 rounded bg-gray-800/30">
                      <span className="text-gray-500">Canopee</span>
                      <div className="font-bold text-white">{terrainData.terrain_fusion?.canopy_height_m}m</div>
                    </div>
                    <div className="text-[9px] px-1 py-0.5 rounded bg-gray-800/30">
                      <span className="text-gray-500">Densite</span>
                      <div className="font-bold text-white">{terrainData.terrain_fusion?.canopy_density_pct}%</div>
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-[9px] mt-1">
                    <span className="text-gray-500">Habitat suitability</span>
                    <span className="font-bold" style={{ color: scoreColor(terrainData.habitat_suitability * 100) }}>
                      {Math.round(terrainData.habitat_suitability * 100)}%
                    </span>
                  </div>
                  <div className="text-[9px] text-emerald-400/80 mt-0.5">{terrainData.recommendation}</div>
                </div>
              )}
            </div>

            {/* PREDICTION SECTION */}
            <div className="rounded-lg overflow-hidden" data-testid="guide-section-predict">
              <button onClick={() => toggleSection('predict')}
                className="w-full flex items-center justify-between px-2 py-1.5 bg-gray-900/50 hover:bg-gray-800/50">
                <div className="flex items-center gap-1.5">
                  <Crosshair className="h-3 w-3 text-blue-400" />
                  <span className="text-[10px] font-bold text-white">Prediction Comportement</span>
                </div>
                {expandedSection === 'predict' ? <ChevronUp className="h-3 w-3 text-gray-500" /> : <ChevronDown className="h-3 w-3 text-gray-500" />}
              </button>
              {expandedSection === 'predict' && predictData && (
                <div className="p-2 bg-gray-900/30 space-y-1">
                  <div className="flex items-center justify-between text-[9px]">
                    <span className="text-gray-500">Probabilite activite</span>
                    <span className="font-bold text-lg" style={{ color: scoreColor(predictData.activity_probability * 100) }}>
                      {Math.round(predictData.activity_probability * 100)}%
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-1">
                    <div className="text-[9px] px-1 py-0.5 rounded bg-gray-800/30">
                      <span className="text-gray-500">Pattern</span>
                      <div className="font-bold text-white">{predictData.movement_pattern}</div>
                    </div>
                    <div className="text-[9px] px-1 py-0.5 rounded bg-gray-800/30">
                      <span className="text-gray-500">Deplacement</span>
                      <div className="font-bold text-white">{predictData.avg_displacement_km}km</div>
                    </div>
                  </div>
                  <div className="text-[9px] text-gray-500">
                    Camera detections: <span className="text-amber-400 font-bold">{predictData.camera_detections}</span>
                  </div>
                </div>
              )}
            </div>

            {/* ECO SECTION */}
            <div className="rounded-lg overflow-hidden" data-testid="guide-section-eco">
              <button onClick={() => toggleSection('eco')}
                className="w-full flex items-center justify-between px-2 py-1.5 bg-gray-900/50 hover:bg-gray-800/50">
                <div className="flex items-center gap-1.5">
                  <Thermometer className="h-3 w-3 text-green-400" />
                  <span className="text-[10px] font-bold text-white">Eco-Dynamique</span>
                </div>
                {expandedSection === 'eco' ? <ChevronUp className="h-3 w-3 text-gray-500" /> : <ChevronDown className="h-3 w-3 text-gray-500" />}
              </button>
              {expandedSection === 'eco' && ecoData && (
                <div className="p-2 bg-gray-900/30 space-y-1">
                  <div className="grid grid-cols-3 gap-1">
                    <div className="text-[9px] px-1 py-1 rounded bg-gray-800/30 text-center">
                      <div className="text-gray-500">Vegetation</div>
                      <div className="font-bold text-green-400">{Math.round(ecoData.vegetation_index * 100)}%</div>
                    </div>
                    <div className="text-[9px] px-1 py-1 rounded bg-gray-800/30 text-center">
                      <div className="text-gray-500">Eau</div>
                      <div className="font-bold text-blue-400">{Math.round(ecoData.water_availability * 100)}%</div>
                    </div>
                    <div className="text-[9px] px-1 py-1 rounded bg-gray-800/30 text-center">
                      <div className="text-gray-500">Nourriture</div>
                      <div className="font-bold text-amber-400">{Math.round(ecoData.food_abundance * 100)}%</div>
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-[9px] mt-1">
                    <span className="text-gray-500">Qualite habitat</span>
                    <span className="font-bold" style={{ color: scoreColor(ecoData.habitat_quality * 100) }}>
                      {Math.round(ecoData.habitat_quality * 100)}%
                    </span>
                  </div>
                  <div className="text-[9px] text-gray-500">Saison: <span className="text-white font-bold">{ecoData.season}</span></div>
                </div>
              )}
            </div>

            {/* SECURITY SECTION */}
            <div className="rounded-lg overflow-hidden" data-testid="guide-section-security">
              <button onClick={() => toggleSection('security')}
                className="w-full flex items-center justify-between px-2 py-1.5 bg-gray-900/50 hover:bg-gray-800/50">
                <div className="flex items-center gap-1.5">
                  <Shield className="h-3 w-3 text-red-400" />
                  <span className="text-[10px] font-bold text-white">Securite & Cameras</span>
                </div>
                {expandedSection === 'security' ? <ChevronUp className="h-3 w-3 text-gray-500" /> : <ChevronDown className="h-3 w-3 text-gray-500" />}
              </button>
              {expandedSection === 'security' && optimData && (
                <div className="p-2 bg-gray-900/30 space-y-1">
                  <div className="text-[9px] text-gray-400">
                    Cameras: <span className="text-amber-400 font-bold">{optimData.data_sources?.cameras || 0}</span> |
                    Hotspots: <span className="text-purple-400 font-bold">{optimData.data_sources?.hotspots || 0}</span> |
                    Affuts: <span className="text-red-400 font-bold">{optimData.data_sources?.affuts_ia || 0}</span>
                  </div>
                </div>
              )}
            </div>
          </>
        )}
      </div>

      {/* Footer */}
      <div className="px-2 py-1.5 bg-gray-900/50 border-t border-gray-800 flex items-center justify-between">
        <span className="text-[8px] text-gray-600">GPS: {lat.toFixed(4)}, {lon.toFixed(4)}</span>
        <Button size="sm" variant="ghost" className="h-5 text-[9px] text-emerald-400 hover:text-emerald-300 px-1"
          onClick={loadGuideData} data-testid="guide-pro-refresh">
          Actualiser
        </Button>
      </div>
    </div>
  );
};

export default GuideProPanel;

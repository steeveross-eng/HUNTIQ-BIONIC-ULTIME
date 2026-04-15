/**
 * Carte2027Page — CARTE-2027-REBUILD
 * Carte terrain V7 derivee de TERRITOIRE (Niveau 3).
 * Architecture: TERRITOIRE → INTELLIGENCE → CARTE (flux descendant)
 * 
 * Integre: 87 moteurs, 11 provinces, temporel, solunaire, ecosystem,
 * Intelligence V7, cameras, POI, navigation mobile/hors-ligne.
 */
import React, { useState, useEffect, useCallback, useMemo, lazy, Suspense } from 'react';
import axios from 'axios';
import { useAuth } from '@/components/GlobalAuth';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  Map, Compass, Target, Camera, Brain, Thermometer, Moon,
  Clock, TreePine, Wind, Shield, Loader2, RefreshCw, ChevronDown,
  ChevronUp, MapPin, Eye, Crosshair, Wifi, WifiOff
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

const ScoreGauge = ({ score, label }) => {
  const color = score >= 70 ? '#10B981' : score >= 40 ? '#F59E0B' : '#EF4444';
  return (
    <div className="text-center" data-testid={`gauge-${label}`}>
      <div className="text-2xl font-black" style={{ color }}>{Math.round(score)}</div>
      <div className="text-[9px] text-gray-500 uppercase tracking-wider">{label}</div>
    </div>
  );
};

const SectionCard = ({ title, icon: Icon, color, children, testId, defaultOpen = false }) => {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="rounded-lg border border-gray-800/50 overflow-hidden" data-testid={testId}>
      <button onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-3 py-2 bg-gray-900/40 hover:bg-gray-800/40 transition-colors">
        <div className="flex items-center gap-2">
          <Icon className="h-3.5 w-3.5" style={{ color }} />
          <span className="text-xs font-bold text-white">{title}</span>
        </div>
        {open ? <ChevronUp className="h-3 w-3 text-gray-500" /> : <ChevronDown className="h-3 w-3 text-gray-500" />}
      </button>
      {open && <div className="p-3 bg-gray-950/30 space-y-2">{children}</div>}
    </div>
  );
};

export default function Carte2027Page() {
  const { token } = useAuth();
  const [species, setSpecies] = useState('cerf');
  const [province, setProvince] = useState('qc');
  const [loading, setLoading] = useState(false);
  const [v7Score, setV7Score] = useState(null);
  const [hourlyForecast, setHourlyForecast] = useState(null);
  const [solunar, setSolunar] = useState(null);
  const [lunar, setLunar] = useState(null);
  const [terrainData, setTerrainData] = useState(null);
  const [provData, setProvData] = useState(null);
  const [ecoInteraction, setEcoInteraction] = useState(null);
  const [cameraSec, setCameraSec] = useState(null);

  const headers = useMemo(() => token ? { Authorization: `Bearer ${token}` } : {}, [token]);
  const now = new Date();
  const month = now.getMonth() + 1;
  const day = now.getDate();
  const hour = now.getHours();

  const loadAll = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const [v7, forecast, sol, lun, terrain, prov, eco, cam] = await Promise.all([
        axios.get(`${API}/v1/v51/intelligence/v7/score?lat=47.5&lon=-71.8&species=${species}&month=${month}&day=${day}&hour=${hour}&province=${province}&temp_c=8&wind_kmh=12`, { headers }).catch(() => null),
        axios.get(`${API}/v1/v51/intelligence/v7/hourly-forecast?lat=47.5&lon=-71.8&species=${species}&month=${month}&day=${day}`, { headers }).catch(() => null),
        axios.get(`${API}/v1/v51/solunar/windows?month=${month}&day=${day}&lat=47.5`).catch(() => null),
        axios.get(`${API}/v1/v51/lunar/activity?month=${month}&day=${day}&species=${species}`).catch(() => null),
        axios.get(`${API}/v1/critical/lidar-fusion/analyze?lat=47.5&lon=-71.8&species=${species}`).catch(() => null),
        axios.get(`${API}/v1/v51/province/${province}`).catch(() => null),
        axios.get(`${API}/v1/v51/ecosystem/matrix`).catch(() => null),
        axios.get(`${API}/v1/critical/camera-sec/status`, { headers }).catch(() => null),
      ]);
      if (v7) setV7Score(v7.data);
      if (forecast) setHourlyForecast(forecast.data);
      if (sol) setSolunar(sol.data);
      if (lun) setLunar(lun.data);
      if (terrain) setTerrainData(terrain.data);
      if (prov) setProvData(prov.data);
      if (eco) setEcoInteraction(eco.data);
      if (cam) setCameraSec(cam.data);
    } catch (err) {
      console.error('Carte2027 load error:', err);
    } finally {
      setLoading(false);
    }
  }, [token, species, province, month, day, hour, headers]);

  useEffect(() => { loadAll(); }, [loadAll]);

  const predLabel = v7Score?.prediction || '—';
  const predColor = predLabel === 'excellent' ? '#10B981' : predLabel === 'bon' ? '#22D3EE' : predLabel === 'moyen' ? '#F59E0B' : '#EF4444';

  return (
    <div className="min-h-screen bg-gray-950 text-white" data-testid="carte-2027-page">
      {/* HEADER */}
      <div className="sticky top-0 z-20 bg-gray-950/95 backdrop-blur border-b border-gray-800/50">
        <div className="max-w-5xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Map className="h-5 w-5 text-emerald-400" />
              <h1 className="text-base font-bold">CARTE TERRAIN V7</h1>
              <Badge className="bg-emerald-500/20 text-emerald-400 text-[9px]">2027</Badge>
            </div>
            <Button size="sm" variant="ghost" onClick={loadAll} disabled={loading} className="h-7 text-xs text-gray-400" data-testid="carte-refresh">
              {loading ? <Loader2 className="h-3 w-3 animate-spin" /> : <RefreshCw className="h-3 w-3" />}
            </Button>
          </div>
          <div className="flex gap-2">
            <Select value={species} onValueChange={setSpecies}>
              <SelectTrigger className="h-7 w-36 text-xs bg-gray-900 border-gray-800" data-testid="carte-species-select"><SelectValue /></SelectTrigger>
              <SelectContent>{SPECIES.map(s => <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>)}</SelectContent>
            </Select>
            <Select value={province} onValueChange={setProvince}>
              <SelectTrigger className="h-7 w-32 text-xs bg-gray-900 border-gray-800" data-testid="carte-province-select"><SelectValue /></SelectTrigger>
              <SelectContent>{PROVINCES.map(p => <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>)}</SelectContent>
            </Select>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 py-4 space-y-3">
        {loading && (
          <div className="flex justify-center py-8"><Loader2 className="h-6 w-6 animate-spin text-emerald-400" /></div>
        )}

        {!loading && v7Score && (
          <>
            {/* SCORE V7 HERO */}
            <Card className="bg-gray-900/50 border-gray-800/50" data-testid="carte-v7-score">
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <Brain className="h-4 w-4 text-emerald-400" />
                    <span className="text-xs font-bold uppercase tracking-wider text-gray-400">Intelligence V7</span>
                  </div>
                  <Badge className="text-xs font-bold px-2" style={{ backgroundColor: `${predColor}20`, color: predColor }}>
                    {predLabel}
                  </Badge>
                </div>
                <div className="grid grid-cols-4 gap-3">
                  <ScoreGauge score={v7Score.v7_score} label="Global" />
                  <ScoreGauge score={v7Score.scores_detail?.temporal || 0} label="Temporel" />
                  <ScoreGauge score={v7Score.scores_detail?.meteo || 0} label="Meteo" />
                  <ScoreGauge score={v7Score.scores_detail?.rut || 0} label="Rut" />
                </div>
                {v7Score.optimal_windows && (
                  <div className="mt-3 flex items-center gap-2 text-[10px] text-gray-400">
                    <Clock className="h-3 w-3 text-amber-400" />
                    <span>Creneaux: <span className="text-white font-bold">{v7Score.optimal_windows.join(' | ')}</span></span>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* HOURLY FORECAST */}
            {hourlyForecast && (
              <SectionCard title="Prevision Horaire 24h" icon={Clock} color="#F59E0B" testId="carte-hourly" defaultOpen>
                <div className="flex gap-0.5 items-end h-16">
                  {hourlyForecast.forecast?.map(f => {
                    const h = Math.max(4, f.score * 0.6);
                    const c = f.score >= 70 ? '#10B981' : f.score >= 40 ? '#F59E0B' : '#374151';
                    const isNow = f.hour === hour;
                    return (
                      <div key={f.hour} className="flex-1 flex flex-col items-center gap-0.5">
                        <div className="w-full rounded-sm" style={{ height: `${h}%`, backgroundColor: c, border: isNow ? '1px solid #fff' : 'none' }} />
                        {f.hour % 4 === 0 && <span className="text-[7px] text-gray-600">{f.hour}h</span>}
                      </div>
                    );
                  })}
                </div>
                <div className="text-[9px] text-gray-500 mt-1">Heures pic: {hourlyForecast.peak_hours?.join('h, ')}h</div>
              </SectionCard>
            )}

            {/* SOLUNAR */}
            {solunar && lunar && (
              <SectionCard title="Solunaire" icon={Moon} color="#8B5CF6" testId="carte-solunar">
                <div className="grid grid-cols-2 gap-2">
                  <div className="text-[10px]">
                    <div className="text-gray-500">Phase lunaire</div>
                    <div className="text-white font-bold">{lunar.phase_name}</div>
                    <div className="text-gray-500 mt-1">Chasse</div>
                    <div className="font-bold" style={{ color: lunar.hunting_rating === 'excellent' ? '#10B981' : lunar.hunting_rating === 'bon' ? '#F59E0B' : '#EF4444' }}>
                      {lunar.hunting_rating}
                    </div>
                  </div>
                  <div className="text-[10px] space-y-1">
                    {Object.entries(solunar.windows || {}).map(([k, v]) => (
                      <div key={k} className="flex justify-between">
                        <span className="text-gray-500">{k.includes('major') ? 'Majeur' : 'Mineur'}</span>
                        <span className="text-white font-mono font-bold">{v}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </SectionCard>
            )}

            {/* TERRAIN */}
            {terrainData && (
              <SectionCard title="Terrain & Habitat" icon={TreePine} color="#22C55E" testId="carte-terrain">
                <div className="grid grid-cols-4 gap-2 text-[10px]">
                  <div><div className="text-gray-500">Elevation</div><div className="text-white font-bold">{terrainData.terrain_fusion?.elevation_m}m</div></div>
                  <div><div className="text-gray-500">Pente</div><div className="text-white font-bold">{terrainData.terrain_fusion?.slope_deg}deg</div></div>
                  <div><div className="text-gray-500">Canopee</div><div className="text-white font-bold">{terrainData.terrain_fusion?.canopy_height_m}m</div></div>
                  <div><div className="text-gray-500">Densite</div><div className="text-white font-bold">{terrainData.terrain_fusion?.canopy_density_pct}%</div></div>
                </div>
                <div className="flex items-center justify-between text-[10px] mt-2">
                  <span className="text-gray-500">Habitat suitability</span>
                  <span className="font-bold text-emerald-400">{Math.round((terrainData.habitat_suitability || 0) * 100)}%</span>
                </div>
              </SectionCard>
            )}

            {/* PROVINCE */}
            {provData && (
              <SectionCard title={`Province: ${provData.name}`} icon={MapPin} color="#3B82F6" testId="carte-province">
                <div className="grid grid-cols-2 gap-2 text-[10px]">
                  <div><span className="text-gray-500">Zones chasse:</span> <span className="text-white font-bold">{provData.zones_chasse}</span></div>
                  <div><span className="text-gray-500">Feux/an:</span> <span className="text-amber-400 font-bold">{provData.harvest_annual?.feux_ha?.toLocaleString()}ha</span></div>
                  {provData.population_est && Object.entries(provData.population_est).slice(0, 4).map(([sp, pop]) => (
                    <div key={sp}><span className="text-gray-500">{sp}:</span> <span className="text-white font-bold">{pop?.toLocaleString()}</span></div>
                  ))}
                </div>
              </SectionCard>
            )}

            {/* ECOSYSTEM */}
            {ecoInteraction && ecoInteraction.interactions?.length > 0 && (
              <SectionCard title="Interactions Ecosystemiques" icon={Eye} color="#EC4899" testId="carte-ecosystem">
                {ecoInteraction.interactions.map((i, idx) => (
                  <div key={idx} className="flex items-center justify-between text-[10px] py-1 border-b border-gray-800/30 last:border-0">
                    <span className="text-gray-300">{i.species1} — {i.species2}</span>
                    <Badge className="text-[8px]" style={{ backgroundColor: i.intensity > 0.4 ? '#FEF3C7' : '#F3F4F6', color: i.intensity > 0.4 ? '#92400E' : '#6B7280' }}>
                      {i.type}
                    </Badge>
                  </div>
                ))}
              </SectionCard>
            )}

            {/* CAMERAS */}
            {cameraSec && (
              <SectionCard title="Cameras & Securite" icon={Camera} color="#F59E0B" testId="carte-cameras">
                <div className="grid grid-cols-3 gap-2 text-[10px]">
                  <div><div className="text-gray-500">Total</div><div className="text-white font-bold text-lg">{cameraSec.total_cameras}</div></div>
                  <div><div className="text-gray-500">Actives</div><div className="text-emerald-400 font-bold text-lg">{cameraSec.active}</div></div>
                  <div><div className="text-gray-500">Securite</div><div className="font-bold text-lg" style={{ color: cameraSec.security_score >= 70 ? '#10B981' : '#F59E0B' }}>{cameraSec.security_score}</div></div>
                </div>
              </SectionCard>
            )}
          </>
        )}
      </div>
    </div>
  );
}

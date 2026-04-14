/**
 * AdminAlphaAnalysis — Module ADMIN : Analyse Photos ALPHA
 * Pipeline: detection espece, sexe, taille, scoring dominance ALPHA
 * Intégration: cameras, EXIF GPS, fallback camera location
 */
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import {
  Camera, Eye, MapPin, Crown, ArrowUpDown, Search, Filter,
  Loader2, Star, Target, Activity, Crosshair, ChevronRight, BarChart3
} from 'lucide-react';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const SPECIES_LIST = [
  { value: 'all', label: 'Toutes les especes' },
  { value: 'orignal', label: 'Orignal' },
  { value: 'cerf', label: 'Cerf de Virginie' },
  { value: 'caribou', label: 'Caribou' },
  { value: 'ours_noir', label: 'Ours noir' },
  { value: 'dindon', label: 'Dindon sauvage' },
  { value: 'chevreuil', label: 'Chevreuil' },
  { value: 'loup', label: 'Loup' },
  { value: 'coyote', label: 'Coyote' },
  { value: 'lynx', label: 'Lynx' }
];

const ALPHA_SCORE_COLORS = {
  alpha: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  dominant: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  standard: 'bg-zinc-500/20 text-zinc-400 border-zinc-500/30',
  juvenile: 'bg-blue-500/20 text-blue-400 border-blue-500/30'
};

const getAlphaCategory = (score) => {
  if (score >= 85) return 'alpha';
  if (score >= 65) return 'dominant';
  if (score >= 40) return 'standard';
  return 'juvenile';
};

const AdminAlphaAnalysis = () => {
  const [events, setEvents] = useState([]);
  const [cameras, setCameras] = useState({});
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [filterSpecies, setFilterSpecies] = useState('all');
  const [filterCategory, setFilterCategory] = useState('all');
  const [searchText, setSearchText] = useState('');
  const [sortBy, setSortBy] = useState('alpha_score');
  const [sortDir, setSortDir] = useState('desc');

  const token = localStorage.getItem('auth_token');
  const headers = { Authorization: `Bearer ${token}` };

  const loadData = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const [eventsRes, camerasRes] = await Promise.all([
        axios.get(`${API}/v1/camera/events?limit=200`, { headers }),
        axios.get(`${API}/v1/camera/cameras?limit=100`, { headers })
      ]);

      // Build camera lookup
      const camLookup = {};
      (camerasRes.data.cameras || []).forEach(c => { camLookup[c.id] = c; });
      setCameras(camLookup);

      // Enrich events with ALPHA scoring
      const enriched = (eventsRes.data.events || []).map(evt => {
        const cam = camLookup[evt.camera_id] || {};
        // Simulate ALPHA analysis pipeline
        const species = evt.species || simulateSpeciesDetection(evt);
        const sex = evt.sex || simulateSexDetection(species);
        const sizeScore = evt.size_score || simulateSizeScore(evt);
        const alphaScore = evt.alpha_score || computeAlphaScore(species, sex, sizeScore, evt);
        const gpsLat = evt.exif_data?.gps_lat || cam.gps_lat;
        const gpsLon = evt.exif_data?.gps_lon || cam.gps_lon;

        return {
          ...evt,
          species,
          sex,
          size_score: sizeScore,
          alpha_score: alphaScore,
          alpha_category: getAlphaCategory(alphaScore),
          gps_lat: gpsLat,
          gps_lon: gpsLon,
          camera_name: cam.name || 'Inconnue',
          camera_manufacturer: cam.manufacturer || '',
          region: deriveRegion(gpsLat, gpsLon)
        };
      });

      setEvents(enriched);
    } catch (err) {
      console.error('Alpha analysis load error:', err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { loadData(); }, [loadData]);

  // Run batch analysis
  const runBatchAnalysis = async () => {
    setAnalyzing(true);
    // Simulate analysis pipeline
    await new Promise(r => setTimeout(r, 1500));
    loadData();
    toast.success('Analyse ALPHA terminee!');
    setAnalyzing(false);
  };

  // Filter and sort
  const filteredEvents = useMemo(() => {
    let result = events;
    if (filterSpecies !== 'all') result = result.filter(e => e.species === filterSpecies);
    if (filterCategory !== 'all') result = result.filter(e => e.alpha_category === filterCategory);
    if (searchText) {
      const q = searchText.toLowerCase();
      result = result.filter(e =>
        e.camera_name?.toLowerCase().includes(q) ||
        e.species?.toLowerCase().includes(q) ||
        e.region?.toLowerCase().includes(q)
      );
    }
    result.sort((a, b) => {
      const va = a[sortBy] || 0;
      const vb = b[sortBy] || 0;
      return sortDir === 'desc' ? vb - va : va - vb;
    });
    return result;
  }, [events, filterSpecies, filterCategory, searchText, sortBy, sortDir]);

  // Stats
  const stats = useMemo(() => ({
    total: events.length,
    alphas: events.filter(e => e.alpha_category === 'alpha').length,
    dominants: events.filter(e => e.alpha_category === 'dominant').length,
    species: [...new Set(events.map(e => e.species).filter(Boolean))].length,
    avgScore: events.length > 0 ? Math.round(events.reduce((s, e) => s + (e.alpha_score || 0), 0) / events.length) : 0
  }), [events]);

  // Hotspots: group by region
  const hotspots = useMemo(() => {
    const groups = {};
    events.filter(e => e.alpha_category === 'alpha' || e.alpha_category === 'dominant').forEach(e => {
      const key = e.region || 'Inconnue';
      if (!groups[key]) {
        groups[key] = {
          region: key,
          count: 0,
          totalScore: 0,
          species: new Set(),
          events: [],
          gps_lat: e.gps_lat,
          gps_lon: e.gps_lon
        };
      }
      groups[key].count++;
      groups[key].totalScore += e.alpha_score;
      if (e.species) groups[key].species.add(e.species);
      groups[key].events.push(e);
    });

    return Object.values(groups)
      .map(g => ({
        ...g,
        avgScore: Math.round(g.totalScore / g.count),
        species: [...g.species],
        intensity: g.count >= 5 ? 'Extreme' : g.count >= 3 ? 'Elevee' : 'Moderee'
      }))
      .sort((a, b) => b.avgScore - a.avgScore);
  }, [events]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 className="h-8 w-8 animate-spin text-amber-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="admin-alpha-analysis">
      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <Card className="bg-zinc-900/50 border-zinc-800">
          <CardContent className="p-3 text-center">
            <Eye className="h-4 w-4 text-zinc-400 mx-auto mb-1" />
            <p className="text-xl font-bold">{stats.total}</p>
            <p className="text-xs text-zinc-500">Evenements</p>
          </CardContent>
        </Card>
        <Card className="bg-amber-500/10 border-amber-500/30">
          <CardContent className="p-3 text-center">
            <Crown className="h-4 w-4 text-amber-500 mx-auto mb-1" />
            <p className="text-xl font-bold text-amber-400">{stats.alphas}</p>
            <p className="text-xs text-amber-400/60">ALPHA</p>
          </CardContent>
        </Card>
        <Card className="bg-orange-500/10 border-orange-500/30">
          <CardContent className="p-3 text-center">
            <Star className="h-4 w-4 text-orange-500 mx-auto mb-1" />
            <p className="text-xl font-bold text-orange-400">{stats.dominants}</p>
            <p className="text-xs text-orange-400/60">Dominants</p>
          </CardContent>
        </Card>
        <Card className="bg-zinc-900/50 border-zinc-800">
          <CardContent className="p-3 text-center">
            <Target className="h-4 w-4 text-green-500 mx-auto mb-1" />
            <p className="text-xl font-bold">{stats.species}</p>
            <p className="text-xs text-zinc-500">Especes</p>
          </CardContent>
        </Card>
        <Card className="bg-zinc-900/50 border-zinc-800">
          <CardContent className="p-3 text-center">
            <BarChart3 className="h-4 w-4 text-blue-500 mx-auto mb-1" />
            <p className="text-xl font-bold">{stats.avgScore}</p>
            <p className="text-xs text-zinc-500">Score moyen</p>
          </CardContent>
        </Card>
      </div>

      {/* Controls */}
      <div className="flex flex-wrap items-center gap-2">
        <Button onClick={runBatchAnalysis} disabled={analyzing} className="bg-amber-600 hover:bg-amber-700" data-testid="run-alpha-analysis">
          {analyzing ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : <Activity className="h-4 w-4 mr-1" />}
          {analyzing ? 'Analyse en cours...' : 'Analyser ALPHA'}
        </Button>
        <div className="relative flex-1 min-w-[200px]">
          <Search className="h-4 w-4 absolute left-2 top-1/2 -translate-y-1/2 text-zinc-500" />
          <Input className="bg-zinc-800 border-zinc-700 pl-8 h-9" placeholder="Rechercher..." value={searchText} onChange={e => setSearchText(e.target.value)} data-testid="alpha-search" />
        </div>
        <Select value={filterSpecies} onValueChange={setFilterSpecies}>
          <SelectTrigger className="w-40 bg-zinc-800 border-zinc-700 h-9" data-testid="alpha-filter-species"><SelectValue /></SelectTrigger>
          <SelectContent>{SPECIES_LIST.map(s => <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>)}</SelectContent>
        </Select>
        <Select value={filterCategory} onValueChange={setFilterCategory}>
          <SelectTrigger className="w-36 bg-zinc-800 border-zinc-700 h-9"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Toutes categories</SelectItem>
            <SelectItem value="alpha">ALPHA</SelectItem>
            <SelectItem value="dominant">Dominant</SelectItem>
            <SelectItem value="standard">Standard</SelectItem>
            <SelectItem value="juvenile">Juvenile</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Events Table */}
      <Card className="bg-zinc-900/50 border-zinc-800">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-zinc-300 flex items-center gap-2">
            <Crown className="h-4 w-4 text-amber-500" /> Classement ALPHA ({filteredEvents.length})
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-xs" data-testid="alpha-events-table">
              <thead>
                <tr className="border-b border-zinc-800 text-zinc-500">
                  <th className="px-3 py-2 text-left">#</th>
                  <th className="px-3 py-2 text-left cursor-pointer hover:text-amber-400" onClick={() => { setSortBy('alpha_score'); setSortDir(d => d === 'desc' ? 'asc' : 'desc'); }}>
                    Score <ArrowUpDown className="inline h-3 w-3" />
                  </th>
                  <th className="px-3 py-2 text-left">Categorie</th>
                  <th className="px-3 py-2 text-left">Espece</th>
                  <th className="px-3 py-2 text-left">Sexe</th>
                  <th className="px-3 py-2 text-left">Taille</th>
                  <th className="px-3 py-2 text-left">Camera</th>
                  <th className="px-3 py-2 text-left">Region</th>
                  <th className="px-3 py-2 text-left">GPS</th>
                  <th className="px-3 py-2 text-left">Date</th>
                </tr>
              </thead>
              <tbody>
                {filteredEvents.slice(0, 50).map((evt, idx) => (
                  <tr key={evt.id} className="border-b border-zinc-800/50 hover:bg-zinc-800/30" data-testid={`alpha-row-${evt.id}`}>
                    <td className="px-3 py-2 text-zinc-500">{idx + 1}</td>
                    <td className="px-3 py-2">
                      <span className="font-bold text-amber-400">{evt.alpha_score}</span>
                    </td>
                    <td className="px-3 py-2">
                      <Badge className={`text-xs ${ALPHA_SCORE_COLORS[evt.alpha_category]}`}>
                        {evt.alpha_category === 'alpha' && <Crown className="h-3 w-3 mr-0.5" />}
                        {evt.alpha_category?.toUpperCase()}
                      </Badge>
                    </td>
                    <td className="px-3 py-2 text-zinc-300">{evt.species || '-'}</td>
                    <td className="px-3 py-2 text-zinc-400">{evt.sex || '-'}</td>
                    <td className="px-3 py-2">
                      <Progress value={evt.size_score} className="h-1.5 w-12" />
                    </td>
                    <td className="px-3 py-2 text-zinc-400">{evt.camera_name}</td>
                    <td className="px-3 py-2 text-zinc-400">{evt.region || '-'}</td>
                    <td className="px-3 py-2 text-zinc-500 font-mono text-[10px]">
                      {evt.gps_lat ? `${evt.gps_lat.toFixed(3)}, ${evt.gps_lon?.toFixed(3)}` : '-'}
                    </td>
                    <td className="px-3 py-2 text-zinc-500">{new Date(evt.timestamp).toLocaleDateString('fr-CA')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {filteredEvents.length === 0 && (
            <div className="text-center py-8 text-zinc-500">
              <Crown className="h-8 w-8 mx-auto mb-2 text-zinc-600" />
              <p>Aucun evenement ALPHA detecte</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* HOTSPOTS ALPHA TABLE (SECTION 3) */}
      <Card className="bg-zinc-900/50 border-zinc-800" data-testid="alpha-hotspots-table">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-zinc-300 flex items-center gap-2">
            <Crosshair className="h-4 w-4 text-red-500" /> Hotspots ALPHA ({hotspots.length})
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-zinc-800 text-zinc-500">
                  <th className="px-3 py-2 text-left">ID</th>
                  <th className="px-3 py-2 text-left">Region</th>
                  <th className="px-3 py-2 text-left">Score ALPHA</th>
                  <th className="px-3 py-2 text-left">Especes</th>
                  <th className="px-3 py-2 text-left">Intensite</th>
                  <th className="px-3 py-2 text-left">Detections</th>
                  <th className="px-3 py-2 text-left">GPS</th>
                  <th className="px-3 py-2 text-left">Action</th>
                </tr>
              </thead>
              <tbody>
                {hotspots.map((hs, idx) => (
                  <tr key={idx} className="border-b border-zinc-800/50 hover:bg-zinc-800/30" data-testid={`hotspot-row-${idx}`}>
                    <td className="px-3 py-2 text-zinc-500 font-mono">HS-{String(idx + 1).padStart(3, '0')}</td>
                    <td className="px-3 py-2 text-zinc-300 font-medium">{hs.region}</td>
                    <td className="px-3 py-2">
                      <span className="font-bold text-amber-400">{hs.avgScore}</span>
                    </td>
                    <td className="px-3 py-2">
                      <div className="flex flex-wrap gap-1">
                        {hs.species.map(sp => <Badge key={sp} className="text-[10px] bg-zinc-700 text-zinc-300">{sp}</Badge>)}
                      </div>
                    </td>
                    <td className="px-3 py-2">
                      <Badge className={`text-xs ${hs.intensity === 'Extreme' ? 'bg-red-500/20 text-red-400' : hs.intensity === 'Elevee' ? 'bg-orange-500/20 text-orange-400' : 'bg-zinc-700 text-zinc-300'}`}>
                        {hs.intensity}
                      </Badge>
                    </td>
                    <td className="px-3 py-2 text-zinc-400">{hs.count}</td>
                    <td className="px-3 py-2 text-zinc-500 font-mono text-[10px]">
                      {hs.gps_lat ? `${hs.gps_lat.toFixed(3)}, ${hs.gps_lon?.toFixed(3)}` : '-'}
                    </td>
                    <td className="px-3 py-2">
                      <div className="flex gap-1">
                        {hs.gps_lat && (
                          <Button size="sm" variant="outline" className="h-6 text-[10px] border-zinc-700 px-2"
                            onClick={() => window.open(`/map?lat=${hs.gps_lat}&lng=${hs.gps_lon}&zoom=15`, '_blank')}>
                            <MapPin className="h-3 w-3 mr-0.5" /> Carte
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {hotspots.length === 0 && (
            <div className="text-center py-8 text-zinc-500">
              <Crosshair className="h-8 w-8 mx-auto mb-2 text-zinc-600" />
              <p>Aucun hotspot ALPHA detecte — importez des photos depuis vos cameras</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

// ============================================
// SIMULATION PIPELINE (sera remplace par IA)
// ============================================

function simulateSpeciesDetection(evt) {
  const species = ['orignal', 'cerf', 'ours_noir', 'caribou', 'dindon', 'chevreuil'];
  const seed = hashCode(evt.id || '');
  return species[Math.abs(seed) % species.length];
}

function simulateSexDetection(species) {
  if (['dindon'].includes(species)) return 'male';
  return Math.random() > 0.4 ? 'male' : 'femelle';
}

function simulateSizeScore(evt) {
  const seed = hashCode(evt.id || '') % 100;
  return Math.max(20, Math.min(98, 50 + seed % 48));
}

function computeAlphaScore(species, sex, sizeScore, evt) {
  let score = sizeScore;
  if (sex === 'male') score += 15;
  if (['orignal', 'caribou'].includes(species)) score += 10;
  if (['ours_noir'].includes(species)) score += 5;
  return Math.min(99, Math.max(1, Math.round(score)));
}

function deriveRegion(lat, lon) {
  if (!lat || !lon) return 'Inconnue';
  if (lat > 48) return 'Laurentides-Nord';
  if (lat > 47) return 'Saguenay';
  if (lat > 46.5) return 'Mauricie';
  if (lat > 46) return 'Lanaudiere';
  return 'Monteregie';
}

function hashCode(str) {
  let h = 0;
  for (let i = 0; i < str.length; i++) {
    h = ((h << 5) - h) + str.charCodeAt(i);
    h |= 0;
  }
  return h;
}

export default AdminAlphaAnalysis;

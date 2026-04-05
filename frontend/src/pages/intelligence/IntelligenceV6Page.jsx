/**
 * Intelligence V6 Dashboard Page — INTELLIGENCE V6-CORE
 * Directive x7000-M3-DASHBOARD + x7100-M4 Phase D | BCE-4X GOLDEN V6+
 * 
 * Dashboard auto-sync : change espece/zone/date → tous les widgets se rafraichissent
 * Consomme exclusivement DataFusionLayer + DataContracts V6
 * 
 * Widgets M3 : W1 (ScoreConsolide), W2 (PredictiveLayer), W3 (BestTimes),
 *              W6 (Trends), W7 (Correlation), W9 (TimeSeries)
 * Widgets M4 : W10 (HunterProfile), W11 (Navigation), W12 (Advice)
 * 
 * Synchronise : CARTE, MON TERRITOIRE, Gestionnaire, SUPRA
 */
import React, { useState, useEffect, useCallback } from 'react';
import useBionicStore from '@/stores/useBionicStore';
import DataFusionLayer from '@/services/DataFusionLayer';
import { ScoreConsolideWidget } from '@/modules/intelligence-v6/components/ScoreConsolideWidget';
import { PredictiveLayerWidget } from '@/modules/intelligence-v6/components/PredictiveLayerWidget';
import { BestTimesWidget } from '@/modules/intelligence-v6/components/BestTimesWidget';
import { TrendsChart } from '@/modules/intelligence-v6/components/TrendsChart';
import { CorrelationMatrixWidget } from '@/modules/intelligence-v6/components/CorrelationMatrixWidget';
import { TimeSeriesChart } from '@/modules/intelligence-v6/components/TimeSeriesChart';
import { HunterProfileWidget } from '@/modules/intelligence-v6/components/HunterProfileWidget';
import { NavigationWidget } from '@/modules/intelligence-v6/components/NavigationWidget';
import { AdviceWidget } from '@/modules/intelligence-v6/components/AdviceWidget';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Brain, RefreshCw, Loader2, User, Navigation, Lightbulb, Shield, CheckCircle2, XCircle, AlertTriangle } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const SPECIES_OPTIONS = [
  { value: 'orignal', label: 'Orignal' },
  { value: 'chevreuil', label: 'Chevreuil' },
  { value: 'ours_noir', label: 'Ours noir' },
  { value: 'dindon_sauvage', label: 'Dindon sauvage' },
];

export default function IntelligenceV6Page() {
  const [species, setSpecies] = useState('orignal');
  const [zoneId, setZoneId] = useState('zone-01');
  const [userId, setUserId] = useState('default_hunter');
  const [loading, setLoading] = useState(false);
  const [m4Data, setM4Data] = useState({ profile: null, advice: null, suggestions: null });
  const [bdreHealth, setBdreHealth] = useState(null);
  const [bdreSources, setBdreSources] = useState([]);

  const {
    setPredictiveLayer, setTrendsData, setCorrelationData,
    setScoreConsolide, setBestTimesData, setM3Loading,
  } = useBionicStore();

  const refreshAll = useCallback(async () => {
    setLoading(true);
    setM3Loading(true);

    try {
      const [consolidated, score, trends, correlation, bestTimes, timeseries, profile, advice, bdreDash, bdreSrc] = await Promise.all([
        DataFusionLayer.fetchConsolidatedView(zoneId, species, null, 46.85, -71.25),
        DataFusionLayer.fetchScoreConsolide(zoneId, species, null, 46.85, -71.25),
        DataFusionLayer.fetchTrends(species, zoneId),
        DataFusionLayer.fetchCorrelationMatrix(zoneId, species, 46.85, -71.25),
        DataFusionLayer.fetchBestTimes(zoneId, species, null, 46.85, -71.25),
        DataFusionLayer.fetchTimeSeries(zoneId, species, 'activity_index'),
        DataFusionLayer.fetchHunterProfile(userId),
        DataFusionLayer.fetchContextualAdvice(userId, 46.85, -71.25),
        fetch(`${API}/api/v1/bdre/dashboard`).then(r => r.json()).catch(() => null),
        fetch(`${API}/api/v1/bdre/sources`).then(r => r.json()).catch(() => null),
      ]);

      setPredictiveLayer(consolidated);
      setScoreConsolide(score);
      setTrendsData(trends);
      setCorrelationData(correlation);
      setBestTimesData(bestTimes);

      setM4Data(prev => ({ ...prev, profile, advice }));
      if (bdreDash) setBdreHealth(bdreDash);
      if (bdreSrc?.sources) setBdreSources(bdreSrc.sources);
    } catch (err) {
      console.error('DFL refresh error:', err);
    } finally {
      setLoading(false);
      setM3Loading(false);
    }
  }, [species, zoneId, userId, setPredictiveLayer, setTrendsData, setCorrelationData, setScoreConsolide, setBestTimesData, setM3Loading]);

  useEffect(() => {
    refreshAll();
  }, [refreshAll]);

  const store = useBionicStore();

  return (
    <div className="min-h-screen bg-[#0c0c14] text-gray-200 p-4 lg:p-6" data-testid="intelligence-v6-page">
      <div className="max-w-7xl mx-auto space-y-4">

        {/* Header */}
        <div className="flex flex-wrap items-center gap-3">
          <Brain className="w-5 h-5 text-violet-400" />
          <h1 className="text-lg font-semibold tracking-tight">Intelligence V6-CORE</h1>
          <Badge variant="outline" className="border-violet-500/30 text-violet-400 text-[10px]">
            M1 + M2 + M3 + M4 FUSION
          </Badge>

          <div className="ml-auto flex items-center gap-2">
            <Select value={species} onValueChange={setSpecies}>
              <SelectTrigger data-testid="species-selector" className="w-36 h-8 text-xs bg-zinc-900 border-zinc-700">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {SPECIES_OPTIONS.map(s => (
                  <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>

            <input data-testid="zone-input" type="text" value={zoneId}
              onChange={(e) => setZoneId(e.target.value)}
              className="h-8 w-28 text-xs bg-zinc-900 border border-zinc-700 rounded px-2 text-zinc-300"
              placeholder="Zone ID" />

            <button data-testid="refresh-btn" onClick={refreshAll} disabled={loading}
              className="h-8 w-8 flex items-center justify-center rounded bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 transition-colors">
              {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin text-zinc-400" /> : <RefreshCw className="w-3.5 h-3.5 text-zinc-400" />}
            </button>
          </div>
        </div>

        {/* BDRE Health — BCE-4X BDRE-FIRST P1 */}
        <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-3" data-testid="bdre-health-widget">
          <div className="flex items-center gap-2 mb-2">
            <Shield className="w-4 h-4 text-[#F5A623]" />
            <span className="text-xs font-medium text-zinc-300">BDRE Data Reliability</span>
            <Badge variant="outline" className="text-[9px] border-[#F5A623]/30 text-[#F5A623] ml-auto">
              {bdreHealth?.bdre_version || '—'}
            </Badge>
          </div>
          <div className="flex items-center gap-4">
            {bdreSources.length > 0 ? (
              <>
                <div className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-3 h-3 text-green-400" />
                  <span className="text-[10px] text-zinc-400">
                    {bdreSources.filter(s => s.status === 'healthy').length} sources actives
                  </span>
                </div>
                <div className="flex items-center gap-1.5">
                  <XCircle className="w-3 h-3 text-zinc-500" />
                  <span className="text-[10px] text-zinc-500">
                    {bdreSources.filter(s => s.status !== 'healthy').length} non connectees
                  </span>
                </div>
                <div className="flex items-center gap-1.5">
                  <AlertTriangle className="w-3 h-3 text-yellow-500" />
                  <span className="text-[10px] text-zinc-400">
                    {bdreHealth?.audit_stats?.total_fallbacks ?? 0} fallbacks
                  </span>
                </div>
                <div className="flex gap-0.5 ml-auto">
                  {bdreSources.slice(0, 8).map((src, i) => (
                    <div key={i} className={`w-2 h-2 rounded-full ${src.status === 'healthy' ? (src.score >= 0.8 ? 'bg-green-400' : src.score >= 0.3 ? 'bg-yellow-400' : 'bg-red-400') : 'bg-zinc-600'}`} title={`${src.source_id}: ${(src.score * 100).toFixed(0)}%`} />
                  ))}
                </div>
              </>
            ) : (
              <span className="text-[10px] text-zinc-500">Chargement BDRE...</span>
            )}
          </div>
        </div>

        {/* Section M4 — Profil + Conseils IA */}
        <div className="flex items-center gap-2 pt-2">
          <User className="w-4 h-4 text-violet-400/60" />
          <span className="text-xs text-zinc-500 uppercase tracking-wider font-medium">Profil Adaptatif + Navigation IA</span>
          <div className="flex-1 h-px bg-zinc-800" />
          <Badge variant="outline" className="text-[9px] border-cyan-500/20 text-cyan-400">M4</Badge>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <HunterProfileWidget initialData={m4Data.profile} userId={userId} />
          <NavigationWidget initialData={null} />
          <AdviceWidget initialData={m4Data.advice} />
        </div>

        {/* Section M3 — Predictif */}
        <div className="flex items-center gap-2 pt-2">
          <Brain className="w-4 h-4 text-violet-400/60" />
          <span className="text-xs text-zinc-500 uppercase tracking-wider font-medium">Intelligence Predictive</span>
          <div className="flex-1 h-px bg-zinc-800" />
          <Badge variant="outline" className="text-[9px] border-violet-500/20 text-violet-400">M3</Badge>
        </div>

        {/* Grid W1 + W3 + W8 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <ScoreConsolideWidget initialData={store.scoreConsolide} />
          <PredictiveLayerWidget initialData={store.predictiveLayer} />
          <BestTimesWidget initialData={store.bestTimesData} />
        </div>

        {/* Grid W6 + W7 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <TrendsChart initialData={store.trendsData} />
          <CorrelationMatrixWidget initialData={store.correlationData} />
        </div>

        {/* W9 TimeSeries */}
        <TimeSeriesChart initialData={null} />

      </div>
    </div>
  );
}

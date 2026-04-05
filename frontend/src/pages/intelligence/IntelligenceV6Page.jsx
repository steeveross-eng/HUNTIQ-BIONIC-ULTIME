/**
 * Intelligence V6 Dashboard Page
 * Directive x7000-M3-DASHBOARD | BCE-4X GOLDEN V6+
 * 
 * Dashboard auto-sync : change espece/zone/date → tous les widgets se rafraichissent
 * Consomme exclusivement DataFusionLayer + DataContracts V6
 */
import React, { useState, useEffect, useCallback } from 'react';
import useBionicStore from '@/stores/useBionicStore';
import { DataFusionLayer } from '@/services/DataFusionLayer';
import { ScoreConsolideWidget } from '@/modules/intelligence-v6/components/ScoreConsolideWidget';
import { PredictiveLayerWidget } from '@/modules/intelligence-v6/components/PredictiveLayerWidget';
import { BestTimesWidget } from '@/modules/intelligence-v6/components/BestTimesWidget';
import { TrendsChart } from '@/modules/intelligence-v6/components/TrendsChart';
import { CorrelationMatrixWidget } from '@/modules/intelligence-v6/components/CorrelationMatrixWidget';
import { TimeSeriesChart } from '@/modules/intelligence-v6/components/TimeSeriesChart';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Brain, RefreshCw, Loader2 } from 'lucide-react';

const SPECIES_OPTIONS = [
  { value: 'orignal', label: 'Orignal' },
  { value: 'chevreuil', label: 'Chevreuil' },
  { value: 'ours_noir', label: 'Ours noir' },
  { value: 'dindon_sauvage', label: 'Dindon sauvage' },
];

export default function IntelligenceV6Page() {
  const [species, setSpecies] = useState('orignal');
  const [zoneId, setZoneId] = useState('zone-01');
  const [loading, setLoading] = useState(false);

  const {
    setPredictiveLayer, setTrendsData, setCorrelationData,
    setScoreConsolide, setBestTimesData, setM3Loading,
  } = useBionicStore();

  const refreshAll = useCallback(async () => {
    setLoading(true);
    setM3Loading(true);

    try {
      const [consolidated, score, trends, correlation, bestTimes, timeseries] = await Promise.all([
        DataFusionLayer.fetchConsolidatedView(zoneId, species, null, 46.85, -71.25),
        DataFusionLayer.fetchScoreConsolide(zoneId, species, null, 46.85, -71.25),
        DataFusionLayer.fetchTrends(species, zoneId),
        DataFusionLayer.fetchCorrelationMatrix(zoneId, species, 46.85, -71.25),
        DataFusionLayer.fetchBestTimes(zoneId, species, null, 46.85, -71.25),
        DataFusionLayer.fetchTimeSeries(zoneId, species, 'activity_index'),
      ]);

      setPredictiveLayer(consolidated);
      setScoreConsolide(score);
      setTrendsData(trends);
      setCorrelationData(correlation);
      setBestTimesData(bestTimes);
    } catch (err) {
      console.error('DFL refresh error:', err);
    } finally {
      setLoading(false);
      setM3Loading(false);
    }
  }, [species, zoneId, setPredictiveLayer, setTrendsData, setCorrelationData, setScoreConsolide, setBestTimesData, setM3Loading]);

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
          <h1 className="text-lg font-semibold tracking-tight">Intelligence V6</h1>
          <Badge variant="outline" className="border-violet-500/30 text-violet-400 text-[10px]">
            M1 + M2 + M3 FUSION
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

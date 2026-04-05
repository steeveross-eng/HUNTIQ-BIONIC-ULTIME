/**
 * W3 — Predictive Layer Widget (Courbe P(h) 24h)
 * Directive x7000-M3-DASHBOARD | BCE-4X GOLDEN V6+
 */
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { EventBusV6, CHANNELS } from '../../../services/EventBusV6';
import { Activity, Clock, TrendingUp, TrendingDown, Minus } from 'lucide-react';

export const PredictiveLayerWidget = ({ initialData }) => {
  const [data, setData] = useState(initialData || null);

  useEffect(() => {
    const unsub = EventBusV6.subscribe(CHANNELS.PREDICTIVE_LAYER_UPDATED, setData);
    return unsub;
  }, []);

  if (!data?.predictive_layer?.predictions?.length) return (
    <Card data-testid="predictive-layer-widget" className="bg-zinc-900 border-zinc-800">
      <CardContent className="p-6 text-center text-zinc-500">Courbe P(h) — en attente de données</CardContent>
    </Card>
  );

  const preds = data.predictive_layer.predictions;
  const agg = data.predictive_layer.aggregation;
  const maxProb = Math.max(...preds.map(p => p.probability));
  const TrendIcon = agg.trend === 'increasing' ? TrendingUp : agg.trend === 'decreasing' ? TrendingDown : Minus;

  return (
    <Card data-testid="predictive-layer-widget" className="bg-zinc-900 border-zinc-800">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-zinc-400 flex items-center gap-2">
          <Activity className="w-4 h-4" /> PRÉDICTION HORAIRE P(h)
          <Badge variant="outline" className="text-xs ml-auto border-zinc-700">
            {data.species || '—'}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center gap-3 text-xs text-zinc-400">
          <span className="flex items-center gap-1">
            <Clock className="w-3 h-3" /> Peak: <strong className="text-white">{agg.peak_hour}h</strong>
          </span>
          <span>Prob: <strong className="text-emerald-400">{Math.round(agg.peak_probability * 100)}%</strong></span>
          <span className="flex items-center gap-1"><TrendIcon className="w-3 h-3" /> {agg.trend}</span>
        </div>

        <div data-testid="prediction-chart" className="flex items-end gap-px h-24">
          {preds.map((p, i) => {
            const h = Math.max(4, (p.probability / (maxProb || 1)) * 100);
            const inWindow = i >= agg.best_window.start && i <= agg.best_window.end;
            return (
              <div key={i} className="flex-1 flex flex-col items-center group relative">
                <div className={`w-full rounded-t transition-all duration-300 ${inWindow ? 'bg-emerald-500' : 'bg-violet-600/70'}`}
                  style={{ height: `${h}%` }}
                  title={`${i}h: ${Math.round(p.probability * 100)}%`} />
                {i % 6 === 0 && <span className="text-[9px] text-zinc-600 mt-0.5">{i}h</span>}
              </div>
            );
          })}
        </div>

        <div className="flex gap-2 text-[10px] text-zinc-500">
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-emerald-500" /> Fenêtre optimale</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-violet-600/70" /> Activité</span>
        </div>
      </CardContent>
    </Card>
  );
};

export default PredictiveLayerWidget;

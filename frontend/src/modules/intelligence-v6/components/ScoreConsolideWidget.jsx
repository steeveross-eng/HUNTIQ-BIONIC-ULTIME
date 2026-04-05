/**
 * W1 — Score Consolidé Widget
 * Directive x7000-M3-DASHBOARD | BCE-4X GOLDEN V6+
 * Gauge 0-100, rating A+→D, decomposition 6 composants
 */
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { EventBusV6, CHANNELS } from '../../../services/EventBusV6';
import { TrendingUp, TrendingDown, Minus, Target } from 'lucide-react';

const COMPONENT_LABELS = {
  predictive: 'Prédictif P(h)',
  solunar: 'Solunaire',
  meteo: 'Météo-Faune',
  nutrition: 'Nutrition V6',
  territory: 'Territoire/POI',
  legal: 'Légal',
};

const COMPONENT_COLORS = {
  predictive: '#8b5cf6',
  solunar: '#f5a623',
  meteo: '#3b82f6',
  nutrition: '#22c55e',
  territory: '#06b6d4',
  legal: '#6b7280',
};

export const ScoreConsolideWidget = ({ initialData }) => {
  const [data, setData] = useState(initialData || null);

  useEffect(() => {
    const unsub = EventBusV6.subscribe(CHANNELS.SCORE_CONSOLIDE_UPDATED, setData);
    return unsub;
  }, []);

  if (!data) return (
    <Card data-testid="score-consolide-widget" className="bg-zinc-900 border-zinc-800">
      <CardContent className="p-6 text-center text-zinc-500">Score Consolidé — en attente de données</CardContent>
    </Card>
  );

  const TrendIcon = data.trend === 'up' ? TrendingUp : data.trend === 'down' ? TrendingDown : Minus;

  return (
    <Card data-testid="score-consolide-widget" className="bg-zinc-900 border-zinc-800">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-zinc-400 flex items-center gap-2">
          <Target className="w-4 h-4" /> SCORE CONSOLIDÉ V6
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center gap-4">
          <div className="relative w-20 h-20">
            <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
              <circle cx="50" cy="50" r="42" fill="none" stroke="#27272a" strokeWidth="8" />
              <circle cx="50" cy="50" r="42" fill="none" stroke={data.ratingColor}
                strokeWidth="8" strokeDasharray={`${data.global * 2.64} 264`}
                strokeLinecap="round" className="transition-all duration-700" />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-xl font-bold text-white">{data.global}</span>
            </div>
          </div>
          <div>
            <Badge data-testid="score-rating" style={{ backgroundColor: data.ratingColor }} className="text-white text-lg px-3 py-1">
              {data.rating}
            </Badge>
            <div className="flex items-center gap-1 mt-1 text-zinc-400 text-xs">
              <TrendIcon className="w-3 h-3" /> {data.trend}
            </div>
          </div>
        </div>
        <div className="space-y-2">
          {Object.entries(data.components).map(([key, value]) => (
            <div key={key} className="flex items-center gap-2">
              <span className="text-xs text-zinc-500 w-24 truncate">{COMPONENT_LABELS[key]}</span>
              <div className="flex-1 h-2 bg-zinc-800 rounded-full overflow-hidden">
                <div className="h-full rounded-full transition-all duration-500"
                  style={{ width: `${value}%`, backgroundColor: COMPONENT_COLORS[key] }} />
              </div>
              <span className="text-xs text-zinc-400 w-8 text-right">{value}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default ScoreConsolideWidget;

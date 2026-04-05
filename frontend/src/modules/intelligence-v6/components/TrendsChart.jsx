/**
 * W6 — Trends Chart (Tendances saisonnières)
 * Directive x7000-M3-DASHBOARD | BCE-4X GOLDEN V6+
 */
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { EventBusV6, CHANNELS } from '../../../services/EventBusV6';
import { BarChart3, TrendingUp, TrendingDown, Minus } from 'lucide-react';

const MONTH_NAMES = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'];
const TREND_ICONS = { up: TrendingUp, down: TrendingDown, stable: Minus };

export const TrendsChart = ({ initialData }) => {
  const [data, setData] = useState(initialData || null);

  useEffect(() => {
    const unsub = EventBusV6.subscribe(CHANNELS.TRENDS_UPDATED, setData);
    return unsub;
  }, []);

  if (!data?.monthly_patterns?.length) return (
    <Card data-testid="trends-chart" className="bg-zinc-900 border-zinc-800">
      <CardContent className="p-6 text-center text-zinc-500">Tendances — en attente</CardContent>
    </Card>
  );

  const maxActivity = Math.max(...data.monthly_patterns.map(m => m.activity_index), 0.01);

  return (
    <Card data-testid="trends-chart" className="bg-zinc-900 border-zinc-800">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-zinc-400 flex items-center gap-2">
          <BarChart3 className="w-4 h-4" /> TENDANCES SAISONNIÈRES
          <Badge variant="outline" className="text-xs ml-auto border-zinc-700">{data.species}</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-end gap-1 h-28">
          {data.monthly_patterns.map((mp, i) => {
            const h = (mp.activity_index / maxActivity) * 100;
            const bh = (mp.baseline_factor / maxActivity) * 100;
            const isPeak = mp.month === data.annual_summary?.peak_month;
            const Icon = TREND_ICONS[mp.trend_vs_previous] || Minus;
            return (
              <div key={i} className="flex-1 flex flex-col items-center group relative">
                <div className="w-full relative" style={{ height: '100%' }}>
                  <div className="absolute bottom-0 w-full bg-zinc-700/30 rounded-t" style={{ height: `${bh}%` }} />
                  <div className={`absolute bottom-0 w-full rounded-t transition-all ${isPeak ? 'bg-emerald-500' : 'bg-violet-600'}`}
                    style={{ height: `${h}%` }} />
                </div>
                <span className="text-[8px] text-zinc-600 mt-0.5">{MONTH_NAMES[i]}</span>
                <div className="absolute -top-6 hidden group-hover:block bg-zinc-800 text-[9px] text-zinc-300 p-1 rounded shadow-lg z-10 whitespace-nowrap">
                  {MONTH_NAMES[i]}: {(mp.activity_index * 100).toFixed(0)}% <Icon className="w-2 h-2 inline" />
                  {mp.observation_count > 0 && ` (${mp.observation_count} obs)`}
                </div>
              </div>
            );
          })}
        </div>
        <div className="flex gap-3 text-[10px] text-zinc-500">
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-violet-600" /> Activité</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-zinc-700/50" /> Baseline V5</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-emerald-500" /> Peak</span>
        </div>
        {data.annual_summary && (
          <div className="text-[10px] text-zinc-500 flex gap-4">
            <span>Peak: <strong className="text-zinc-300">{MONTH_NAMES[(data.annual_summary.peak_month || 1) - 1]}</strong></span>
            <span>Low: <strong className="text-zinc-300">{MONTH_NAMES[(data.annual_summary.low_month || 1) - 1]}</strong></span>
            <span>Moy: <strong className="text-zinc-300">{(data.annual_summary.avg_activity * 100).toFixed(0)}%</strong></span>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default TrendsChart;

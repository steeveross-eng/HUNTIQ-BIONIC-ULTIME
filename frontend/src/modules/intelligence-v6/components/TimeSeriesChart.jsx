/**
 * W9 — Time Series Chart
 * Directive x7000-M3-DASHBOARD | BCE-4X GOLDEN V6+
 */
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { EventBusV6, CHANNELS } from '../../../services/EventBusV6';
import { LineChart, Activity } from 'lucide-react';

export const TimeSeriesChart = ({ initialData }) => {
  const [data, setData] = useState(initialData || null);

  useEffect(() => {
    const unsub = EventBusV6.subscribe(CHANNELS.TIMESERIES_UPDATED, setData);
    return unsub;
  }, []);

  if (!data?.values?.length) return (
    <Card data-testid="timeseries-chart" className="bg-zinc-900 border-zinc-800">
      <CardContent className="p-6 text-center text-zinc-500">Séries temporelles — en attente</CardContent>
    </Card>
  );

  const values = data.values.slice(-50);
  const maxVal = Math.max(...values.map(v => v.value), 0.01);
  const minVal = Math.min(...values.map(v => v.value), 0);

  return (
    <Card data-testid="timeseries-chart" className="bg-zinc-900 border-zinc-800">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-zinc-400 flex items-center gap-2">
          <LineChart className="w-4 h-4" /> SÉRIES TEMPORELLES
          <Badge variant="outline" className="text-xs ml-auto border-zinc-700">{data.metric}</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center gap-3 text-xs text-zinc-400">
          <span>{data.species} | {data.zone_id}</span>
          <Badge variant="outline" className="text-[9px] border-zinc-700">{data.total_points} pts</Badge>
          <span className="ml-auto flex items-center gap-1">
            <Activity className="w-3 h-3" /> Dernier: <strong className="text-white">{data.latest_value}</strong>
          </span>
        </div>
        <div data-testid="ts-chart" className="flex items-end gap-px h-20">
          {values.map((v, i) => {
            const range = maxVal - minVal || 1;
            const h = Math.max(4, ((v.value - minVal) / range) * 100);
            const sourceColor = v.source === 'poi_graph' ? '#8b5cf6' : v.source === 'hunting_trip' ? '#22c55e' : '#3b82f6';
            return (
              <div key={i} className="flex-1 rounded-t transition-all" style={{ height: `${h}%`, backgroundColor: sourceColor }}
                title={`${v.timestamp?.slice(0, 16) || i}: ${v.value}`} />
            );
          })}
        </div>
        <div className="flex gap-3 text-[10px] text-zinc-500">
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-blue-500" /> Manuel</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-violet-500" /> POI Graph</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-emerald-500" /> Sortie chasse</span>
        </div>
      </CardContent>
    </Card>
  );
};

export default TimeSeriesChart;

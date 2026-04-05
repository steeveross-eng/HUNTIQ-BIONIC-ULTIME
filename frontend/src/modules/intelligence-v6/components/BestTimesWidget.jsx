/**
 * W8 — Best Times Widget (Créneaux optimaux combinés)
 * Directive x7000-M3-DASHBOARD | BCE-4X GOLDEN V6+
 */
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { EventBusV6, CHANNELS } from '../../../services/EventBusV6';
import { Clock, Sun, Sunset, Moon, CloudSun } from 'lucide-react';

const PERIOD_ICONS = { aube: Sun, midi: CloudSun, crepuscule: Sunset, nuit: Moon };
const PERIOD_COLORS = { aube: '#f5a623', midi: '#eab308', crepuscule: '#f97316', nuit: '#6366f1' };

export const BestTimesWidget = ({ initialData }) => {
  const [data, setData] = useState(initialData || null);

  useEffect(() => {
    const unsub = EventBusV6.subscribe(CHANNELS.PREDICTIVE_LAYER_UPDATED, (consolidated) => {
      if (consolidated?.bestTimes) setData(consolidated.bestTimes);
    });
    return unsub;
  }, []);

  const setDirect = (d) => setData(d);
  useEffect(() => {
    if (initialData) setDirect(initialData);
  }, [initialData]);

  if (!data?.best_windows?.length) return (
    <Card data-testid="best-times-widget" className="bg-zinc-900 border-zinc-800">
      <CardContent className="p-6 text-center text-zinc-500">Créneaux — en attente</CardContent>
    </Card>
  );

  return (
    <Card data-testid="best-times-widget" className="bg-zinc-900 border-zinc-800">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-zinc-400 flex items-center gap-2">
          <Clock className="w-4 h-4" /> MEILLEURS CRÉNEAUX
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {data.best_windows.slice(0, 4).map((w, i) => {
          const Icon = PERIOD_ICONS[w.period] || Clock;
          const color = PERIOD_COLORS[w.period] || '#6b7280';
          const pct = Math.round(w.avg_probability * 100);
          return (
            <div key={i} data-testid={`best-time-${i}`} className="flex items-center gap-2 p-2 bg-zinc-800/50 rounded">
              <Icon className="w-4 h-4 shrink-0" style={{ color }} />
              <span className="text-xs text-zinc-300 w-24">{w.label}</span>
              <div className="flex-1 h-1.5 bg-zinc-700 rounded-full overflow-hidden">
                <div className="h-full rounded-full" style={{ width: `${pct}%`, backgroundColor: color }} />
              </div>
              <span className="text-xs font-medium text-white w-8 text-right">{pct}%</span>
              <Badge variant="outline" className="text-[9px] border-zinc-700 text-zinc-500">{w.dominant_factor}</Badge>
            </div>
          );
        })}
        {data.recommendation && (
          <p data-testid="recommendation" className="text-[11px] text-zinc-500 mt-2 italic">{data.recommendation}</p>
        )}
      </CardContent>
    </Card>
  );
};

export default BestTimesWidget;

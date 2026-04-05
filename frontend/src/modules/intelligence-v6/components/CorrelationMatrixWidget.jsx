/**
 * W7 — Correlation Matrix Widget (Corrélations météo-faune)
 * Directive x7000-M3-DASHBOARD | BCE-4X GOLDEN V6+
 */
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { EventBusV6, CHANNELS } from '../../../services/EventBusV6';
import { Thermometer, Wind, CloudRain, Gauge, Moon, Droplets } from 'lucide-react';

const FACTOR_CONFIG = {
  temperature: { Icon: Thermometer, label: 'Température', color: '#ef4444' },
  barometric_pressure: { Icon: Gauge, label: 'Pression', color: '#8b5cf6' },
  wind_speed: { Icon: Wind, label: 'Vent', color: '#06b6d4' },
  precipitation: { Icon: CloudRain, label: 'Précipitations', color: '#3b82f6' },
  lunar_phase: { Icon: Moon, label: 'Phase lunaire', color: '#f5a623' },
  humidity: { Icon: Droplets, label: 'Humidité', color: '#22c55e' },
};

const IMPACT_COLORS = { primary: '#ef4444', secondary: '#f5a623', tertiary: '#6b7280' };

export const CorrelationMatrixWidget = ({ initialData }) => {
  const [data, setData] = useState(initialData || null);

  useEffect(() => {
    const unsub = EventBusV6.subscribe(CHANNELS.CORRELATION_UPDATED, setData);
    return unsub;
  }, []);

  if (!data?.correlation_matrix || !Object.keys(data.correlation_matrix).length) return (
    <Card data-testid="correlation-matrix-widget" className="bg-zinc-900 border-zinc-800">
      <CardContent className="p-6 text-center text-zinc-500">Corrélations — en attente</CardContent>
    </Card>
  );

  const entries = Object.entries(data.correlation_matrix);

  return (
    <Card data-testid="correlation-matrix-widget" className="bg-zinc-900 border-zinc-800">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-zinc-400 flex items-center gap-2">
          <Gauge className="w-4 h-4" /> CORRÉLATIONS MÉTÉO-FAUNE
          <Badge variant="outline" className="text-xs ml-auto border-zinc-700">{data.species}</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {entries.map(([key, val]) => {
          const cfg = FACTOR_CONFIG[key] || { Icon: Gauge, label: key, color: '#6b7280' };
          const strength = val.correlation_strength || 0;
          const absStrength = Math.abs(strength);
          const isNeg = strength < 0;
          return (
            <div key={key} data-testid={`correlation-${key}`} className="flex items-center gap-2">
              <cfg.Icon className="w-3.5 h-3.5 shrink-0" style={{ color: cfg.color }} />
              <span className="text-[11px] text-zinc-400 w-20 truncate">{cfg.label}</span>
              <div className="flex-1 h-2 bg-zinc-800 rounded-full overflow-hidden relative">
                <div className="absolute left-1/2 top-0 w-px h-full bg-zinc-600" />
                {isNeg ? (
                  <div className="absolute right-1/2 h-full rounded-l-full bg-red-500/70"
                    style={{ width: `${absStrength * 50}%` }} />
                ) : (
                  <div className="absolute left-1/2 h-full rounded-r-full"
                    style={{ width: `${absStrength * 50}%`, backgroundColor: cfg.color }} />
                )}
              </div>
              <span className="text-[10px] text-zinc-400 w-8 text-right">{strength > 0 ? '+' : ''}{strength.toFixed(2)}</span>
              <Badge className="text-[8px] px-1" style={{ backgroundColor: IMPACT_COLORS[val.impact] || '#6b7280', color: '#fff' }}>
                {val.impact}
              </Badge>
            </div>
          );
        })}
        {data.optimal_conditions && (
          <div className="mt-2 p-2 bg-zinc-800/50 rounded text-[10px] text-zinc-500">
            Optimal: {data.optimal_conditions.optimal_temp_min}°C — {data.optimal_conditions.optimal_temp_max}°C |
            Vent max: {data.optimal_conditions.max_wind_speed} km/h |
            Pression: {data.optimal_conditions.pressure_trend}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default CorrelationMatrixWidget;

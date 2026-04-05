/**
 * W12 — Contextual Advice Widget (Conseils IA)
 * Directive x7100-M4 Phase D | BCE-4X GOLDEN V6+
 *
 * Consomme : DC-11 (ContextualAdvice) via EB-16 (CONTEXTUAL_ADVICE_UPDATED)
 * Source : DFL.fetchContextualAdvice(userId, lat, lng)
 * ANTI-DOUBLON : ZERO logique IA, LECTURE exclusive DataContracts V6
 *
 * Fusions : M3 (prediction), M2 (POIs), M1 (legal), solunaire, meteo
 */
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { EventBusV6, CHANNELS } from '../../../services/EventBusV6';
import { Lightbulb, AlertTriangle, TrendingUp, Moon, MapPin, Shield, Target } from 'lucide-react';

const PRIORITY_CONFIG = {
  critical: { color: '#ef4444', icon: AlertTriangle, bg: 'bg-red-500/10' },
  high: { color: '#f5a623', icon: TrendingUp, bg: 'bg-orange-500/10' },
  medium: { color: '#3b82f6', icon: Lightbulb, bg: 'bg-blue-500/10' },
  low: { color: '#6b7280', icon: Lightbulb, bg: 'bg-zinc-500/10' },
};

const TYPE_ICONS = {
  prediction: TrendingUp,
  solunar: Moon,
  zone: MapPin,
  legal: Shield,
  species: Target,
  trend: TrendingUp,
  timing: null,
  progression: null,
};

export const AdviceWidget = ({ initialData }) => {
  const [data, setData] = useState(initialData || null);

  useEffect(() => {
    const unsub = EventBusV6.subscribe(CHANNELS.CONTEXTUAL_ADVICE_UPDATED, setData);
    return unsub;
  }, []);

  useEffect(() => {
    if (initialData) setData(initialData);
  }, [initialData]);

  if (!data) return (
    <Card data-testid="advice-widget" className="bg-zinc-900 border-zinc-800">
      <CardContent className="p-6 text-center text-zinc-500">Conseils IA — en attente de position</CardContent>
    </Card>
  );

  const adviceList = data.advice || [];
  const prediction = data.prediction || {};
  const solunar = data.solunar || {};
  const nearbyPois = data.nearby_pois || [];

  return (
    <Card data-testid="advice-widget" className="bg-zinc-900 border-zinc-800">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-sm">
          <Lightbulb className="w-4 h-4 text-amber-400" />
          Conseils IA
          <Badge variant="outline" className="ml-auto text-[9px] border-zinc-700 text-zinc-400">DC-11</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Prediction + Solunar compact */}
        <div className="grid grid-cols-2 gap-2">
          <div className="bg-zinc-800/50 rounded p-2">
            <div className="flex items-center gap-1 mb-1">
              <TrendingUp className="w-3 h-3 text-violet-400" />
              <span className="text-[10px] text-zinc-400">Prediction</span>
            </div>
            <div className="text-lg font-semibold" style={{ color: prediction.current_probability > 0.6 ? '#22c55e' : prediction.current_probability > 0.3 ? '#f5a623' : '#6b7280' }}>
              {Math.round((prediction.current_probability || 0) * 100)}%
            </div>
            <div className="text-[9px] text-zinc-500">Peak: {prediction.peak_hour || '?'}h | {prediction.trend || 'stable'}</div>
          </div>
          <div className="bg-zinc-800/50 rounded p-2">
            <div className="flex items-center gap-1 mb-1">
              <Moon className="w-3 h-3 text-amber-400" />
              <span className="text-[10px] text-zinc-400">Solunaire</span>
            </div>
            <div className="text-lg font-semibold text-amber-400">{solunar.score || 0}</div>
            <div className="text-[9px] text-zinc-500">{solunar.phase || 'N/A'} | {solunar.next_window || 'N/A'}</div>
          </div>
        </div>

        {/* Advice list */}
        {adviceList.length > 0 && (
          <div className="space-y-1.5">
            <div className="text-[10px] text-zinc-500 uppercase tracking-wider">Recommandations ({adviceList.length})</div>
            {adviceList.map((a, i) => {
              const cfg = PRIORITY_CONFIG[a.priority] || PRIORITY_CONFIG.low;
              const Icon = TYPE_ICONS[a.type] || Lightbulb;
              return (
                <div key={i} className={`flex items-start gap-2 rounded p-1.5 ${cfg.bg}`}>
                  <Icon className="w-3.5 h-3.5 mt-0.5 shrink-0" style={{ color: cfg.color }} />
                  <span className="text-xs text-zinc-300 leading-tight">{a.text}</span>
                </div>
              );
            })}
          </div>
        )}

        {adviceList.length === 0 && (
          <div className="text-center text-zinc-600 text-xs py-2">Aucun conseil pour cette position</div>
        )}

        {/* Nearby POIs */}
        {nearbyPois.length > 0 && (
          <div className="space-y-1 border-t border-zinc-800 pt-2">
            <div className="text-[10px] text-zinc-500 uppercase tracking-wider">POIs proches ({nearbyPois.length})</div>
            {nearbyPois.slice(0, 3).map((poi, i) => (
              <div key={i} className="flex items-center gap-2 text-xs">
                <MapPin className="w-3 h-3 text-cyan-400/60" />
                <span className="text-zinc-300 flex-1 truncate">{poi.name || poi.poi_id}</span>
                <span className="text-zinc-500">{poi.distance_m}m</span>
              </div>
            ))}
          </div>
        )}

        {/* Position info */}
        {data.position && (
          <div className="text-[9px] text-zinc-600 text-right">
            {data.position.lat?.toFixed(4)}, {data.position.lng?.toFixed(4)} | {data.species}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

/**
 * W11 — Navigation Session Widget (Routes & Waypoints)
 * Directive x7100-M4 Phase D | BCE-4X GOLDEN V6+
 *
 * Consomme : DC-10 (NavigationSession) via EB-15 (NAVIGATION_SESSION_UPDATED)
 * Source : DFL.fetchNavigationSession(sessionId)
 * ANTI-DOUBLON : ZERO logique de routing, LECTURE exclusive DataContracts V6
 */
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { EventBusV6, CHANNELS } from '../../../services/EventBusV6';
import { Navigation, MapPin, Clock, Route, Footprints, Target } from 'lucide-react';

const STATUS_CONFIG = {
  planned: { color: '#3b82f6', label: 'Planifie', bg: 'bg-blue-500/10' },
  active: { color: '#22c55e', label: 'En cours', bg: 'bg-green-500/10' },
  completed: { color: '#6b7280', label: 'Termine', bg: 'bg-zinc-500/10' },
};

export const NavigationWidget = ({ initialData }) => {
  const [session, setSession] = useState(initialData || null);

  useEffect(() => {
    const unsub = EventBusV6.subscribe(CHANNELS.NAVIGATION_SESSION_UPDATED, setSession);
    return unsub;
  }, []);

  useEffect(() => {
    if (initialData) setSession(initialData);
  }, [initialData]);

  if (!session || !session.session_id) return (
    <Card data-testid="navigation-widget" className="bg-zinc-900 border-zinc-800">
      <CardContent className="p-6 text-center text-zinc-500">Navigation — aucune session</CardContent>
    </Card>
  );

  const status = STATUS_CONFIG[session.status] || STATUS_CONFIG.planned;
  const summary = session.route_summary || {};
  const metrics = session.metrics || {};
  const waypoints = (session.waypoints || []).slice(0, 5);

  return (
    <Card data-testid="navigation-widget" className="bg-zinc-900 border-zinc-800">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-sm">
          <Navigation className="w-4 h-4 text-cyan-400" />
          Session Navigation
          <Badge variant="outline" className="ml-auto text-[9px] border-zinc-700 text-zinc-400">DC-10</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Status & target */}
        <div className="flex items-center gap-2">
          <Badge className={`text-[10px] ${status.bg}`} style={{ color: status.color, borderColor: status.color + '44' }}>
            {status.label}
          </Badge>
          <Target className="w-3 h-3 text-zinc-500" />
          <span className="text-xs text-zinc-300 capitalize">{session.target_species}</span>
          <span className="text-[10px] text-zinc-500 ml-auto">{session.zone_id}</span>
        </div>

        {/* Route summary */}
        <div className="grid grid-cols-3 gap-2 text-center">
          <div className="bg-zinc-800/50 rounded p-1.5">
            <Route className="w-3 h-3 text-cyan-400/60 mx-auto mb-0.5" />
            <div className="text-xs font-medium text-zinc-200">{summary.total_distance_m ? `${(summary.total_distance_m / 1000).toFixed(1)}km` : '—'}</div>
            <div className="text-[9px] text-zinc-500">Distance</div>
          </div>
          <div className="bg-zinc-800/50 rounded p-1.5">
            <Clock className="w-3 h-3 text-cyan-400/60 mx-auto mb-0.5" />
            <div className="text-xs font-medium text-zinc-200">{summary.total_eta_minutes || 0}min</div>
            <div className="text-[9px] text-zinc-500">ETA</div>
          </div>
          <div className="bg-zinc-800/50 rounded p-1.5">
            <MapPin className="w-3 h-3 text-cyan-400/60 mx-auto mb-0.5" />
            <div className="text-xs font-medium text-zinc-200">{session.waypoints_count || 0}</div>
            <div className="text-[9px] text-zinc-500">Waypoints</div>
          </div>
        </div>

        {/* Progress (active session) */}
        {session.status === 'active' && (
          <div className="space-y-1">
            <div className="flex justify-between text-[10px] text-zinc-500">
              <span>Progression</span>
              <span>{metrics.pois_visited || 0}/{session.waypoints_count || 0} POIs</span>
            </div>
            <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
              <div className="h-full bg-green-500 rounded-full transition-all duration-500"
                style={{ width: `${session.waypoints_count ? ((metrics.pois_visited || 0) / session.waypoints_count) * 100 : 0}%` }} />
            </div>
          </div>
        )}

        {/* Top Waypoints */}
        {waypoints.length > 0 && (
          <div className="space-y-1">
            <div className="text-[10px] text-zinc-500 uppercase tracking-wider">Top Waypoints</div>
            {waypoints.map((wp, i) => (
              <div key={i} className="flex items-center gap-2 py-0.5">
                <span className="w-4 h-4 rounded-full bg-zinc-800 flex items-center justify-center text-[9px] text-cyan-400 font-medium">
                  {i + 1}
                </span>
                <span className="text-xs text-zinc-300 flex-1 truncate">{wp.name || wp.poi_id}</span>
                <span className="text-[10px] text-zinc-500">{wp.distance_m}m</span>
                <div className="w-10 h-1 bg-zinc-800 rounded-full overflow-hidden">
                  <div className="h-full bg-cyan-500 rounded-full" style={{ width: `${(wp.score || 0) * 100}%` }} />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Completed metrics */}
        {session.status === 'completed' && (
          <div className="grid grid-cols-3 gap-2 text-center border-t border-zinc-800 pt-2">
            <div>
              <Footprints className="w-3 h-3 text-zinc-500 mx-auto mb-0.5" />
              <div className="text-xs text-zinc-300">{metrics.distance_walked_km || 0}km</div>
              <div className="text-[9px] text-zinc-500">Parcouru</div>
            </div>
            <div>
              <Clock className="w-3 h-3 text-zinc-500 mx-auto mb-0.5" />
              <div className="text-xs text-zinc-300">{metrics.duration_hours || 0}h</div>
              <div className="text-[9px] text-zinc-500">Duree</div>
            </div>
            <div>
              <MapPin className="w-3 h-3 text-zinc-500 mx-auto mb-0.5" />
              <div className="text-xs text-zinc-300">{metrics.pois_visited || 0}</div>
              <div className="text-[9px] text-zinc-500">Visites</div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

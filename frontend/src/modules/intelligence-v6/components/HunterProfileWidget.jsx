/**
 * W10 — Hunter Profile Widget (Profil Adaptatif)
 * Directive x7100-M4 Phase D | BCE-4X GOLDEN V6+
 * 
 * Consomme : DC-09 (HunterProfile) via EB-14 (HUNTER_PROFILE_UPDATED)
 * Source : DFL.fetchHunterProfile(userId)
 * ANTI-DOUBLON : ZERO logique de profil, LECTURE exclusive DataContracts V6
 */
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { EventBusV6, CHANNELS } from '../../../services/EventBusV6';
import { User, Target, MapPin, Clock, Mountain, Award } from 'lucide-react';

const SKILL_CONFIG = {
  debutant: { color: '#6b7280', label: 'Debutant', pct: 15 },
  intermediaire: { color: '#3b82f6', label: 'Intermediaire', pct: 40 },
  avance: { color: '#f5a623', label: 'Avance', pct: 70 },
  expert: { color: '#22c55e', label: 'Expert', pct: 95 },
};

const RADAR_FACTORS = [
  { key: 'species', label: 'Especes', icon: Target },
  { key: 'zones', label: 'Zones', icon: MapPin },
  { key: 'timing', label: 'Timing', icon: Clock },
  { key: 'endurance', label: 'Endurance', icon: Mountain },
  { key: 'success', label: 'Succes', icon: Award },
];

function computeRadar(profile) {
  if (!profile) return RADAR_FACTORS.map(() => 0);
  const sp = profile.species_preferences || [];
  const zp = profile.zone_preferences || [];
  const stats = profile.history_stats || {};
  const avgSuccess = sp.length > 0 ? sp.reduce((s, p) => s + (p.success_rate || 0), 0) / sp.length : 0;
  return [
    Math.min(1, sp.length / 5),
    Math.min(1, zp.length / 5),
    Math.min(1, (profile.time_preferences?.preferred_hours?.length || 0) / 6),
    Math.min(1, (stats.avg_distance_km || 0) / 15),
    Math.min(1, avgSuccess),
  ];
}

function RadarChart({ values }) {
  const cx = 70, cy = 70, r = 55;
  const n = values.length;
  const angles = values.map((_, i) => (Math.PI * 2 * i) / n - Math.PI / 2);
  const outerPoints = angles.map((a) => `${cx + r * Math.cos(a)},${cy + r * Math.sin(a)}`).join(' ');
  const midPoints = angles.map((a) => `${cx + r * 0.5 * Math.cos(a)},${cy + r * 0.5 * Math.sin(a)}`).join(' ');
  const dataPoints = angles.map((a, i) => {
    const v = values[i] || 0;
    return `${cx + r * v * Math.cos(a)},${cy + r * v * Math.sin(a)}`;
  }).join(' ');

  return (
    <svg viewBox="0 0 140 140" className="w-full max-w-[180px] mx-auto">
      <polygon points={outerPoints} fill="none" stroke="#374151" strokeWidth="0.5" />
      <polygon points={midPoints} fill="none" stroke="#374151" strokeWidth="0.5" strokeDasharray="2,2" />
      {angles.map((a, i) => (
        <line key={i} x1={cx} y1={cy} x2={cx + r * Math.cos(a)} y2={cy + r * Math.sin(a)} stroke="#374151" strokeWidth="0.5" />
      ))}
      <polygon points={dataPoints} fill="rgba(139,92,246,0.25)" stroke="#8b5cf6" strokeWidth="1.5" />
      {angles.map((a, i) => {
        const v = values[i] || 0;
        return <circle key={i} cx={cx + r * v * Math.cos(a)} cy={cy + r * v * Math.sin(a)} r="2.5" fill="#8b5cf6" />;
      })}
      {RADAR_FACTORS.map((f, i) => {
        const lx = cx + (r + 14) * Math.cos(angles[i]);
        const ly = cy + (r + 14) * Math.sin(angles[i]);
        return <text key={i} x={lx} y={ly} fill="#9ca3af" fontSize="7" textAnchor="middle" dominantBaseline="middle">{f.label}</text>;
      })}
    </svg>
  );
}

export const HunterProfileWidget = ({ initialData, userId }) => {
  const [profile, setProfile] = useState(initialData || null);

  useEffect(() => {
    const unsub = EventBusV6.subscribe(CHANNELS.HUNTER_PROFILE_UPDATED, setProfile);
    return unsub;
  }, []);

  useEffect(() => {
    if (initialData) setProfile(initialData);
  }, [initialData]);

  if (!profile) return (
    <Card data-testid="hunter-profile-widget" className="bg-zinc-900 border-zinc-800">
      <CardContent className="p-6 text-center text-zinc-500">Profil Chasseur — en attente</CardContent>
    </Card>
  );

  const skill = SKILL_CONFIG[profile.skill_level] || SKILL_CONFIG.intermediaire;
  const stats = profile.history_stats || {};
  const radarValues = computeRadar(profile);
  const topSpecies = (profile.species_affinity || profile.species_preferences || []).slice(0, 3);

  return (
    <Card data-testid="hunter-profile-widget" className="bg-zinc-900 border-zinc-800">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-sm">
          <User className="w-4 h-4 text-violet-400" />
          Profil Adaptatif
          <Badge variant="outline" className="ml-auto text-[9px] border-zinc-700 text-zinc-400">DC-09</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Skill Level */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-zinc-400">Niveau</span>
          <Badge className="text-[10px]" style={{ backgroundColor: skill.color + '22', color: skill.color, borderColor: skill.color + '44' }}>
            {skill.label}
          </Badge>
          <div className="flex-1 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
            <div className="h-full rounded-full transition-all duration-700" style={{ width: `${skill.pct}%`, backgroundColor: skill.color }} />
          </div>
        </div>

        {/* Radar Chart */}
        <RadarChart values={radarValues} />

        {/* Stats compactes */}
        <div className="grid grid-cols-3 gap-2 text-center">
          <div className="bg-zinc-800/50 rounded p-1.5">
            <div className="text-xs font-medium text-zinc-200">{stats.total_trips || 0}</div>
            <div className="text-[9px] text-zinc-500">Sorties</div>
          </div>
          <div className="bg-zinc-800/50 rounded p-1.5">
            <div className="text-xs font-medium text-zinc-200">{stats.total_hours || 0}h</div>
            <div className="text-[9px] text-zinc-500">Heures</div>
          </div>
          <div className="bg-zinc-800/50 rounded p-1.5">
            <div className="text-xs font-medium text-zinc-200">{stats.avg_distance_km || 0}km</div>
            <div className="text-[9px] text-zinc-500">Moy. dist.</div>
          </div>
        </div>

        {/* Top especes */}
        {topSpecies.length > 0 && (
          <div className="space-y-1">
            <div className="text-[10px] text-zinc-500 uppercase tracking-wider">Affinites especes</div>
            {topSpecies.map((sp, i) => (
              <div key={i} className="flex items-center gap-2">
                <Target className="w-3 h-3 text-violet-400/60" />
                <span className="text-xs text-zinc-300 flex-1 capitalize">{sp.species}</span>
                <div className="w-16 h-1 bg-zinc-800 rounded-full overflow-hidden">
                  <div className="h-full bg-violet-500 rounded-full" style={{ width: `${(sp.affinity || sp.frequency || 0) * 100}%` }} />
                </div>
                <span className="text-[10px] text-zinc-500 w-8 text-right">{Math.round((sp.affinity || sp.frequency || 0) * 100)}%</span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

import React, { useState } from 'react';
import { Crosshair, Wind, Mountain, Droplets, TreePine, ShieldAlert, Thermometer, Navigation, MapPin, ChevronDown, ChevronUp, Target, Eye } from 'lucide-react';
import PinnablePanel from './PinnablePanel';

/**
 * StandDetailPanel.jsx — Panneau PLEINE PAGE Affut naturel
 * x4700-VISUAL_REDESIGN-R2 CORRECTIF: 100vh, ZERO scroll, X + Imprimer fixes
 * Style: Dashboard BIONIC premium
 */

const BIONIC = {
  green: '#00C853', yellow: '#F9D423', orange: '#FF9800', red: '#D32F2F',
  blue: '#2196F3', card: '#1a1a2e', cardBorder: 'rgba(255,255,255,0.06)',
};

const FACTOR_META = {
  wind: { label: 'Vent', icon: Wind, accent: BIONIC.blue },
  corridor: { label: 'Corridor', icon: Navigation, accent: '#9C27B0' },
  topography: { label: 'Topo', icon: Mountain, accent: BIONIC.orange },
  cover: { label: 'Couvert', icon: TreePine, accent: BIONIC.green },
  hydrology: { label: 'Hydro', icon: Droplets, accent: BIONIC.blue },
  pressure: { label: 'Pression', icon: ShieldAlert, accent: BIONIC.red },
  coolzone: { label: 'Fraicheur', icon: Thermometer, accent: '#00BCD4' },
};

function getScoreGrade(score) {
  if (score >= 80) return { label: 'EXCELLENT', color: BIONIC.green, bg: 'rgba(0,200,83,0.12)' };
  if (score >= 65) return { label: 'BON', color: BIONIC.yellow, bg: 'rgba(249,212,35,0.12)' };
  if (score >= 50) return { label: 'MODERE', color: BIONIC.orange, bg: 'rgba(255,152,0,0.12)' };
  return { label: 'FAIBLE', color: BIONIC.red, bg: 'rgba(211,47,47,0.12)' };
}

function getBarColor(s) { return s >= 75 ? BIONIC.green : s >= 55 ? BIONIC.orange : BIONIC.red; }

const Card = ({ children, testId, className = '' }) => (
  <div className={`rounded-[14px] border p-3 ${className}`} style={{ backgroundColor: BIONIC.card, borderColor: BIONIC.cardBorder, boxShadow: '0 2px 8px rgba(0,0,0,0.18)' }} data-testid={testId}>{children}</div>
);

const StandDetailPanel = ({ stand, onClose }) => {
  const [showJustif, setShowJustif] = useState(false);
  if (!stand) return null;

  const grade = getScoreGrade(stand.score);
  const j = stand.justification || {};
  const justifSections = [
    { key: 'analyse_vent', title: 'Vent', accent: BIONIC.blue },
    { key: 'lecture_corridor', title: 'Corridor', accent: '#9C27B0' },
    { key: 'lecture_zones_600m', title: 'Zones 600m', accent: BIONIC.orange },
    { key: 'lecture_topographie', title: 'Topographie', accent: BIONIC.green },
    { key: 'lecture_hydrographie', title: 'Hydrographie', accent: BIONIC.blue },
    { key: 'analyse_pression', title: 'Pression', accent: BIONIC.orange },
    { key: 'justification_type_affut', title: "Type d'affut", accent: BIONIC.red },
    { key: 'justification_orientation', title: 'Orientation', accent: BIONIC.green },
    { key: 'justification_score', title: 'Score', accent: BIONIC.yellow },
    { key: 'recommandations_pratiques', title: 'Recommandations', accent: BIONIC.orange },
  ].filter(s => j[s.key]);

  return (
    <PinnablePanel
      title="Affut naturel"
      subtitle={`Score ${stand.score}/100 | ${stand.type_name || stand.type_key} | ${stand.distance_to_center_m || '?'}m`}
      icon={Crosshair}
      accentColor={grade.color}
      onClose={onClose}
      defaultWidth={580}
      maxHeight="100vh"
      testId="stand-detail-panel"
      fullHeight={true}
    >
      {/* GRID LAYOUT — 2 colonnes pour tout afficher en 100vh sans scroll */}
      <div className="h-full grid grid-cols-2 gap-3 p-4 overflow-hidden" data-testid="stand-detail-content">

        {/* COLONNE GAUCHE */}
        <div className="flex flex-col gap-3 min-h-0">
          {/* Score Header */}
          <Card testId="stand-score-card">
            <div className="flex items-center gap-3">
              <div className="w-14 h-14 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: `linear-gradient(135deg, ${grade.color}22, ${grade.color}08)`, border: `2.5px solid ${grade.color}` }} data-testid="stand-score-badge">
                <span className="text-2xl font-black" style={{ color: grade.color }}>{stand.score}</span>
              </div>
              <div className="min-w-0">
                <div className="text-white text-sm font-bold truncate">{stand.type_name || stand.type_key}</div>
                <div className="text-gray-400 text-xs mt-0.5">
                  {stand.corridor_level && <span className="font-semibold" style={{ color: '#9C27B0' }}>{stand.corridor_level}</span>}
                  {stand.corridor_distance_m != null && <span className="ml-1">{stand.corridor_distance_m}m</span>}
                </div>
                <div className="flex items-center gap-1 text-gray-500 text-[10px] mt-0.5">
                  <MapPin className="h-2.5 w-2.5" /><span>{stand.distance_to_center_m || '?'}m</span>
                </div>
              </div>
              <div className="px-2 py-1 rounded-lg text-[10px] font-bold ml-auto flex-shrink-0" style={{ backgroundColor: grade.bg, color: grade.color }} data-testid="stand-grade-badge">{grade.label}</div>
            </div>
          </Card>

          {/* Facteurs — BarFlow */}
          <Card testId="stand-factors-card" className="flex-1 flex flex-col min-h-0">
            <div className="flex items-center gap-2 mb-2">
              <Target className="h-3.5 w-3.5" style={{ color: BIONIC.yellow }} />
              <span className="text-xs font-bold text-white">Facteurs d'analyse</span>
              <span className="text-[10px] text-gray-500 ml-auto">7 criteres</span>
            </div>
            <div className="space-y-1.5 flex-1" data-testid="stand-factor-bars">
              {Object.entries(FACTOR_META).map(([key, meta]) => {
                const score = stand.factors?.[key]?.score ?? 0;
                const bc = getBarColor(score);
                return (
                  <div key={key} className="flex items-center gap-2" data-testid={`stand-factor-${key}`}>
                    <div className="w-5 h-5 rounded flex items-center justify-center flex-shrink-0" style={{ backgroundColor: `${meta.accent}18` }}>
                      <meta.icon className="h-3 w-3" style={{ color: meta.accent }} />
                    </div>
                    <span className="text-[10px] text-gray-300 w-16 flex-shrink-0">{meta.label}</span>
                    <div className="flex-1 h-[5px] rounded-full overflow-hidden" style={{ backgroundColor: 'rgba(255,255,255,0.04)' }}>
                      <div className="h-full rounded-full" style={{ width: `${score}%`, backgroundColor: bc, transition: 'width 0.6s ease' }} />
                    </div>
                    <span className="text-xs font-bold w-8 text-right tabular-nums" style={{ color: bc }}>{Math.round(score)}</span>
                  </div>
                );
              })}
            </div>
          </Card>
        </div>

        {/* COLONNE DROITE */}
        <div className="flex flex-col gap-3 min-h-0">
          {/* Coherence ecologique */}
          {stand.factors?.corridor && (
            <Card testId="stand-corridor-card">
              <div className="flex items-center gap-2 mb-2">
                <Navigation className="h-3.5 w-3.5" style={{ color: '#9C27B0' }} />
                <span className="text-xs font-bold text-white">Coherence ecologique</span>
              </div>
              <div className="grid grid-cols-2 gap-x-4 gap-y-1">
                {[
                  { label: 'Corridor', value: stand.factors.corridor.name, c: '#CE93D8' },
                  { label: 'Niveau', value: stand.factors.corridor.level, c: '#CE93D8' },
                  { label: 'Distance', value: `${stand.factors.corridor.distance_m}m`, c: '#fff' },
                  { label: 'Frequence', value: stand.factors.corridor.frequency, c: '#fff' },
                  stand.factors.corridor.visible_length_m && { label: 'Visible', value: `${stand.factors.corridor.visible_length_m}m`, c: '#fff' },
                  stand.factors.feeding_distance_m && { label: 'Alimentation', value: `${stand.factors.feeding_distance_m}m`, c: BIONIC.green },
                ].filter(Boolean).map((item, i) => (
                  <div key={i} className="flex justify-between items-center py-1 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
                    <span className="text-[10px] text-gray-500">{item.label}</span>
                    <span className="text-[10px] font-semibold" style={{ color: item.c }}>{item.value}</span>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Orientation + Hauteur */}
          <div className="grid grid-cols-2 gap-2">
            <Card testId="stand-orientation-card">
              <div className="flex items-center gap-1.5 mb-1">
                <Eye className="h-3 w-3" style={{ color: BIONIC.blue }} />
                <span className="text-[10px] font-bold text-gray-400">Orientation</span>
              </div>
              <div className="text-base font-black text-white">{stand.orientation_label || '?'}</div>
              <div className="text-[10px] text-gray-500">{stand.orientation_deg || '?'}</div>
            </Card>
            <Card testId="stand-height-card">
              <div className="flex items-center gap-1.5 mb-1">
                <Mountain className="h-3 w-3" style={{ color: BIONIC.orange }} />
                <span className="text-[10px] font-bold text-gray-400">Hauteur</span>
              </div>
              <div className="text-base font-black text-white">{stand.height_m || '?'}m</div>
              <div className="text-[10px] text-gray-500">Rang #{stand.rank}</div>
            </Card>
          </div>

          {/* Justification repliable */}
          {justifSections.length > 0 && (
            <Card testId="stand-justif-card" className="flex-1 flex flex-col min-h-0">
              <button onClick={() => setShowJustif(v => !v)} className="w-full flex items-center justify-between" data-testid="stand-justif-toggle">
                <div className="flex items-center gap-2">
                  <Crosshair className="h-3.5 w-3.5" style={{ color: BIONIC.yellow }} />
                  <span className="text-xs font-bold text-white">Justification</span>
                  <span className="text-[10px] text-gray-500">({justifSections.length})</span>
                </div>
                {showJustif ? <ChevronUp className="h-3.5 w-3.5 text-gray-500" /> : <ChevronDown className="h-3.5 w-3.5 text-gray-500" />}
              </button>
              {showJustif && (
                <div className="mt-2 space-y-1.5 overflow-y-auto flex-1 min-h-0" data-testid="stand-justif-content">
                  {justifSections.map(({ key, title, accent }) => (
                    <div key={key} className="rounded-lg p-2" style={{ backgroundColor: `${accent}08`, borderLeft: `2px solid ${accent}` }} data-testid={`stand-justify-${key}`}>
                      <div className="text-[10px] font-bold" style={{ color: accent }}>{title}</div>
                      <p className="text-[10px] text-gray-400 leading-relaxed line-clamp-2">{j[key]}</p>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          )}
        </div>

        {/* FOOTER — pleine largeur */}
        <div className="col-span-2 text-center text-[10px] text-gray-600" data-testid="stand-footer">
          x4700-R2 | Affut naturel | Dashboard BIONIC | STEEVE-MAX V6
        </div>
      </div>
    </PinnablePanel>
  );
};

export default StandDetailPanel;

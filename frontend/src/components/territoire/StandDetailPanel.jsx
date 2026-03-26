import React, { useState } from 'react';
import { Crosshair, Wind, Mountain, Droplets, TreePine, ShieldAlert, Thermometer, Navigation, MapPin, ChevronDown, ChevronUp, Target, Eye } from 'lucide-react';
import PinnablePanel from './PinnablePanel';

/**
 * StandDetailPanel.jsx — Panneau premium Affut naturel
 * DIRECTIVE x4700-VISUAL_REDESIGN-R2-DASHBOARD_STYLE
 * Style: Dashboard BIONIC cards premium
 * Palette: #00C853, #F9D423, #FF9800, #D32F2F, #2196F3, #ECEFF1, #37474F
 */

const BIONIC = {
  green: '#00C853',
  yellow: '#F9D423',
  orange: '#FF9800',
  red: '#D32F2F',
  blue: '#2196F3',
  light: '#ECEFF1',
  dark: '#37474F',
  card: '#1a1a2e',
  cardBorder: 'rgba(255,255,255,0.06)',
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

function getBarColor(score) {
  if (score >= 75) return BIONIC.green;
  if (score >= 55) return BIONIC.orange;
  return BIONIC.red;
}

const Card = ({ children, className = '', testId, noPad = false }) => (
  <div
    className={`rounded-[14px] border ${className}`}
    style={{ backgroundColor: BIONIC.card, borderColor: BIONIC.cardBorder, boxShadow: '0 2px 8px rgba(0,0,0,0.18)' }}
    data-testid={testId}
  >
    {!noPad ? <div className="p-4">{children}</div> : children}
  </div>
);

const StandDetailPanel = ({ stand, onClose }) => {
  const [showJustif, setShowJustif] = useState(false);

  if (!stand) return null;

  const grade = getScoreGrade(stand.score);
  const j = stand.justification || {};

  const justifSections = [
    { key: 'analyse_vent', title: 'Analyse du vent', accent: BIONIC.blue },
    { key: 'lecture_corridor', title: 'Lecture corridor', accent: '#9C27B0' },
    { key: 'lecture_zones_600m', title: 'Zones 600m', accent: BIONIC.orange },
    { key: 'lecture_topographie', title: 'Topographie', accent: BIONIC.green },
    { key: 'lecture_hydrographie', title: 'Hydrographie', accent: BIONIC.blue },
    { key: 'lecture_zones_fraicheur', title: 'Zones fraicheur', accent: '#00BCD4' },
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
      showPrint={true}
      fullHeight={true}
    >
      <div className="p-4 space-y-3 flex flex-col" style={{ maxWidth: 620 }} data-testid="stand-detail-content">

        {/* HEADER PREMIUM — Score + Grade + Distance */}
        <Card testId="stand-score-card">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div
                className="w-[68px] h-[68px] rounded-2xl flex items-center justify-center"
                style={{ background: `linear-gradient(135deg, ${grade.color}22, ${grade.color}08)`, border: `2.5px solid ${grade.color}` }}
                data-testid="stand-score-badge"
              >
                <span className="text-2xl font-black" style={{ color: grade.color }}>{stand.score}</span>
              </div>
              <div>
                <div className="text-white text-base font-bold">{stand.type_name || stand.type_key}</div>
                <div className="text-gray-400 text-sm mt-0.5">
                  {stand.corridor_level && <span className="font-semibold" style={{ color: '#9C27B0' }}>{stand.corridor_level}</span>}
                  {stand.corridor_distance_m != null && <span className="ml-1.5">{stand.corridor_distance_m}m du corridor</span>}
                </div>
                <div className="flex items-center gap-1 text-gray-500 text-xs mt-1">
                  <MapPin className="h-3 w-3" />
                  <span>{stand.distance_to_center_m || '?'}m du centre</span>
                </div>
              </div>
            </div>
            <div
              className="px-3 py-1.5 rounded-xl text-xs font-bold tracking-wide"
              style={{ backgroundColor: grade.bg, color: grade.color, border: `1px solid ${grade.color}30` }}
              data-testid="stand-grade-badge"
            >
              {grade.label}
            </div>
          </div>
        </Card>

        {/* FACTEURS — BarFlow premium */}
        <Card testId="stand-factors-card">
          <div className="flex items-center gap-2 mb-4">
            <Target className="h-4 w-4" style={{ color: BIONIC.yellow }} />
            <span className="text-sm font-bold text-white">Facteurs d'analyse</span>
            <span className="text-xs text-gray-500 ml-auto">7 criteres</span>
          </div>
          <div className="space-y-2" data-testid="stand-factor-bars">
            {Object.entries(FACTOR_META).map(([key, meta]) => {
              const score = stand.factors?.[key]?.score ?? 0;
              const barColor = getBarColor(score);
              return (
                <div key={key} className="flex items-center gap-3" data-testid={`stand-factor-${key}`}>
                  <div className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0" style={{ backgroundColor: `${meta.accent}18` }}>
                    <meta.icon className="h-3.5 w-3.5" style={{ color: meta.accent }} />
                  </div>
                  <span className="text-xs text-gray-300 w-20 flex-shrink-0 font-medium">{meta.label}</span>
                  <div className="flex-1 h-[6px] rounded-full overflow-hidden" style={{ backgroundColor: 'rgba(255,255,255,0.04)' }}>
                    <div
                      className="h-full rounded-full"
                      style={{ width: `${score}%`, backgroundColor: barColor, transition: 'width 0.6s ease' }}
                    />
                  </div>
                  <span className="text-sm font-bold w-10 text-right tabular-nums" style={{ color: barColor }}>
                    {Math.round(score)}
                  </span>
                </div>
              );
            })}
          </div>
        </Card>

        {/* COHERENCE ECOLOGIQUE */}
        {stand.factors?.corridor && (
          <Card testId="stand-corridor-card">
            <div className="flex items-center gap-2 mb-3">
              <Navigation className="h-4 w-4" style={{ color: '#9C27B0' }} />
              <span className="text-sm font-bold text-white">Coherence ecologique</span>
            </div>
            <div className="grid grid-cols-2 gap-x-6 gap-y-2">
              {[
                { label: 'Corridor', value: stand.factors.corridor.name, color: '#CE93D8' },
                { label: 'Niveau', value: stand.factors.corridor.level, color: '#CE93D8' },
                { label: 'Distance', value: `${stand.factors.corridor.distance_m}m`, color: '#fff' },
                { label: 'Frequence', value: stand.factors.corridor.frequency, color: '#fff' },
                stand.factors.corridor.visible_length_m && { label: 'Visible', value: `${stand.factors.corridor.visible_length_m}m`, color: '#fff' },
                stand.factors.feeding_distance_m && { label: 'Alimentation', value: `${stand.factors.feeding_distance_m}m`, color: BIONIC.green },
                stand.factors.bedding_distance_m && { label: 'Repos', value: `${stand.factors.bedding_distance_m}m`, color: BIONIC.blue },
                stand.factors.rut_distance_m && { label: 'Zone rut', value: `${stand.factors.rut_distance_m}m`, color: BIONIC.red },
              ].filter(Boolean).map((item, i) => (
                <div key={i} className="flex justify-between items-center py-1.5 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
                  <span className="text-xs text-gray-500">{item.label}</span>
                  <span className="text-xs font-semibold" style={{ color: item.color }}>{item.value}</span>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* ORIENTATION + HAUTEUR */}
        <div className="grid grid-cols-2 gap-3">
          <Card testId="stand-orientation-card">
            <div className="flex items-center gap-2 mb-2">
              <Eye className="h-3.5 w-3.5" style={{ color: BIONIC.blue }} />
              <span className="text-xs font-bold text-gray-400">Orientation</span>
            </div>
            <div className="text-lg font-black text-white">{stand.orientation_label || '?'}</div>
            <div className="text-xs text-gray-500 mt-0.5">{stand.orientation_deg || '?'}</div>
          </Card>
          <Card testId="stand-height-card">
            <div className="flex items-center gap-2 mb-2">
              <Mountain className="h-3.5 w-3.5" style={{ color: BIONIC.orange }} />
              <span className="text-xs font-bold text-gray-400">Hauteur</span>
            </div>
            <div className="text-lg font-black text-white">{stand.height_m || '?'}m</div>
            <div className="text-xs text-gray-500 mt-0.5">Rang #{stand.rank}</div>
          </Card>
        </div>

        {/* JUSTIFICATION REPLIABLE */}
        {justifSections.length > 0 && (
          <Card testId="stand-justif-card" noPad>
            <button
              onClick={() => setShowJustif(v => !v)}
              className="w-full flex items-center justify-between p-4 hover:bg-white/[0.02] transition-colors rounded-[14px]"
              data-testid="stand-justif-toggle"
            >
              <div className="flex items-center gap-2">
                <Crosshair className="h-4 w-4" style={{ color: BIONIC.yellow }} />
                <span className="text-sm font-bold text-white">Justification professionnelle</span>
                <span className="text-xs text-gray-500 ml-1">({justifSections.length})</span>
              </div>
              {showJustif ? <ChevronUp className="h-4 w-4 text-gray-500" /> : <ChevronDown className="h-4 w-4 text-gray-500" />}
            </button>
            {showJustif && (
              <div className="px-4 pb-4 space-y-2.5" data-testid="stand-justif-content">
                {justifSections.map(({ key, title, accent }) => (
                  <div
                    key={key}
                    className="rounded-xl p-3"
                    style={{ backgroundColor: `${accent}08`, borderLeft: `3px solid ${accent}` }}
                    data-testid={`stand-justify-${key}`}
                  >
                    <div className="text-xs font-bold mb-1" style={{ color: accent }}>{title}</div>
                    <p className="text-xs text-gray-400 leading-relaxed whitespace-pre-line">{j[key]}</p>
                  </div>
                ))}
              </div>
            )}
          </Card>
        )}

        {/* FOOTER */}
        <div className="text-center text-[10px] text-gray-600 pt-1" data-testid="stand-footer">
          x4700-R2 | Dashboard BIONIC Style | STEEVE-MAX V6
        </div>
      </div>
    </PinnablePanel>
  );
};

export default StandDetailPanel;

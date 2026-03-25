import React from 'react';
import { Crosshair, Wind, Mountain, Droplets, TreePine, ShieldAlert, Thermometer, Navigation, MapPin } from 'lucide-react';
import PinnablePanel from './PinnablePanel';

/**
 * StandDetailPanel.jsx — Panneau détaillé d'un affût recommandé
 * DIRECTIVE STEEVE-MAX x4520-E: PinnablePanel V2 (pleine page, fixable, scrollable)
 * Remplace le popup Leaflet natif par un vrai panneau React
 */

const FACTOR_META = {
  wind: { label: 'Vent', icon: Wind, color: '#3498DB' },
  corridor: { label: 'Corridor', icon: Navigation, color: '#9B59B6' },
  topography: { label: 'Topo', icon: Mountain, color: '#F39C12' },
  cover: { label: 'Couvert', icon: TreePine, color: '#2ECC71' },
  hydrology: { label: 'Hydro', icon: Droplets, color: '#3498DB' },
  pressure: { label: 'Pression', icon: ShieldAlert, color: '#E74C3C' },
  coolzone: { label: 'Fraicheur', icon: Thermometer, color: '#1ABC9C' },
};

const StandDetailPanel = ({ stand, onClose }) => {
  if (!stand) return null;

  const scoreColor = stand.score > 75 ? '#2ECC71' : stand.score > 55 ? '#F39C12' : '#E74C3C';
  const j = stand.justification || {};

  const sections = [
    { key: 'analyse_vent', title: 'Analyse du vent', color: '#3498DB' },
    { key: 'lecture_corridor', title: 'Lecture corridor', color: '#9B59B6' },
    { key: 'lecture_zones_600m', title: 'Zones 600m', color: '#FF6B35' },
    { key: 'lecture_topographie', title: 'Topographie', color: '#27AE60' },
    { key: 'lecture_hydrographie', title: 'Hydrographie', color: '#3498DB' },
    { key: 'lecture_zones_fraicheur', title: 'Zones fraicheur', color: '#1ABC9C' },
    { key: 'analyse_pression', title: 'Pression', color: '#E67E22' },
    { key: 'justification_type_affut', title: 'Type d\'affut', color: '#E74C3C' },
    { key: 'justification_orientation', title: 'Orientation', color: '#2ECC71' },
    { key: 'justification_score', title: 'Score', color: '#F39C12' },
    { key: 'recommandations_pratiques', title: 'Recommandations', color: '#FF6B35' },
  ].filter(s => j[s.key]);

  return (
    <PinnablePanel
      title={`Affut ${stand.type_name || stand.type_key}`}
      subtitle={`Rang #${stand.rank} | ${stand.orientation_label} (${stand.orientation_deg}) | ${stand.height_m}m`}
      icon={Crosshair}
      accentColor={scoreColor}
      onClose={onClose}
      defaultWidth={400}
      maxHeight="85vh"
      testId="stand-detail-panel"
    >
      <div className="p-4 space-y-4" data-testid="stand-detail-content">
        {/* Score header */}
        <div className="flex items-center justify-between" data-testid="stand-score-header">
          <div className="flex items-center gap-3">
            <div
              className="w-14 h-14 rounded-full flex items-center justify-center text-xl font-black"
              style={{ border: `3px solid ${scoreColor}`, color: scoreColor }}
              data-testid="stand-score-badge"
            >
              {stand.score}
            </div>
            <div>
              <div className="text-white text-sm font-bold">{stand.type_name || stand.type_key}</div>
              <div className="text-gray-500 text-xs">
                {stand.corridor_level && (
                  <span className="text-purple-400 font-semibold mr-2">{stand.corridor_level}</span>
                )}
                {stand.corridor_distance_m != null && `${stand.corridor_distance_m}m du corridor`}
              </div>
              {stand.distance_to_center_m != null && (
                <div className="text-gray-600 text-xs mt-0.5">
                  <MapPin className="inline h-3 w-3 mr-1" />{stand.distance_to_center_m}m du centre
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Factor bars */}
        <div className="space-y-1.5" data-testid="stand-factor-bars">
          <div className="text-xs font-semibold text-amber-400 mb-2">Facteurs (7)</div>
          {Object.entries(FACTOR_META).map(([key, meta]) => {
            const score = stand.factors?.[key]?.score ?? 0;
            const barColor = score > 70 ? '#2ECC71' : score > 50 ? '#F39C12' : '#E74C3C';
            return (
              <div key={key} className="flex items-center gap-2" data-testid={`stand-factor-${key}`}>
                <meta.icon className="h-3.5 w-3.5 flex-shrink-0" style={{ color: meta.color }} />
                <span className="text-xs text-gray-400 w-16 flex-shrink-0">{meta.label}</span>
                <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all"
                    style={{ width: `${score}%`, backgroundColor: barColor }}
                  />
                </div>
                <span className="text-xs font-bold w-8 text-right" style={{ color: barColor }}>
                  {Math.round(score)}
                </span>
              </div>
            );
          })}
        </div>

        {/* Ecological coherence */}
        {stand.factors?.corridor && (
          <div className="bg-[#0d0d18] rounded-xl p-3 border border-purple-500/20" data-testid="stand-corridor-detail">
            <div className="text-xs font-semibold text-purple-400 mb-1.5">Coherence ecologique</div>
            <div className="grid grid-cols-2 gap-2 text-xs text-gray-400">
              <div>Corridor: <span className="text-purple-300 font-semibold">{stand.factors.corridor.name}</span></div>
              <div>Niveau: <span className="text-purple-300 font-semibold">{stand.factors.corridor.level}</span></div>
              <div>Distance: <span className="text-white font-semibold">{stand.factors.corridor.distance_m}m</span></div>
              <div>Frequence: <span className="text-white">{stand.factors.corridor.frequency}</span></div>
              {stand.factors.corridor.visible_length_m && (
                <div>Visible: <span className="text-white">{stand.factors.corridor.visible_length_m}m</span></div>
              )}
              {stand.factors.feeding_distance_m && (
                <div>Alimentation: <span className="text-green-400">{stand.factors.feeding_distance_m}m</span></div>
              )}
              {stand.factors.bedding_distance_m && (
                <div>Repos: <span className="text-blue-400">{stand.factors.bedding_distance_m}m</span></div>
              )}
              {stand.factors.rut_distance_m && (
                <div>Zone rut: <span className="text-red-400">{stand.factors.rut_distance_m}m</span></div>
              )}
            </div>
          </div>
        )}

        {/* Justification sections */}
        {sections.length > 0 && (
          <div className="space-y-2" data-testid="stand-justifications">
            <div className="text-xs font-semibold text-amber-400">Justification professionnelle</div>
            {sections.map(({ key, title, color }) => (
              <div
                key={key}
                className="bg-[#0d0d18] rounded-lg p-3 border-l-2"
                style={{ borderLeftColor: color }}
                data-testid={`stand-justify-${key}`}
              >
                <div className="text-xs font-semibold mb-1" style={{ color }}>{title}</div>
                <p className="text-xs text-gray-400 leading-relaxed whitespace-pre-line">{j[key]}</p>
              </div>
            ))}
          </div>
        )}

        {/* Footer */}
        <div className="text-center text-[10px] text-gray-600 pt-2 border-t border-gray-800/50" data-testid="stand-footer">
          x4520-E | PinnablePanel V2 | STEEVE-MAX V6
        </div>
      </div>
    </PinnablePanel>
  );
};

export default StandDetailPanel;

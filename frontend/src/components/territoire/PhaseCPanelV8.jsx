/**
 * PhaseCPanelV8.jsx — Panneau institutionnel Phase C
 * ====================================================
 * V8-ULTIME-INSTITUTIONNEL-Omega
 * Thermal + Scenario + Multi-Engine dans un seul panneau TERRITOIRE
 * ZERO duplication, ZERO panneau supplementaire
 */
import React, { useState, useEffect, useCallback } from 'react';
import { X, Thermometer, Zap, BarChart3, Wind, ChevronDown, ChevronUp, Loader2 } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const ScoreBar = ({ label, value, max = 100, color = '#F5A623' }) => (
  <div className="flex items-center gap-2">
    <span className="text-[10px] text-gray-500 w-[72px] shrink-0">{label}</span>
    <div className="flex-1 h-1.5 bg-gray-800 rounded-full overflow-hidden">
      <div className="h-full rounded-full transition-all duration-500" style={{ width: `${Math.min(100, (value / max) * 100)}%`, background: color }} />
    </div>
    <span className="text-[10px] text-gray-400 w-8 text-right">{typeof value === 'number' ? value.toFixed?.(1) ?? value : value}</span>
  </div>
);

const ZONE_COLORS = { extreme_froid: '#3B82F6', froid: '#60A5FA', optimal: '#10B981', chaud: '#F59E0B', extreme_chaud: '#EF4444' };
const ZONE_LABELS = { extreme_froid: 'Extreme froid', froid: 'Froid', optimal: 'Optimal', chaud: 'Chaud', extreme_chaud: 'Extreme chaud' };
const VERDICT_COLORS = { FAVORABLE: '#10B981', NEUTRE: '#F59E0B', DEFAVORABLE: '#EF4444' };

const PhaseCPanelV8 = ({ waypointCenter, selectedSpecies, onClose }) => {
  const [activeSection, setActiveSection] = useState('multi');
  const [thermal, setThermal] = useState(null);
  const [multiScore, setMultiScore] = useState(null);
  const [scenarios, setScenarios] = useState([]);
  const [loading, setLoading] = useState(false);
  const [expandedScenario, setExpandedScenario] = useState(null);

  const fetchData = useCallback(async () => {
    const lat = waypointCenter?.lat;
    const lng = waypointCenter?.lng;
    if (!lat || !lng) return;
    const sp = selectedSpecies === 'tous' ? 'cerf' : (selectedSpecies || 'cerf');
    setLoading(true);
    try {
      const [thermalRes, multiRes] = await Promise.all([
        fetch(`${API}/api/v8/engines/thermal?lat=${lat}&lon=${lng}`).then(r => r.json()),
        fetch(`${API}/api/v8/engines/multi-score?lat=${lat}&lon=${lng}&species=${sp}`).then(r => r.json()),
      ]);
      setThermal(thermalRes);
      setMultiScore(multiRes);

      const presetIds = ['chasse_matin', 'chasse_soir', 'rut_peak', 'canicule', 'tempete_neige', 'vent_fort'];
      const scenarioResults = await Promise.all(
        presetIds.map(id =>
          fetch(`${API}/api/v8/engines/scenario?lat=${lat}&lon=${lng}&species=${sp}&scenario=${id}`).then(r => r.json())
        )
      );
      setScenarios(scenarioResults);
    } catch (e) {
      console.error('[PHASE-C]', e);
    } finally {
      setLoading(false);
    }
  }, [waypointCenter?.lat, waypointCenter?.lng, selectedSpecies]);

  useEffect(() => { fetchData(); }, [fetchData]);

  return (
    <div className="fixed top-[180px] right-0 z-[1100] w-[340px] bg-[#0c0c14]/95 backdrop-blur-xl border-l border-gray-800/50 overflow-y-auto" style={{ height: 'calc(100vh - 180px)' }} data-testid="phase-c-panel">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-[#0c0c14]/98 border-b border-gray-800/50 p-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Zap className="h-4 w-4 text-amber-400" />
            <span className="text-sm font-bold text-white tracking-wide">MOTEURS V8</span>
            <span className="text-[9px] px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-400 font-semibold">PHASE C</span>
          </div>
          <button onClick={onClose} className="p-1 rounded hover:bg-gray-800" data-testid="phase-c-panel-close">
            <X className="h-4 w-4 text-gray-500" />
          </button>
        </div>
        <div className="flex gap-1 mt-2">
          {[
            { id: 'multi', icon: BarChart3, label: 'Score', color: 'amber' },
            { id: 'thermal', icon: Thermometer, label: 'Thermal', color: 'cyan' },
            { id: 'scenario', icon: Zap, label: 'Scenarios', color: 'violet' },
          ].map(tab => (
            <button key={tab.id} onClick={() => setActiveSection(tab.id)}
              className={`flex-1 text-[10px] py-1.5 rounded font-semibold transition-colors flex items-center justify-center gap-1 ${
                activeSection === tab.id
                  ? `bg-${tab.color}-500/15 text-${tab.color}-400 border border-${tab.color}-500/30`
                  : 'text-gray-500 hover:text-gray-400 border border-transparent'
              }`}
              style={activeSection === tab.id ? { background: `var(--${tab.color}, rgba(245,158,11,0.1))` } : {}}
              data-testid={`phase-c-tab-${tab.id}`}
            >
              <tab.icon className="h-3 w-3" />{tab.label}
            </button>
          ))}
        </div>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-12" data-testid="phase-c-loading">
          <Loader2 className="h-5 w-5 text-amber-400 animate-spin" />
          <span className="ml-2 text-xs text-gray-500">Moteurs V8...</span>
        </div>
      )}

      {!loading && (
        <div className="p-3 space-y-3">
          {/* ═══ MULTI-ENGINE SCORE ═══ */}
          {activeSection === 'multi' && multiScore && (
            <>
              <div className="rounded-lg bg-gray-900/50 border border-gray-800/50 p-3 text-center" data-testid="phase-c-multi-score">
                <div className="text-[9px] text-gray-600 uppercase tracking-wider mb-1">Score Composite V8</div>
                <div className="text-3xl font-bold text-white">{multiScore.composite_score}</div>
                <div className="text-[10px] font-semibold mt-1" style={{ color: multiScore.classification === 'EXCEPTIONNEL' ? '#10B981' : multiScore.classification === 'EXCELLENT' ? '#22D3EE' : multiScore.classification === 'BON' ? '#F59E0B' : '#EF4444' }}>
                  {multiScore.classification}
                </div>
              </div>

              <div className="space-y-1.5">
                <div className="text-[9px] text-gray-600 uppercase tracking-wider">Decomposition</div>
                <ScoreBar label="Terrain" value={multiScore.breakdown?.terrain} color="#10B981" />
                <ScoreBar label="Thermal" value={multiScore.breakdown?.thermal} max={15} color="#06B6D4" />
                <ScoreBar label="Temporal" value={multiScore.breakdown?.temporal} max={10} color="#8B5CF6" />
              </div>

              <div className="space-y-1.5 mt-3">
                <div className="text-[9px] text-gray-600 uppercase tracking-wider">Composantes</div>
                <ScoreBar label="Zones" value={multiScore.components?.zones_avg} color="#4CAF50" />
                <ScoreBar label="Corridors" value={multiScore.components?.corridors_avg} color="#FF9800" />
                <ScoreBar label="Affuts" value={multiScore.components?.affuts_avg} color="#3B82F6" />
                <ScoreBar label="Saline" value={multiScore.components?.saline_score} color="#F59E0B" />
                <ScoreBar label="Confort" value={multiScore.components?.confort_animal} color="#06B6D4" />
              </div>
            </>
          )}

          {/* ═══ THERMAL ═══ */}
          {activeSection === 'thermal' && thermal && (
            <>
              <div className="rounded-lg bg-gray-900/50 border border-gray-800/50 p-3" data-testid="phase-c-thermal">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-bold text-gray-400 uppercase">Zone Thermique</span>
                  <span className="text-[10px] px-2 py-0.5 rounded font-bold" style={{ background: `${ZONE_COLORS[thermal.zone_thermique]}20`, color: ZONE_COLORS[thermal.zone_thermique] }}>
                    {ZONE_LABELS[thermal.zone_thermique] || thermal.zone_thermique}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-3 mt-3">
                  <div className="text-center">
                    <div className="text-lg font-bold text-white">{thermal.temp_air_c}°C</div>
                    <div className="text-[8px] text-gray-600">TEMPERATURE</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-bold" style={{ color: thermal.wind_chill_c < -10 ? '#3B82F6' : thermal.wind_chill_c > 25 ? '#EF4444' : '#10B981' }}>{thermal.wind_chill_c}°C</div>
                    <div className="text-[8px] text-gray-600">RESSENTI</div>
                  </div>
                </div>
              </div>

              <div className="space-y-1.5">
                <ScoreBar label="Confort" value={thermal.confort_animal} color={ZONE_COLORS[thermal.zone_thermique] || '#F59E0B'} />
                <ScoreBar label="Vent" value={thermal.wind_speed_kmh} max={60} color="#94A3B8" />
                <ScoreBar label="Vent effectif" value={thermal.effective_wind_kmh} max={60} color="#64748B" />
                <ScoreBar label="Abri canopy" value={thermal.canopy_shelter_pct} color="#10B981" />
              </div>

              <div className="grid grid-cols-2 gap-x-3 gap-y-1 mt-3">
                {thermal.terrain && Object.entries(thermal.terrain).map(([k, v]) => (
                  <div key={k} className="flex justify-between text-[10px]">
                    <span className="text-gray-600">{k.replace(/_/g, ' ')}</span>
                    <span className="text-gray-400">{typeof v === 'number' ? (v < 2 ? (v * 100).toFixed(0) + '%' : v) : v}</span>
                  </div>
                ))}
              </div>
            </>
          )}

          {/* ═══ SCENARIOS ═══ */}
          {activeSection === 'scenario' && (
            <>
              {scenarios.length === 0 && (
                <div className="text-center py-6 text-xs text-gray-600">Aucun scenario disponible</div>
              )}
              {scenarios.map((sc, idx) => {
                const isExpanded = expandedScenario === idx;
                const vColor = VERDICT_COLORS[sc.verdict] || '#F59E0B';
                return (
                  <div key={idx} className="rounded-lg border transition-colors" style={{
                    background: isExpanded ? `${vColor}08` : 'rgba(17,17,24,0.5)',
                    borderColor: isExpanded ? `${vColor}40` : 'rgba(55,55,75,0.3)',
                  }} data-testid={`phase-c-scenario-${idx}`}>
                    <button className="w-full p-3 flex items-center gap-3" onClick={() => setExpandedScenario(isExpanded ? null : idx)}>
                      <div className="flex-1 text-left">
                        <div className="text-xs font-semibold text-white">{sc.description}</div>
                        <div className="text-[10px] text-gray-500">M{sc.conditions?.month} H{sc.conditions?.hour} {sc.conditions?.temp_c}°C</div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-bold" style={{ color: vColor }}>{sc.impact_global > 0 ? '+' : ''}{sc.impact_global}</div>
                        <div className="text-[8px] font-bold" style={{ color: vColor }}>{sc.verdict}</div>
                      </div>
                      {isExpanded ? <ChevronUp className="h-3.5 w-3.5 text-gray-600" /> : <ChevronDown className="h-3.5 w-3.5 text-gray-600" />}
                    </button>
                    {isExpanded && (
                      <div className="px-3 pb-3 space-y-2 border-t border-gray-800/30 pt-2">
                        <div className="grid grid-cols-2 gap-2 text-[10px]">
                          <div>
                            <div className="text-gray-600 font-bold mb-1">Baseline</div>
                            <div className="text-gray-400">Zones: {sc.baseline?.zones_avg}</div>
                            <div className="text-gray-400">Thermal: {sc.baseline?.thermal_confort}</div>
                          </div>
                          <div>
                            <div className="font-bold mb-1" style={{ color: vColor }}>Scenario</div>
                            <div className="text-gray-400">Zones: {sc.scenario?.zones_avg}</div>
                            <div className="text-gray-400">Thermal: {sc.scenario?.thermal_confort}</div>
                          </div>
                        </div>
                        <div className="text-[9px] text-gray-600 mt-1">
                          Deltas: zones {sc.deltas?.zones > 0 ? '+' : ''}{sc.deltas?.zones} | thermal {sc.deltas?.thermal > 0 ? '+' : ''}{sc.deltas?.thermal}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </>
          )}

          <div className="pt-2 border-t border-gray-800/30">
            <div className="text-[8px] text-gray-700 text-center">V8-PHASE-C — Thermal + Scenario + Multi-Engine</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PhaseCPanelV8;

/**
 * PhaseAPanelV8.jsx — Panneau lateral Phase A (Relocalisation + Salines)
 * =======================================================================
 * V8-FRONTEND-PHASE-A-Omega
 * Affiche: top-3 relocalisations, salines optimales, scoring terrain, explications
 * Style conforme STEEVE-MAX: dark, compact, informationnel
 */
import React, { useState } from 'react';
import { X, MapPin, Droplets, Target, ChevronDown, ChevronUp, Navigation, Loader2, AlertTriangle } from 'lucide-react';

const RELOC_COLORS = ['#10B981', '#3B82F6', '#8B5CF6'];
const SALINE_COLOR = '#F59E0B';

const ScoreBar = ({ label, value, max = 100, color = '#F5A623' }) => (
  <div className="flex items-center gap-2">
    <span className="text-[10px] text-gray-500 w-20 shrink-0">{label}</span>
    <div className="flex-1 h-1.5 bg-gray-800 rounded-full overflow-hidden">
      <div
        className="h-full rounded-full transition-all duration-500"
        style={{ width: `${Math.min(100, (value / max) * 100)}%`, background: color }}
      />
    </div>
    <span className="text-[10px] text-gray-400 w-8 text-right">{value}</span>
  </div>
);

const TerrainDetail = ({ terrain }) => {
  if (!terrain) return null;
  return (
    <div className="grid grid-cols-2 gap-x-3 gap-y-1 mt-2">
      {[
        { l: 'Canopy', v: `${Math.round(terrain.canopy * 100)}%` },
        { l: 'Pente', v: `${terrain.pente_deg}°` },
        { l: 'Strate', v: `${Math.round(terrain.strate_1_3m * 100)}%` },
        { l: 'Feuillus', v: `${Math.round(terrain.feuillus_ratio * 100)}%` },
        { l: 'Eau', v: `${terrain.distance_eau_m}m` },
        { l: 'Route', v: `${terrain.distance_route_m}m` },
      ].map((t, i) => (
        <div key={i} className="flex justify-between text-[10px]">
          <span className="text-gray-600">{t.l}</span>
          <span className="text-gray-400">{t.v}</span>
        </div>
      ))}
    </div>
  );
};

const PhaseAPanelV8 = ({
  relocData,
  salinesData,
  loading,
  error,
  onClose,
  onNavigateToPosition,
}) => {
  const [expandedReloc, setExpandedReloc] = useState(0);
  const [expandedSaline, setExpandedSaline] = useState(null);
  const [activeSection, setActiveSection] = useState('reloc');

  const relocalisations = relocData?.relocalisations || [];
  const siteActuel = relocData?.site_actuel || null;
  const salines = salinesData?.salines || [];
  const relocMs = relocData?.compute_ms || 0;
  const salinesMs = salinesData?.compute_ms || 0;

  return (
    <div
      className="fixed top-[180px] right-0 z-[1100] w-[340px] bg-[#0c0c14]/95 backdrop-blur-xl border-l border-gray-800/50 overflow-y-auto"
      style={{ height: 'calc(100vh - 180px)' }}
      data-testid="phase-a-panel"
    >
      {/* Header */}
      <div className="sticky top-0 z-10 bg-[#0c0c14]/98 border-b border-gray-800/50 p-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Target className="h-4 w-4 text-emerald-400" />
            <span className="text-sm font-bold text-white tracking-wide">PHASE A — V8</span>
            <span className="text-[9px] px-1.5 py-0.5 rounded bg-emerald-500/15 text-emerald-400 font-semibold">SANDBOX</span>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded hover:bg-gray-800 transition-colors"
            data-testid="phase-a-panel-close"
          >
            <X className="h-4 w-4 text-gray-500" />
          </button>
        </div>
        {/* Tabs */}
        <div className="flex gap-1 mt-2">
          <button
            onClick={() => setActiveSection('reloc')}
            className={`flex-1 text-[10px] py-1.5 rounded font-semibold transition-colors ${
              activeSection === 'reloc'
                ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                : 'text-gray-500 hover:text-gray-400 border border-transparent'
            }`}
            data-testid="phase-a-tab-reloc"
          >
            <MapPin className="h-3 w-3 inline mr-1" />
            Relocalisation ({relocalisations.length})
          </button>
          <button
            onClick={() => setActiveSection('salines')}
            className={`flex-1 text-[10px] py-1.5 rounded font-semibold transition-colors ${
              activeSection === 'salines'
                ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                : 'text-gray-500 hover:text-gray-400 border border-transparent'
            }`}
            data-testid="phase-a-tab-salines"
          >
            <Droplets className="h-3 w-3 inline mr-1" />
            Salines ({salines.length})
          </button>
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-12" data-testid="phase-a-loading">
          <Loader2 className="h-5 w-5 text-emerald-400 animate-spin" />
          <span className="ml-2 text-xs text-gray-500">Analyse terrain V8...</span>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="p-3 mx-3 mt-3 rounded bg-red-500/10 border border-red-500/20" data-testid="phase-a-error">
          <div className="flex items-center gap-2 text-xs text-red-400">
            <AlertTriangle className="h-3.5 w-3.5" />
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Content */}
      {!loading && !error && (
        <div className="p-3 space-y-3">
          {/* ═══ SECTION RELOCALISATION ═══ */}
          {activeSection === 'reloc' && (
            <>
              {/* Site Actuel */}
              {siteActuel && (
                <div className="rounded-lg bg-gray-900/50 border border-gray-800/50 p-3" data-testid="phase-a-site-actuel">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Site Actuel</span>
                    <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold ${
                      siteActuel.status === 'A EVITER' ? 'bg-red-500/15 text-red-400' :
                      siteActuel.status === 'BON' ? 'bg-emerald-500/15 text-emerald-400' :
                      'bg-amber-500/15 text-amber-400'
                    }`}>
                      {siteActuel.status}
                    </span>
                  </div>
                  <div className="flex gap-3">
                    <div className="text-center">
                      <div className="text-lg font-bold text-white">{siteActuel.composite_score}</div>
                      <div className="text-[8px] text-gray-600">COMPOSITE</div>
                    </div>
                    <div className="flex-1 space-y-1">
                      <ScoreBar label="Saline" value={siteActuel.saline_score} color="#F59E0B" />
                      <ScoreBar label="Affut" value={siteActuel.affut_score} color="#3B82F6" />
                    </div>
                  </div>
                </div>
              )}

              {/* Top-3 Relocalisations */}
              {relocalisations.length === 0 && !loading && (
                <div className="text-center py-6 text-xs text-gray-600" data-testid="phase-a-no-reloc">
                  Aucune relocalisation disponible pour cette position.
                  <br /><span className="text-[10px] text-gray-700">Les candidats ont ete exclus par le moteur BCE-4X.</span>
                </div>
              )}

              {relocalisations.slice(0, 3).map((r, idx) => {
                const color = RELOC_COLORS[idx];
                const isExpanded = expandedReloc === idx;
                return (
                  <div
                    key={idx}
                    className="rounded-lg border transition-colors"
                    style={{
                      background: isExpanded ? `${color}08` : 'rgba(17,17,24,0.5)',
                      borderColor: isExpanded ? `${color}40` : 'rgba(55,55,75,0.3)',
                    }}
                    data-testid={`phase-a-reloc-${idx}`}
                  >
                    {/* Header */}
                    <button
                      className="w-full p-3 flex items-center gap-3"
                      onClick={() => setExpandedReloc(isExpanded ? -1 : idx)}
                    >
                      <div
                        className="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold text-white shrink-0"
                        style={{ background: color, boxShadow: `0 0 8px ${color}40` }}
                      >
                        {idx + 1}
                      </div>
                      <div className="flex-1 text-left">
                        <div className="text-xs font-semibold text-white">Relocalisation #{idx + 1}</div>
                        <div className="text-[10px] text-gray-500">{r.distance_m}m du site actuel</div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-bold" style={{ color }}>{r.composite_score}</div>
                        <div className="text-[8px] text-gray-600">/100</div>
                      </div>
                      {isExpanded ? <ChevronUp className="h-3.5 w-3.5 text-gray-600" /> : <ChevronDown className="h-3.5 w-3.5 text-gray-600" />}
                    </button>

                    {/* Detail */}
                    {isExpanded && (
                      <div className="px-3 pb-3 space-y-2 border-t border-gray-800/30 pt-2">
                        <div className="space-y-1">
                          <ScoreBar label="Saline" value={r.saline_score} color="#F59E0B" />
                          <ScoreBar label="Affut" value={r.affut_score} color="#3B82F6" />
                          <ScoreBar label="Composite" value={r.composite_score} color={color} />
                        </div>
                        <TerrainDetail terrain={r.terrain} />
                        {/* Explications */}
                        {r.explanation && r.explanation.length > 0 && (
                          <div className="mt-2 p-2 rounded bg-gray-900/60 border border-gray-800/30">
                            <div className="text-[9px] font-bold text-gray-500 uppercase mb-1">Analyse terrain</div>
                            {r.explanation.map((line, li) => (
                              <div key={li} className="text-[10px] text-gray-400 leading-relaxed">
                                {line}
                              </div>
                            ))}
                          </div>
                        )}
                        {/* Navigate */}
                        <button
                          onClick={() => onNavigateToPosition && onNavigateToPosition(r.lat, r.lon)}
                          className="w-full mt-1 flex items-center justify-center gap-1.5 py-1.5 rounded text-[10px] font-semibold transition-colors"
                          style={{ background: `${color}15`, color, border: `1px solid ${color}30` }}
                          data-testid={`phase-a-navigate-reloc-${idx}`}
                        >
                          <Navigation className="h-3 w-3" />
                          Centrer sur la carte
                        </button>
                      </div>
                    )}
                  </div>
                );
              })}

              {/* Compute time */}
              {relocMs > 0 && (
                <div className="text-[9px] text-gray-700 text-right">
                  V8-RELOCALISATION — {relocMs}ms
                </div>
              )}
            </>
          )}

          {/* ═══ SECTION SALINES ═══ */}
          {activeSection === 'salines' && (
            <>
              {salines.length === 0 && !loading && (
                <div className="text-center py-6 text-xs text-gray-600" data-testid="phase-a-no-salines">
                  Aucune saline optimale identifiee.
                  <br /><span className="text-[10px] text-gray-700">Terrain exclu ou pente excessive.</span>
                </div>
              )}

              {salines.map((s, idx) => {
                const isExpanded = expandedSaline === idx;
                return (
                  <div
                    key={idx}
                    className="rounded-lg border transition-colors"
                    style={{
                      background: isExpanded ? `${SALINE_COLOR}08` : 'rgba(17,17,24,0.5)',
                      borderColor: isExpanded ? `${SALINE_COLOR}40` : 'rgba(55,55,75,0.3)',
                    }}
                    data-testid={`phase-a-saline-${idx}`}
                  >
                    <button
                      className="w-full p-3 flex items-center gap-3"
                      onClick={() => setExpandedSaline(isExpanded ? null : idx)}
                    >
                      <div className="w-6 h-6 rounded flex items-center justify-center text-[10px] font-bold text-white shrink-0 rotate-45"
                        style={{ background: SALINE_COLOR, boxShadow: `0 0 8px ${SALINE_COLOR}40` }}
                      >
                        <span className="-rotate-45">{idx + 1}</span>
                      </div>
                      <div className="flex-1 text-left">
                        <div className="text-xs font-semibold text-white">Saline #{idx + 1}</div>
                        <div className="text-[10px] text-gray-500">{s.distance_centre_m}m du centre</div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-bold" style={{ color: SALINE_COLOR }}>{s.score}</div>
                        <div className="text-[8px] text-gray-600">/100</div>
                      </div>
                      {isExpanded ? <ChevronUp className="h-3.5 w-3.5 text-gray-600" /> : <ChevronDown className="h-3.5 w-3.5 text-gray-600" />}
                    </button>

                    {isExpanded && (
                      <div className="px-3 pb-3 space-y-2 border-t border-gray-800/30 pt-2">
                        {/* Score detail */}
                        {s.detail && (
                          <div className="space-y-1">
                            <ScoreBar label="Eau" value={s.detail.eau} color="#06B6D4" />
                            <ScoreBar label="Couvert" value={s.detail.couvert} color="#10B981" />
                            <ScoreBar label="Pente" value={s.detail.pente} color="#8B5CF6" />
                            <ScoreBar label="Accessibilite" value={s.detail.accessibilite} color="#3B82F6" />
                            <ScoreBar label="Securite" value={s.detail.securite} color="#EF4444" />
                            <ScoreBar label="Diversite" value={s.detail.diversite} color="#F59E0B" />
                          </div>
                        )}
                        <TerrainDetail terrain={s.terrain} />
                        {/* Explications */}
                        {s.explanation && s.explanation.length > 0 && (
                          <div className="mt-2 p-2 rounded bg-gray-900/60 border border-gray-800/30">
                            <div className="text-[9px] font-bold text-gray-500 uppercase mb-1">Analyse placement</div>
                            {s.explanation.map((line, li) => (
                              <div key={li} className="text-[10px] text-gray-400 leading-relaxed">
                                {line}
                              </div>
                            ))}
                          </div>
                        )}
                        <button
                          onClick={() => onNavigateToPosition && onNavigateToPosition(s.lat, s.lon)}
                          className="w-full mt-1 flex items-center justify-center gap-1.5 py-1.5 rounded text-[10px] font-semibold transition-colors"
                          style={{ background: `${SALINE_COLOR}15`, color: SALINE_COLOR, border: `1px solid ${SALINE_COLOR}30` }}
                          data-testid={`phase-a-navigate-saline-${idx}`}
                        >
                          <Navigation className="h-3 w-3" />
                          Centrer sur la carte
                        </button>
                      </div>
                    )}
                  </div>
                );
              })}

              {salinesMs > 0 && (
                <div className="text-[9px] text-gray-700 text-right">
                  V8-SALINES — {salinesMs}ms
                </div>
              )}
            </>
          )}

          {/* Footer */}
          <div className="pt-2 border-t border-gray-800/30">
            <div className="text-[8px] text-gray-700 text-center">
              V8-PHASE-A-Omega — Engine SANDBOX — ZERO impact couches existantes
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PhaseAPanelV8;

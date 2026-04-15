/**
 * IntelligenceDashboard — Cockpit unifie V6-CORE
 * x4520-UNIFICATION_DASHBOARD
 * ZERO relique V1/V2/V10 — 22 moteurs, interface unique — V6-CORE
 * Fusionne: INTELLIGENCE + GUIDE PRO + SCIENTIFIQUE + TERRAIN
 * Integre: Luna/SolCal
 */
import { useState, useEffect, useCallback, useMemo } from 'react';
import {
  X, Brain, TrendingUp, ClipboardList, AlertTriangle,
  Activity, ChevronRight, Moon, Database, Layers,
} from 'lucide-react';
import useBionicStore from '@/stores/useBionicStore';
import SolunarChart from './intelligence/SolunarChart';

const TP = {
  cream: '#F2E9D8', creamDim: '#C8BBA6',
  forest: '#2D5016', forestLight: '#4A7A2E', forestDim: '#1A3A0A',
  earth: '#8B6F47', earthLight: '#A8885E', earthDim: '#5C4A30',
  sand: '#C2A97E', sandLight: '#D4C4A0', sandDim: '#9A8560',
  rock: '#9CA3AF', rockDim: '#6B7280',
  bionic: '#D97706', bionicGlow: '#F59E0B', bionicDim: '#92400E',
};

const CL = {
  OPTIMAL: { color: TP.bionicGlow, bg: 'rgba(217,119,6,0.12)', border: 'rgba(217,119,6,0.25)' },
  BON: { color: TP.forestLight, bg: 'rgba(74,122,46,0.12)', border: 'rgba(74,122,46,0.25)' },
  MODERE: { color: TP.sand, bg: 'rgba(194,169,126,0.1)', border: 'rgba(194,169,126,0.2)' },
  FAIBLE: { color: TP.rock, bg: 'rgba(156,163,175,0.08)', border: 'rgba(156,163,175,0.15)' },
};

const URG = {
  CRITIQUE: { border: '1px solid rgba(217,119,6,0.45)', bg: 'rgba(217,119,6,0.12)', color: TP.bionicGlow },
  HAUTE: { border: '1px solid rgba(139,111,71,0.35)', bg: 'rgba(139,111,71,0.12)', color: TP.cream },
  MOYENNE: { border: '1px solid rgba(194,169,126,0.25)', bg: 'rgba(194,169,126,0.06)', color: TP.creamDim },
  FAIBLE: { border: '1px solid rgba(156,163,175,0.2)', bg: 'rgba(156,163,175,0.06)', color: TP.rock },
};

const DOMAIN_ICONS = {
  habitat: Layers, deplacement: Activity, pression: AlertTriangle,
  environnement: TrendingUp, comportement: Brain, strategie: ClipboardList,
  intelligence: Database,
};

const DOMAIN_COLORS = {
  habitat: '#4A7A2E', deplacement: '#D97706', pression: '#EF4444',
  environnement: '#3B82F6', comportement: '#A78BFA', strategie: '#F59E0B',
  intelligence: '#06B6D4',
};

function getClasse(score) {
  if (score >= 80) return CL.OPTIMAL;
  if (score >= 60) return CL.BON;
  if (score >= 40) return CL.MODERE;
  return CL.FAIBLE;
}
function getUrg(u) { return URG[u] || URG.FAIBLE; }

const TOPO_BG = `url("data:image/svg+xml,%3Csvg width='80' height='80' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 40 Q20 30 40 40 T80 40' fill='none' stroke='rgba(74,122,46,0.06)' stroke-width='0.5'/%3E%3Cpath d='M0 60 Q20 50 40 60 T80 60' fill='none' stroke='rgba(139,111,71,0.04)' stroke-width='0.4'/%3E%3C/svg%3E")`;

export default function IntelligenceDashboard({
  onClose, waypointCenter, selectedSpecies, currentMonth,
  onNavigateToPosition, onHighlightZoneType, onShowApproachMarkers,
}) {
  const {
    summary, forecast, plan, solunar, loading,
    fetchSummary, fetchForecast, fetchPlan, fetchSolunar,
    setLocation, setSpecies, setMonth,
  } = useBionicStore();

  const [guidePro, setGuidePro] = useState(null);

  useEffect(() => {
    if (waypointCenter) setLocation({ lat: waypointCenter.lat, lng: waypointCenter.lng });
  }, [waypointCenter, setLocation]);
  useEffect(() => { if (selectedSpecies) setSpecies(selectedSpecies); }, [selectedSpecies, setSpecies]);
  useEffect(() => { if (currentMonth) setMonth(currentMonth); }, [currentMonth, setMonth]);

  const location = useMemo(() => (
    waypointCenter ? { lat: waypointCenter.lat, lng: waypointCenter.lng } : null
  ), [waypointCenter]);
  const species = selectedSpecies || 'CHEVREUIL';
  const month = currentMonth || new Date().getMonth() + 1;

  useEffect(() => {
    if (!location) return;
    fetchSummary(); fetchForecast(); fetchPlan(); fetchSolunar();
  }, [location, species, month, fetchSummary, fetchForecast, fetchPlan, fetchSolunar]);

  // Guide Pro data
  const API = process.env.REACT_APP_BACKEND_URL;
  useEffect(() => {
    if (!location) return;
    const params = new URLSearchParams({ lat: location.lat, lng: location.lng, species, month });
    fetch(`${API}/api/v3/intelligence/guide-pro?${params}`)
      .then(r => r.json()).then(setGuidePro).catch(() => {});
  }, [location, species, month, API]);

  const handleNavigate = useCallback((lat, lng) => {
    if (onNavigateToPosition) onNavigateToPosition(lat, lng);
  }, [onNavigateToPosition]);

  const handleDomainClick = useCallback((domain) => {
    if (onHighlightZoneType) onHighlightZoneType(domain.toLowerCase());
  }, [onHighlightZoneType]);

  const classeStyle = summary ? (CL[summary.consolidated?.classe] || CL.FAIBLE) : CL.FAIBLE;

  return (
    <div className="absolute inset-0 z-[900] pointer-events-none flex items-start justify-center p-4 pt-2" data-testid="intelligence-dashboard">
      <div
        className="pointer-events-auto w-full max-w-6xl max-h-full rounded-xl overflow-hidden flex flex-col shadow-2xl"
        style={{
          background: 'rgba(22, 18, 12, 0.78)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          border: '1px solid rgba(139, 111, 71, 0.2)',
          backgroundImage: TOPO_BG,
          backgroundRepeat: 'repeat',
        }}
        data-testid="intelligence-panel"
      >
        {/* HEADER — V6-CORE Unifie */}
        <div className="flex-shrink-0 px-5 py-2.5 flex items-center gap-3"
          style={{ background: 'rgba(26, 22, 16, 0.6)', borderBottom: '1px solid rgba(139, 111, 71, 0.18)' }}
        >
          <Brain className="w-5 h-5" style={{ color: TP.forestLight }} />
          <span className="text-base font-bold tracking-tight" style={{ color: TP.cream }}>INTELLIGENCE V7</span>
          <span className="text-xs px-2 py-0.5 rounded font-mono" style={{ background: 'rgba(74,122,46,0.15)', color: TP.forestLight, border: '1px solid rgba(74,122,46,0.25)' }}>V7 | 87+ MOTEURS</span>

          <div className="ml-auto flex items-center gap-3">
            {location && (
              <span className="text-xs font-mono" style={{ color: TP.creamDim }}>{location.lat.toFixed(3)},{location.lng.toFixed(3)}</span>
            )}
            <span className="text-xs px-2 py-1 rounded font-mono" style={{ background: 'rgba(139,111,71,0.12)', color: TP.creamDim }}>{species}</span>
            <span className="text-xs px-2 py-1 rounded font-mono" style={{ background: 'rgba(139,111,71,0.12)', color: TP.creamDim }}>M{month}</span>
            <button onClick={onClose} className="p-1.5 rounded transition-colors hover:brightness-125" style={{ color: TP.creamDim }} data-testid="intelligence-close">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* CONTENT — Unifie scrollable */}
        <div className="flex-1 overflow-auto min-h-0">
          {!location ? (
            <div className="flex flex-col items-center justify-center py-16 gap-3">
              <Brain className="w-8 h-8" style={{ color: TP.rockDim }} />
              <div className="text-base font-medium" style={{ color: TP.creamDim }}>Selectionnez un waypoint pour activer INTELLIGENCE</div>
            </div>
          ) : (
            <div className="p-5 space-y-5">
              {/* SECTION 1: SCORE CONSOLIDE + 22 MOTEURS PAR DOMAINE */}
              <div className="grid grid-cols-1 lg:grid-cols-4 gap-3" data-testid="block-analytics">
                <div className="rounded-lg p-5 flex flex-col justify-center items-center"
                  style={{ background: classeStyle.bg, border: `1px solid ${classeStyle.border}` }}
                >
                  <div className="text-sm uppercase tracking-wider font-medium mb-1" style={{ color: TP.creamDim }}>Score Consolide</div>
                  <div className="text-6xl font-black tracking-tighter" style={{ color: classeStyle.color }}>{summary?.consolidated?.score ?? '--'}</div>
                  <div className="text-xl font-bold mt-1" style={{ color: classeStyle.color }}>{summary?.consolidated?.label || '--'}</div>
                  <div className="text-sm mt-1" style={{ color: TP.creamDim }}>{summary?.engines_count || 0} moteurs actifs</div>
                  {summary?.option && <div className="text-xs mt-1 font-mono" style={{ color: TP.rockDim }}>{summary.option}</div>}
                </div>
                <div className="lg:col-span-3 grid grid-cols-2 md:grid-cols-4 gap-2.5">
                  {summary?.domains ? Object.entries(summary.domains).map(([domain, engines]) => {
                    const avg = Math.round(engines.reduce((s, e) => s + e.score, 0) / engines.length);
                    const cl = getClasse(avg);
                    const DIcon = DOMAIN_ICONS[domain] || Activity;
                    const dColor = DOMAIN_COLORS[domain] || TP.creamDim;
                    const domainLabel = summary.domain_labels?.[domain] || domain;
                    return (
                      <div key={domain} className="rounded-lg p-3 cursor-pointer transition-all hover:brightness-110"
                        style={{ background: 'rgba(45,80,22,0.07)', border: '1px solid rgba(139,111,71,0.12)' }}
                        onClick={() => handleDomainClick(domain)}
                        data-testid={`domain-${domain}`}
                      >
                        <div className="flex items-center gap-1.5 mb-1">
                          <DIcon className="w-3.5 h-3.5" style={{ color: dColor }} />
                          <div className="text-xs uppercase tracking-wider font-medium truncate" style={{ color: dColor }}>{domainLabel}</div>
                        </div>
                        <div className="text-3xl font-bold" style={{ color: cl.color }}>{avg}</div>
                        <div className="mt-1.5 space-y-0.5">
                          {engines.map(e => (
                            <div key={e.key || e.engine} className="flex justify-between text-xs">
                              <span className="font-medium truncate mr-1" style={{ color: TP.creamDim }}>{e.engine}</span>
                              <span className="font-mono font-semibold flex-shrink-0" style={{ color: TP.cream }}>{e.score}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    );
                  }) : (
                    <div className="col-span-4 text-center text-base py-6 font-medium" style={{ color: TP.creamDim }}>
                      {loading ? 'Chargement...' : 'Aucune donnee'}
                    </div>
                  )}
                </div>
              </div>

              {/* SECTION 2: CONDITIONS & ALERTES */}
              {summary?.recommendations?.length > 0 && (
                <div className="rounded-lg p-5" style={{ background: 'rgba(139,111,71,0.05)', border: '1px solid rgba(139,111,71,0.12)' }} data-testid="block-conditions">
                  <div className="flex items-center gap-2 mb-3">
                    <AlertTriangle className="w-5 h-5" style={{ color: TP.bionic }} />
                    <span className="text-base uppercase tracking-wider font-bold" style={{ color: TP.cream }}>Conditions & Alertes</span>
                  </div>
                  <div className="space-y-2">
                    {summary.recommendations.map((r, i) => {
                      const u = getUrg(r.priority);
                      return (
                        <div key={i} className="flex items-center gap-3 px-4 py-3 rounded-lg"
                          style={{ border: u.border, background: u.bg, color: u.color }}
                        >
                          {r.priority === 'HAUTE' ? <AlertTriangle className="w-5 h-5 flex-shrink-0" /> : <Activity className="w-5 h-5 flex-shrink-0" />}
                          <span className="text-base font-medium flex-1">{r.action}</span>
                          <span className="text-sm font-bold uppercase tracking-wider">{r.priority}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* SECTION 3: LUNA/SOLCAL + GUIDE PRO (2/3) — FORECAST (1/3) */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4" data-testid="block-guide-forecast">
                {/* Luna/SolCal + Guide Pro */}
                <div className="lg:col-span-2 space-y-4">
                  {/* SolunarChart */}
                  <div className="rounded-lg p-4" style={{ background: 'rgba(45,80,22,0.05)', border: '1px solid rgba(139,111,71,0.12)' }} data-testid="block-solunar">
                    <div className="flex items-center gap-2 mb-3">
                      <Moon className="w-5 h-5" style={{ color: TP.sand }} />
                      <span className="text-sm uppercase tracking-wider font-bold" style={{ color: TP.cream }}>Luna / SolCal</span>
                    </div>
                    {solunar ? (
                      <SolunarChart solunar={solunar} />
                    ) : (
                      <div className="text-sm py-6 text-center font-medium" style={{ color: TP.creamDim }}>{loading ? 'Chargement...' : '--'}</div>
                    )}
                  </div>

                  {/* Guide Pro Best Time */}
                  {guidePro?.best_time && (
                    <div className="rounded-lg p-4" style={{ background: 'rgba(139,111,71,0.06)', border: '1px solid rgba(139,111,71,0.12)' }} data-testid="block-guide-pro">
                      <div className="flex items-center gap-2 mb-3">
                        <Activity className="w-5 h-5" style={{ color: TP.forestLight }} />
                        <span className="text-sm uppercase tracking-wider font-bold" style={{ color: TP.cream }}>Guide Pro — Meilleur Temps</span>
                      </div>
                      <div className="grid grid-cols-3 gap-3">
                        <div className="text-center rounded-lg p-3" style={{ background: 'rgba(217,119,6,0.1)', border: '1px solid rgba(217,119,6,0.2)' }}>
                          <div className="text-3xl font-black" style={{ color: TP.bionicGlow }}>{guidePro.best_time.score}</div>
                          <div className="text-xs uppercase mt-1 font-bold" style={{ color: TP.bionic }}>{guidePro.best_time.label}</div>
                        </div>
                        <div className="text-center rounded-lg p-3" style={{ background: 'rgba(45,80,22,0.08)' }}>
                          <div className="text-2xl font-bold" style={{ color: TP.cream }}>{guidePro.best_time.solunar_contribution}</div>
                          <div className="text-xs mt-1 font-medium" style={{ color: TP.creamDim }}>Solunaire</div>
                        </div>
                        <div className="text-center rounded-lg p-3" style={{ background: 'rgba(45,80,22,0.08)' }}>
                          <div className="text-2xl font-bold" style={{ color: TP.cream }}>{guidePro.best_time.terrain_contribution}</div>
                          <div className="text-xs mt-1 font-medium" style={{ color: TP.creamDim }}>Terrain</div>
                        </div>
                      </div>
                      {/* Weather */}
                      {guidePro.weather_official && (
                        <div className="flex gap-3 mt-3">
                          <div className="text-xs px-3 py-1.5 rounded-lg font-mono" style={{ background: 'rgba(139,111,71,0.1)', color: TP.creamDim }}>
                            {guidePro.weather_official.temperature}C
                          </div>
                          <div className="text-xs px-3 py-1.5 rounded-lg font-mono" style={{ background: 'rgba(139,111,71,0.1)', color: TP.creamDim }}>
                            Vent: {guidePro.weather_official.wind_speed_kmh} km/h ({guidePro.weather_official.wind_force})
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* SIDEBAR: Forecast + Plan */}
                <div className="space-y-3">
                  {/* FORECAST */}
                  <div className="rounded-lg p-4" style={{ background: 'rgba(139,111,71,0.06)', border: '1px solid rgba(139,111,71,0.12)' }} data-testid="block-forecast">
                    <div className="flex items-center gap-2 mb-3">
                      <TrendingUp className="w-5 h-5" style={{ color: TP.forestLight }} />
                      <span className="text-sm uppercase tracking-wider font-bold" style={{ color: TP.cream }}>Forecast</span>
                    </div>
                    {forecast ? (
                      <>
                        <div className="flex items-end gap-1 h-20">
                          {forecast.monthly_data?.map(m => {
                            const h = Math.max(8, (m.score / 100) * 100);
                            const barColor = m.month === forecast.best_month ? TP.forestLight
                              : m.month === forecast.worst_month ? TP.bionicDim
                              : TP.earthDim;
                            return (
                              <div key={m.month} className="flex-1 flex flex-col items-center gap-0.5">
                                <span className="text-xs font-mono font-semibold" style={{ color: TP.creamDim }}>{m.score}</span>
                                <div className="w-full rounded-t" style={{ height: `${h}%`, background: barColor }} />
                                <span className="text-xs font-mono" style={{ color: TP.creamDim }}>{m.month}</span>
                              </div>
                            );
                          })}
                        </div>
                        <div className="grid grid-cols-2 gap-2 mt-3">
                          {forecast.seasonal_scores && Object.entries(forecast.seasonal_scores).map(([s, score]) => (
                            <div key={s} className="text-center rounded p-2" style={{ background: 'rgba(45,80,22,0.07)' }}>
                              <div className="text-xl font-bold" style={{ color: TP.cream }}>{score}</div>
                              <div className="text-xs uppercase font-medium" style={{ color: TP.creamDim }}>{s}</div>
                            </div>
                          ))}
                        </div>
                      </>
                    ) : <div className="text-sm py-4 text-center font-medium" style={{ color: TP.creamDim }}>{loading ? '...' : '--'}</div>}
                  </div>

                  {/* PLAN MAITRE */}
                  <div className="rounded-lg p-4" style={{ background: 'rgba(139,111,71,0.06)', border: '1px solid rgba(139,111,71,0.12)' }} data-testid="block-plan">
                    <div className="flex items-center gap-2 mb-3">
                      <ClipboardList className="w-5 h-5" style={{ color: TP.earth }} />
                      <span className="text-sm uppercase tracking-wider font-bold" style={{ color: TP.cream }}>Plan Maitre</span>
                    </div>
                    {plan ? (
                      <div className="space-y-2">
                        {plan.actions?.slice(0, 5).map(a => {
                          const u = getUrg(a.urgency);
                          return (
                            <div key={a.rank} onClick={() => handleNavigate(location.lat, location.lng)}
                              className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm cursor-pointer hover:brightness-110 transition-all"
                              style={{ border: u.border, background: u.bg, color: u.color }}
                              data-testid={`plan-action-${a.rank}`}
                            >
                              <span className="font-bold text-base w-8">{a.score}</span>
                              <div className="flex-1 truncate">
                                <div className="font-semibold">{a.engine}</div>
                                <div className="text-xs opacity-70 truncate">{a.action}</div>
                              </div>
                              <ChevronRight className="w-4 h-4 opacity-50" />
                            </div>
                          );
                        })}
                      </div>
                    ) : <div className="text-sm py-4 text-center font-medium" style={{ color: TP.creamDim }}>{loading ? '...' : '--'}</div>}
                  </div>

                  {/* DONNEES BRUTES */}
                  <div className="rounded-lg p-4" style={{ background: 'rgba(45,80,22,0.05)', border: '1px solid rgba(74,122,46,0.1)' }} data-testid="block-raw-data">
                    <div className="flex items-center gap-2 mb-2">
                      <Database className="w-4 h-4" style={{ color: TP.creamDim }} />
                      <span className="text-sm uppercase tracking-wider font-bold" style={{ color: TP.cream }}>Donnees V6-CORE</span>
                    </div>
                    <div className="text-sm font-mono space-y-1" style={{ color: TP.creamDim }}>
                      <div>Pos: {location?.lat.toFixed(5)}, {location?.lng.toFixed(5)}</div>
                      <div>Score: {summary?.consolidated?.score ?? '--'} | {summary?.consolidated?.classe ?? '--'}</div>
                      <div>Moteurs: {summary?.engines_count || '--'} | Option: C</div>
                      <div>Fort: {summary?.analysis?.strongest_engine || '--'} ({summary?.analysis?.strongest_score || '--'})</div>
                      <div>Faible: {summary?.analysis?.weakest_engine || '--'} ({summary?.analysis?.weakest_score || '--'})</div>
                      {forecast && <div>Best: M{forecast.best_month} | Avg: {forecast.annual_average}</div>}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

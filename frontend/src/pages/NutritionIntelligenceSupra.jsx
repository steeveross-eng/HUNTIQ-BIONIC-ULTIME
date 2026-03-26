import React, { useState, useEffect, useCallback } from 'react';
import {
  FlaskConical, ShoppingCart, Leaf, Beaker, Mountain, DollarSign, BookOpen,
  ChevronDown, ChevronUp, MapPin, Thermometer, Droplets, AlertTriangle,
  FileText, ExternalLink, Zap, Package, Construction, Scale
} from 'lucide-react';
import axios from 'axios';

/**
 * NutritionIntelligenceSupra.jsx — Interface ×5400 MINERAL_SCORE_UI
 * Dashboard BIONIC premium pour ×5100-×5900
 * BCE-4X / STEEVE-MAX V6
 */

const API = process.env.REACT_APP_BACKEND_URL;

// BCE-4X P0: Couleur officielle SUPRA pour TOUS les boutons
const SUPRA_CMD_COLOR = '#FF9800';

const BIONIC = {
  green: '#00C853', yellow: '#F9D423', orange: '#FF9800', red: '#D32F2F',
  blue: '#2196F3', light: '#ECEFF1', dark: '#37474F', card: '#1a1a2e',
  cardBorder: 'rgba(255,255,255,0.06)',
  supraCmd: SUPRA_CMD_COLOR,
};

const SPECIES_OPTIONS = [
  { value: 'chevreuil', label: 'Chevreuil' },
  { value: 'orignal', label: 'Orignal' },
  { value: 'wapiti', label: 'Wapiti' },
];

const SEASON_OPTIONS = [
  { value: 'printemps', label: 'Printemps' },
  { value: 'ete', label: 'Ete' },
  { value: 'pre_rut', label: 'Pre-rut' },
  { value: 'rut', label: 'Rut' },
  { value: 'post_rut', label: 'Post-rut' },
  { value: 'hiver', label: 'Hiver' },
];

const SOIL_OPTIONS = [
  { value: 'acide', label: 'Sol acide' },
  { value: 'loam', label: 'Loam' },
  { value: 'coniferes', label: 'Coniferes' },
  { value: 'mixte', label: 'Mixte' },
  { value: 'sableux', label: 'Sableux' },
];

function gradeColor(grade) {
  if (grade === 'EXCELLENT') return BIONIC.green;
  if (grade === 'BON') return BIONIC.yellow;
  if (grade === 'MODERE') return BIONIC.orange;
  return BIONIC.red;
}

function zoneColor(zone) {
  if (zone === 'vert') return BIONIC.green;
  if (zone === 'jaune') return BIONIC.orange;
  return BIONIC.red;
}

function priorityColor(p) {
  if (p === 'CRITIQUE') return BIONIC.red;
  if (p === 'RECOMMANDE') return BIONIC.orange;
  return BIONIC.green;
}

const Card = ({ children, className = '', testId }) => (
  <div className={`rounded-[14px] border p-4 ${className}`} style={{ backgroundColor: BIONIC.card, borderColor: BIONIC.cardBorder, boxShadow: '0 2px 8px rgba(0,0,0,0.18)' }} data-testid={testId}>{children}</div>
);

const Section = ({ icon: Icon, title, color, badge, children, collapsible = false, testId }) => {
  const [open, setOpen] = useState(!collapsible);
  return (
    <Card testId={testId}>
      <button onClick={collapsible ? () => setOpen(v => !v) : undefined} className={`w-full flex items-center justify-between ${collapsible ? 'cursor-pointer' : 'cursor-default'}`}>
        <div className="flex items-center gap-2">
          <Icon className="h-4 w-4" style={{ color }} />
          <span className="text-sm font-bold text-white">{title}</span>
        </div>
        <div className="flex items-center gap-2">
          {badge && <span className="text-[10px] font-bold px-2 py-0.5 rounded-lg" style={{ backgroundColor: `${color}18`, color }}>{badge}</span>}
          {collapsible && (open ? <ChevronUp className="h-4 w-4 text-gray-500" /> : <ChevronDown className="h-4 w-4 text-gray-500" />)}
        </div>
      </button>
      {open && <div className="mt-3">{children}</div>}
    </Card>
  );
};

export default function NutritionIntelligenceSupra() {
  const [species, setSpecies] = useState('chevreuil');
  const [season, setSeason] = useState('printemps');
  const [soilType, setSoilType] = useState('mixte');
  const [substrate, setSubstrate] = useState('bois_mou');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchAnalysis = useCallback(async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API}/api/v6/nutrition-intelligence/full-analysis`, {
        species, season, soil_type: soilType, substrate,
      });
      setData(res.data);
    } catch (e) {
      console.error('[x5000]', e);
    } finally {
      setLoading(false);
    }
  }, [species, season, soilType, substrate]);

  useEffect(() => { fetchAnalysis(); }, [fetchAnalysis]);

  const recipe = data?.recipe;
  const score = recipe?.score;
  const evidence = data?.evidence || [];
  const comparison = data?.substrate_comparison;

  const gc = score ? gradeColor(score.grade) : BIONIC.blue;

  return (
    <div className="min-h-screen bg-[#0a0a14] text-white" data-testid="nutrition-intelligence-supra">
      {/* HEADER */}
      <div className="border-b border-gray-800/50 bg-black/40 px-6 py-4">
        <div className="max-w-[1200px] mx-auto flex items-center justify-between flex-wrap gap-4">
          <div>
            <h1 className="text-lg font-black tracking-tight" data-testid="supra-title">Nutrition Intelligence SUPRA</h1>
            <p className="text-xs text-gray-500">x5000 | 9 moteurs | BCE-4X / STEEVE-MAX V6</p>
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <Select value={species} onChange={setSpecies} options={SPECIES_OPTIONS} testId="select-species" />
            <Select value={season} onChange={setSeason} options={SEASON_OPTIONS} testId="select-season" />
            <Select value={soilType} onChange={setSoilType} options={SOIL_OPTIONS} testId="select-soil" />
            <select value={substrate} onChange={e => setSubstrate(e.target.value)} className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-xs text-white" data-testid="select-substrate">
              <option value="bois_mou">Bois mou</option>
              <option value="bois_dur">Bois dur</option>
            </select>
          </div>
        </div>
      </div>

      {loading && <div className="text-center py-12 text-gray-500 text-sm animate-pulse">Analyse en cours...</div>}

      {!loading && score && recipe && (
        <div className="max-w-[1200px] mx-auto px-6 py-6 space-y-4" data-testid="supra-content">

          {/* ROW 1: Score global + Phase physiologique */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Score global */}
            <Card testId="score-global-card" className="lg:col-span-1">
              <div className="flex items-center gap-4 mb-3">
                <div className="w-[72px] h-[72px] rounded-2xl flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${gc}22, ${gc}08)`, border: `2.5px solid ${gc}` }}>
                  <span className="text-3xl font-black" style={{ color: gc }}>{score.score_global}</span>
                </div>
                <div>
                  <div className="text-xl font-black text-white">Score Mineral</div>
                  <div className="text-xs font-bold px-2 py-0.5 rounded-lg inline-block mt-1" style={{ backgroundColor: `${gc}18`, color: gc }}>{score.grade}</div>
                </div>
              </div>
              <div className="flex gap-3 text-xs">
                <span style={{ color: BIONIC.green }}>{score.zones_resume.vert} vert</span>
                <span style={{ color: BIONIC.orange }}>{score.zones_resume.jaune} jaune</span>
                <span style={{ color: BIONIC.red }}>{score.zones_resume.rouge} rouge</span>
              </div>
            </Card>

            {/* Phase + Energie/Proteines */}
            <Card testId="phase-card" className="lg:col-span-2">
              <div className="flex items-center gap-2 mb-2">
                <Zap className="h-4 w-4" style={{ color: BIONIC.yellow }} />
                <span className="text-sm font-bold">{recipe.phase_physiologique}</span>
              </div>
              <div className="text-xs text-gray-400 mb-3">{recipe.title} | Sol {recipe.soil_type} | {recipe.substrate.replace('_', ' ')}</div>
              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-xl p-3" style={{ backgroundColor: `${BIONIC.orange}10`, borderLeft: `3px solid ${BIONIC.orange}` }}>
                  <div className="text-[10px] text-gray-500 uppercase font-bold">Energie</div>
                  <div className="text-sm font-bold mt-0.5" style={{ color: BIONIC.orange }}>{recipe.melange_saisonnier?.name}</div>
                </div>
                <div className="rounded-xl p-3" style={{ backgroundColor: `${BIONIC.blue}10`, borderLeft: `3px solid ${BIONIC.blue}` }}>
                  <div className="text-[10px] text-gray-500 uppercase font-bold">Proteines</div>
                  <div className="text-sm font-bold mt-0.5" style={{ color: BIONIC.blue }}>{recipe.proteines_cles?.[0]?.brand || 'N/A'}</div>
                </div>
              </div>
            </Card>
          </div>

          {/* ROW 2: Scores par mineral + Boutons COMMANDE */}
          <Section icon={FlaskConical} title="Score par mineral" color={BIONIC.yellow} badge={`${Object.keys(score.scores_par_mineral).length} mineraux`} testId="minerals-section">
            <div className="space-y-2">
              {Object.entries(score.scores_par_mineral).map(([key, m]) => (
                <div key={key} className="flex items-center gap-3" data-testid={`mineral-row-${key}`}>
                  <span className="text-xs text-gray-300 w-28 flex-shrink-0 font-medium">{m.name}</span>
                  <div className="flex-1 h-[6px] rounded-full overflow-hidden" style={{ backgroundColor: 'rgba(255,255,255,0.04)' }}>
                    <div className="h-full rounded-full" style={{ width: `${m.score}%`, backgroundColor: zoneColor(m.zone), transition: 'width 0.6s ease' }} />
                  </div>
                  <span className="text-sm font-bold w-10 text-right tabular-nums" style={{ color: zoneColor(m.zone) }}>{m.score}</span>
                  <span className="text-[10px] font-bold w-12 text-right uppercase" style={{ color: zoneColor(m.zone) }}>{m.zone}</span>
                  <button
                    className="flex items-center gap-1.5 h-8 px-3 rounded-lg text-xs font-bold uppercase tracking-wider transition-all duration-150 hover:brightness-125 active:scale-[0.97]"
                    style={{
                      backgroundColor: `${SUPRA_CMD_COLOR}18`,
                      color: SUPRA_CMD_COLOR,
                      border: `2px solid ${SUPRA_CMD_COLOR}50`,
                    }}
                    data-testid={`order-btn-${key}`}
                  >
                    <ShoppingCart className="h-3.5 w-3.5" />
                    CMD
                  </button>
                </div>
              ))}
            </div>
          </Section>

          {/* ROW 3: Recette + Couts side by side */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Recette */}
            <Section icon={BookOpen} title="Recette saisonniere" color={BIONIC.green} badge={`${recipe.nb_deficits_critiques} critiques`} testId="recipe-section">
              <div className="space-y-2">
                {recipe.ingredients_cles?.map((ing, i) => (
                  <div key={i} className="flex items-center justify-between py-1.5 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
                    <div>
                      <div className="text-xs text-white font-medium">{ing.mineral}</div>
                      <div className="text-[10px] text-gray-500">{ing.product} — {ing.dosage}</div>
                    </div>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-lg" style={{ backgroundColor: `${priorityColor(ing.priority)}15`, color: priorityColor(ing.priority) }}>{ing.priority}</span>
                  </div>
                ))}
                {recipe.melange_saisonnier && (
                  <div className="rounded-xl p-3 mt-2" style={{ backgroundColor: `${BIONIC.green}08`, borderLeft: `3px solid ${BIONIC.green}` }}>
                    <div className="text-xs font-bold" style={{ color: BIONIC.green }}>{recipe.melange_saisonnier.name}</div>
                    <div className="text-[10px] text-gray-400 mt-1">{recipe.melange_saisonnier.ingredients?.join(' | ')}</div>
                    <div className="text-[10px] text-gray-500 mt-0.5">{recipe.melange_saisonnier.cost_per_25kg_cad}$ / 25kg | {recipe.melange_saisonnier.coverage_m2}m2</div>
                  </div>
                )}
              </div>
            </Section>

            {/* Couts */}
            <Section icon={DollarSign} title="Couts estimes" color={BIONIC.orange} testId="costs-section">
              {comparison && (
                <div className="space-y-3">
                  {['bois_mou', 'bois_dur'].map(sub => {
                    const c = comparison[sub];
                    const isRecommended = comparison.recommended === sub;
                    return (
                      <div key={sub} className="rounded-xl p-3 border" style={{ borderColor: isRecommended ? `${BIONIC.green}40` : 'rgba(255,255,255,0.04)', backgroundColor: isRecommended ? `${BIONIC.green}06` : 'transparent' }}>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs font-bold text-white">{c.substrate_name}</span>
                          {isRecommended && <span className="text-[10px] font-bold px-2 py-0.5 rounded-lg" style={{ backgroundColor: `${BIONIC.green}18`, color: BIONIC.green }}>RECOMMANDE</span>}
                        </div>
                        <div className="grid grid-cols-3 gap-2 text-center">
                          <div>
                            <div className="text-[10px] text-gray-500">Initial</div>
                            <div className="text-sm font-bold text-white">{c.initial_cost_cad}$</div>
                          </div>
                          <div>
                            <div className="text-[10px] text-gray-500">Annuel</div>
                            <div className="text-sm font-bold" style={{ color: BIONIC.orange }}>{c.annual_cost_cad}$</div>
                          </div>
                          <div>
                            <div className="text-[10px] text-gray-500">Par visite</div>
                            <div className="text-sm font-bold text-white">{c.cost_per_visit_cad}$</div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                  <div className="text-[10px] text-gray-500 text-center">Economie annuelle: {comparison.savings_annual_cad}$ | {comparison.recommendation_reason}</div>
                </div>
              )}
            </Section>
          </div>

          {/* ROW 4: Guide site + Construction */}
          <Section icon={Construction} title="Guide d'implantation" color={BIONIC.blue} collapsible testId="site-guide-section">
            <div className="grid grid-cols-2 gap-x-6 gap-y-2 mb-3">
              {Object.entries(recipe.lieu || {}).map(([key, val]) => (
                <div key={key} className="flex justify-between py-1 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
                  <span className="text-xs text-gray-500 capitalize">{key.replace(/_/g, ' ')}</span>
                  <span className="text-xs font-semibold" style={{ color: BIONIC.blue }}>{val}</span>
                </div>
              ))}
            </div>
            <div className="space-y-1">
              {recipe.construction?.map((step, i) => (
                <div key={i} className="text-xs text-gray-400 flex gap-2">
                  <span className="text-amber-400 font-bold flex-shrink-0">{i + 1}.</span>
                  <span>{step}</span>
                </div>
              ))}
            </div>
          </Section>

          {/* ROW 5: Preuves scientifiques */}
          <Section icon={FileText} title="Preuves scientifiques" color="#9C27B0" badge={`${evidence.length} references`} collapsible testId="evidence-section">
            <div className="space-y-2">
              {evidence.length > 0 ? evidence.map((ref, i) => (
                <div key={i} className="rounded-xl p-3" style={{ backgroundColor: 'rgba(156,39,176,0.06)', borderLeft: '3px solid #9C27B0' }} data-testid={`evidence-ref-${i}`}>
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <div className="text-xs font-bold text-white">{ref.titre || ref.title}</div>
                      <div className="text-[10px] text-gray-500">{ref.auteurs || ref.authors}, {ref.annee || ref.year} — {ref.organisme || ref.journal}</div>
                    </div>
                    <a href={ref.doi_ou_url || ref.url} target="_blank" rel="noopener noreferrer" className="text-purple-400 flex-shrink-0 hover:text-purple-300">
                      <ExternalLink className="h-3.5 w-3.5" />
                    </a>
                  </div>
                  <p className="text-[10px] text-gray-400 mt-1.5 leading-relaxed">{ref.resume_court || ref.summary}</p>
                  <div className="flex items-center gap-1.5 mt-1">
                    {ref.type_source && <span className="text-[8px] px-1.5 py-0.5 rounded" style={{ backgroundColor: 'rgba(156,39,176,0.12)', color: '#9C27B0' }}>{ref.type_source?.replace(/_/g, ' ')}</span>}
                    {ref.niveau_preuve && <span className="text-[8px] font-bold px-1.5 py-0.5 rounded" style={{ backgroundColor: ref.niveau_preuve === 'A' ? 'rgba(0,200,83,0.12)' : 'rgba(255,152,0,0.12)', color: ref.niveau_preuve === 'A' ? '#00C853' : '#FF9800' }}>Niv.{ref.niveau_preuve}</span>}
                    {ref.context && <span className="text-[9px] text-purple-300/60">{ref.context}</span>}
                  </div>
                </div>
              )) : (
                <div className="rounded-xl p-4 text-center" style={{ backgroundColor: 'rgba(255,255,255,0.02)' }}>
                  <span className="text-sm text-gray-500">Aucune preuve scientifique formelle disponible pour ce cas.</span>
                </div>
              )}
            </div>
          </Section>

          {/* FOOTER */}
          <div className="text-center text-[10px] text-gray-600 pt-2 pb-4" data-testid="supra-footer">
            x5000 NUTRITION INTELLIGENCE SUPRA | 9 moteurs | BCE-4X / STEEVE-MAX V6
          </div>
        </div>
      )}
    </div>
  );
}

const Select = ({ value, onChange, options, testId }) => (
  <select value={value} onChange={e => onChange(e.target.value)} className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-xs text-white" data-testid={testId}>
    {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
  </select>
);

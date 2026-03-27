/**
 * NutritionIntelligenceSupra.jsx — SUPRA SAL-10 PREMIUM
 * =====================================================
 * Refonte PREMIUM: tableau d'intelligence terrain aligne avec
 * le dossier technique des salines BIONIC.
 * 
 * Sections:
 * 1. Score Global + Phase physiologique
 * 2. Physiologie minerale (narratif)
 * 3. Influence du support (hierarchie substrats)
 * 4. Recette optimale + VOIR LE PRODUIT
 * 5. Score par mineral (barre)
 * 6. Comportement des males (narratif)
 * 7. Guide d'implantation
 * 8. Preuves scientifiques
 * 9. Couts (TOUT EN BAS, discret, collapsible)
 *
 * BCE-4X / STEEVE-MAX V6
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FlaskConical, ShoppingCart, Leaf, Beaker, Mountain, DollarSign, BookOpen,
  ChevronDown, ChevronUp, Thermometer, Droplets, AlertTriangle,
  FileText, ExternalLink, Zap, Package, Construction, Scale,
  Eye, Crown, Activity, ArrowRight, Layers, TreeDeciduous, Gem
} from 'lucide-react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL;

const SUPRA_CMD = '#FF9800';

const BIONIC = {
  green: '#00C853', yellow: '#F9D423', orange: '#FF9800', red: '#D32F2F',
  blue: '#2196F3', purple: '#9C27B0', card: '#111122', cardBorder: 'rgba(255,255,255,0.06)',
  amber: '#FFB300', cyan: '#00BCD4', teal: '#009688',
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

const SUBSTRATE_OPTIONS = [
  { value: 'bois_mou', label: 'Bois mou (recommande)' },
  { value: 'bois_dur', label: 'Bois dur' },
];

// Donnees narratives dossier technique salines BIONIC
const PHYSIOLOGY_DATA = {
  chevreuil: {
    printemps: "Sortie d'hiver. Les reserves minerales sont au plus bas. Le sodium est le premier mineral recherche activement. Le calcium et le phosphore sont critiques pour la regeneration du panache.",
    ete: "Phase de croissance maximale du panache. Besoins en calcium et phosphore x3. Le magnesium soutient la fixation. L'appetit mineral est a son pic.",
    pre_rut: "Transition hormonale. Le testosterone monte. Les mineraux de structure (Ca, P) sont fixes. Le sodium maintient l'hydratation sous effort territorial.",
    rut: "Activite maximale. Perte de poids de 20-30%. Le sodium compense la deshydratation. Le potassium soutient la fonction musculaire. Les visites aux salines diminuent.",
    post_rut: "Recuperation energetique. Les besoins en mineraux de structure baissent. L'appetit mineral reprend progressivement pour reconstituer les reserves.",
    hiver: "Phase de survie. Metabolisme ralenti. Les besoins sont minimaux mais le sodium reste recherche. Les visites sont irregulieres et dependantes de la meteo.",
  },
  orignal: {
    printemps: "Sortie d'hivernage. Deficience severe en sodium apres 5 mois de regime ligneux. Les femelles gestantes ont des besoins en calcium x4.",
    ete: "Panache en velours. Croissance rapide necessitant calcium, phosphore et magnesium. L'orignal consomme activement les plantes aquatiques riches en sodium.",
    rut: "Activite territoriale intense. Pertes hydriques majeures. Le sodium est vital pour maintenir la pression osmotique.",
    hiver: "Metabolisme hivernal. Besoins reduits. Alimentation a base de ramilles.",
  },
};

const SUPPORT_HIERARCHY = [
  { name: 'Bois mou (epinette, sapin)', score: 95, color: BIONIC.green, desc: 'Absorption maximale, retention longue, cout reduit. Support recommande.' },
  { name: 'Bois dur (erable, bouleau)', score: 70, color: BIONIC.yellow, desc: 'Absorption moderee, dissolution plus rapide. Acceptable si bois mou indisponible.' },
  { name: 'Sol nu / terre', score: 45, color: BIONIC.orange, desc: 'Dispersion rapide, contamination possible. Non recommande sauf terrain rocheux.' },
  { name: 'Bloc mineral commercial', score: 60, color: BIONIC.yellow, desc: 'Pratique mais dissolution non controlee. Complement uniquement.' },
];

const MALE_BEHAVIOR = {
  chevreuil: {
    printemps: "Les males visitent les salines 2-4 fois/semaine. Visites matinales (5h-8h) et crepusculaires (18h-21h). Duree moyenne: 8-15 min.",
    ete: "Frequence maximale: 4-7 visites/semaine. Duree prolongee (15-25 min). Marquage territorial frequent autour du site.",
    pre_rut: "Visites irregulieres. Les males commencent a patrouiller. Les frottoirs apparaissent dans un rayon de 200m des salines actives.",
    rut: "Visites rares (1-2/semaine). Durees courtes (<5 min). Les males suivent les femelles qui elles, continuent de visiter.",
    post_rut: "Reprise progressive. 2-3 visites/semaine. Comportement moins territorial.",
    hiver: "Visites sporadiques selon meteo. 1-2/semaine max. Sensible au couvert thermique environnant.",
  },
};

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
  <div className={`rounded-2xl border p-5 ${className}`} style={{ backgroundColor: BIONIC.card, borderColor: BIONIC.cardBorder, boxShadow: '0 2px 12px rgba(0,0,0,0.2)' }} data-testid={testId}>{children}</div>
);

const Section = ({ icon: Icon, title, color, badge, children, collapsible = false, defaultOpen = true, testId }) => {
  const [open, setOpen] = useState(collapsible ? defaultOpen : true);
  return (
    <Card testId={testId}>
      <button onClick={collapsible ? () => setOpen(v => !v) : undefined} className={`w-full flex items-center justify-between ${collapsible ? 'cursor-pointer' : 'cursor-default'}`}>
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${color}15` }}>
            <Icon className="h-4 w-4" style={{ color }} />
          </div>
          <span className="text-sm font-bold text-white uppercase tracking-wider">{title}</span>
        </div>
        <div className="flex items-center gap-2">
          {badge && <span className="text-[10px] font-bold px-2.5 py-1 rounded-lg" style={{ backgroundColor: `${color}18`, color }}>{badge}</span>}
          {collapsible && (open ? <ChevronUp className="h-4 w-4 text-gray-500" /> : <ChevronDown className="h-4 w-4 text-gray-500" />)}
        </div>
      </button>
      {open && <div className="mt-4">{children}</div>}
    </Card>
  );
};

const SupraButton = ({ children, onClick, size = 'md', variant = 'primary', testId }) => {
  const sizeClasses = { sm: 'h-8 px-3 text-xs gap-1.5', md: 'h-9 px-5 text-sm gap-2', lg: 'h-10 px-6 text-sm gap-2' };
  const isPrimary = variant === 'primary';
  return (
    <button
      onClick={onClick}
      className={`flex items-center justify-center rounded-lg font-bold uppercase tracking-wider transition-all duration-150 hover:brightness-125 active:scale-[0.97] ${sizeClasses[size]}`}
      style={{
        backgroundColor: isPrimary ? `${SUPRA_CMD}18` : `${BIONIC.blue}15`,
        color: isPrimary ? SUPRA_CMD : BIONIC.blue,
        border: `2px solid ${isPrimary ? `${SUPRA_CMD}50` : `${BIONIC.blue}40`}`,
      }}
      data-testid={testId}
    >
      {children}
    </button>
  );
};

const Select = ({ value, onChange, options, testId }) => (
  <select value={value} onChange={e => onChange(e.target.value)} className="bg-gray-800/80 border border-gray-700 rounded-lg px-3 py-1.5 text-xs text-white font-bold" data-testid={testId}>
    {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
  </select>
);

export default function NutritionIntelligenceSupra() {
  const navigate = useNavigate();
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
      console.error('[SUPRA]', e);
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

  const physioText = PHYSIOLOGY_DATA[species]?.[season] || PHYSIOLOGY_DATA.chevreuil?.printemps;
  const behaviorText = MALE_BEHAVIOR[species]?.[season] || MALE_BEHAVIOR.chevreuil?.printemps;

  return (
    <div className="min-h-screen bg-[#0a0a14] text-white" data-testid="nutrition-intelligence-supra">
      {/* HEADER PREMIUM */}
      <div className="border-b border-gray-800/50 bg-black/60 backdrop-blur-sm px-6 py-4">
        <div className="max-w-[1200px] mx-auto flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${SUPRA_CMD}30, ${SUPRA_CMD}08)`, border: `2px solid ${SUPRA_CMD}60` }}>
              <FlaskConical className="h-5 w-5" style={{ color: SUPRA_CMD }} />
            </div>
            <div>
              <h1 className="text-lg font-black tracking-tight uppercase" data-testid="supra-title">SUPRA — Intelligence Terrain</h1>
              <p className="text-[10px] text-gray-500 uppercase tracking-wider">Dossier technique salines BIONIC | BCE-4X / STEEVE-MAX V6</p>
            </div>
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <Select value={species} onChange={setSpecies} options={SPECIES_OPTIONS} testId="select-species" />
            <Select value={season} onChange={setSeason} options={SEASON_OPTIONS} testId="select-season" />
            <Select value={soilType} onChange={setSoilType} options={SOIL_OPTIONS} testId="select-soil" />
            <Select value={substrate} onChange={setSubstrate} options={SUBSTRATE_OPTIONS} testId="select-substrate" />
          </div>
        </div>
      </div>

      {loading && (
        <div className="text-center py-16">
          <div className="inline-block w-8 h-8 border-2 border-t-[#FF9800] border-gray-700 rounded-full animate-spin" />
          <p className="text-sm text-gray-500 mt-3">Analyse SUPRA en cours...</p>
        </div>
      )}

      {!loading && score && recipe && (
        <div className="max-w-[1200px] mx-auto px-6 py-6 space-y-4" data-testid="supra-content">

          {/* ═══════════════════════════════════════════════ */}
          {/* 1. SCORE GLOBAL + PHASE PHYSIOLOGIQUE         */}
          {/* ═══════════════════════════════════════════════ */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <Card testId="score-global-card">
              <div className="flex items-center gap-4 mb-3">
                <div className="w-[72px] h-[72px] rounded-2xl flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${gc}22, ${gc}08)`, border: `2.5px solid ${gc}` }}>
                  <span className="text-3xl font-black tabular-nums" style={{ color: gc }}>{score.score_global}</span>
                </div>
                <div>
                  <div className="text-xl font-black text-white">Score Mineral</div>
                  <div className="text-xs font-bold px-2.5 py-0.5 rounded-lg inline-block mt-1" style={{ backgroundColor: `${gc}18`, color: gc }}>{score.grade}</div>
                </div>
              </div>
              <div className="flex gap-3 text-xs font-bold">
                <span style={{ color: BIONIC.green }}>{score.zones_resume.vert} vert</span>
                <span style={{ color: BIONIC.orange }}>{score.zones_resume.jaune} jaune</span>
                <span style={{ color: BIONIC.red }}>{score.zones_resume.rouge} rouge</span>
              </div>
            </Card>

            <Card testId="phase-card" className="lg:col-span-2">
              <div className="flex items-center gap-2 mb-2">
                <Zap className="h-4 w-4" style={{ color: BIONIC.yellow }} />
                <span className="text-sm font-bold uppercase tracking-wider">{recipe.phase_physiologique}</span>
              </div>
              <div className="text-xs text-gray-400 mb-3">{recipe.title} | Sol {recipe.soil_type} | Support: {recipe.substrate?.replace('_', ' ')}</div>
              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-xl p-3" style={{ backgroundColor: `${BIONIC.orange}10`, borderLeft: `3px solid ${BIONIC.orange}` }}>
                  <div className="text-[10px] text-gray-500 uppercase font-bold">Energie</div>
                  <div className="text-sm font-bold mt-0.5" style={{ color: BIONIC.orange }}>{recipe.melange_saisonnier?.name || 'N/A'}</div>
                </div>
                <div className="rounded-xl p-3" style={{ backgroundColor: `${BIONIC.blue}10`, borderLeft: `3px solid ${BIONIC.blue}` }}>
                  <div className="text-[10px] text-gray-500 uppercase font-bold">Proteines</div>
                  <div className="text-sm font-bold mt-0.5" style={{ color: BIONIC.blue }}>{recipe.proteines_cles?.[0]?.brand || 'N/A'}</div>
                </div>
              </div>
            </Card>
          </div>

          {/* ═══════════════════════════════════════════════ */}
          {/* 2. PHYSIOLOGIE MINERALE (narratif)             */}
          {/* ═══════════════════════════════════════════════ */}
          <Section icon={Activity} title="Physiologie minerale" color={BIONIC.cyan} badge={season} testId="physiology-section">
            <p className="text-sm text-gray-300 leading-relaxed">{physioText}</p>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mt-4">
              {[
                { label: 'Sodium (Na)', role: 'Osmose / Hydratation', icon: Droplets, color: BIONIC.blue },
                { label: 'Calcium (Ca)', role: 'Panache / Os', icon: Gem, color: BIONIC.green },
                { label: 'Phosphore (P)', role: 'Energie / ADN', icon: Zap, color: BIONIC.orange },
                { label: 'Magnesium (Mg)', role: 'Muscles / Nerfs', icon: Activity, color: BIONIC.purple },
              ].map((m) => (
                <div key={m.label} className="rounded-xl p-3" style={{ backgroundColor: `${m.color}08`, borderLeft: `3px solid ${m.color}40` }}>
                  <div className="flex items-center gap-1.5 mb-1">
                    <m.icon className="h-3.5 w-3.5" style={{ color: m.color }} />
                    <span className="text-xs font-bold text-white">{m.label}</span>
                  </div>
                  <span className="text-[10px] text-gray-500">{m.role}</span>
                </div>
              ))}
            </div>
          </Section>

          {/* ═══════════════════════════════════════════════ */}
          {/* 3. INFLUENCE DU SUPPORT (hierarchie substrats) */}
          {/* ═══════════════════════════════════════════════ */}
          <Section icon={TreeDeciduous} title="Influence du support" color={BIONIC.teal} badge={substrate.replace('_', ' ')} testId="substrate-section">
            <div className="space-y-2.5">
              {SUPPORT_HIERARCHY.map((s) => {
                const isActive = (substrate === 'bois_mou' && s.name.includes('mou')) || (substrate === 'bois_dur' && s.name.includes('dur'));
                return (
                  <div key={s.name} className="flex items-center gap-4 rounded-xl p-3 transition-all" style={{ backgroundColor: isActive ? `${s.color}10` : 'rgba(255,255,255,0.02)', border: isActive ? `2px solid ${s.color}40` : '2px solid transparent' }}>
                    <div className="w-11 h-11 rounded-lg flex items-center justify-center flex-shrink-0" style={{ backgroundColor: `${s.color}15`, border: `2px solid ${s.color}` }}>
                      <span className="text-sm font-black tabular-nums" style={{ color: s.color }}>{s.score}</span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-bold text-white">{s.name}</div>
                      <div className="text-xs text-gray-400 mt-0.5">{s.desc}</div>
                    </div>
                    {isActive && <span className="text-[10px] font-bold px-2 py-1 rounded-lg flex-shrink-0" style={{ backgroundColor: `${BIONIC.green}18`, color: BIONIC.green }}>ACTIF</span>}
                  </div>
                );
              })}
            </div>
          </Section>

          {/* ═══════════════════════════════════════════════ */}
          {/* 4. RECETTE OPTIMALE + VOIR LE PRODUIT          */}
          {/* ═══════════════════════════════════════════════ */}
          <Section icon={BookOpen} title="Recette optimale" color={BIONIC.green} badge={`${recipe.nb_deficits_critiques} critiques`} testId="recipe-section">
            <div className="space-y-2">
              {recipe.ingredients_cles?.map((ing, i) => (
                <div key={i} className="flex items-center gap-4 py-3 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-bold text-white">{ing.mineral}</div>
                    <div className="text-xs text-gray-500 mt-0.5">{ing.product} — {ing.dosage}</div>
                  </div>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-lg flex-shrink-0" style={{ backgroundColor: `${priorityColor(ing.priority)}15`, color: priorityColor(ing.priority) }}>{ing.priority}</span>
                  <SupraButton
                    size="sm"
                    variant="secondary"
                    testId={`view-product-${i}`}
                    onClick={() => navigate(`/product/${encodeURIComponent(ing.mineral)}`)}
                  >
                    <Eye className="h-3.5 w-3.5" /> Voir le produit
                  </SupraButton>
                </div>
              ))}
            </div>
            {recipe.melange_saisonnier && (
              <div className="rounded-xl p-4 mt-3" style={{ backgroundColor: `${BIONIC.green}08`, borderLeft: `3px solid ${BIONIC.green}` }}>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-bold" style={{ color: BIONIC.green }}>{recipe.melange_saisonnier.name}</div>
                    <div className="text-xs text-gray-400 mt-1">{recipe.melange_saisonnier.ingredients?.join(' | ')}</div>
                    <div className="text-xs text-gray-500 mt-0.5">{recipe.melange_saisonnier.cost_per_25kg_cad}$ / 25kg | {recipe.melange_saisonnier.coverage_m2}m2</div>
                  </div>
                  <SupraButton size="sm" testId="order-melange-btn">
                    <ShoppingCart className="h-3.5 w-3.5" /> CMD
                  </SupraButton>
                </div>
              </div>
            )}
          </Section>

          {/* ═══════════════════════════════════════════════ */}
          {/* 5. SCORE PAR MINERAL (barres)                  */}
          {/* ═══════════════════════════════════════════════ */}
          <Section icon={FlaskConical} title="Score par mineral" color={BIONIC.yellow} badge={`${Object.keys(score.scores_par_mineral).length} mineraux`} testId="minerals-section">
            <div className="space-y-2">
              {Object.entries(score.scores_par_mineral).map(([key, m]) => (
                <div key={key} className="flex items-center gap-3" data-testid={`mineral-row-${key}`}>
                  <span className="text-xs text-gray-300 w-28 flex-shrink-0 font-bold">{m.name}</span>
                  <div className="flex-1 h-[6px] rounded-full overflow-hidden" style={{ backgroundColor: 'rgba(255,255,255,0.04)' }}>
                    <div className="h-full rounded-full" style={{ width: `${m.score}%`, backgroundColor: zoneColor(m.zone), transition: 'width 0.6s ease' }} />
                  </div>
                  <span className="text-sm font-bold w-10 text-right tabular-nums" style={{ color: zoneColor(m.zone) }}>{m.score}</span>
                  <span className="text-[10px] font-bold w-16 text-right uppercase" style={{ color: zoneColor(m.zone) }}>{m.zone}</span>
                  <SupraButton size="sm" testId={`order-btn-${key}`}>
                    <ShoppingCart className="h-3.5 w-3.5" /> CMD
                  </SupraButton>
                </div>
              ))}
            </div>
          </Section>

          {/* ═══════════════════════════════════════════════ */}
          {/* 6. COMPORTEMENT DES MALES (narratif)           */}
          {/* ═══════════════════════════════════════════════ */}
          <Section icon={Crown} title="Comportement des males" color={BIONIC.amber} badge={season} collapsible testId="behavior-section">
            <p className="text-sm text-gray-300 leading-relaxed">{behaviorText}</p>
            <div className="grid grid-cols-3 gap-3 mt-4">
              {[
                { label: 'Frequence', value: season === 'rut' ? '1-2/sem' : season === 'ete' ? '4-7/sem' : '2-4/sem', color: BIONIC.blue },
                { label: 'Duree visite', value: season === 'rut' ? '<5 min' : season === 'ete' ? '15-25 min' : '8-15 min', color: BIONIC.green },
                { label: 'Heures', value: '5h-8h / 18h-21h', color: BIONIC.orange },
              ].map((s) => (
                <div key={s.label} className="rounded-xl p-3 text-center" style={{ backgroundColor: `${s.color}08` }}>
                  <div className="text-[10px] text-gray-500 uppercase font-bold">{s.label}</div>
                  <div className="text-sm font-bold mt-1" style={{ color: s.color }}>{s.value}</div>
                </div>
              ))}
            </div>
          </Section>

          {/* ═══════════════════════════════════════════════ */}
          {/* 7. GUIDE D'IMPLANTATION                        */}
          {/* ═══════════════════════════════════════════════ */}
          <Section icon={Construction} title="Guide d'implantation" color={BIONIC.blue} collapsible testId="site-guide-section">
            <div className="grid grid-cols-2 gap-x-6 gap-y-2 mb-3">
              {Object.entries(recipe.lieu || {}).map(([key, val]) => (
                <div key={key} className="flex justify-between py-1.5 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
                  <span className="text-xs text-gray-500 capitalize">{key.replace(/_/g, ' ')}</span>
                  <span className="text-xs font-bold" style={{ color: BIONIC.blue }}>{val}</span>
                </div>
              ))}
            </div>
            <div className="space-y-1.5">
              {recipe.construction?.map((step, i) => (
                <div key={i} className="text-xs text-gray-400 flex gap-2">
                  <span className="text-amber-400 font-bold flex-shrink-0 w-5">{i + 1}.</span>
                  <span>{step}</span>
                </div>
              ))}
            </div>
          </Section>

          {/* ═══════════════════════════════════════════════ */}
          {/* 8. PREUVES SCIENTIFIQUES                       */}
          {/* ═══════════════════════════════════════════════ */}
          <Section icon={FileText} title="Preuves scientifiques" color={BIONIC.purple} badge={`${evidence.length} references`} collapsible testId="evidence-section">
            <div className="space-y-2">
              {evidence.length > 0 ? evidence.map((ref, i) => (
                <div key={i} className="rounded-xl p-3" style={{ backgroundColor: `${BIONIC.purple}06`, borderLeft: `3px solid ${BIONIC.purple}` }} data-testid={`evidence-ref-${i}`}>
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
                </div>
              )) : (
                <div className="rounded-xl p-4 text-center" style={{ backgroundColor: 'rgba(255,255,255,0.02)' }}>
                  <span className="text-sm text-gray-500">Aucune preuve scientifique formelle disponible.</span>
                </div>
              )}
            </div>
          </Section>

          {/* ═══════════════════════════════════════════════ */}
          {/* 9. COUTS (TOUT EN BAS, discret, collapsible)   */}
          {/* ═══════════════════════════════════════════════ */}
          <Section icon={DollarSign} title="Couts estimes" color={BIONIC.orange} collapsible defaultOpen={false} testId="costs-section">
            {comparison && (
              <div className="space-y-3">
                {['bois_mou', 'bois_dur'].map(sub => {
                  const c = comparison[sub];
                  if (!c) return null;
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
                          <div className="text-sm font-bold text-white tabular-nums">{c.initial_cost_cad}$</div>
                        </div>
                        <div>
                          <div className="text-[10px] text-gray-500">Annuel</div>
                          <div className="text-sm font-bold tabular-nums" style={{ color: BIONIC.orange }}>{c.annual_cost_cad}$</div>
                        </div>
                        <div>
                          <div className="text-[10px] text-gray-500">Par visite</div>
                          <div className="text-sm font-bold text-white tabular-nums">{c.cost_per_visit_cad}$</div>
                        </div>
                      </div>
                    </div>
                  );
                })}
                <div className="text-[10px] text-gray-500 text-center">Economie annuelle: {comparison.savings_annual_cad}$ | {comparison.recommendation_reason}</div>
              </div>
            )}
          </Section>

          {/* FOOTER */}
          <div className="text-center text-[10px] text-gray-600 pt-2 pb-6" data-testid="supra-footer">
            SUPRA Intelligence Terrain | Dossier Technique Salines BIONIC | BCE-4X / STEEVE-MAX V6
          </div>
        </div>
      )}
    </div>
  );
}

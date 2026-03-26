import React, { useState, useEffect, useCallback } from 'react';
import {
  Droplets, FlaskConical, Leaf, MapPin, AlertTriangle, Layers, Beaker,
  ShoppingCart, DollarSign, BookOpen, FileText, ExternalLink, Zap, Package,
  Construction, Scale, BarChart3, ArrowRight
} from 'lucide-react';
import axios from 'axios';
import PinnablePanel from './PinnablePanel';

/**
 * NutritionPointDetailPanel.jsx — SUPRA PANEL complet
 * BCE-4X P0: Uniformisation SUPRA — Couleur unique, format unique, typo WAYPOINT
 * Tous les boutons CMD/Commandez/Commander tout -> couleur officielle SUPRA #FF9800
 * Titres 24px | Sous-titres 20px | Valeurs 22-26px | Desc 17-18px | Labels 14px+
 * Espacements 20-28px | WCAG AA | BCE-4X / STEEVE-MAX V6
 */

const API = process.env.REACT_APP_BACKEND_URL;

// BCE-4X P0: Couleur officielle SUPRA pour TOUS les boutons de commande
const SUPRA_CMD_COLOR = '#FF9800';

const BIONIC = {
  green: '#00C853', yellow: '#F9D423', orange: '#FF9800', red: '#D32F2F',
  blue: '#2196F3', purple: '#9C27B0', card: '#111122', cardBorder: 'rgba(255,255,255,0.06)',
  supraCmd: SUPRA_CMD_COLOR,
};

function gradeColor(grade) {
  if (grade === 'EXCELLENT') return BIONIC.green;
  if (grade === 'BON') return BIONIC.yellow;
  if (grade === 'MODERE') return BIONIC.orange;
  return BIONIC.red;
}
function zoneColor(z) { return z === 'vert' ? BIONIC.green : z === 'jaune' ? BIONIC.orange : BIONIC.red; }
function priorityColor(p) { return p === 'CRITIQUE' ? BIONIC.red : p === 'RECOMMANDE' ? BIONIC.orange : BIONIC.green; }

const Card = ({ children, testId, className = '' }) => (
  <div
    className={`rounded-xl border p-5 ${className}`}
    style={{ backgroundColor: BIONIC.card, borderColor: BIONIC.cardBorder, boxShadow: '0 2px 12px rgba(0,0,0,0.25)' }}
    data-testid={testId}
  >
    {children}
  </div>
);

const TABS = [
  { id: 'analyse', label: 'Analyse', icon: FlaskConical },
  { id: 'intelligence', label: 'Intelligence', icon: BarChart3 },
  { id: 'comparez', label: 'Comparez', icon: Scale },
  { id: 'commandez', label: 'Commandez', icon: ShoppingCart },
];

const NutritionPointDetailPanel = ({ nutritionPoint, onClose }) => {
  const [activeTab, setActiveTab] = useState('analyse');
  const [supraData, setSupraData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [compareIds, setCompareIds] = useState([]);

  const np = nutritionPoint;
  const species = np?.species || 'chevreuil';
  const season = np?.season || 'printemps';
  const soilType = np?.soil_type || 'mixte';

  const fetchSupra = useCallback(async () => {
    if (!np) return;
    setLoading(true);
    try {
      const res = await axios.post(`${API}/api/v6/nutrition-intelligence/supra-panel`, {
        species, season, soil_type: soilType, substrate: 'bois_mou',
      });
      setSupraData(res.data);
    } catch (e) {
      console.error('[SUPRA]', e);
    } finally {
      setLoading(false);
    }
  }, [np, species, season, soilType]);

  useEffect(() => { fetchSupra(); }, [fetchSupra]);

  if (!np) return null;

  const score = supraData?.score;
  const recipe = supraData?.recipe;
  const recommendations = supraData?.recommendations;
  const products = supraData?.products;
  const evidence = supraData?.evidence || [];
  const costs = supraData?.costs;
  const comparison = supraData?.substrate_comparison;
  const order = supraData?.order;
  const ecozone = supraData?.ecozone?.data;
  const energyProtein = supraData?.energy_protein;
  const terrainSolutions = supraData?.terrain_solutions;
  const gc = score ? gradeColor(score.grade) : BIONIC.blue;

  const toggleCompare = (pid) => {
    setCompareIds(prev => prev.includes(pid) ? prev.filter(x => x !== pid) : prev.length < 4 ? [...prev, pid] : prev);
  };

  return (
    <PinnablePanel
      title={`SUPRA — ${np.id}`}
      subtitle={`${species} | ${season} | ${soilType} | ${np.distance_centre_m}m`}
      icon={Droplets}
      accentColor={gc}
      onClose={onClose}
      defaultWidth={580}
      maxHeight="100vh"
      testId="nutrition-point-detail-panel"
      showPrint={true}
      fullHeight={true}
    >
      <div className="h-full flex flex-col overflow-hidden" data-testid="supra-panel-content">
        {/* TABS — BCE-4X P0: Typographie WAYPOINT, couleur SUPRA unifiee */}
        <div className="flex items-center gap-2 px-5 pt-4 pb-3 border-b flex-shrink-0" style={{ borderColor: 'rgba(255,255,255,0.08)' }} data-testid="supra-tabs">
          {TABS.map(tab => {
            const active = activeTab === tab.id;
            const Icon = tab.icon;
            const isOrder = tab.id === 'commandez';
            const activeColor = isOrder ? SUPRA_CMD_COLOR : gc;
            return (
              <button
                key={tab.id}
                data-testid={`supra-tab-${tab.id}`}
                onClick={() => setActiveTab(tab.id)}
                className="flex items-center gap-2 h-9 px-5 rounded-lg text-sm font-bold uppercase tracking-wider transition-all duration-150"
                style={{
                  backgroundColor: active ? `${activeColor}18` : 'transparent',
                  color: active ? activeColor : '#6b7280',
                  border: active ? `2px solid ${activeColor}50` : '2px solid transparent',
                }}
              >
                <Icon className="h-4 w-4" />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* CONTENT — padding 20px */}
        <div className="flex-1 overflow-y-auto p-5" style={{ maxHeight: 'calc(100vh - 140px)' }}>
          {loading && <div className="text-center py-10 text-gray-400 text-[17px] animate-pulse">Analyse SUPRA en cours...</div>}

          {!loading && score && activeTab === 'analyse' && (
            <AnalyseTab score={score} recipe={recipe} recommendations={recommendations} evidence={evidence} costs={costs} comparison={comparison} ecozone={ecozone} energyProtein={energyProtein} terrainSolutions={terrainSolutions} gc={gc} np={np} />
          )}

          {!loading && products && activeTab === 'intelligence' && (
            <IntelligenceTab products={products} gc={gc} compareIds={compareIds} toggleCompare={toggleCompare} />
          )}

          {!loading && products && activeTab === 'comparez' && (
            <ComparezTab products={products} compareIds={compareIds} gc={gc} toggleCompare={toggleCompare} />
          )}

          {!loading && order && activeTab === 'commandez' && (
            <CommandezTab order={order} products={products} recipe={recipe} gc={gc} />
          )}
        </div>

        {/* FOOTER — 13px minimum */}
        <div className="text-center text-[13px] text-gray-500 py-2.5 border-t flex-shrink-0" style={{ borderColor: 'rgba(255,255,255,0.06)' }} data-testid="supra-footer">
          x5000 SUPRA | x6000 PRODUCT_SCORE | BCE-4X / STEEVE-MAX V6
        </div>
      </div>
    </PinnablePanel>
  );
};

/* ============================================================ */
/* TAB: ANALYSE — Typographie BIONIC Premium                    */
/* ============================================================ */
const AnalyseTab = ({ score, recipe, recommendations, evidence, costs, comparison, ecozone, energyProtein, terrainSolutions, gc, np }) => {
  const needColor = (level) => {
    if (level === 'EXTREME' || level === 'CRITIQUE') return BIONIC.red;
    if (level === 'TRES ELEVE' || level === 'ELEVE') return BIONIC.orange;
    if (level === 'MODERE') return BIONIC.yellow;
    if (level === 'N/A') return '#6b7280';
    return BIONIC.green;
  };

  return (
  <div className="grid grid-cols-2 gap-6" data-testid="supra-analyse-tab">
    {/* COL GAUCHE */}
    <div className="flex flex-col gap-5">
      {/* Score global — Titre 24px, Score 26px */}
      <Card testId="supra-score-card">
        <div className="flex items-center gap-4">
          <div className="w-[72px] h-[72px] rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: `linear-gradient(135deg, ${gc}22, ${gc}08)`, border: `2.5px solid ${gc}` }}>
            <span className="text-[26px] font-black" style={{ color: gc }}>{score.score_global}</span>
          </div>
          <div>
            <div className="text-[20px] font-black text-white leading-tight">Score Mineral</div>
            <div className="text-[14px] font-bold px-3 py-1 rounded-lg inline-block mt-1.5" style={{ backgroundColor: `${gc}18`, color: gc }}>{score.grade}</div>
            <div className="flex gap-3 mt-2 text-[14px]">
              <span style={{ color: BIONIC.green }}>{score.zones_resume.vert} vert</span>
              <span style={{ color: BIONIC.orange }}>{score.zones_resume.jaune} jaune</span>
              <span style={{ color: BIONIC.red }}>{score.zones_resume.rouge} rouge</span>
            </div>
          </div>
        </div>
      </Card>

      {/* Mineraux — barres — Titre 20px, Labels 15px, Scores 16px */}
      <Card testId="supra-minerals-card" className="flex-1">
        <div className="flex items-center gap-2.5 mb-4">
          <FlaskConical className="h-5 w-5" style={{ color: BIONIC.yellow }} />
          <span className="text-[20px] font-bold text-white">Mineraux</span>
        </div>
        <div className="space-y-2.5">
          {Object.entries(score.scores_par_mineral).map(([key, m]) => (
            <div key={key} className="flex items-center gap-3" data-testid={`supra-mineral-${key}`}>
              <span className="text-[15px] text-gray-300 w-24 flex-shrink-0">{m.name}</span>
              <div className="flex-1 h-[6px] rounded-full overflow-hidden" style={{ backgroundColor: 'rgba(255,255,255,0.06)' }}>
                <div className="h-full rounded-full transition-all" style={{ width: `${m.score}%`, backgroundColor: zoneColor(m.zone) }} />
              </div>
              <span className="text-[16px] font-bold w-10 text-right" style={{ color: zoneColor(m.zone) }}>{m.score}</span>
            </div>
          ))}
        </div>
      </Card>

      {/* PHASE 3A — Besoins nutritionnels (Energie/Proteines) */}
      {energyProtein && (
        <Card testId="supra-energy-protein-card">
          <div className="flex items-center gap-2.5 mb-3">
            <Zap className="h-5 w-5" style={{ color: BIONIC.orange }} />
            <span className="text-[20px] font-bold text-white">Besoins nutritionnels</span>
          </div>
          <div className="text-[15px] text-gray-300 mb-3">{energyProtein.phase}</div>
          <div className="grid grid-cols-2 gap-3 mb-3">
            <div className="rounded-lg p-3" style={{ backgroundColor: 'rgba(255,255,255,0.04)', borderLeft: `3px solid ${needColor(energyProtein.energy_need)}` }}>
              <div className="text-[14px] text-gray-400 mb-1">Energie</div>
              <div className="text-[17px] font-bold" style={{ color: needColor(energyProtein.energy_need) }}>{energyProtein.energy_need}</div>
            </div>
            <div className="rounded-lg p-3" style={{ backgroundColor: 'rgba(255,255,255,0.04)', borderLeft: `3px solid ${needColor(energyProtein.protein_need)}` }}>
              <div className="text-[14px] text-gray-400 mb-1">Proteines</div>
              <div className="text-[17px] font-bold" style={{ color: needColor(energyProtein.protein_need) }}>{energyProtein.protein_need}</div>
            </div>
          </div>
          {energyProtein.seasonal_mix && (
            <div className="rounded-lg p-3" style={{ backgroundColor: 'rgba(255,255,255,0.03)' }}>
              <div className="text-[14px] font-bold text-white mb-1">{energyProtein.seasonal_mix.name}</div>
              <div className="flex flex-wrap gap-1.5">
                {energyProtein.seasonal_mix.ingredients?.map((ing, i) => (
                  <span key={i} className="text-[12px] px-2 py-0.5 rounded" style={{ backgroundColor: `${BIONIC.orange}12`, color: BIONIC.orange }}>{ing}</span>
                ))}
              </div>
              <div className="text-[14px] text-gray-400 mt-2">{energyProtein.seasonal_mix.cost_per_25kg_cad}$ / 25kg</div>
            </div>
          )}
        </Card>
      )}

      {/* Ecozone — Titre 20px, Desc 17px, Detail 15px */}
      {ecozone && (
        <Card testId="supra-ecozone-card">
          <div className="flex items-center gap-2.5 mb-3">
            <Leaf className="h-5 w-5" style={{ color: BIONIC.green }} />
            <span className="text-[20px] font-bold text-white">Zone ecologique</span>
          </div>
          <div className="text-[17px] text-gray-300 mb-2">{ecozone.nom_commun}</div>
          <div className="text-[15px] text-gray-400 leading-relaxed">{ecozone.habitat_principal}</div>
          {ecozone.comportement_saisonnier?.[recipe?.season] && (
            <div className="mt-3 rounded-lg p-3" style={{ backgroundColor: `${BIONIC.green}08`, borderLeft: `3px solid ${BIONIC.green}` }}>
              <span className="text-[15px] text-gray-300">{ecozone.comportement_saisonnier[recipe.season]}</span>
            </div>
          )}
        </Card>
      )}
    </div>

    {/* COL DROITE */}
    <div className="flex flex-col gap-5">
      {/* Recette — Titre 20px, Ingredients 17px, Labels 14px */}
      {recipe && (
        <Card testId="supra-recipe-card">
          <div className="flex items-center gap-2.5 mb-3">
            <BookOpen className="h-5 w-5" style={{ color: BIONIC.green }} />
            <span className="text-[20px] font-bold text-white">Recette</span>
            <span className="text-[14px] text-gray-400 ml-auto">{recipe.title}</span>
          </div>
          <div className="space-y-2">
            {recipe.ingredients_cles?.slice(0, 5).map((ing, i) => (
              <div key={i} className="flex items-center justify-between py-1.5 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
                <div>
                  <span className="text-[17px] text-white">{ing.mineral}</span>
                  <span className="text-[14px] text-gray-400 ml-2">{ing.product}</span>
                </div>
                <span className="text-[14px] font-bold px-2.5 py-1 rounded" style={{ backgroundColor: `${priorityColor(ing.priority)}15`, color: priorityColor(ing.priority) }}>{ing.priority}</span>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Couts — Titre 20px, Valeurs 22px, Labels 14px */}
      {costs && (
        <Card testId="supra-costs-card">
          <div className="flex items-center gap-2.5 mb-3">
            <DollarSign className="h-5 w-5" style={{ color: BIONIC.orange }} />
            <span className="text-[20px] font-bold text-white">Couts</span>
          </div>
          <div className="grid grid-cols-3 gap-3 text-center">
            <div className="rounded-lg p-3" style={{ backgroundColor: 'rgba(255,255,255,0.04)' }}>
              <div className="text-[14px] text-gray-400 mb-1">Initial</div>
              <div className="text-[22px] font-bold text-white">{costs.initial_cost_cad}$</div>
            </div>
            <div className="rounded-lg p-3" style={{ backgroundColor: 'rgba(255,255,255,0.04)' }}>
              <div className="text-[14px] text-gray-400 mb-1">Annuel</div>
              <div className="text-[22px] font-bold" style={{ color: BIONIC.orange }}>{costs.annual_cost_cad}$</div>
            </div>
            <div className="rounded-lg p-3" style={{ backgroundColor: 'rgba(255,255,255,0.04)' }}>
              <div className="text-[14px] text-gray-400 mb-1">Par visite</div>
              <div className="text-[22px] font-bold text-white">{costs.cost_per_visit_cad}$</div>
            </div>
          </div>
        </Card>
      )}

      {/* PHASE 3B — Solutions Terrain */}
      {terrainSolutions && terrainSolutions.total > 0 && (
        <Card testId="supra-terrain-solutions-card">
          <div className="flex items-center gap-2.5 mb-3">
            <Construction className="h-5 w-5" style={{ color: BIONIC.green }} />
            <span className="text-[20px] font-bold text-white">Solutions terrain</span>
            <span className="text-[14px] text-gray-400 ml-auto">{terrainSolutions.critiques} critiques</span>
          </div>
          <div className="space-y-2">
            {terrainSolutions.solutions?.slice(0, 5).map((sol, i) => (
              <div key={i} className="rounded-lg p-3" style={{ backgroundColor: 'rgba(255,255,255,0.03)', borderLeft: `3px solid ${sol.priority === 'CRITIQUE' ? BIONIC.red : BIONIC.green}` }} data-testid={`terrain-solution-${i}`}>
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <div className="text-[15px] font-bold text-white">{sol.name}</div>
                    <div className="text-[14px] text-gray-400 mt-0.5">{sol.deficit}</div>
                  </div>
                  <span className="text-[12px] font-bold px-2 py-0.5 rounded flex-shrink-0" style={{ backgroundColor: `${sol.priority === 'CRITIQUE' ? BIONIC.red : BIONIC.green}15`, color: sol.priority === 'CRITIQUE' ? BIONIC.red : BIONIC.green }}>{sol.priority}</span>
                </div>
                <div className="text-[13px] text-gray-500 mt-1">{sol.description?.slice(0, 80)}...</div>
                <div className="flex gap-2 mt-1.5">
                  <span className="text-[12px] px-2 py-0.5 rounded" style={{ backgroundColor: `${BIONIC.blue}12`, color: BIONIC.blue }}>{sol.type?.replace(/_/g, ' ')}</span>
                  <span className="text-[12px] text-gray-500">{sol.cost_range_cad}</span>
                  <span className="text-[12px] text-gray-500">{sol.efficacy_months} mois</span>
                </div>
              </div>
            ))}
          </div>
          <div className="text-[14px] text-gray-400 mt-3">Cout total estime: {terrainSolutions.cost_estimate_min_cad}$ - {terrainSolutions.cost_estimate_max_cad}$</div>
        </Card>
      )}

      {/* Preuves — Titre 20px, Refs 15px, Auteurs 14px, Badges 12px */}
      {evidence.length > 0 ? (
        <Card testId="supra-evidence-card" className="flex-1">
          <div className="flex items-center gap-2.5 mb-3">
            <FileText className="h-5 w-5" style={{ color: BIONIC.purple }} />
            <span className="text-[20px] font-bold text-white">Preuves scientifiques</span>
            <span className="text-[14px] text-gray-400 ml-auto">{evidence.length} refs</span>
          </div>
          <div className="space-y-2.5">
            {evidence.slice(0, 4).map((ref, i) => (
              <div key={i} className="rounded-lg p-3" style={{ backgroundColor: 'rgba(156,39,176,0.06)', borderLeft: `3px solid ${BIONIC.purple}` }} data-testid={`supra-evidence-${i}`}>
                <div className="flex items-start justify-between gap-2">
                  <span className="text-[15px] font-bold text-white leading-snug">{ref.titre}</span>
                  <a href={ref.doi_ou_url} target="_blank" rel="noopener noreferrer" className="flex-shrink-0"><ExternalLink className="h-4 w-4 text-purple-400" /></a>
                </div>
                <span className="text-[14px] text-gray-400 block mt-1">{ref.auteurs}, {ref.annee}</span>
                <div className="flex items-center gap-2 mt-1.5">
                  <span className="text-[12px] px-2 py-0.5 rounded" style={{ backgroundColor: `${BIONIC.purple}15`, color: BIONIC.purple }}>{ref.type_source?.replace(/_/g, ' ')}</span>
                  <span className="text-[12px] text-gray-500">{ref.organisme}</span>
                  {ref.niveau_preuve && <span className="text-[12px] font-bold px-2 py-0.5 rounded" style={{ backgroundColor: ref.niveau_preuve === 'A' ? `${BIONIC.green}15` : `${BIONIC.orange}15`, color: ref.niveau_preuve === 'A' ? BIONIC.green : BIONIC.orange }}>Niv.{ref.niveau_preuve}</span>}
                </div>
              </div>
            ))}
          </div>
        </Card>
      ) : (
        <Card testId="supra-evidence-card" className="flex-1">
          <div className="flex items-center gap-2.5 mb-3">
            <FileText className="h-5 w-5" style={{ color: BIONIC.purple }} />
            <span className="text-[20px] font-bold text-white">Preuves scientifiques</span>
          </div>
          <div className="rounded-lg p-4 text-center" style={{ backgroundColor: 'rgba(255,255,255,0.03)' }}>
            <AlertTriangle className="h-6 w-6 text-gray-500 mx-auto mb-2" />
            <span className="text-[16px] text-gray-400">Aucune preuve scientifique formelle disponible pour ce cas.</span>
          </div>
        </Card>
      )}
    </div>
  </div>
  );
};

/* ============================================================ */
/* TAB: INTELLIGENCE — Typographie BIONIC Premium               */
/* ============================================================ */
const IntelligenceTab = ({ products, gc, compareIds, toggleCompare }) => (
  <div className="space-y-5" data-testid="supra-intelligence-tab">
    <div className="text-[17px] text-gray-300 mb-4">Score d'adequation par produit — {products.total} produits analyses</div>
    <div className="space-y-3">
      {products.products?.map((p, i) => {
        const sc = p.score_global >= 85 ? BIONIC.green : p.score_global >= 70 ? BIONIC.yellow : p.score_global >= 50 ? BIONIC.orange : BIONIC.red;
        const isCompared = compareIds.includes(p.product_id);
        return (
          <Card key={p.product_id} testId={`product-${p.product_id}`}>
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: `linear-gradient(135deg, ${sc}22, ${sc}08)`, border: `2px solid ${sc}` }}>
                <span className="text-[22px] font-black" style={{ color: sc }}>{p.score_global}</span>
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-[17px] font-bold text-white truncate">{p.name}</div>
                <div className="text-[14px] text-gray-400 mt-0.5">{p.type} | {p.price_cad}$ | {p.weight_kg}kg | {p.duration_weeks} sem</div>
                <div className="flex gap-1.5 mt-1.5 flex-wrap">
                  {p.optimal_for?.map((tag, j) => (
                    <span key={j} className="text-[12px] px-2 py-0.5 rounded" style={{ backgroundColor: `${BIONIC.green}15`, color: BIONIC.green }}>{tag}</span>
                  ))}
                  {p.tags?.slice(0, 2).map((tag, j) => (
                    <span key={`t${j}`} className="text-[12px] px-2 py-0.5 rounded" style={{ backgroundColor: 'rgba(255,255,255,0.05)', color: '#9ca3af' }}>{tag}</span>
                  ))}
                  {p.quality && <span className="text-[12px] px-2 py-0.5 rounded" style={{ backgroundColor: `${p.quality.score >= 85 ? BIONIC.green : BIONIC.orange}15`, color: p.quality.score >= 85 ? BIONIC.green : BIONIC.orange }}>Q:{p.quality.score}</span>}
                  {p.availability && <span className="text-[12px] px-2 py-0.5 rounded" style={{ backgroundColor: `${p.availability.province_status === 'disponible' ? BIONIC.green : BIONIC.orange}15`, color: p.availability.province_status === 'disponible' ? BIONIC.green : BIONIC.orange }}>{p.availability.province_status === 'disponible' ? 'Dispo QC' : 'Import'}</span>}
                  {p.compliance && <span className="text-[12px] px-2 py-0.5 rounded" style={{ backgroundColor: `${p.compliance.score >= 85 ? BIONIC.green : BIONIC.orange}15`, color: p.compliance.score >= 85 ? BIONIC.green : BIONIC.orange }}>{p.compliance.grade}</span>}
                </div>
              </div>
              <div className="flex flex-col gap-2 flex-shrink-0">
                <div className="grid grid-cols-3 gap-2 text-center">
                  <div><div className="text-[12px] text-gray-400">Espece</div><div className="text-[16px] font-bold" style={{ color: p.score_species >= 85 ? BIONIC.green : BIONIC.orange }}>{p.score_species}%</div></div>
                  <div><div className="text-[12px] text-gray-400">Saison</div><div className="text-[16px] font-bold" style={{ color: p.score_season >= 85 ? BIONIC.green : BIONIC.orange }}>{p.score_season}%</div></div>
                  <div><div className="text-[12px] text-gray-400">Sol</div><div className="text-[16px] font-bold" style={{ color: p.score_soil >= 85 ? BIONIC.green : BIONIC.orange }}>{p.score_soil}%</div></div>
                </div>
                <button
                  onClick={() => toggleCompare(p.product_id)}
                  className="text-[14px] font-bold px-3 py-1.5 rounded-lg transition-all"
                  style={{
                    backgroundColor: isCompared ? `${BIONIC.blue}20` : 'rgba(255,255,255,0.05)',
                    color: isCompared ? BIONIC.blue : '#9ca3af',
                    border: `1px solid ${isCompared ? `${BIONIC.blue}40` : 'transparent'}`,
                  }}
                  data-testid={`compare-toggle-${p.product_id}`}
                >
                  {isCompared ? 'Retire' : 'Comparer'}
                </button>
              </div>
            </div>
          </Card>
        );
      })}
    </div>
  </div>
);

/* ============================================================ */
/* TAB: COMPAREZ — Typographie BIONIC Premium                   */
/* ============================================================ */
const ComparezTab = ({ products, compareIds, gc, toggleCompare }) => {
  const compared = (products.products || []).filter(p => compareIds.includes(p.product_id));
  if (compared.length === 0) {
    return (
      <div className="text-center py-12" data-testid="supra-comparez-tab">
        <Scale className="h-10 w-10 text-gray-500 mx-auto mb-4" />
        <div className="text-[18px] text-gray-300 font-semibold">Aucun produit selectionne</div>
        <div className="text-[15px] text-gray-500 mt-2">Allez dans l'onglet INTELLIGENCE et selectionnez 2-4 produits a comparer</div>
      </div>
    );
  }

  const best = compared.reduce((a, b) => a.score_global > b.score_global ? a : b);
  return (
    <div data-testid="supra-comparez-tab">
      <div className="text-[17px] text-gray-300 mb-4">{compared.length} produit(s) compares — max 4</div>
      <div className="grid gap-5" style={{ gridTemplateColumns: `repeat(${Math.min(compared.length, 4)}, 1fr)` }}>
        {compared.map(p => {
          const isBest = p.product_id === best.product_id;
          const sc = p.score_global >= 85 ? BIONIC.green : p.score_global >= 70 ? BIONIC.yellow : p.score_global >= 50 ? BIONIC.orange : BIONIC.red;
          return (
            <Card key={p.product_id} testId={`compare-card-${p.product_id}`} className={isBest ? 'ring-1 ring-green-500/30' : ''}>
              {isBest && <div className="text-[14px] font-bold text-center mb-2" style={{ color: BIONIC.green }}>MEILLEUR CHOIX</div>}
              <div className="text-center mb-4">
                <div className="w-16 h-16 rounded-xl flex items-center justify-center mx-auto" style={{ background: `linear-gradient(135deg, ${sc}22, ${sc}08)`, border: `2px solid ${sc}` }}>
                  <span className="text-[24px] font-black" style={{ color: sc }}>{p.score_global}</span>
                </div>
                <div className="text-[16px] font-bold text-white mt-2">{p.name}</div>
                <div className="text-[14px] text-gray-400">{p.type}</div>
              </div>
              <div className="space-y-2">
                {[
                  { label: 'Espece', val: `${p.score_species}%`, color: p.score_species >= 85 ? BIONIC.green : BIONIC.orange },
                  { label: 'Saison', val: `${p.score_season}%`, color: p.score_season >= 85 ? BIONIC.green : BIONIC.orange },
                  { label: 'Sol', val: `${p.score_soil}%`, color: p.score_soil >= 85 ? BIONIC.green : BIONIC.orange },
                  { label: 'Prix', val: `${p.price_cad}$`, color: '#fff' },
                  { label: 'Duree', val: `${p.duration_weeks} sem`, color: '#fff' },
                ].map((row, i) => (
                  <div key={i} className="flex justify-between py-1 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
                    <span className="text-[14px] text-gray-400">{row.label}</span>
                    <span className="text-[14px] font-bold" style={{ color: row.color }}>{row.val}</span>
                  </div>
                ))}
              </div>
              <div className="flex gap-1.5 mt-3 flex-wrap">
                {p.minerals?.map((m, j) => (
                  <span key={j} className="text-[12px] px-2 py-0.5 rounded" style={{ backgroundColor: `${BIONIC.yellow}15`, color: BIONIC.yellow }}>{m}</span>
                ))}
              </div>
              <button
                onClick={() => toggleCompare(p.product_id)}
                className="w-full mt-3 text-[14px] font-bold py-2 rounded-lg transition-all"
                style={{ backgroundColor: `${BIONIC.red}15`, color: BIONIC.red }}
              >
                Retirer
              </button>
            </Card>
          );
        })}
      </div>
    </div>
  );
};

/* ============================================================ */
/* TAB: COMMANDEZ — BCE-4X P0 SUPRA UNIFORMISATION             */
/* Couleur unique: #FF9800 | Format unifie | Typo WAYPOINT     */
/* ============================================================ */
const SupraButton = ({ children, onClick, size = 'md', disabled = false, testId }) => {
  const sizeClasses = {
    sm: 'h-8 px-3 text-xs gap-1.5',
    md: 'h-9 px-5 text-sm gap-2',
    lg: 'h-10 px-6 text-sm gap-2',
  };
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`flex items-center justify-center rounded-lg font-bold uppercase tracking-wider transition-all duration-150 ${sizeClasses[size]} ${
        disabled
          ? 'opacity-40 cursor-not-allowed'
          : 'hover:brightness-125 active:scale-[0.97]'
      }`}
      style={{
        backgroundColor: disabled ? '#37415115' : `${SUPRA_CMD_COLOR}18`,
        color: disabled ? '#6b7280' : SUPRA_CMD_COLOR,
        border: `2px solid ${disabled ? '#37415130' : `${SUPRA_CMD_COLOR}50`}`,
      }}
      data-testid={testId}
      data-bce4x-locked="true"
    >
      {children}
    </button>
  );
};

const CommandezTab = ({ order, products, recipe, gc }) => (
  <div className="space-y-5" data-testid="supra-commandez-tab">
    {/* Pack complet */}
    <Card testId="order-pack-card">
      <div className="flex items-center gap-3 mb-4">
        <Package className="h-5 w-5" style={{ color: SUPRA_CMD_COLOR }} />
        <span className="text-[20px] font-bold text-white">Recette complete</span>
        <span className="text-[18px] font-bold ml-auto" style={{ color: SUPRA_CMD_COLOR }}>{order.summary.cost_initial_cad}$</span>
      </div>
      <div className="space-y-0">
        {order.items?.map((item, i) => (
          <div key={i} className="flex items-center gap-4 py-3 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
            <div className="flex-1 min-w-0">
              <div className="text-[15px] font-bold text-white truncate">{item.name}</div>
              <div className="text-[13px] text-gray-500 mt-0.5">{item.brand} | {item.dosage} | Qte: {item.quantity}</div>
            </div>
            <div className="flex items-center gap-3 flex-shrink-0">
              <span className="text-[15px] font-bold text-white tabular-nums w-16 text-right">{item.total_price_cad}$</span>
              <span className="text-[11px] font-bold px-2 py-0.5 rounded-md uppercase" style={{ backgroundColor: `${priorityColor(item.priority)}12`, color: priorityColor(item.priority) }}>{item.priority}</span>
            </div>
          </div>
        ))}
      </div>
      <div className="flex items-center justify-between mt-4 pt-3 border-t" style={{ borderColor: 'rgba(255,255,255,0.08)' }}>
        <div className="text-[13px] text-gray-400">
          {order.summary.reactivation_frequency_weeks} sem | {order.summary.cost_annual_cad}$/an | {order.summary.cost_per_visit_cad}$/visite
        </div>
        <SupraButton size="md" testId="order-complete-btn">
          <ShoppingCart className="h-4 w-4" /> Commander
        </SupraButton>
      </div>
    </Card>

    {/* Produits individuels — tableau modernise */}
    <div className="text-[15px] font-bold text-gray-300 uppercase tracking-wider mb-3">Produits individuels</div>
    <div className="space-y-2">
      {products?.products?.slice(0, 8).map(p => {
        const sc = p.score_global >= 85 ? BIONIC.green : p.score_global >= 70 ? BIONIC.yellow : p.score_global >= 50 ? BIONIC.orange : BIONIC.red;
        return (
          <div
            key={p.product_id}
            className="flex items-center gap-4 px-4 py-3 rounded-xl border transition-all hover:border-[#FF980030]"
            style={{ backgroundColor: BIONIC.card, borderColor: BIONIC.cardBorder }}
            data-testid={`shop-product-${p.product_id}`}
          >
            {/* Score badge */}
            <div className="w-11 h-11 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: `${sc}12`, border: `2px solid ${sc}` }}>
              <span className="text-[15px] font-black tabular-nums" style={{ color: sc }}>{p.score_global}</span>
            </div>
            {/* Product info */}
            <div className="flex-1 min-w-0">
              <div className="text-[15px] font-bold text-white truncate">{p.name}</div>
              <div className="flex gap-1.5 mt-1 flex-wrap">
                {p.optimal_for?.map((tag, j) => (
                  <span key={j} className="text-[11px] px-2 py-0.5 rounded-md" style={{ backgroundColor: `${BIONIC.green}12`, color: BIONIC.green }}>Optimal: {tag}</span>
                ))}
              </div>
            </div>
            {/* Price — aligned */}
            <span className="text-[15px] font-bold text-white tabular-nums w-16 text-right flex-shrink-0">{p.price_cad}$</span>
            {/* CMD button — unifie SUPRA */}
            <SupraButton size="sm" testId={`shop-order-${p.product_id}`}>
              <ShoppingCart className="h-3.5 w-3.5" /> CMD
            </SupraButton>
          </div>
        );
      })}
    </div>
  </div>
);

export default NutritionPointDetailPanel;

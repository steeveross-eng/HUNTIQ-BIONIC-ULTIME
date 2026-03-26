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
 * Directive SUPRA Phase 2C: appels API reels x5100-x6000
 * Layout pleine page 100vh, ZERO scroll, X + Imprimer fixes
 * BCE-4X / STEEVE-MAX V6
 */

const API = process.env.REACT_APP_BACKEND_URL;

const BIONIC = {
  green: '#00C853', yellow: '#F9D423', orange: '#FF9800', red: '#D32F2F',
  blue: '#2196F3', purple: '#9C27B0', card: '#111122', cardBorder: 'rgba(255,255,255,0.06)',
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
  <div className={`rounded-xl border p-2.5 ${className}`} style={{ backgroundColor: BIONIC.card, borderColor: BIONIC.cardBorder, boxShadow: '0 2px 8px rgba(0,0,0,0.2)' }} data-testid={testId}>{children}</div>
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
        {/* TABS */}
        <div className="flex items-center gap-1 px-3 pt-2 pb-1 border-b flex-shrink-0" style={{ borderColor: 'rgba(255,255,255,0.06)' }} data-testid="supra-tabs">
          {TABS.map(tab => {
            const active = activeTab === tab.id;
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                data-testid={`supra-tab-${tab.id}`}
                onClick={() => setActiveTab(tab.id)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px] font-bold transition-all"
                style={{
                  backgroundColor: active ? `${gc}20` : 'transparent',
                  color: active ? gc : '#9ca3af',
                  border: active ? `1px solid ${gc}40` : '1px solid transparent',
                }}
              >
                <Icon className="h-3.5 w-3.5" />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* CONTENT */}
        <div className="flex-1 overflow-y-auto p-3" style={{ maxHeight: 'calc(100vh - 120px)' }}>
          {loading && <div className="text-center py-8 text-gray-500 text-sm animate-pulse">Analyse SUPRA en cours...</div>}

          {!loading && score && activeTab === 'analyse' && (
            <AnalyseTab score={score} recipe={recipe} recommendations={recommendations} evidence={evidence} costs={costs} comparison={comparison} ecozone={ecozone} gc={gc} np={np} />
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

        {/* FOOTER */}
        <div className="text-center text-[9px] text-gray-600 py-1 border-t flex-shrink-0" style={{ borderColor: 'rgba(255,255,255,0.04)' }} data-testid="supra-footer">
          x5000 SUPRA | x6000 PRODUCT_SCORE | BCE-4X / STEEVE-MAX V6
        </div>
      </div>
    </PinnablePanel>
  );
};

/* ============================================================ */
/* TAB: ANALYSE                                                 */
/* ============================================================ */
const AnalyseTab = ({ score, recipe, recommendations, evidence, costs, comparison, ecozone, gc, np }) => (
  <div className="grid grid-cols-2 gap-2.5" data-testid="supra-analyse-tab">
    {/* COL GAUCHE */}
    <div className="flex flex-col gap-2.5">
      {/* Score global */}
      <Card testId="supra-score-card">
        <div className="flex items-center gap-3">
          <div className="w-14 h-14 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: `linear-gradient(135deg, ${gc}22, ${gc}08)`, border: `2.5px solid ${gc}` }}>
            <span className="text-2xl font-black" style={{ color: gc }}>{score.score_global}</span>
          </div>
          <div>
            <div className="text-sm font-black text-white">Score Mineral</div>
            <div className="text-[10px] font-bold px-2 py-0.5 rounded-lg inline-block mt-0.5" style={{ backgroundColor: `${gc}18`, color: gc }}>{score.grade}</div>
            <div className="flex gap-2 mt-1 text-[10px]">
              <span style={{ color: BIONIC.green }}>{score.zones_resume.vert} vert</span>
              <span style={{ color: BIONIC.orange }}>{score.zones_resume.jaune} jaune</span>
              <span style={{ color: BIONIC.red }}>{score.zones_resume.rouge} rouge</span>
            </div>
          </div>
        </div>
      </Card>

      {/* Mineraux — barres */}
      <Card testId="supra-minerals-card" className="flex-1">
        <div className="flex items-center gap-1.5 mb-2">
          <FlaskConical className="h-3 w-3" style={{ color: BIONIC.yellow }} />
          <span className="text-[11px] font-bold text-white">Mineraux</span>
        </div>
        <div className="space-y-1">
          {Object.entries(score.scores_par_mineral).map(([key, m]) => (
            <div key={key} className="flex items-center gap-1.5" data-testid={`supra-mineral-${key}`}>
              <span className="text-[9px] text-gray-300 w-16 flex-shrink-0">{m.name}</span>
              <div className="flex-1 h-[4px] rounded-full overflow-hidden" style={{ backgroundColor: 'rgba(255,255,255,0.04)' }}>
                <div className="h-full rounded-full" style={{ width: `${m.score}%`, backgroundColor: zoneColor(m.zone) }} />
              </div>
              <span className="text-[10px] font-bold w-7 text-right" style={{ color: zoneColor(m.zone) }}>{m.score}</span>
            </div>
          ))}
        </div>
      </Card>

      {/* Ecozone */}
      {ecozone && (
        <Card testId="supra-ecozone-card">
          <div className="flex items-center gap-1.5 mb-1.5">
            <Leaf className="h-3 w-3" style={{ color: BIONIC.green }} />
            <span className="text-[11px] font-bold text-white">Zone ecologique</span>
          </div>
          <div className="text-[10px] text-gray-400 mb-1.5">{ecozone.nom_commun}</div>
          <div className="text-[9px] text-gray-500 leading-relaxed">{ecozone.habitat_principal}</div>
          {ecozone.comportement_saisonnier?.[recipe?.season] && (
            <div className="mt-1.5 rounded-lg p-1.5" style={{ backgroundColor: `${BIONIC.green}08`, borderLeft: `2px solid ${BIONIC.green}` }}>
              <span className="text-[9px] text-gray-400">{ecozone.comportement_saisonnier[recipe.season]}</span>
            </div>
          )}
        </Card>
      )}
    </div>

    {/* COL DROITE */}
    <div className="flex flex-col gap-2.5">
      {/* Recette */}
      {recipe && (
        <Card testId="supra-recipe-card">
          <div className="flex items-center gap-1.5 mb-1.5">
            <BookOpen className="h-3 w-3" style={{ color: BIONIC.green }} />
            <span className="text-[11px] font-bold text-white">Recette</span>
            <span className="text-[9px] text-gray-500 ml-auto">{recipe.title}</span>
          </div>
          <div className="space-y-1">
            {recipe.ingredients_cles?.slice(0, 5).map((ing, i) => (
              <div key={i} className="flex items-center justify-between py-0.5 border-b" style={{ borderColor: 'rgba(255,255,255,0.03)' }}>
                <div>
                  <span className="text-[10px] text-white">{ing.mineral}</span>
                  <span className="text-[8px] text-gray-500 ml-1">{ing.product}</span>
                </div>
                <span className="text-[9px] font-bold px-1.5 py-0.5 rounded" style={{ backgroundColor: `${priorityColor(ing.priority)}12`, color: priorityColor(ing.priority) }}>{ing.priority}</span>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Couts */}
      {costs && (
        <Card testId="supra-costs-card">
          <div className="flex items-center gap-1.5 mb-1.5">
            <DollarSign className="h-3 w-3" style={{ color: BIONIC.orange }} />
            <span className="text-[11px] font-bold text-white">Couts</span>
          </div>
          <div className="grid grid-cols-3 gap-1.5 text-center">
            <div className="rounded-lg p-1.5" style={{ backgroundColor: 'rgba(255,255,255,0.03)' }}>
              <div className="text-[8px] text-gray-500">Initial</div>
              <div className="text-sm font-bold text-white">{costs.initial_cost_cad}$</div>
            </div>
            <div className="rounded-lg p-1.5" style={{ backgroundColor: 'rgba(255,255,255,0.03)' }}>
              <div className="text-[8px] text-gray-500">Annuel</div>
              <div className="text-sm font-bold" style={{ color: BIONIC.orange }}>{costs.annual_cost_cad}$</div>
            </div>
            <div className="rounded-lg p-1.5" style={{ backgroundColor: 'rgba(255,255,255,0.03)' }}>
              <div className="text-[8px] text-gray-500">Par visite</div>
              <div className="text-sm font-bold text-white">{costs.cost_per_visit_cad}$</div>
            </div>
          </div>
        </Card>
      )}

      {/* Preuves */}
      {evidence.length > 0 ? (
        <Card testId="supra-evidence-card" className="flex-1">
          <div className="flex items-center gap-1.5 mb-1.5">
            <FileText className="h-3 w-3" style={{ color: BIONIC.purple }} />
            <span className="text-[11px] font-bold text-white">Preuves scientifiques</span>
            <span className="text-[9px] text-gray-500 ml-auto">{evidence.length} refs</span>
          </div>
          <div className="space-y-1">
            {evidence.slice(0, 4).map((ref, i) => (
              <div key={i} className="rounded-lg p-1.5" style={{ backgroundColor: 'rgba(156,39,176,0.05)', borderLeft: `2px solid ${BIONIC.purple}` }} data-testid={`supra-evidence-${i}`}>
                <div className="flex items-start justify-between gap-1">
                  <span className="text-[9px] font-bold text-white leading-tight">{ref.titre}</span>
                  <a href={ref.doi_ou_url} target="_blank" rel="noopener noreferrer" className="flex-shrink-0"><ExternalLink className="h-2.5 w-2.5 text-purple-400" /></a>
                </div>
                <span className="text-[8px] text-gray-500">{ref.auteurs}, {ref.annee}</span>
                <div className="flex items-center gap-1 mt-0.5">
                  <span className="text-[7px] px-1 py-0.5 rounded" style={{ backgroundColor: `${BIONIC.purple}12`, color: BIONIC.purple }}>{ref.type_source?.replace(/_/g, ' ')}</span>
                  <span className="text-[7px] text-gray-600">{ref.organisme}</span>
                  {ref.niveau_preuve && <span className="text-[7px] font-bold px-1 py-0.5 rounded" style={{ backgroundColor: ref.niveau_preuve === 'A' ? `${BIONIC.green}12` : `${BIONIC.orange}12`, color: ref.niveau_preuve === 'A' ? BIONIC.green : BIONIC.orange }}>Niv.{ref.niveau_preuve}</span>}
                </div>
              </div>
            ))}
          </div>
        </Card>
      ) : (
        <Card testId="supra-evidence-card" className="flex-1">
          <div className="flex items-center gap-1.5 mb-1.5">
            <FileText className="h-3 w-3" style={{ color: BIONIC.purple }} />
            <span className="text-[11px] font-bold text-white">Preuves scientifiques</span>
          </div>
          <div className="rounded-lg p-2 text-center" style={{ backgroundColor: 'rgba(255,255,255,0.02)' }}>
            <AlertTriangle className="h-4 w-4 text-gray-600 mx-auto mb-1" />
            <span className="text-[10px] text-gray-500">Aucune preuve scientifique formelle disponible pour ce cas.</span>
          </div>
        </Card>
      )}
    </div>
  </div>
);

/* ============================================================ */
/* TAB: INTELLIGENCE                                            */
/* ============================================================ */
const IntelligenceTab = ({ products, gc, compareIds, toggleCompare }) => (
  <div className="space-y-2.5" data-testid="supra-intelligence-tab">
    <div className="text-[11px] text-gray-400 mb-2">Score d'adequation par produit — {products.total} produits analyses</div>
    <div className="space-y-1.5">
      {products.products?.map((p, i) => {
        const sc = p.score_global >= 85 ? BIONIC.green : p.score_global >= 70 ? BIONIC.yellow : p.score_global >= 50 ? BIONIC.orange : BIONIC.red;
        const isCompared = compareIds.includes(p.product_id);
        return (
          <Card key={p.product_id} testId={`product-${p.product_id}`}>
            <div className="flex items-center gap-2.5">
              <div className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: `linear-gradient(135deg, ${sc}22, ${sc}08)`, border: `2px solid ${sc}` }}>
                <span className="text-sm font-black" style={{ color: sc }}>{p.score_global}</span>
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-[11px] font-bold text-white truncate">{p.name}</div>
                <div className="text-[9px] text-gray-500">{p.type} | {p.price_cad}$ | {p.weight_kg}kg | {p.duration_weeks} sem</div>
                <div className="flex gap-1 mt-0.5 flex-wrap">
                  {p.optimal_for?.map((tag, j) => (
                    <span key={j} className="text-[8px] px-1.5 py-0.5 rounded" style={{ backgroundColor: `${BIONIC.green}12`, color: BIONIC.green }}>{tag}</span>
                  ))}
                  {p.tags?.slice(0, 2).map((tag, j) => (
                    <span key={`t${j}`} className="text-[8px] px-1.5 py-0.5 rounded" style={{ backgroundColor: 'rgba(255,255,255,0.04)', color: '#9ca3af' }}>{tag}</span>
                  ))}
                </div>
              </div>
              <div className="flex flex-col gap-1 flex-shrink-0">
                <div className="grid grid-cols-3 gap-1 text-center">
                  <div><div className="text-[7px] text-gray-500">Espece</div><div className="text-[10px] font-bold" style={{ color: p.score_species >= 85 ? BIONIC.green : BIONIC.orange }}>{p.score_species}%</div></div>
                  <div><div className="text-[7px] text-gray-500">Saison</div><div className="text-[10px] font-bold" style={{ color: p.score_season >= 85 ? BIONIC.green : BIONIC.orange }}>{p.score_season}%</div></div>
                  <div><div className="text-[7px] text-gray-500">Sol</div><div className="text-[10px] font-bold" style={{ color: p.score_soil >= 85 ? BIONIC.green : BIONIC.orange }}>{p.score_soil}%</div></div>
                </div>
                <button
                  onClick={() => toggleCompare(p.product_id)}
                  className="text-[9px] font-bold px-2 py-1 rounded-lg"
                  style={{
                    backgroundColor: isCompared ? `${BIONIC.blue}20` : 'rgba(255,255,255,0.04)',
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
/* TAB: COMPAREZ                                                */
/* ============================================================ */
const ComparezTab = ({ products, compareIds, gc, toggleCompare }) => {
  const compared = (products.products || []).filter(p => compareIds.includes(p.product_id));
  if (compared.length === 0) {
    return (
      <div className="text-center py-8" data-testid="supra-comparez-tab">
        <Scale className="h-8 w-8 text-gray-600 mx-auto mb-3" />
        <div className="text-sm text-gray-400">Aucun produit selectionne</div>
        <div className="text-[10px] text-gray-600 mt-1">Allez dans l'onglet INTELLIGENCE et selectionnez 2-4 produits a comparer</div>
      </div>
    );
  }

  const best = compared.reduce((a, b) => a.score_global > b.score_global ? a : b);
  return (
    <div data-testid="supra-comparez-tab">
      <div className="text-[11px] text-gray-400 mb-2">{compared.length} produit(s) compares — max 4</div>
      <div className="grid gap-2.5" style={{ gridTemplateColumns: `repeat(${Math.min(compared.length, 4)}, 1fr)` }}>
        {compared.map(p => {
          const isBest = p.product_id === best.product_id;
          const sc = p.score_global >= 85 ? BIONIC.green : p.score_global >= 70 ? BIONIC.yellow : p.score_global >= 50 ? BIONIC.orange : BIONIC.red;
          return (
            <Card key={p.product_id} testId={`compare-card-${p.product_id}`} className={isBest ? 'ring-1 ring-green-500/30' : ''}>
              {isBest && <div className="text-[8px] font-bold text-center mb-1" style={{ color: BIONIC.green }}>MEILLEUR CHOIX</div>}
              <div className="text-center mb-2">
                <div className="w-12 h-12 rounded-xl flex items-center justify-center mx-auto" style={{ background: `linear-gradient(135deg, ${sc}22, ${sc}08)`, border: `2px solid ${sc}` }}>
                  <span className="text-lg font-black" style={{ color: sc }}>{p.score_global}</span>
                </div>
                <div className="text-[10px] font-bold text-white mt-1">{p.name}</div>
                <div className="text-[8px] text-gray-500">{p.type}</div>
              </div>
              <div className="space-y-1">
                {[
                  { label: 'Espece', val: `${p.score_species}%`, color: p.score_species >= 85 ? BIONIC.green : BIONIC.orange },
                  { label: 'Saison', val: `${p.score_season}%`, color: p.score_season >= 85 ? BIONIC.green : BIONIC.orange },
                  { label: 'Sol', val: `${p.score_soil}%`, color: p.score_soil >= 85 ? BIONIC.green : BIONIC.orange },
                  { label: 'Prix', val: `${p.price_cad}$`, color: '#fff' },
                  { label: 'Duree', val: `${p.duration_weeks} sem`, color: '#fff' },
                ].map((row, i) => (
                  <div key={i} className="flex justify-between py-0.5 border-b" style={{ borderColor: 'rgba(255,255,255,0.03)' }}>
                    <span className="text-[9px] text-gray-500">{row.label}</span>
                    <span className="text-[9px] font-bold" style={{ color: row.color }}>{row.val}</span>
                  </div>
                ))}
              </div>
              <div className="flex gap-1 mt-1.5 flex-wrap">
                {p.minerals?.map((m, j) => (
                  <span key={j} className="text-[7px] px-1 py-0.5 rounded" style={{ backgroundColor: `${BIONIC.yellow}12`, color: BIONIC.yellow }}>{m}</span>
                ))}
              </div>
              <button
                onClick={() => toggleCompare(p.product_id)}
                className="w-full mt-2 text-[9px] font-bold py-1 rounded-lg"
                style={{ backgroundColor: `${BIONIC.red}12`, color: BIONIC.red }}
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
/* TAB: COMMANDEZ                                               */
/* ============================================================ */
const CommandezTab = ({ order, products, recipe, gc }) => (
  <div className="space-y-2.5" data-testid="supra-commandez-tab">
    {/* Pack complet */}
    <Card testId="order-pack-card">
      <div className="flex items-center gap-2 mb-2">
        <Package className="h-3.5 w-3.5" style={{ color: BIONIC.green }} />
        <span className="text-[11px] font-bold text-white">Commander la recette complete</span>
        <span className="text-[10px] font-bold ml-auto" style={{ color: BIONIC.green }}>{order.summary.cost_initial_cad}$</span>
      </div>
      <div className="space-y-1">
        {order.items?.map((item, i) => (
          <div key={i} className="flex items-center justify-between py-1 border-b" style={{ borderColor: 'rgba(255,255,255,0.03)' }}>
            <div className="flex-1">
              <div className="text-[10px] text-white">{item.name} — <span className="text-gray-500">{item.brand}</span></div>
              <div className="text-[8px] text-gray-600">{item.dosage} | Qte: {item.quantity}</div>
            </div>
            <div className="text-right flex-shrink-0">
              <div className="text-[10px] font-bold text-white">{item.total_price_cad}$</div>
              <span className="text-[8px] font-bold px-1.5 py-0.5 rounded" style={{ backgroundColor: `${priorityColor(item.priority)}12`, color: priorityColor(item.priority) }}>{item.priority}</span>
            </div>
          </div>
        ))}
      </div>
      <div className="flex items-center justify-between mt-2 pt-2 border-t" style={{ borderColor: 'rgba(255,255,255,0.06)' }}>
        <div className="text-[9px] text-gray-500">
          Reactivation: {order.summary.reactivation_frequency_weeks} sem | Annuel: {order.summary.cost_annual_cad}$ | Par visite: {order.summary.cost_per_visit_cad}$
        </div>
        <button
          className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-[10px] font-bold"
          style={{ backgroundColor: `${BIONIC.green}20`, color: BIONIC.green, border: `1px solid ${BIONIC.green}40` }}
          data-testid="order-complete-btn"
        >
          <ShoppingCart className="h-3 w-3" /> Commander tout
        </button>
      </div>
    </Card>

    {/* Produits individuels */}
    <div className="text-[11px] text-gray-400 mb-1">Commander individuellement</div>
    <div className="space-y-1.5">
      {products?.products?.slice(0, 6).map(p => {
        const sc = p.score_global >= 85 ? BIONIC.green : p.score_global >= 70 ? BIONIC.yellow : p.score_global >= 50 ? BIONIC.orange : BIONIC.red;
        return (
          <Card key={p.product_id} testId={`shop-product-${p.product_id}`}>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: `${sc}15`, border: `1.5px solid ${sc}` }}>
                <span className="text-[10px] font-black" style={{ color: sc }}>{p.score_global}</span>
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-[10px] font-bold text-white truncate">{p.name}</div>
                <div className="flex gap-1 mt-0.5 flex-wrap">
                  {p.optimal_for?.map((tag, j) => (
                    <span key={j} className="text-[7px] px-1 py-0.5 rounded" style={{ backgroundColor: `${BIONIC.green}10`, color: BIONIC.green }}>Optimal: {tag}</span>
                  ))}
                </div>
              </div>
              <div className="flex items-center gap-2 flex-shrink-0">
                <span className="text-[10px] font-bold text-white">{p.price_cad}$</span>
                <button
                  className="flex items-center gap-1 px-2 py-1 rounded-lg text-[9px] font-bold"
                  style={{ backgroundColor: `${BIONIC.blue}15`, color: BIONIC.blue, border: `1px solid ${BIONIC.blue}30` }}
                  data-testid={`shop-order-${p.product_id}`}
                >
                  <ShoppingCart className="h-2.5 w-2.5" /> CMD
                </button>
              </div>
            </div>
          </Card>
        );
      })}
    </div>
  </div>
);

export default NutritionPointDetailPanel;

import React, { useState, useEffect, useCallback } from 'react';
import {
  Droplets, FlaskConical, Leaf, MapPin, AlertTriangle, Layers, Beaker,
  ShoppingCart, DollarSign, BookOpen, FileText, ExternalLink, Zap, Package,
  Construction, Scale, BarChart3, ArrowRight, ChevronDown, ChevronUp,
  Mountain, Activity, Thermometer, Wind, Plus, Minus, X, Loader2,
  TreeDeciduous, Gem, Crown, Eye, Crosshair, Share2, Shield, ClipboardList, Info
} from 'lucide-react';
import axios from 'axios';
import PinnablePanel from './PinnablePanel';
import { ShareBionicButton } from './ui/ShareBionicButton';
import { CriteriaDetailModal } from './ui/CriteriaDetailModal';
import PedagogieModule from './PedagogieModule';

/**
 * SUPRA v2 — Moteur Unifie
 * ========================
 * Fusion SUPRA LOCAL + NUTRITION INTELLIGENCE ULTRA + SUPRA PREMIUM
 * 
 * Onglets:
 * 1. ANALYSE — Score + Gauge + 7 moteurs ULTRA + Mineraux + Narration PREMIUM
 * 2. INTELLIGENCE — Score adequation produits + match_score ULTRA
 * 3. COMPAREZ — Comparaison cote-a-cote 2-4 produits
 * 4. COMMANDEZ — Panier Stripe reel + Checkout
 *
 * BCE-4X / STEEVE-MAX V6 — PHASE P0 FUSION TOTALE
 */

const API = process.env.REACT_APP_BACKEND_URL;

const SUPRA_CMD_COLOR = '#FF9800';

const BIONIC = {
  green: '#00C853', yellow: '#F9D423', orange: '#FF9800', red: '#D32F2F',
  blue: '#2196F3', purple: '#9C27B0', card: '#111122', cardBorder: 'rgba(255,255,255,0.06)',
  supraCmd: SUPRA_CMD_COLOR, amber: '#FFB300', cyan: '#00BCD4', teal: '#009688',
};

function gradeColor(grade) {
  if (grade === 'EXCELLENT') return BIONIC.green;
  if (grade === 'BON') return BIONIC.yellow;
  if (grade === 'MODERE') return BIONIC.orange;
  return BIONIC.red;
}
function zoneColor(z) { return z === 'vert' ? BIONIC.green : z === 'jaune' ? BIONIC.orange : BIONIC.red; }
function priorityColor(p) { return p === 'CRITIQUE' ? BIONIC.red : p === 'RECOMMANDE' ? BIONIC.orange : BIONIC.green; }

// === SESSION SALINE (Panier Stripe unifie) ===
const getSalineSession = () => {
  let sid = localStorage.getItem('saline_session_id');
  if (!sid) {
    sid = 'sal_' + Math.random().toString(36).substr(2, 12);
    localStorage.setItem('saline_session_id', sid);
  }
  return sid;
};

// === GAUGE MINI — Dashboard-style compact (BCE-4X GOLDEN) ===
const GaugeMini = ({ value, max = 100, label, color = BIONIC.orange }) => {
  const radius = 36;
  const circumference = 2 * Math.PI * radius;
  const pct = Math.min(value / max, 1);
  const offset = circumference * (1 - pct * 0.75);
  return (
    <div className="relative flex flex-col items-center" data-testid="supra-gauge">
      <svg viewBox="0 0 84 84" className="w-[64px] h-[64px]">
        <circle cx="42" cy="42" r={radius} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="6"
          strokeDasharray={`${circumference * 0.75} ${circumference * 0.25}`} strokeLinecap="round"
          transform="rotate(135 42 42)" />
        <circle cx="42" cy="42" r={radius} fill="none" stroke={color} strokeWidth="6"
          strokeDasharray={`${circumference * 0.75} ${circumference * 0.25}`} strokeDashoffset={offset}
          strokeLinecap="round" transform="rotate(135 42 42)" style={{ transition: 'stroke-dashoffset 0.8s ease' }} />
        <text x="42" y="40" textAnchor="middle" fill={color} fontSize="18" fontWeight="900" fontFamily="system-ui">{Math.round(value)}</text>
        <text x="42" y="54" textAnchor="middle" fill="#6b7280" fontSize="8" fontWeight="600" fontFamily="system-ui">{label}</text>
      </svg>
    </div>
  );
};

// === MICRO CARD — SUPPRIME, remplace par layout vertical inline ===

// === NARRATION DATA (from SUPRA PREMIUM) ===
const PHYSIOLOGY_DATA = {
  chevreuil: {
    printemps: "Sortie d'hiver. Les reserves minerales sont au plus bas. Le sodium est le premier mineral recherche activement. Le calcium et le phosphore sont critiques pour la regeneration du panache.",
    ete: "Phase de croissance maximale du panache. Besoins en calcium et phosphore x3. Le magnesium soutient la fixation. L'appetit mineral est a son pic.",
    pre_rut: "Transition hormonale. Le testosterone monte. Les mineraux de structure (Ca, P) sont fixes. Le sodium maintient l'hydratation sous effort territorial.",
    rut: "Activite maximale. Perte de poids de 20-30%. Le sodium compense la deshydratation. Le potassium soutient la fonction musculaire.",
    post_rut: "Recuperation energetique. Les besoins en mineraux de structure baissent. L'appetit mineral reprend progressivement.",
    hiver: "Phase de survie. Metabolisme ralenti. Les besoins sont minimaux mais le sodium reste recherche.",
  },
  orignal: {
    printemps: "Sortie d'hivernage. Deficience severe en sodium apres 5 mois de regime ligneux. Les femelles gestantes ont des besoins en calcium x4.",
    ete: "Panache en velours. Croissance rapide necessitant calcium, phosphore et magnesium. L'orignal consomme activement les plantes aquatiques riches en sodium.",
    rut: "Activite territoriale intense. Pertes hydriques majeures. Le sodium est vital pour maintenir la pression osmotique.",
    hiver: "Metabolisme hivernal. Besoins reduits. Alimentation a base de ramilles.",
  },
};

const MALE_BEHAVIOR = {
  chevreuil: {
    printemps: "Les males visitent les salines 2-4 fois/semaine. Visites matinales (5h-8h) et crepusculaires (18h-21h). Duree moyenne: 8-15 min.",
    ete: "Frequence maximale: 4-7 visites/semaine. Duree prolongee (15-25 min). Marquage territorial frequent autour du site.",
    pre_rut: "Visites irregulieres. Les males commencent a patrouiller. Les frottoirs apparaissent dans un rayon de 200m des salines actives.",
    rut: "Visites rares (1-2/semaine). Durees courtes (<5 min). Les males suivent les femelles qui elles, continuent de visiter.",
    post_rut: "Reprise progressive. 2-3 visites/semaine. Comportement moins territorial.",
    hiver: "Visites sporadiques selon meteo. 1-2/semaine max.",
  },
};

const SUPPORT_HIERARCHY = [
  { name: 'Bois mou (epinette, sapin)', score: 95, color: BIONIC.green, desc: 'Absorption maximale, retention longue, cout reduit.' },
  { name: 'Bois dur (erable, bouleau)', score: 70, color: BIONIC.yellow, desc: 'Absorption moderee, dissolution plus rapide.' },
  { name: 'Sol nu / terre', score: 45, color: BIONIC.orange, desc: 'Dispersion rapide, contamination possible.' },
  { name: 'Bloc mineral commercial', score: 60, color: BIONIC.yellow, desc: 'Pratique mais dissolution non controlee.' },
];

// ============================================================================
// STANDARD GOLDEN — COMPOSANTS UI BCE-4X STEEVE-MAX
// Norme: ZERO bordure visible | Accent bar gauche | Icones en cercles
// Hierarchie: Valeurs 30-40px | Labels 14px | Corps 16px
// Coins: rounded-xl (12-16px) | Contraste: fond #0F172A / carte #1E293B
// Box-shadow: leger GOLDEN | Structure: 100% VERTICALE
// ============================================================================

const GOLDEN = {
  cardBg: '#1E293B',
  pageBg: '#0F172A',
  shadow: '0 2px 8px rgba(0,0,0,0.25)',
};

const GoldenCard = ({ children, testId, accentColor, className = '', compact = false }) => (
  <div className={`rounded-lg ${compact ? 'px-2.5 py-2' : 'px-4 py-3'} ${className}`}
    style={{
      backgroundColor: GOLDEN.cardBg,
      boxShadow: GOLDEN.shadow,
      borderLeft: accentColor ? `3px solid ${accentColor}` : 'none',
    }}
    data-testid={testId}>
    {children}
  </div>
);

const GoldenCollapsible = ({ icon: Icon, title, color, badge, children, defaultOpen = true, testId }) => {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="rounded-lg px-4 py-2.5" style={{ backgroundColor: GOLDEN.cardBg, boxShadow: GOLDEN.shadow }} data-testid={testId}>
      <button onClick={() => setOpen(v => !v)} className="w-full flex items-center justify-between cursor-pointer">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full flex items-center justify-center" style={{ backgroundColor: `${color}20` }}>
            <Icon className="h-4 w-4" style={{ color }} />
          </div>
          <span className="text-[16px] font-bold text-white">{title}</span>
        </div>
        <div className="flex items-center gap-2">
          {badge && <span className="text-[14px] font-semibold px-2.5 py-0.5 rounded-lg" style={{ backgroundColor: `${color}18`, color }}>{badge}</span>}
          {open ? <ChevronUp className="h-4 w-4 text-slate-500" /> : <ChevronDown className="h-4 w-4 text-slate-500" />}
        </div>
      </button>
      {open && <div className="mt-3">{children}</div>}
    </div>
  );
};

// Backward compat aliases
const Card = GoldenCard;
const CollapsibleSection = GoldenCollapsible;

const SupraButton = ({ children, onClick, size = 'md', disabled = false, testId }) => {
  const sizeClasses = { sm: 'h-8 px-3 text-xs gap-1.5', md: 'h-9 px-5 text-sm gap-2', lg: 'h-10 px-6 text-sm gap-2' };
  return (
    <button onClick={onClick} disabled={disabled}
      className={`flex items-center justify-center rounded-lg font-bold uppercase tracking-wider transition-all duration-150 ${sizeClasses[size]} ${disabled ? 'opacity-40 cursor-not-allowed' : 'hover:brightness-125 active:scale-[0.97]'}`}
      style={{ backgroundColor: disabled ? '#37415115' : `${SUPRA_CMD_COLOR}18`, color: disabled ? '#6b7280' : SUPRA_CMD_COLOR, border: `2px solid ${disabled ? '#37415130' : `${SUPRA_CMD_COLOR}50`}` }}
      data-testid={testId} data-bce4x-locked="true">
      {children}
    </button>
  );
};

const TABS = [
  { id: 'analyse', label: 'Analyse', icon: FlaskConical },
  { id: 'fiche', label: 'Fiche', icon: ClipboardList },
  { id: 'intelligence', label: 'Intelligence', icon: BarChart3 },
  { id: 'comparez', label: 'Comparez', icon: Scale },
  { id: 'commandez', label: 'Commandez', icon: ShoppingCart },
];

// ============================================================
// MAIN COMPONENT — SUPRA v2 MOTEUR UNIFIE
// ============================================================
const NutritionPointDetailPanel = ({ nutritionPoint, onClose, selectedSpecies }) => {
  const [activeTab, setActiveTab] = useState('analyse');
  const [supraData, setSupraData] = useState(null);
  const [ultraData, setUltraData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [compareIds, setCompareIds] = useState([]);
  // Cart state (Stripe unifie)
  const [cart, setCart] = useState({ items: [], item_count: 0, total: 0 });
  const [cartLoading, setCartLoading] = useState(false);
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  // FICHE SALINE ULTIME state
  const [ficheData, setFicheData] = useState(null);
  // SOIL ENGINE state
  const [soilData, setSoilData] = useState(null);

  const np = nutritionPoint;
  // PRIORITE: selectedSpecies (choix utilisateur) > np.species > fallback orignal
  const species = (selectedSpecies || np?.species || 'orignal').toLowerCase();
  const season = np?.season || 'printemps';
  const soilType = np?.soil_type || 'mixte';
  const lat = np?.lat || np?.position?.[0] || 47.3;
  const lng = np?.lng || np?.position?.[1] || -71.2;
  const seasonMap = { 1:'hiver',2:'hiver',3:'printemps',4:'printemps',5:'ete',6:'ete',7:'ete',8:'pre_rut',9:'pre_rut',10:'rut',11:'post_rut',12:'hiver' };
  const month = new Date().getMonth() + 1;

  // Fetch SUPRA + ULTRA data in parallel
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const fetchAll = useCallback(async () => {
    if (!np) return;
    setLoading(true);
    try {
      const [supraRes, ultraRes, ficheRes, soilRes] = await Promise.allSettled([
        axios.post(`${API}/api/v6/nutrition-intelligence/supra-panel`, {
          species, season, soil_type: soilType, substrate: 'bois_mou',
          lat: parseFloat(lat), lng: parseFloat(lng),
          saline_score: np?.score || null,
        }),
        axios.post(`${API}/api/v1/saline/analyze`, {
          lat: parseFloat(lat), lng: parseFloat(lng), species, sex: 'male', age: 'adult',
          month, season: seasonMap[month] || season,
        }),
        axios.get(`${API}/api/v1/salines-ultime/fiche?lat=${parseFloat(lat)}&lng=${parseFloat(lng)}&species=${species}&season=${seasonMap[month] || season}`),
        axios.get(`${API}/api/v1/soil/analyze?lat=${parseFloat(lat)}&lng=${parseFloat(lng)}&species=${species}&season=${seasonMap[month] || season}`),
      ]);
      if (supraRes.status === 'fulfilled') setSupraData(supraRes.value.data);
      if (ultraRes.status === 'fulfilled') setUltraData(ultraRes.value.data);
      if (ficheRes.status === 'fulfilled') setFicheData(ficheRes.value.data);
      if (soilRes.status === 'fulfilled') setSoilData(soilRes.value.data);
    } catch (e) {
      console.error('[SUPRA v2]', e);
    } finally {
      setLoading(false);
    }
  }, [np, species, season, soilType, lat, lng, month]);

  // Fetch cart on mount
  const fetchCart = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/api/v1/saline/shop/cart/${getSalineSession()}`);
      setCart(res.data);
    } catch (e) { /* cart vide */ }
  }, []);

  const addToCart = useCallback(async (productId) => {
    setCartLoading(true);
    try {
      await axios.post(`${API}/api/v1/saline/shop/cart/add`, {
        session_id: getSalineSession(), product_id: productId, quantity: 1,
      });
      await fetchCart();
    } catch (e) { console.error('[CART]', e); }
    finally { setCartLoading(false); }
  }, [fetchCart]);

  const handleCheckout = useCallback(async () => {
    setCheckoutLoading(true);
    try {
      const res = await axios.post(`${API}/api/v1/saline/shop/checkout`, {
        session_id: getSalineSession(), user_id: 'guest', origin_url: window.location.origin,
      });
      if (res.data.url) window.location.href = res.data.url;
    } catch (e) { console.error('[CHECKOUT]', e); }
    finally { setCheckoutLoading(false); }
  }, []);

  useEffect(() => { fetchAll(); }, [fetchAll]);
  useEffect(() => { fetchCart(); }, [fetchCart]);

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

  // ULTRA 7 engines data
  const engines = ultraData?.engines || {};
  const ultraScore = ultraData?.analysis?.intelligence_score || {};
  const ultraDeficits = ultraData?.analysis?.adjusted_deficits || {};

  const toggleCompare = (pid) => {
    setCompareIds(prev => prev.includes(pid) ? prev.filter(x => x !== pid) : prev.length < 4 ? [...prev, pid] : prev);
  };

  const cartCount = cart.item_count || 0;

  return (
    <PinnablePanel
      title={`SUPRA v2 — ${np.id}`}
      subtitle={`${species} | ${season} | ${soilType} | ${np.distance_centre_m}m`}
      icon={Droplets}
      accentColor={gc}
      onClose={onClose}
      defaultWidth={680}
      maxHeight="100vh"
      testId="nutrition-point-detail-panel"
      fullHeight={true}
    >
      <div className="h-full flex flex-col overflow-hidden" data-testid="supra-v2-panel-content">
        {/* TABS — 100% VERTICAL GOLDEN | TYPO 16px */}
        <div className="flex items-center gap-2 px-4 pt-3 pb-2 border-b flex-shrink-0" style={{ borderColor: 'rgb(51 65 85)' }} data-testid="supra-tabs">
          {TABS.map(tab => {
            const active = activeTab === tab.id;
            const Icon = tab.icon;
            const isOrder = tab.id === 'commandez';
            const activeColor = isOrder ? SUPRA_CMD_COLOR : gc;
            return (
              <button key={tab.id} data-testid={`supra-tab-${tab.id}`}
                onClick={() => setActiveTab(tab.id)}
                className="flex items-center gap-1.5 h-9 px-3 rounded-lg text-[14px] font-bold uppercase tracking-wider transition-all duration-150 relative"
                style={{ backgroundColor: active ? `${activeColor}18` : 'transparent', color: active ? activeColor : '#6b7280', border: active ? `2px solid ${activeColor}50` : '2px solid transparent' }}>
                <Icon className="h-4 w-4" />
                {tab.label}
                {isOrder && cartCount > 0 && (
                  <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full text-[10px] font-black flex items-center justify-center" style={{ backgroundColor: SUPRA_CMD_COLOR, color: '#000' }}>{cartCount}</span>
                )}
              </button>
            );
          })}
          <div className="ml-auto flex-shrink-0">
            <ShareBionicButton />
          </div>
        </div>

        {/* CONTENT — 100% VERTICAL GOLDEN | Scroll GOLDEN */}
        <div className="flex-1 px-4 py-3 overflow-y-auto" style={{ scrollBehavior: 'smooth' }} data-testid="supra-v2-content-area">
          {loading && <div className="text-center py-12 text-slate-400 text-base animate-pulse" data-testid="supra-loading">Analyse SUPRA v2 en cours...</div>}

          {!loading && !score && (
            <div className="text-center py-12 space-y-3" data-testid="supra-no-data">
              <AlertTriangle className="h-8 w-8 text-amber-400 mx-auto" />
              <div className="text-slate-300 text-base font-semibold">Donnees SUPRA non disponibles</div>
              <div className="text-slate-500 text-sm">L&apos;analyse n&apos;a pas pu etre chargee. Verifiez la connexion et reessayez.</div>
              <button onClick={fetchAll} className="mt-3 px-5 py-2.5 rounded-lg text-sm font-bold uppercase tracking-wider transition-all"
                style={{ backgroundColor: `${BIONIC.orange}18`, color: BIONIC.orange, border: `2px solid ${BIONIC.orange}40` }}
                data-testid="supra-retry-btn">
                Reessayer
              </button>
            </div>
          )}

          {!loading && score && activeTab === 'analyse' && (
            <AnalyseTab score={score} recipe={recipe} recommendations={recommendations} evidence={evidence}
              costs={costs} comparison={comparison} ecozone={ecozone} energyProtein={energyProtein}
              terrainSolutions={terrainSolutions} gc={gc} np={np} engines={engines}
              ultraScore={ultraScore} ultraDeficits={ultraDeficits} species={species} season={season} soilData={soilData} />
          )}
          {!loading && activeTab === 'fiche' && (
            <FicheTab ficheData={ficheData} species={species} season={season} lat={lat} lng={lng} np={np} soilData={soilData} />
          )}
          {!loading && products && activeTab === 'intelligence' && (
            <IntelligenceTab products={products} gc={gc} compareIds={compareIds} toggleCompare={toggleCompare} addToCart={addToCart} cartLoading={cartLoading} />
          )}
          {!loading && products && activeTab === 'comparez' && (
            <ComparezTab products={products} compareIds={compareIds} gc={gc} toggleCompare={toggleCompare} />
          )}
          {!loading && activeTab === 'commandez' && (
            <CommandezTab order={order} products={products} recipe={recipe} gc={gc}
              cart={cart} addToCart={addToCart} cartLoading={cartLoading}
              handleCheckout={handleCheckout} checkoutLoading={checkoutLoading} fetchCart={fetchCart} />
          )}
        </div>

        <div className="text-center text-xs text-slate-500 py-2.5 border-t flex-shrink-0" style={{ borderColor: 'rgb(51 65 85)' }} data-testid="supra-footer">
          SUPRA v2 | 7 Moteurs ULTRA | Stripe | BCE-4X / STEEVE-MAX V6
        </div>
      </div>
    </PinnablePanel>
  );
};

// ============================================================
// TAB: ANALYSE — GRILLE 3 COLONNES RÉPLIQUE DASHBOARD BIONIC™
// Score + Gauge | 4 Moteurs | Minéraux + Besoins + Recette + Coûts
// BCE-4X STEEVE-MAX — STANDARD GOLDEN — DENSITÉ MAXIMALE
// ============================================================
const AnalyseTab = ({ score, recipe, recommendations, evidence, costs, comparison, ecozone, energyProtein, terrainSolutions, gc, np, engines, ultraScore, ultraDeficits, species, season, soilData }) => {
  const needColor = (level) => {
    if (level === 'EXTREME' || level === 'CRITIQUE') return BIONIC.red;
    if (level === 'TRES ELEVE' || level === 'ELEVE') return BIONIC.orange;
    if (level === 'MODERE') return BIONIC.yellow;
    return BIONIC.green;
  };
  const physioText = PHYSIOLOGY_DATA[species]?.[season] || PHYSIOLOGY_DATA.chevreuil?.printemps;
  const behaviorText = MALE_BEHAVIOR[species]?.[season] || MALE_BEHAVIOR.chevreuil?.printemps;
  const ratingColor = { premium: BIONIC.amber, optimal: BIONIC.green, adequat: BIONIC.blue, insuffisant: BIONIC.red }[ultraScore.rating] || BIONIC.blue;

  const IC = ({ Icon, color, sz = 28 }) => (
    <div className="rounded-full flex items-center justify-center flex-shrink-0" style={{ width: sz, height: sz, backgroundColor: `${color}20` }}>
      <Icon style={{ color, width: sz * 0.5, height: sz * 0.5 }} />
    </div>
  );

  return (
    <div className="space-y-1.5" data-testid="supra-analyse-tab">
      {/* ═══════════════════════════════════════════════════════
          GUIDE PRO — BCE-4X GOLDEN V6+
          POSITIONNEMENT PRIORITAIRE — EN TETE DE HIERARCHIE
          COMMANDANT STEEVE-MAX
          ═══════════════════════════════════════════════════════ */}
      <PedagogieModule species={species} season={season} score={score} gc={gc} />

      {/* ═══════════════════════════════════════════════════════
          GRILLE 3 COLONNES — RÉPLIQUE EXACTE DASHBOARD BIONIC™
          Densité GOLDEN V9 | Gaps eliminés | BCE-4X
          ═══════════════════════════════════════════════════════ */}
      <div className="grid grid-cols-3 gap-1.5" data-testid="supra-3col-grid">

        {/* ══════════ COLONNE 1: Score + Gauge + Ecozone ══════════ */}
        <div className="space-y-1.5" data-testid="supra-col-1">
          {/* Score SUPRA */}
          <GoldenCard testId="supra-score-card" accentColor={gc} compact>
            <div className="flex items-center gap-3">
              <div className="w-[48px] h-[48px] rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: `linear-gradient(135deg, ${gc}30, ${gc}10)` }}>
                <span className="text-[30px] font-black tabular-nums" style={{ color: gc }}>{score.score_global}</span>
              </div>
              <div className="min-w-0">
                <div className="text-[16px] font-black text-white">Score SUPRA</div>
                <div className="flex items-center gap-1.5 mt-0.5">
                  <span className="text-[14px] font-bold px-2 py-0.5 rounded-lg" style={{ backgroundColor: `${gc}20`, color: gc }}>{score.grade}</span>
                  {score.score_source === 'SUPRA_UNIFIED' && <span className="text-[10px] font-bold px-1.5 py-0.5 rounded" style={{ backgroundColor: '#00BCD415', color: '#00BCD4' }}>UNIFIE</span>}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3 mt-2">
              <span className="text-[14px] font-semibold" style={{ color: BIONIC.green }}>{score.zones_resume?.vert} vert</span>
              <span className="text-[14px] font-semibold" style={{ color: BIONIC.orange }}>{score.zones_resume?.jaune} jaune</span>
              <span className="text-[14px] font-semibold" style={{ color: BIONIC.red }}>{score.zones_resume?.rouge} rouge</span>
            </div>
            {score.score_mineral != null && (
              <div className="flex items-center justify-between mt-1.5 pt-1.5 border-t" style={{ borderColor: 'rgba(255,255,255,0.06)' }}>
                <span className="text-[12px] text-slate-500">Score mineral</span>
                <span className="text-[14px] font-bold" style={{ color: BIONIC.purple }}>{score.score_mineral}/100</span>
              </div>
            )}
          </GoldenCard>

          {/* Gauge ULTRA */}
          <GoldenCard testId="ultra-gauge-card" accentColor={ratingColor} compact>
            <div className="flex items-center gap-3">
              <GaugeMini value={ultraScore.global_score || score.score_global || 0} label="ULTRA" color={ratingColor} />
              <div>
                <div className="text-[14px] font-bold text-white">7 Moteurs ULTRA</div>
                <div className="text-[30px] font-black leading-none" style={{ color: ratingColor }}>{(ultraScore.rating || 'N/A').toUpperCase()}</div>
                {ultraDeficits.total_critical > 0 && (
                  <div className="text-[14px] text-red-400">{ultraDeficits.total_critical} carences</div>
                )}
              </div>
            </div>
          </GoldenCard>

          {/* Ecozone */}
          {ecozone && (
            <GoldenCard testId="supra-ecozone-card" accentColor={BIONIC.green} compact>
              <div className="flex items-center gap-2 mb-1">
                <IC Icon={Leaf} color={BIONIC.green} />
                <span className="text-[16px] font-bold text-white">Ecozone</span>
              </div>
              <div className="text-[16px] text-gray-300 font-semibold">{ecozone.nom_commun}</div>
              <div className="text-[14px] text-gray-400 mt-1 leading-snug">{ecozone.habitat_principal}</div>
            </GoldenCard>
          )}

          {/* Besoins nutritionnels */}
          {energyProtein && (
            <GoldenCard testId="supra-energy-protein-card" accentColor={BIONIC.orange} compact>
              <div className="flex items-center gap-2 mb-2">
                <IC Icon={Zap} color={BIONIC.orange} />
                <span className="text-[16px] font-bold text-white">Besoins</span>
              </div>
              <div className="text-[14px] text-gray-400 mb-1.5">{energyProtein.phase}</div>
              <div className="rounded-lg px-3 py-2 mb-1.5" style={{ backgroundColor: 'rgba(255,255,255,0.04)', borderLeft: `4px solid ${needColor(energyProtein.energy_need)}` }}>
                <div className="flex justify-between">
                  <span className="text-[14px] text-gray-400">Energie</span>
                  <span className="text-[16px] font-bold" style={{ color: needColor(energyProtein.energy_need) }}>{energyProtein.energy_need}</span>
                </div>
              </div>
              <div className="rounded-lg px-3 py-2" style={{ backgroundColor: 'rgba(255,255,255,0.04)', borderLeft: `4px solid ${needColor(energyProtein.protein_need)}` }}>
                <div className="flex justify-between">
                  <span className="text-[14px] text-gray-400">Proteines</span>
                  <span className="text-[16px] font-bold" style={{ color: needColor(energyProtein.protein_need) }}>{energyProtein.protein_need}</span>
                </div>
              </div>
            </GoldenCard>
          )}
        </div>

        {/* ══════════ COLONNE 2: 4 Moteurs ULTRA ══════════ */}
        <div className="space-y-1.5" data-testid="supra-col-2">
          {(engines.soil || soilData) && (
            <GoldenCard testId="info-card-sol" accentColor={BIONIC.amber} compact>
              <div className="flex items-center gap-2 mb-2">
                <IC Icon={Mountain} color={BIONIC.amber} />
                <span className="text-[16px] font-bold text-white">Sol — Analyse pedologique</span>
                {soilData?.grade && <span className="text-[14px] font-bold px-2 py-0.5 rounded-lg ml-auto" style={{ backgroundColor: soilData.grade === 'S' || soilData.grade === 'A' ? `${BIONIC.green}18` : soilData.grade === 'B' ? `${BIONIC.orange}18` : `${BIONIC.red}18`, color: soilData.grade === 'S' || soilData.grade === 'A' ? BIONIC.green : soilData.grade === 'B' ? BIONIC.orange : BIONIC.red }}>{soilData.grade} — {soilData.score}/100</span>}
              </div>
              {soilData ? (
                <>
                  {[{ l: 'Type', v: soilData.soil_name }, { l: 'Classe', v: soilData.soil_class }, { l: 'Retention min.', v: `${soilData.metrics?.retention_mineraux}/100` }, { l: 'Drainage', v: `${soilData.metrics?.drainage_naturel}/100` }, { l: 'Lessivage', v: `${soilData.metrics?.risque_lessivage}/100` }, { l: 'Portance', v: `${soilData.metrics?.capacite_portance}/100` }, { l: 'pH', v: soilData.metrics?.ph_typique }, { l: 'Profondeur', v: `${soilData.metrics?.profondeur_cm} cm` }, { l: 'Mat. org.', v: `${soilData.metrics?.matiere_organique_pct}%` }].map((r, i) => (
                    <div key={i} className="flex justify-between py-0.5">
                      <span className="text-[14px] text-slate-400">{r.l}</span>
                      <span className="text-[16px] font-semibold text-white">{r.v || '—'}</span>
                    </div>
                  ))}
                  <div className="mt-2 rounded-lg px-3 py-2" style={{ backgroundColor: '#0F172A' }}>
                    <p className="text-[14px] text-slate-300 leading-relaxed">{soilData.description}</p>
                  </div>
                  <div className="mt-2">
                    <span className="text-[14px] text-slate-500">Texture: Argile {soilData.texture?.argile_pct}% | Sable {soilData.texture?.sable_pct}% | Limon {soilData.texture?.limon_pct}%</span>
                  </div>
                </>
              ) : (
                <>
                  {[{ l: 'Type', v: engines.soil?.soil_type }, { l: 'pH', v: engines.soil?.pH }, { l: 'Qualite', v: `${engines.soil?.quality_index || 0}/100` }].map((r, i) => (
                    <div key={i} className="flex justify-between py-0.5">
                      <span className="text-[14px] text-slate-400">{r.l}</span>
                      <span className="text-[16px] font-semibold text-white">{r.v || '—'}</span>
                    </div>
                  ))}
                </>
              )}
            </GoldenCard>
          )}
          {engines.metabolism && (
            <GoldenCard testId="info-card-metabolisme" accentColor={BIONIC.orange} compact>
              <div className="flex items-center gap-2 mb-2">
                <IC Icon={Activity} color={BIONIC.orange} />
                <span className="text-[16px] font-bold text-white">Metabolisme</span>
              </div>
              {[{ l: 'Phase', v: (engines.metabolism.metabolic_phase || '').replace(/_/g, ' ') }, { l: 'Energie', v: `x${engines.metabolism.energy_demand_factor || 0}` }, { l: 'Activite', v: engines.metabolism.activity_level }].map((r, i) => (
                <div key={i} className="flex justify-between py-0.5">
                  <span className="text-[14px] text-slate-400">{r.l}</span>
                  <span className="text-[16px] font-semibold text-white">{r.v || '—'}</span>
                </div>
              ))}
            </GoldenCard>
          )}
          {/* Vegetation + Hydrologie — BCE-4X: cote a cote pour equilibre visuel */}
          <div className="grid grid-cols-2 gap-1.5">
          {engines.vegetation && (
            <GoldenCard testId="info-card-vegetation" accentColor={BIONIC.green} compact>
              <div className="flex items-center gap-2 mb-2">
                <IC Icon={Leaf} color={BIONIC.green} />
                <span className="text-[16px] font-bold text-white">Vegetation</span>
              </div>
              {[{ l: 'Phase', v: engines.vegetation.phenophase }, { l: 'Couvert', v: `${engines.vegetation.couvert_pct || 0}%` }, { l: 'Fourrage', v: `${((engines.vegetation.avg_forage_quality || 0) * 100).toFixed(0)}%` }].map((r, i) => (
                <div key={i} className="flex justify-between py-0.5">
                  <span className="text-[14px] text-slate-400">{r.l}</span>
                  <span className="text-[16px] font-semibold text-white">{r.v || '—'}</span>
                </div>
              ))}
            </GoldenCard>
          )}
          {engines.hydrology && (
            <GoldenCard testId="info-card-hydrologie" accentColor={BIONIC.blue} compact>
              <div className="flex items-center gap-2 mb-2">
                <IC Icon={Droplets} color={BIONIC.blue} />
                <span className="text-[16px] font-bold text-white">Hydrologie</span>
              </div>
              {[{ l: 'Drainage', v: engines.hydrology.drainage }, { l: 'Lessivage', v: engines.hydrology.leaching_risk }, { l: 'Dist. eau', v: `${engines.hydrology.distance_eau_m || 0}m` }].map((r, i) => (
                <div key={i} className="flex justify-between py-0.5">
                  <span className="text-[14px] text-slate-400">{r.l}</span>
                  <span className="text-[16px] font-semibold text-white">{r.v || '—'}</span>
                </div>
              ))}
            </GoldenCard>
          )}
          </div>
        </div>

        {/* ══════════ COLONNE 3: Minéraux + Recette + Coûts ══════════ */}
        <div className="space-y-1.5" data-testid="supra-col-3">
          {/* Mineraux — mini-bars */}
          <GoldenCard testId="supra-minerals-card" accentColor="#f5a623" compact>
            <div className="flex items-center gap-2 mb-2">
              <IC Icon={FlaskConical} color="#f5a623" />
              <span className="text-[16px] font-bold text-white">Mineraux</span>
            </div>
            <div className="space-y-1.5">
              {Object.entries(score.scores_par_mineral || {}).map(([key, m]) => (
                <div key={key} className="flex items-center gap-2" data-testid={`supra-mineral-${key}`}>
                  <span className="text-[14px] text-slate-400 w-[60px] flex-shrink-0 truncate">{m.name}</span>
                  <div className="flex-1 h-[6px] rounded-full overflow-hidden" style={{ backgroundColor: 'rgba(255,255,255,0.06)' }}>
                    <div className="h-full rounded-full" style={{ width: `${m.score}%`, backgroundColor: zoneColor(m.zone) }} />
                  </div>
                  <span className="text-[16px] font-bold w-8 text-right tabular-nums" style={{ color: zoneColor(m.zone) }}>{m.score}</span>
                </div>
              ))}
            </div>
          </GoldenCard>

          {/* Recette */}
          {recipe && (
            <GoldenCard testId="supra-recipe-card" accentColor={BIONIC.green} compact>
              <div className="flex items-center gap-2 mb-2">
                <IC Icon={BookOpen} color={BIONIC.green} />
                <span className="text-[16px] font-bold text-white">Recette</span>
              </div>
              {recipe.ingredients_cles?.slice(0, 4).map((ing, i) => (
                <div key={i} className="flex items-center justify-between py-1 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
                  <div className="min-w-0 flex-1">
                    <span className="text-[14px] text-white">{ing.mineral}</span>
                    <span className="text-[14px] text-gray-500 ml-1">{ing.product}</span>
                  </div>
                  <span className="text-[14px] font-bold px-1.5 py-0.5 rounded-lg flex-shrink-0" style={{ backgroundColor: `${priorityColor(ing.priority)}15`, color: priorityColor(ing.priority) }}>{ing.priority}</span>
                </div>
              ))}
            </GoldenCard>
          )}

          {/* Couts */}
          {costs && (
            <GoldenCard testId="supra-costs-card" accentColor={BIONIC.orange} compact>
              <div className="flex items-center gap-2 mb-2">
                <IC Icon={DollarSign} color={BIONIC.orange} />
                <span className="text-[16px] font-bold text-white">Couts</span>
              </div>
              {[{ l: 'Initial', v: `${costs.initial_cost_cad}$`, c: 'white' }, { l: 'Annuel', v: `${costs.annual_cost_cad}$`, c: BIONIC.orange }, { l: 'Par visite', v: `${costs.cost_per_visit_cad}$`, c: 'white' }].map((r, i) => (
                <div key={i} className="flex justify-between py-0.5">
                  <span className="text-[14px] text-gray-400">{r.l}</span>
                  <span className="text-[16px] font-bold" style={{ color: r.c }}>{r.v}</span>
                </div>
              ))}
            </GoldenCard>
          )}
        </div>
      </div>

      {/* ═══ Sections PREMIUM — intégrées grille 3 colonnes — STANDARD GOLDEN ═══ */}
      <div className="grid grid-cols-3 gap-2 mt-1.5" data-testid="supra-premium-grid">
        <GoldenCard testId="supra-physiology" accentColor={BIONIC.purple} compact>
          <div className="flex items-center gap-2 mb-1.5">
            <IC Icon={Crown} color={BIONIC.purple} sz={24} />
            <span className="text-[13px] font-bold text-white">Physiologie</span>
            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded ml-auto" style={{ backgroundColor: `${BIONIC.purple}15`, color: BIONIC.purple }}>{species}</span>
          </div>
          <p className="text-[11px] text-slate-400 leading-snug line-clamp-4">{physioText}</p>
        </GoldenCard>
        <GoldenCard testId="supra-behavior" accentColor={BIONIC.cyan} compact>
          <div className="flex items-center gap-2 mb-1.5">
            <IC Icon={Eye} color={BIONIC.cyan} sz={24} />
            <span className="text-[13px] font-bold text-white">Comportement males</span>
            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded ml-auto" style={{ backgroundColor: `${BIONIC.cyan}15`, color: BIONIC.cyan }}>{season}</span>
          </div>
          <p className="text-[11px] text-slate-400 leading-snug line-clamp-4">{behaviorText}</p>
        </GoldenCard>
        <GoldenCard testId="supra-support" accentColor={BIONIC.green} compact>
          <div className="flex items-center gap-2 mb-1.5">
            <IC Icon={TreeDeciduous} color={BIONIC.green} sz={24} />
            <span className="text-[13px] font-bold text-white">Support</span>
            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded ml-auto" style={{ backgroundColor: `${BIONIC.green}15`, color: BIONIC.green }}>Hierarchie</span>
          </div>
          <div className="space-y-0.5">
            {SUPPORT_HIERARCHY.map((s, i) => (
              <div key={i} className="flex items-center justify-between">
                <span className="text-[11px] text-slate-400 truncate">{s.name}</span>
                <span className="text-[12px] font-bold tabular-nums" style={{ color: s.color }}>{s.score}</span>
              </div>
            ))}
          </div>
        </GoldenCard>
      </div>

      {evidence.length > 0 && (
        <div className="mt-1.5">
          <GoldenCard testId="supra-evidence" accentColor={BIONIC.purple} compact>
            <div className="flex items-center gap-2 mb-1.5">
              <IC Icon={FileText} color={BIONIC.purple} sz={24} />
              <span className="text-[13px] font-bold text-white">Sources scientifiques</span>
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded ml-auto" style={{ backgroundColor: `${BIONIC.purple}15`, color: BIONIC.purple }}>{evidence.length} refs</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {evidence.slice(0, 4).map((ref, i) => (
                <span key={i} className="text-[10px] text-slate-400 px-1.5 py-0.5 rounded" style={{ backgroundColor: 'rgba(255,255,255,0.04)' }}>{ref.auteurs} ({ref.annee})</span>
              ))}
            </div>
          </GoldenCard>
        </div>
      )}
    </div>
  );
};

// ============================================================
// TAB: INTELLIGENCE — 3 COLONNES GOLDEN — BCE-4X STEEVE-MAX
// Produits avec match_score en grille dense
// ============================================================
const IntelligenceTab = ({ products, gc, compareIds, toggleCompare, addToCart, cartLoading }) => {
  const productList = products.products || [];
  const third = Math.ceil(productList.length / 3);
  const col1 = productList.slice(0, third);
  const col2 = productList.slice(third, third * 2);
  const col3 = productList.slice(third * 2);

  const IC = ({ Icon, color, sz = 28 }) => (
    <div className="rounded-full flex items-center justify-center flex-shrink-0" style={{ width: sz, height: sz, backgroundColor: `${color}20` }}>
      <Icon style={{ color, width: sz * 0.5, height: sz * 0.5 }} />
    </div>
  );

  const ProductCard = ({ p }) => {
    const sc = p.score_global >= 85 ? BIONIC.green : p.score_global >= 70 ? BIONIC.yellow : p.score_global >= 50 ? BIONIC.orange : BIONIC.red;
    const isCompared = compareIds.includes(p.product_id);
    return (
      <GoldenCard testId={`product-${p.product_id}`} accentColor={sc} compact>
        <div className="flex items-center gap-2.5">
          <div className="w-[42px] h-[42px] rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: `linear-gradient(135deg, ${sc}30, ${sc}10)` }}>
            <span className="text-[18px] font-black tabular-nums" style={{ color: sc }}>{p.score_global}</span>
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-[16px] font-bold text-white truncate">{p.name}</div>
            <div className="text-[14px] text-gray-400">{p.type} | {p.price_cad}$ | {p.weight_kg}kg</div>
          </div>
        </div>
        <div className="flex gap-1 mt-1.5 flex-wrap">
          {p.optimal_for?.slice(0, 3).map((tag, j) => (
            <span key={j} className="text-[14px] px-1.5 py-0.5 rounded-lg" style={{ backgroundColor: `${BIONIC.green}15`, color: BIONIC.green }}>{tag}</span>
          ))}
        </div>
        <div className="grid grid-cols-3 gap-1 text-center mt-2">
          <div><span className="text-[14px] text-gray-500">Esp</span><div className="text-[16px] font-bold" style={{ color: p.score_species >= 85 ? BIONIC.green : BIONIC.orange }}>{p.score_species}%</div></div>
          <div><span className="text-[14px] text-gray-500">Sai</span><div className="text-[16px] font-bold" style={{ color: p.score_season >= 85 ? BIONIC.green : BIONIC.orange }}>{p.score_season}%</div></div>
          <div><span className="text-[14px] text-gray-500">Sol</span><div className="text-[16px] font-bold" style={{ color: p.score_soil >= 85 ? BIONIC.green : BIONIC.orange }}>{p.score_soil}%</div></div>
        </div>
        <div className="flex gap-1.5 mt-2">
          <button onClick={() => toggleCompare(p.product_id)}
            className="flex-1 text-[14px] font-bold px-2 py-1.5 rounded-lg transition-all"
            style={{ backgroundColor: isCompared ? `${BIONIC.blue}20` : 'rgba(255,255,255,0.05)', color: isCompared ? BIONIC.blue : '#9ca3af' }}
            data-testid={`compare-toggle-${p.product_id}`}>
            {isCompared ? 'Retire' : 'Comparer'}
          </button>
          <SupraButton size="sm" onClick={() => addToCart(p.product_id)} disabled={cartLoading} testId={`add-cart-${p.product_id}`}>
            <ShoppingCart className="h-3 w-3" /> CMD
          </SupraButton>
        </div>
      </GoldenCard>
    );
  };

  return (
    <div className="space-y-1.5" data-testid="supra-intelligence-tab">
      {/* Header GOLDEN */}
      <GoldenCard testId="intelligence-header" accentColor={BIONIC.amber} compact>
        <div className="flex items-center gap-3">
          <IC Icon={FlaskConical} color={BIONIC.amber} />
          <span className="text-[16px] font-bold text-white">Score d'adequation</span>
          <span className="text-[14px] font-semibold px-2 py-0.5 rounded-lg ml-auto" style={{ backgroundColor: `${BIONIC.amber}18`, color: BIONIC.amber }}>{products.total} produits</span>
        </div>
      </GoldenCard>

      {/* GRILLE 3 COLONNES — RÉPLIQUE DASHBOARD */}
      <div className="grid grid-cols-3 gap-1.5" data-testid="intelligence-3col-grid">
        <div className="space-y-1.5">{col1.map(p => <ProductCard key={p.product_id} p={p} />)}</div>
        <div className="space-y-1.5">{col2.map(p => <ProductCard key={p.product_id} p={p} />)}</div>
        <div className="space-y-1.5">{col3.map(p => <ProductCard key={p.product_id} p={p} />)}</div>
      </div>
    </div>
  );
};

// ============================================================
// TAB: FICHE — SALINES ULTIME (5 Scores + 20 Sources + Guides)
// 100% VERTICAL | COMPACT GOLDEN | BCE-4X STEEVE-MAX
// ============================================================
const FICHE_SCORES = [
  { key: 'logistique', label: 'Logistique', icon: MapPin, color: '#3b82f6' },
  { key: 'gros_males', label: 'Gros Males', icon: TreeDeciduous, color: '#22c55e' },
  { key: 'strategique', label: 'Strategique', icon: Shield, color: '#f59e0b' },
  { key: 'cout_roi', label: 'Retour sur Investissement', icon: DollarSign, color: '#a855f7' },
  { key: 'tcs', label: 'Terrain — Conditions Structurelles', icon: Mountain, color: '#ef4444' },
];

const FicheGradeTag = ({ grade, color }) => {
  const colors = { S: '#f59e0b', A: '#22c55e', B: '#3b82f6', C: '#f97316', D: '#ef4444', F: '#991b1b' };
  const c = colors[grade] || color || '#6b7280';
  return <span className="px-2 py-0.5 text-[10px] font-black rounded" style={{ backgroundColor: `${c}20`, color: c, border: `1px solid ${c}40` }}>{grade}</span>;
};

const FicheTab = ({ ficheData, species, season, lat, lng, np, soilData }) => {
  const [showSources, setShowSources] = useState(false);
  const [selectedCriteria, setSelectedCriteria] = useState(null);
  const [selectedCriteriaValue, setSelectedCriteriaValue] = useState(null);

  const openCriteria = (key, value) => {
    setSelectedCriteria(key);
    setSelectedCriteriaValue(value);
  };

  if (!ficheData) {
    return (
      <div className="text-center py-8 space-y-2" data-testid="fiche-loading">
        <Droplets className="h-6 w-6 text-cyan-400 mx-auto" />
        <div className="text-slate-300 text-[16px] font-semibold">FICHE SALINE ULTIME</div>
        <div className="text-slate-500 text-[16px]">Chargement des 5 scores...</div>
      </div>
    );
  }

  const { global_score, scores, scientific_sources } = ficheData;

  const IC = ({ Icon, color, sz = 28 }) => (
    <div className="rounded-full flex items-center justify-center flex-shrink-0" style={{ width: sz, height: sz, backgroundColor: `${color}20` }}>
      <Icon style={{ color, width: sz * 0.5, height: sz * 0.5 }} />
    </div>
  );

  // Composant de sous-critère CLIQUABLE avec hyperlien
  const CriteriaRow = ({ criteriaKey, criteriaValue }) => (
    <button
      onClick={() => openCriteria(criteriaKey, criteriaValue)}
      className="w-full flex items-center justify-between py-1 px-1 rounded-lg cursor-pointer transition-all hover:bg-white/5 group"
      data-testid={`criteria-link-${criteriaKey.replace(/[\s_]/g, '-')}`}
      title={`Cliquez pour voir la fiche complete: ${criteriaKey.replace(/_/g, ' ')}`}
    >
      <span className="text-[14px] text-slate-400 group-hover:text-cyan-400 transition-colors flex items-center gap-1.5">
        <Info className="h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity" style={{ color: '#00BCD4' }} />
        {criteriaKey.replace(/_/g, ' ')}
      </span>
      <span className="text-[16px] text-white font-medium group-hover:text-cyan-300 transition-colors underline decoration-dotted decoration-slate-600 group-hover:decoration-cyan-500">{criteriaValue.value}</span>
    </button>
  );

  return (
    <div className="space-y-1.5" data-testid="supra-fiche-tab">
      {/* Modal fiche explicative — GUIDE BIONIC NIVEAU PROFESSIONNEL */}
      {selectedCriteria && (
        <CriteriaDetailModal
          criteriaKey={selectedCriteria}
          criteriaValue={selectedCriteriaValue}
          species={species}
          season={season}
          onClose={() => { setSelectedCriteria(null); setSelectedCriteriaValue(null); }}
        />
      )}
      {/* ═══ Score Global FICHE — STANDARD GOLDEN pleine largeur ═══ */}
      <GoldenCard testId="fiche-global-score" accentColor="#00BCD4" compact>
        <div className="flex items-center gap-4">
          <div className="w-[48px] h-[48px] rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: 'linear-gradient(135deg, #00BCD430, #00BCD410)' }}>
            <span className="text-[30px] font-black text-cyan-400">{global_score.score}</span>
          </div>
          <div className="min-w-0">
            <div className="text-[16px] font-black text-white">FICHE SALINE ULTIME</div>
            <div className="flex items-center gap-2 mt-0.5">
              <FicheGradeTag grade={global_score.grade} color="#00BCD4" />
              <span className="text-[14px] text-slate-500">5 scores | 20 sources</span>
            </div>
            <div className="text-[14px] text-slate-600">{species} | {season} | {np?.id || `${parseFloat(lat).toFixed(2)}, ${parseFloat(lng).toFixed(2)}`}</div>
          </div>
        </div>
      </GoldenCard>

      {/* ═══════════════════════════════════════════════════════
          GRILLE 3 COLONNES — RÉPLIQUE EXACTE DASHBOARD BIONIC™
          ═══════════════════════════════════════════════════════ */}
      <div className="grid grid-cols-3 gap-1.5" data-testid="fiche-3col-grid">

        {/* ══════════ COLONNE 1: Logistique + Gros Males ══════════ */}
        <div className="space-y-1.5">
          {FICHE_SCORES.slice(0, 2).map(({ key, label, icon: Icon, color }) => {
            const data = scores?.[key];
            if (!data) return null;
            return (
              <GoldenCard key={key} testId={`fiche-score-${key}`} accentColor={color} compact>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <IC Icon={Icon} color={color} />
                    <span className="text-[16px] font-bold text-white">{label}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-[30px] font-black text-white leading-none">{data.score}</span>
                    <FicheGradeTag grade={data.grade} color={color} />
                  </div>
                </div>
                <div className="w-full h-[6px] rounded-full mb-2" style={{ backgroundColor: 'rgba(255,255,255,0.06)' }}>
                  <div className="h-full rounded-full" style={{ width: `${data.score}%`, backgroundColor: color }} />
                </div>
                {Object.entries(data.components || {}).map(([ck, cv]) => (
                  <CriteriaRow key={ck} criteriaKey={ck} criteriaValue={cv} />
                ))}
              </GoldenCard>
            );
          })}
          {/* Guide Logistique */}
          <GoldenCard testId="fiche-guide-logistique" accentColor={BIONIC.blue} compact>
            <div className="flex items-center gap-2 mb-1.5">
              <IC Icon={MapPin} color={BIONIC.blue} />
              <span className="text-[16px] font-bold text-white">Logistique</span>
              <span className="text-[14px] px-1.5 py-0.5 rounded-lg font-bold ml-auto" style={{ backgroundColor: `${BIONIC.blue}15`, color: BIONIC.blue }}>GUIDE</span>
            </div>
            <p className="text-[14px] text-slate-400 leading-relaxed">Accessibilite vehiculaire: transport mineraux (20-25kg). Portage max: 200m. Budget annuel: 150-250$.</p>
          </GoldenCard>
        </div>

        {/* ══════════ COLONNE 2: Strategique + Cout/ROI + TCS ══════════ */}
        <div className="space-y-1.5">
          {FICHE_SCORES.slice(2, 5).map(({ key, label, icon: Icon, color }) => {
            const data = scores?.[key];
            if (!data) return null;
            return (
              <GoldenCard key={key} testId={`fiche-score-${key}`} accentColor={color} compact>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <IC Icon={Icon} color={color} />
                    <span className="text-[16px] font-bold text-white">{label}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-[30px] font-black text-white leading-none">{data.score}</span>
                    <FicheGradeTag grade={data.grade} color={color} />
                  </div>
                </div>
                <div className="w-full h-[6px] rounded-full mb-2" style={{ backgroundColor: 'rgba(255,255,255,0.06)' }}>
                  <div className="h-full rounded-full" style={{ width: `${data.score}%`, backgroundColor: color }} />
                </div>
                {Object.entries(data.components || {}).map(([ck, cv]) => (
                  <CriteriaRow key={ck} criteriaKey={ck} criteriaValue={cv} />
                ))}
              </GoldenCard>
            );
          })}
        </div>

        {/* ══════════ COLONNE 3: Plan Gros Males + ROI + Sources ══════════ */}
        <div className="space-y-1.5">
          {/* Plan Gros Males */}
          <GoldenCard testId="fiche-plan-males" accentColor={BIONIC.green} compact>
            <div className="flex items-center gap-2 mb-1.5">
              <IC Icon={TreeDeciduous} color={BIONIC.green} />
              <span className="text-[16px] font-bold text-white">Plan Gros Males</span>
              <span className="text-[14px] px-1.5 py-0.5 rounded-lg font-bold ml-auto" style={{ backgroundColor: `${BIONIC.green}15`, color: BIONIC.green }}>GUIDE</span>
            </div>
            <p className="text-[14px] text-slate-400 leading-relaxed">Positionnez la saline a proximite des corridors de deplacement. Les gros males preferent les zones de transition foret-clairiere avec couvert lateral 60%+.</p>
            <p className="text-[14px] text-slate-400 mt-1">Frequence: bi-mensuelle en pre-rut, hebdomadaire pendant le rut actif.</p>
          </GoldenCard>

          {/* Guide ROI */}
          <GoldenCard testId="fiche-guide-roi" accentColor={BIONIC.purple} compact>
            <div className="flex items-center gap-2 mb-1.5">
              <IC Icon={DollarSign} color={BIONIC.purple} />
              <span className="text-[16px] font-bold text-white">Analyse Cout / ROI</span>
              <span className="text-[14px] px-1.5 py-0.5 rounded-lg font-bold ml-auto" style={{ backgroundColor: `${BIONIC.purple}15`, color: BIONIC.purple }}>GUIDE</span>
            </div>
            <p className="text-[14px] text-slate-400 leading-relaxed">ROI = observations qualitatives par saison. Objectif: 15+ observations positives. Saline mature (2+ saisons) reduit cout/observation de 40-60%.</p>
          </GoldenCard>

          {/* SOIL ENGINE — Analyse pedologique */}
          {soilData && (
            <GoldenCard testId="fiche-soil-analysis" accentColor={BIONIC.amber} compact>
              <div className="flex items-center gap-2 mb-1.5">
                <IC Icon={Mountain} color={BIONIC.amber} />
                <span className="text-[16px] font-bold text-white">Sol — Type detecte</span>
                <span className="text-[14px] px-1.5 py-0.5 rounded-lg font-bold ml-auto" style={{ backgroundColor: soilData.grade === 'A' || soilData.grade === 'S' ? `${BIONIC.green}18` : `${BIONIC.orange}18`, color: soilData.grade === 'A' || soilData.grade === 'S' ? BIONIC.green : BIONIC.orange }}>{soilData.grade} — {soilData.score}/100</span>
              </div>
              <div className="space-y-1">
                <div className="flex justify-between"><span className="text-[14px] text-slate-400">Type</span><span className="text-[16px] font-semibold text-white">{soilData.soil_name}</span></div>
                <div className="flex justify-between"><span className="text-[14px] text-slate-400">Retention</span><span className="text-[16px] font-semibold text-white">{soilData.metrics?.retention_mineraux}/100</span></div>
                <div className="flex justify-between"><span className="text-[14px] text-slate-400">Drainage</span><span className="text-[16px] font-semibold text-white">{soilData.metrics?.drainage_naturel}/100</span></div>
                <div className="flex justify-between"><span className="text-[14px] text-slate-400">Lessivage</span><span className="text-[16px] font-semibold text-white">{soilData.metrics?.risque_lessivage}/100</span></div>
              </div>
              <p className="text-[14px] text-slate-500 mt-1.5 leading-relaxed">{soilData.seasonal_note}</p>
              {soilData.recommendations?.length > 0 && (
                <div className="mt-2 space-y-1">
                  {soilData.recommendations.slice(0, 4).map((r, i) => (
                    <p key={i} className="text-[14px] text-slate-400 leading-relaxed flex items-start gap-1.5">
                      <span className="text-amber-500 mt-0.5 flex-shrink-0">&#9670;</span>{r}
                    </p>
                  ))}
                </div>
              )}
            </GoldenCard>
          )}

          {/* 20 Sources Scientifiques */}
          <GoldenCard testId="fiche-sources-card" accentColor="#00BCD4" compact>
            <button onClick={() => setShowSources(!showSources)} className="w-full flex items-center justify-between cursor-pointer" data-testid="fiche-toggle-sources">
              <div className="flex items-center gap-2">
                <IC Icon={BookOpen} color="#00BCD4" />
                <span className="text-[16px] font-bold text-white">20 Sources</span>
              </div>
              {showSources ? <ChevronUp className="h-4 w-4 text-slate-500" /> : <ChevronDown className="h-4 w-4 text-slate-500" />}
            </button>
            {showSources && (
              <div className="mt-2 space-y-1">
                {(scientific_sources || []).map((src) => (
                  <div key={src.id} className="flex items-start gap-2 py-1 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
                    <span className="text-[14px] font-bold text-cyan-500 flex-shrink-0">[{src.id}]</span>
                    <span className="text-[14px] text-slate-300">{src.ref}</span>
                  </div>
                ))}
              </div>
            )}
          </GoldenCard>

          {/* Integrations */}
          <div className="flex flex-wrap gap-1">
            {['SUPRA/V6', 'ACCESS v7', 'PARTAGER', 'ADMIN Premium'].map((tag, i) => (
              <span key={i} className="text-[14px] px-1.5 py-0.5 rounded font-bold" style={{ backgroundColor: `${['#00BCD4', '#22c55e', '#34d399', '#f5a623'][i]}10`, color: ['#00BCD4', '#22c55e', '#34d399', '#f5a623'][i] }}>{tag}</span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// ============================================================
// TAB: COMPAREZ — 3 COLONNES GOLDEN — BCE-4X STEEVE-MAX
// ============================================================
const ComparezTab = ({ products, compareIds, gc, toggleCompare }) => {
  const compared = (products.products || []).filter(p => compareIds.includes(p.product_id));

  const IC = ({ Icon, color, sz = 28 }) => (
    <div className="rounded-full flex items-center justify-center flex-shrink-0" style={{ width: sz, height: sz, backgroundColor: `${color}20` }}>
      <Icon style={{ color, width: sz * 0.5, height: sz * 0.5 }} />
    </div>
  );

  if (compared.length === 0) {
    return (
      <div className="text-center py-12" data-testid="supra-comparez-tab">
        <div className="grid grid-cols-3 gap-1.5">
          <div />
          <GoldenCard testId="compare-empty" accentColor={BIONIC.blue} compact>
            <div className="text-center py-6">
              <IC Icon={Scale} color={BIONIC.blue} sz={40} />
              <div className="text-[16px] text-gray-300 font-semibold mt-3">Aucun produit selectionne</div>
              <div className="text-[14px] text-gray-500 mt-1">Allez dans INTELLIGENCE et selectionnez 2-4 produits</div>
            </div>
          </GoldenCard>
          <div />
        </div>
      </div>
    );
  }

  const best = compared.reduce((a, b) => a.score_global > b.score_global ? a : b);

  // Pad to exactly 3 columns
  const padded = [...compared];
  while (padded.length < 3) padded.push(null);

  return (
    <div className="space-y-1.5" data-testid="supra-comparez-tab">
      {/* Header GOLDEN */}
      <GoldenCard testId="compare-header" accentColor={BIONIC.blue} compact>
        <div className="flex items-center gap-3">
          <IC Icon={Scale} color={BIONIC.blue} />
          <span className="text-[16px] font-bold text-white">Comparaison</span>
          <span className="text-[14px] font-semibold px-2 py-0.5 rounded-lg ml-auto" style={{ backgroundColor: `${BIONIC.blue}18`, color: BIONIC.blue }}>{compared.length} produit(s)</span>
        </div>
      </GoldenCard>

      {/* GRILLE 3 COLONNES — RÉPLIQUE DASHBOARD */}
      <div className="grid grid-cols-3 gap-1.5" data-testid="compare-3col-grid">
        {padded.slice(0, 3).map((p, idx) => {
          if (!p) return <div key={`empty-${idx}`} />;
          const isBest = p.product_id === best.product_id;
          const sc = p.score_global >= 85 ? BIONIC.green : p.score_global >= 70 ? BIONIC.yellow : p.score_global >= 50 ? BIONIC.orange : BIONIC.red;
          return (
            <GoldenCard key={p.product_id} testId={`compare-card-${p.product_id}`} accentColor={isBest ? BIONIC.green : sc} compact>
              {isBest && <div className="text-[14px] font-bold text-center mb-2" style={{ color: BIONIC.green }}>MEILLEUR CHOIX</div>}
              <div className="text-center mb-3">
                <div className="w-[56px] h-[56px] rounded-xl flex items-center justify-center mx-auto" style={{ background: `linear-gradient(135deg, ${sc}30, ${sc}10)` }}>
                  <span className="text-[30px] font-black tabular-nums" style={{ color: sc }}>{p.score_global}</span>
                </div>
                <div className="text-[16px] font-bold text-white mt-2">{p.name}</div>
                <div className="text-[14px] text-gray-400">{p.type}</div>
              </div>
              <div className="space-y-1.5">
                {[
                  { label: 'Espece', val: `${p.score_species}%`, c: p.score_species >= 85 ? BIONIC.green : BIONIC.orange },
                  { label: 'Saison', val: `${p.score_season}%`, c: p.score_season >= 85 ? BIONIC.green : BIONIC.orange },
                  { label: 'Sol', val: `${p.score_soil}%`, c: p.score_soil >= 85 ? BIONIC.green : BIONIC.orange },
                  { label: 'Prix', val: `${p.price_cad}$`, c: 'white' },
                  { label: 'Poids', val: `${p.weight_kg}kg`, c: 'white' },
                ].map((row, i) => (
                  <div key={i} className="flex justify-between py-0.5">
                    <span className="text-[14px] text-gray-400">{row.label}</span>
                    <span className="text-[16px] font-bold" style={{ color: row.c }}>{row.val}</span>
                  </div>
                ))}
              </div>
              {/* Mini-bars pour les 3 scores */}
              <div className="space-y-1.5 mt-2">
                {[
                  { l: 'Espece', v: p.score_species, c: p.score_species >= 85 ? BIONIC.green : BIONIC.orange },
                  { l: 'Saison', v: p.score_season, c: p.score_season >= 85 ? BIONIC.green : BIONIC.orange },
                  { l: 'Sol', v: p.score_soil, c: p.score_soil >= 85 ? BIONIC.green : BIONIC.orange },
                ].map((bar, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <span className="text-[14px] text-slate-500 w-12">{bar.l}</span>
                    <div className="flex-1 h-[6px] rounded-full overflow-hidden" style={{ backgroundColor: 'rgba(255,255,255,0.06)' }}>
                      <div className="h-full rounded-full" style={{ width: `${bar.v}%`, backgroundColor: bar.c }} />
                    </div>
                  </div>
                ))}
              </div>
              <button onClick={() => toggleCompare(p.product_id)}
                className="w-full mt-3 text-[14px] font-bold py-2 rounded-lg transition-all"
                style={{ backgroundColor: `${BIONIC.red}15`, color: BIONIC.red }}
                data-testid={`compare-remove-${p.product_id}`}>
                Retirer
              </button>
            </GoldenCard>
          );
        })}
      </div>
    </div>
  );
};

// ============================================================
// TAB: COMMANDEZ — 3 COLONNES GOLDEN — BCE-4X STEEVE-MAX
// Panier Stripe REEL + Checkout
// ============================================================
const CommandezTab = ({ order, products, recipe, gc, cart, addToCart, cartLoading, handleCheckout, checkoutLoading, fetchCart }) => {
  const IC = ({ Icon, color, sz = 28 }) => (
    <div className="rounded-full flex items-center justify-center flex-shrink-0" style={{ width: sz, height: sz, backgroundColor: `${color}20` }}>
      <Icon style={{ color, width: sz * 0.5, height: sz * 0.5 }} />
    </div>
  );

  return (
    <div className="space-y-1.5" data-testid="supra-commandez-tab">
      {/* GRILLE 3 COLONNES — RÉPLIQUE DASHBOARD */}
      <div className="grid grid-cols-3 gap-1.5" data-testid="commandez-3col-grid">

        {/* ══════════ COLONNE 1: Recette complete ══════════ */}
        <div className="space-y-1.5">
          {order && (
            <GoldenCard testId="order-pack-card" accentColor={SUPRA_CMD_COLOR} compact>
              <div className="flex items-center gap-2 mb-2">
                <IC Icon={Package} color={SUPRA_CMD_COLOR} />
                <span className="text-[16px] font-bold text-white">Recette complete</span>
              </div>
              <div className="text-[30px] font-black mb-2" style={{ color: SUPRA_CMD_COLOR }}>{order.summary?.cost_initial_cad}$</div>
              <div className="space-y-0">
                {order.items?.map((item, i) => (
                  <div key={i} className="flex items-center gap-2 py-2 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
                    <div className="flex-1 min-w-0">
                      <div className="text-[14px] font-bold text-white truncate">{item.name}</div>
                      <div className="text-[14px] text-gray-500">{item.brand} | {item.dosage}</div>
                    </div>
                    <span className="text-[16px] font-bold text-white flex-shrink-0">{item.total_price_cad}$</span>
                    <SupraButton size="sm" onClick={() => addToCart(item.product_id || `sal_00${i+1}`)} disabled={cartLoading} testId={`order-add-${i}`}>
                      <Plus className="h-3 w-3" />
                    </SupraButton>
                  </div>
                ))}
              </div>
            </GoldenCard>
          )}
          {!order && (
            <GoldenCard testId="order-empty" accentColor={BIONIC.orange} compact>
              <div className="text-center py-4">
                <IC Icon={Package} color={BIONIC.orange} sz={36} />
                <div className="text-[16px] text-gray-400 mt-2">Aucune recette disponible</div>
              </div>
            </GoldenCard>
          )}
        </div>

        {/* ══════════ COLONNE 2: Produits individuels ══════════ */}
        <div className="space-y-1.5">
          <GoldenCard testId="shop-header" accentColor={BIONIC.amber} compact>
            <div className="flex items-center gap-2">
              <IC Icon={ShoppingCart} color={BIONIC.amber} />
              <span className="text-[16px] font-bold text-white">Produits individuels</span>
            </div>
          </GoldenCard>
          {products?.products?.slice(0, 6).map(p => {
            const sc = p.score_global >= 85 ? BIONIC.green : p.score_global >= 70 ? BIONIC.yellow : p.score_global >= 50 ? BIONIC.orange : BIONIC.red;
            return (
              <GoldenCard key={p.product_id} testId={`shop-product-${p.product_id}`} accentColor={sc} compact>
                <div className="flex items-center gap-2">
                  <div className="w-[36px] h-[36px] rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: `linear-gradient(135deg, ${sc}30, ${sc}10)` }}>
                    <span className="text-[16px] font-black tabular-nums" style={{ color: sc }}>{p.score_global}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-[14px] font-bold text-white truncate">{p.name}</div>
                    <div className="text-[14px] text-gray-500">{p.type} | {p.weight_kg}kg</div>
                  </div>
                  <span className="text-[16px] font-bold text-white flex-shrink-0">{p.price_cad}$</span>
                  <SupraButton size="sm" onClick={() => addToCart(p.product_id)} disabled={cartLoading} testId={`shop-order-${p.product_id}`}>
                    <ShoppingCart className="h-3 w-3" />
                  </SupraButton>
                </div>
              </GoldenCard>
            );
          })}
        </div>

        {/* ══════════ COLONNE 3: Panier Stripe REEL ══════════ */}
        <div className="space-y-1.5">
          <GoldenCard testId="supra-cart-stripe" accentColor={BIONIC.amber} compact>
            <div className="flex items-center gap-2 mb-3">
              <IC Icon={ShoppingCart} color={BIONIC.amber} />
              <span className="text-[16px] font-bold text-white">Panier</span>
              <span className="text-[14px] text-gray-400 ml-auto">{cart.item_count || 0} article(s)</span>
            </div>
            {cart.items?.length > 0 ? (
              <>
                <div className="space-y-1.5">
                  {cart.items.map((item) => (
                    <div key={item.item_id} className="flex items-center gap-2 py-1.5 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }} data-testid={`cart-item-${item.product_id}`}>
                      <div className="flex-1 min-w-0">
                        <div className="text-[14px] font-semibold text-white truncate">{item.name}</div>
                        <div className="text-[14px] text-gray-500">{item.format} — {item.unit_price}$/u</div>
                      </div>
                      <span className="text-[14px] font-bold text-gray-300">x{item.quantity}</span>
                      <span className="text-[16px] font-bold" style={{ color: BIONIC.amber }}>{item.subtotal}$</span>
                    </div>
                  ))}
                </div>
                <div className="flex items-center justify-between mt-3 pt-2 border-t" style={{ borderColor: 'rgba(255,255,255,0.08)' }}>
                  <span className="text-[14px] text-gray-400">Total</span>
                  <span className="text-[30px] font-black tabular-nums" style={{ color: BIONIC.amber }}>{cart.total}$</span>
                </div>
                <SupraButton size="lg" onClick={handleCheckout} disabled={checkoutLoading} testId="supra-checkout-btn">
                  {checkoutLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <ShoppingCart className="h-4 w-4" />}
                  {checkoutLoading ? 'Traitement...' : 'Payer avec Stripe'}
                  <ArrowRight className="h-4 w-4" />
                </SupraButton>
                <p className="text-[14px] text-gray-600 text-center mt-1.5">Paiement securise par Stripe</p>
              </>
            ) : (
              <div className="text-center py-6">
                <IC Icon={ShoppingCart} color={BIONIC.amber} sz={36} />
                <p className="text-[14px] text-gray-500 mt-2">Votre panier est vide</p>
                <p className="text-[14px] text-gray-600 mt-0.5">Cliquez CMD pour ajouter</p>
              </div>
            )}
          </GoldenCard>
        </div>
      </div>
    </div>
  );
};

export default NutritionPointDetailPanel;

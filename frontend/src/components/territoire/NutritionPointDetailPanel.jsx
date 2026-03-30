import React, { useState, useEffect, useCallback } from 'react';
import {
  Droplets, FlaskConical, Leaf, MapPin, AlertTriangle, Layers, Beaker,
  ShoppingCart, DollarSign, BookOpen, FileText, ExternalLink, Zap, Package,
  Construction, Scale, BarChart3, ArrowRight, ChevronDown, ChevronUp,
  Mountain, Activity, Thermometer, Wind, Plus, Minus, X, Loader2,
  TreeDeciduous, Gem, Crown, Eye, Crosshair, Share2, Shield, ClipboardList
} from 'lucide-react';
import axios from 'axios';
import PinnablePanel from './PinnablePanel';
import { ShareBionicButton } from './ui/ShareBionicButton';

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

// === GAUGE COMPONENT (from ULTRA) ===
const Gauge = ({ value, max = 100, label, color = BIONIC.orange }) => {
  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const pct = Math.min(value / max, 1);
  const offset = circumference * (1 - pct * 0.75);
  return (
    <div className="flex flex-col items-center" data-testid="supra-gauge">
      <svg viewBox="0 0 140 140" className="w-28 h-28">
        <circle cx="70" cy="70" r={radius} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="8"
          strokeDasharray={`${circumference * 0.75} ${circumference * 0.25}`} strokeLinecap="round"
          transform="rotate(135 70 70)" />
        <circle cx="70" cy="70" r={radius} fill="none" stroke={color} strokeWidth="8"
          strokeDasharray={`${circumference * 0.75} ${circumference * 0.25}`} strokeDashoffset={offset}
          strokeLinecap="round" transform="rotate(135 70 70)" style={{ transition: 'stroke-dashoffset 0.8s ease' }} />
      </svg>
      <div className="absolute flex flex-col items-center justify-center" style={{ marginTop: '28px' }}>
        <span className="text-2xl font-black tabular-nums" style={{ color }}>{Math.round(value)}</span>
        <span className="text-[10px] text-gray-400 uppercase tracking-wider">{label}</span>
      </div>
    </div>
  );
};

// === INFO CARD — Dashboard-aligned (BCE-4X Phase 2.9) ===
const InfoCard = ({ icon, title, items, color = BIONIC.blue }) => (
  <div className="rounded-xl border p-4" style={{ backgroundColor: 'rgb(30 41 59)', borderColor: 'rgb(51 65 85)' }} data-testid={`info-card-${title.toLowerCase()}`}>
    <div className="flex items-center gap-2 mb-3">
      <span style={{ color }}>{icon}</span>
      <span className="text-sm font-semibold text-white">{title}</span>
    </div>
    <div className="space-y-2">
      {items.map((item, i) => (
        <div key={i} className="flex justify-between text-sm">
          <span className="text-slate-400">{item.label}</span>
          <span className="font-semibold text-slate-200">{item.value || '—'}</span>
        </div>
      ))}
    </div>
  </div>
);

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

// === UI COMPONENTS — Dashboard-aligned (BCE-4X Phase 2.9 typographie verrouillée) ===
const Card = ({ children, testId, className = '' }) => (
  <div className={`rounded-xl border p-5 ${className}`}
    style={{ backgroundColor: 'rgb(30 41 59)', borderColor: 'rgb(51 65 85)', boxShadow: '0 1px 8px rgba(0,0,0,0.2)' }}
    data-testid={testId}>
    {children}
  </div>
);

const CollapsibleSection = ({ icon: Icon, title, color, badge, children, defaultOpen = true, testId }) => {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="rounded-xl border p-5" style={{ backgroundColor: 'rgb(30 41 59)', borderColor: 'rgb(51 65 85)' }} data-testid={testId}>
      <button onClick={() => setOpen(v => !v)} className="w-full flex items-center justify-between cursor-pointer">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${color}15` }}>
            <Icon className="h-4 w-4" style={{ color }} />
          </div>
          <span className="text-sm font-semibold text-white uppercase tracking-wider">{title}</span>
        </div>
        <div className="flex items-center gap-2">
          {badge && <span className="text-xs font-semibold px-2.5 py-1 rounded-lg" style={{ backgroundColor: `${color}18`, color }}>{badge}</span>}
          {open ? <ChevronUp className="h-4 w-4 text-slate-500" /> : <ChevronDown className="h-4 w-4 text-slate-500" />}
        </div>
      </button>
      {open && <div className="mt-4">{children}</div>}
    </div>
  );
};

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
const NutritionPointDetailPanel = ({ nutritionPoint, onClose }) => {
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

  const np = nutritionPoint;
  const species = np?.species || 'chevreuil';
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
      const [supraRes, ultraRes, ficheRes] = await Promise.allSettled([
        axios.post(`${API}/api/v6/nutrition-intelligence/supra-panel`, {
          species, season, soil_type: soilType, substrate: 'bois_mou',
        }),
        axios.post(`${API}/api/v1/saline/analyze`, {
          lat: parseFloat(lat), lng: parseFloat(lng), species, sex: 'male', age: 'adult',
          month, season: seasonMap[month] || season,
        }),
        axios.get(`${API}/api/v1/salines-ultime/fiche?lat=${parseFloat(lat)}&lng=${parseFloat(lng)}&species=${species}&season=${seasonMap[month] || season}`),
      ]);
      if (supraRes.status === 'fulfilled') setSupraData(supraRes.value.data);
      if (ultraRes.status === 'fulfilled') setUltraData(ultraRes.value.data);
      if (ficheRes.status === 'fulfilled') setFicheData(ficheRes.value.data);
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
        {/* TABS — Dashboard-aligned + PARTAGER */}
        <div className="flex items-center gap-2 px-5 pt-4 pb-3 border-b flex-shrink-0" style={{ borderColor: 'rgb(51 65 85)' }} data-testid="supra-tabs">
          {TABS.map(tab => {
            const active = activeTab === tab.id;
            const Icon = tab.icon;
            const isOrder = tab.id === 'commandez';
            const activeColor = isOrder ? SUPRA_CMD_COLOR : gc;
            return (
              <button key={tab.id} data-testid={`supra-tab-${tab.id}`}
                onClick={() => setActiveTab(tab.id)}
                className="flex items-center gap-2 h-10 px-4 rounded-lg text-xs font-bold uppercase tracking-wider transition-all duration-150 relative"
                style={{ backgroundColor: active ? `${activeColor}18` : 'transparent', color: active ? activeColor : '#6b7280', border: active ? `2px solid ${activeColor}50` : '2px solid transparent' }}>
                <Icon className="h-4 w-4" />
                {tab.label}
                {isOrder && cartCount > 0 && (
                  <span className="absolute -top-1.5 -right-1.5 w-4 h-4 rounded-full text-[9px] font-black flex items-center justify-center" style={{ backgroundColor: SUPRA_CMD_COLOR, color: '#000' }}>{cartCount}</span>
                )}
              </button>
            );
          })}
          <div className="ml-auto flex-shrink-0">
            <ShareBionicButton />
          </div>
        </div>

        {/* CONTENT — BCE-4X Phase 2.9: ZERO scroll interne, PinnablePanel gere le scroll */}
        <div className="flex-1 p-5" data-testid="supra-v2-content-area">
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
              ultraScore={ultraScore} ultraDeficits={ultraDeficits} species={species} season={season} />
          )}
          {!loading && activeTab === 'fiche' && (
            <FicheTab ficheData={ficheData} species={species} season={season} lat={lat} lng={lng} np={np} />
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
// TAB: ANALYSE — Score + Gauge + 7 Engines + Narration
// ============================================================
const AnalyseTab = ({ score, recipe, recommendations, evidence, costs, comparison, ecozone, energyProtein, terrainSolutions, gc, np, engines, ultraScore, ultraDeficits, species, season }) => {
  const needColor = (level) => {
    if (level === 'EXTREME' || level === 'CRITIQUE') return BIONIC.red;
    if (level === 'TRES ELEVE' || level === 'ELEVE') return BIONIC.orange;
    if (level === 'MODERE') return BIONIC.yellow;
    return BIONIC.green;
  };
  const physioText = PHYSIOLOGY_DATA[species]?.[season] || PHYSIOLOGY_DATA.chevreuil?.printemps;
  const behaviorText = MALE_BEHAVIOR[species]?.[season] || MALE_BEHAVIOR.chevreuil?.printemps;
  const ratingColor = { premium: BIONIC.amber, optimal: BIONIC.green, adequat: BIONIC.blue, insuffisant: BIONIC.red }[ultraScore.rating] || BIONIC.blue;

  return (
    <div className="space-y-6" data-testid="supra-analyse-tab">
      {/* ROW 1: Score SUPRA + Gauge ULTRA */}
      <div className="grid grid-cols-2 gap-5">
        <Card testId="supra-score-card">
          <div className="flex items-center gap-5">
            <div className="w-[76px] h-[76px] rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: `linear-gradient(135deg, ${gc}22, ${gc}08)`, border: `2.5px solid ${gc}` }}>
              <span className="text-[28px] font-black" style={{ color: gc }}>{score.score_global}</span>
            </div>
            <div>
              <div className="text-xl font-black text-white leading-tight">Score SUPRA</div>
              <div className="text-sm font-bold px-3 py-1.5 rounded-lg inline-block mt-1.5" style={{ backgroundColor: `${gc}18`, color: gc }}>{score.grade}</div>
              <div className="flex gap-3 mt-2 text-sm">
                <span style={{ color: BIONIC.green }}>{score.zones_resume?.vert} vert</span>
                <span style={{ color: BIONIC.orange }}>{score.zones_resume?.jaune} jaune</span>
                <span style={{ color: BIONIC.red }}>{score.zones_resume?.rouge} rouge</span>
              </div>
            </div>
          </div>
        </Card>
        <Card testId="ultra-gauge-card">
          <div className="flex items-center justify-center gap-5">
            <div className="relative">
              <Gauge value={ultraScore.global_score || score.score_global || 0} label="ULTRA" color={ratingColor} />
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-400">7 Moteurs</div>
              <div className="text-base font-bold mt-1.5" style={{ color: ratingColor }}>
                {(ultraScore.rating || 'N/A').toUpperCase()}
              </div>
              {ultraDeficits.total_critical > 0 && (
                <div className="text-xs mt-1.5 text-red-400">{ultraDeficits.total_critical} carences critiques</div>
              )}
            </div>
          </div>
        </Card>
      </div>

      {/* ROW 2: Info Cards — 4 moteurs ULTRA */}
      {(engines.soil || engines.metabolism || engines.vegetation || engines.hydrology) && (
        <div className="grid grid-cols-2 gap-3">
          {engines.soil && (
            <InfoCard icon={<Mountain size={18} />} title="Sol" color={BIONIC.amber} items={[
              { label: 'Type', value: engines.soil.soil_type },
              { label: 'pH', value: engines.soil.pH },
              { label: 'Qualite', value: `${engines.soil.quality_index || 0}/100` },
            ]} />
          )}
          {engines.metabolism && (
            <InfoCard icon={<Activity size={18} />} title="Metabolisme" color={BIONIC.orange} items={[
              { label: 'Phase', value: (engines.metabolism.metabolic_phase || '').replace(/_/g, ' ') },
              { label: 'Energie', value: `x${engines.metabolism.energy_demand_factor || 0}` },
              { label: 'Activite', value: engines.metabolism.activity_level },
            ]} />
          )}
          {engines.vegetation && (
            <InfoCard icon={<Leaf size={18} />} title="Vegetation" color={BIONIC.green} items={[
              { label: 'Phase', value: engines.vegetation.phenophase },
              { label: 'Couvert', value: `${engines.vegetation.couvert_pct || 0}%` },
              { label: 'Fourrage', value: `${((engines.vegetation.avg_forage_quality || 0) * 100).toFixed(0)}%` },
            ]} />
          )}
          {engines.hydrology && (
            <InfoCard icon={<Droplets size={18} />} title="Hydrologie" color={BIONIC.blue} items={[
              { label: 'Drainage', value: engines.hydrology.drainage },
              { label: 'Lessivage', value: engines.hydrology.leaching_risk },
              { label: 'Dist. eau', value: `${engines.hydrology.distance_eau_m || 0}m` },
            ]} />
          )}
        </div>
      )}

      {/* Mineraux — barres Dashboard-aligned */}
      <Card testId="supra-minerals-card">
        <div className="flex items-center gap-2 mb-4">
          <FlaskConical className="h-5 w-5" style={{ color: '#f5a623' }} />
          <span className="text-lg font-bold text-white">Mineraux</span>
        </div>
        <div className="space-y-2.5">
          {Object.entries(score.scores_par_mineral || {}).map(([key, m]) => (
            <div key={key} className="flex items-center gap-3" data-testid={`supra-mineral-${key}`}>
              <span className="text-sm text-slate-300 w-20 flex-shrink-0">{m.name}</span>
              <div className="flex-1 h-2 rounded-full overflow-hidden" style={{ backgroundColor: 'rgba(255,255,255,0.08)' }}>
                <div className="h-full rounded-full transition-all duration-500" style={{ width: `${m.score}%`, backgroundColor: zoneColor(m.zone) }} />
              </div>
              <span className="text-sm font-bold w-8 text-right tabular-nums" style={{ color: zoneColor(m.zone) }}>{m.score}</span>
            </div>
          ))}
        </div>
      </Card>

      {/* SUPRA PREMIUM — Physiologie minerale — Dashboard-aligned */}
      <CollapsibleSection icon={Crown} title="Physiologie minerale" color={BIONIC.purple} badge={`${species} / ${season}`} testId="supra-physiology">
        <p className="text-sm text-slate-300 leading-relaxed">{physioText}</p>
      </CollapsibleSection>

      {/* SUPRA PREMIUM — Influence du support */}
      <CollapsibleSection icon={TreeDeciduous} title="Influence du support" color={BIONIC.green} badge="Hierarchie" defaultOpen={false} testId="supra-support">
        <div className="space-y-3">
          {SUPPORT_HIERARCHY.map((s, i) => (
            <div key={i} className="flex items-center gap-4 py-2.5 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
              <div className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0" style={{ backgroundColor: `${s.color}15`, border: `2px solid ${s.color}` }}>
                <span className="text-sm font-black" style={{ color: s.color }}>{s.score}</span>
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-base font-bold text-white">{s.name}</div>
                <div className="text-sm text-gray-500">{s.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </CollapsibleSection>

      {/* SUPRA PREMIUM — Comportement des males — Dashboard-aligned */}
      {behaviorText && (
        <CollapsibleSection icon={Eye} title="Comportement des males" color={BIONIC.cyan} badge={season} defaultOpen={false} testId="supra-behavior">
          <p className="text-sm text-slate-300 leading-relaxed">{behaviorText}</p>
        </CollapsibleSection>
      )}

      {/* Besoins nutritionnels */}
      {energyProtein && (
        <Card testId="supra-energy-protein-card">
          <div className="flex items-center gap-3 mb-4">
            <Zap className="h-6 w-6" style={{ color: BIONIC.orange }} />
            <span className="text-xl font-bold text-white">Besoins nutritionnels</span>
          </div>
          <div className="text-base text-gray-300 mb-4">{energyProtein.phase}</div>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="rounded-lg p-4" style={{ backgroundColor: 'rgba(255,255,255,0.04)', borderLeft: `3px solid ${needColor(energyProtein.energy_need)}` }}>
              <div className="text-sm text-gray-400 mb-1.5">Energie</div>
              <div className="text-lg font-bold" style={{ color: needColor(energyProtein.energy_need) }}>{energyProtein.energy_need}</div>
            </div>
            <div className="rounded-lg p-4" style={{ backgroundColor: 'rgba(255,255,255,0.04)', borderLeft: `3px solid ${needColor(energyProtein.protein_need)}` }}>
              <div className="text-sm text-gray-400 mb-1.5">Proteines</div>
              <div className="text-lg font-bold" style={{ color: needColor(energyProtein.protein_need) }}>{energyProtein.protein_need}</div>
            </div>
          </div>
        </Card>
      )}

      {/* Ecozone */}
      {ecozone && (
        <Card testId="supra-ecozone-card">
          <div className="flex items-center gap-3 mb-4">
            <Leaf className="h-6 w-6" style={{ color: BIONIC.green }} />
            <span className="text-xl font-bold text-white">Zone ecologique</span>
          </div>
          <div className="text-lg text-gray-300 mb-2">{ecozone.nom_commun}</div>
          <div className="text-base text-gray-400 leading-relaxed">{ecozone.habitat_principal}</div>
        </Card>
      )}

      {/* Recette */}
      {recipe && (
        <Card testId="supra-recipe-card">
          <div className="flex items-center gap-3 mb-4">
            <BookOpen className="h-6 w-6" style={{ color: BIONIC.green }} />
            <span className="text-xl font-bold text-white">Recette</span>
          </div>
          <div className="space-y-3">
            {recipe.ingredients_cles?.slice(0, 5).map((ing, i) => (
              <div key={i} className="flex items-center justify-between py-2.5 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
                <div>
                  <span className="text-base text-white">{ing.mineral}</span>
                  <span className="text-sm text-gray-400 ml-3">{ing.product}</span>
                </div>
                <span className="text-xs font-bold px-3 py-1 rounded" style={{ backgroundColor: `${priorityColor(ing.priority)}15`, color: priorityColor(ing.priority) }}>{ing.priority}</span>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Couts — collapsible */}
      {costs && (
        <CollapsibleSection icon={DollarSign} title="Couts" color={BIONIC.orange} defaultOpen={false} testId="supra-costs">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="rounded-lg p-4" style={{ backgroundColor: 'rgba(255,255,255,0.04)' }}>
              <div className="text-sm text-gray-400 mb-2">Initial</div>
              <div className="text-xl font-bold text-white">{costs.initial_cost_cad}$</div>
            </div>
            <div className="rounded-lg p-4" style={{ backgroundColor: 'rgba(255,255,255,0.04)' }}>
              <div className="text-sm text-gray-400 mb-2">Annuel</div>
              <div className="text-xl font-bold" style={{ color: BIONIC.orange }}>{costs.annual_cost_cad}$</div>
            </div>
            <div className="rounded-lg p-4" style={{ backgroundColor: 'rgba(255,255,255,0.04)' }}>
              <div className="text-sm text-gray-400 mb-2">Par visite</div>
              <div className="text-xl font-bold text-white">{costs.cost_per_visit_cad}$</div>
            </div>
          </div>
        </CollapsibleSection>
      )}

      {/* Preuves scientifiques */}
      {evidence.length > 0 && (
        <CollapsibleSection icon={FileText} title="Preuves scientifiques" color={BIONIC.purple} badge={`${evidence.length} refs`} defaultOpen={false} testId="supra-evidence">
          <div className="space-y-3">
            {evidence.slice(0, 4).map((ref, i) => (
              <div key={i} className="rounded-lg p-4" style={{ backgroundColor: 'rgba(156,39,176,0.06)', borderLeft: `3px solid ${BIONIC.purple}` }}>
                <div className="flex items-start justify-between gap-2">
                  <span className="text-base font-bold text-white leading-snug">{ref.titre}</span>
                  <a href={ref.doi_ou_url} target="_blank" rel="noopener noreferrer" className="flex-shrink-0"><ExternalLink className="h-4 w-4 text-purple-400" /></a>
                </div>
                <span className="text-sm text-gray-400 block mt-1.5">{ref.auteurs}, {ref.annee}</span>
              </div>
            ))}
          </div>
        </CollapsibleSection>
      )}
    </div>
  );
};

// ============================================================
// TAB: INTELLIGENCE — Produits avec match_score
// ============================================================
const IntelligenceTab = ({ products, gc, compareIds, toggleCompare, addToCart, cartLoading }) => (
  <div className="space-y-4" data-testid="supra-intelligence-tab">
    <div className="text-[15px] text-gray-300 mb-3">Score d'adequation — {products.total} produits</div>
    <div className="space-y-2.5">
      {products.products?.map((p) => {
        const sc = p.score_global >= 85 ? BIONIC.green : p.score_global >= 70 ? BIONIC.yellow : p.score_global >= 50 ? BIONIC.orange : BIONIC.red;
        const isCompared = compareIds.includes(p.product_id);
        return (
          <Card key={p.product_id} testId={`product-${p.product_id}`}>
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: `linear-gradient(135deg, ${sc}22, ${sc}08)`, border: `2px solid ${sc}` }}>
                <span className="text-[18px] font-black" style={{ color: sc }}>{p.score_global}</span>
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-[15px] font-bold text-white truncate">{p.name}</div>
                <div className="text-[12px] text-gray-400 mt-0.5">{p.type} | {p.price_cad}$ | {p.weight_kg}kg</div>
                <div className="flex gap-1 mt-1 flex-wrap">
                  {p.optimal_for?.map((tag, j) => (
                    <span key={j} className="text-[10px] px-1.5 py-0.5 rounded" style={{ backgroundColor: `${BIONIC.green}15`, color: BIONIC.green }}>{tag}</span>
                  ))}
                </div>
              </div>
              <div className="flex flex-col gap-1.5 flex-shrink-0">
                <div className="grid grid-cols-3 gap-1 text-center">
                  <div><div className="text-[10px] text-gray-500">Esp</div><div className="text-[13px] font-bold" style={{ color: p.score_species >= 85 ? BIONIC.green : BIONIC.orange }}>{p.score_species}%</div></div>
                  <div><div className="text-[10px] text-gray-500">Sai</div><div className="text-[13px] font-bold" style={{ color: p.score_season >= 85 ? BIONIC.green : BIONIC.orange }}>{p.score_season}%</div></div>
                  <div><div className="text-[10px] text-gray-500">Sol</div><div className="text-[13px] font-bold" style={{ color: p.score_soil >= 85 ? BIONIC.green : BIONIC.orange }}>{p.score_soil}%</div></div>
                </div>
                <div className="flex gap-1">
                  <button onClick={() => toggleCompare(p.product_id)}
                    className="text-[11px] font-bold px-2 py-1 rounded-lg transition-all"
                    style={{ backgroundColor: isCompared ? `${BIONIC.blue}20` : 'rgba(255,255,255,0.05)', color: isCompared ? BIONIC.blue : '#9ca3af' }}
                    data-testid={`compare-toggle-${p.product_id}`}>
                    {isCompared ? 'Retire' : 'Comp.'}
                  </button>
                  <SupraButton size="sm" onClick={() => addToCart(p.product_id)} disabled={cartLoading} testId={`add-cart-${p.product_id}`}>
                    <ShoppingCart className="h-3 w-3" /> CMD
                  </SupraButton>
                </div>
              </div>
            </div>
          </Card>
        );
      })}
    </div>
  </div>
);

// ============================================================
// TAB: FICHE — SALINES ULTIME (5 Scores + 20 Sources + Guides)
// ============================================================
const FICHE_SCORES = {
  logistique: { label: 'Score Logistique', icon: MapPin, color: '#3b82f6', desc: 'Accessibilite, maintenance, infrastructure, securite' },
  gros_males: { label: 'Score Gros Males', icon: TreeDeciduous, color: '#22c55e', desc: 'Corridors, couvert, eau, observations, tranquillite' },
  strategique: { label: 'Score Strategique', icon: Shield, color: '#f59e0b', desc: 'Position affuts, vent, visibilite, complementarite' },
  cout_roi: { label: 'Cout / ROI', icon: DollarSign, color: '#a855f7', desc: 'Cout mineraux, transport, temps, retour observation' },
  tcs: { label: 'TCS (Terrain Clarity)', icon: Mountain, color: '#ef4444', desc: 'Sentiers, lissage, penetrabilite, topographie' },
};

const FicheGradeTag = ({ grade, color }) => {
  const colors = { S: '#f59e0b', A: '#22c55e', B: '#3b82f6', C: '#f97316', D: '#ef4444', F: '#991b1b' };
  const c = colors[grade] || color || '#6b7280';
  return <span className="px-2 py-0.5 text-xs font-black rounded" style={{ backgroundColor: `${c}20`, color: c, border: `1px solid ${c}40` }}>{grade}</span>;
};

const FicheTab = ({ ficheData, species, season, lat, lng, np }) => {
  const [showSources, setShowSources] = useState(false);

  if (!ficheData) {
    return (
      <div className="text-center py-12 space-y-3" data-testid="fiche-loading">
        <Droplets className="h-8 w-8 text-cyan-400 mx-auto" />
        <div className="text-slate-300 text-base font-semibold">FICHE SALINE ULTIME</div>
        <div className="text-slate-500 text-sm">Chargement des 5 scores...</div>
      </div>
    );
  }

  const { global_score, scores, scientific_sources } = ficheData;

  return (
    <div className="space-y-4" data-testid="supra-fiche-tab">
      {/* Score Global */}
      <Card testId="fiche-global-score">
        <div className="flex items-center gap-4">
          <div className="w-[76px] h-[76px] rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: 'linear-gradient(135deg, #00BCD422, #00BCD408)', border: '2.5px solid #00BCD4' }}>
            <span className="text-[28px] font-black text-cyan-400">{global_score.score}</span>
          </div>
          <div>
            <div className="text-lg font-black text-white leading-tight">FICHE SALINE ULTIME</div>
            <div className="flex items-center gap-2 mt-1">
              <FicheGradeTag grade={global_score.grade} color="#00BCD4" />
              <span className="text-xs text-slate-400">5 scores | 20 sources | BCE-4X</span>
            </div>
            <div className="text-xs text-slate-500 mt-1">{species} | {season} | {np?.id || `${lat}, ${lng}`}</div>
          </div>
        </div>
      </Card>

      {/* 5 Score Cards — Vertical */}
      {Object.entries(scores).map(([key, data]) => {
        const config = FICHE_SCORES[key];
        if (!config) return null;
        const Icon = config.icon;
        return (
          <Card key={key} testId={`fiche-score-${key}`}>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${config.color}15` }}>
                  <Icon className="h-4 w-4" style={{ color: config.color }} />
                </div>
                <div>
                  <span className="text-sm font-bold text-white">{config.label}</span>
                  <div className="text-[10px] text-slate-500">{config.desc}</div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-black text-white">{data.score}</span>
                <FicheGradeTag grade={data.grade} color={config.color} />
              </div>
            </div>
            {/* Progress bar */}
            <div className="w-full h-2 rounded-full mb-3" style={{ backgroundColor: 'rgba(255,255,255,0.08)' }}>
              <div className="h-2 rounded-full transition-all duration-700" style={{ width: `${data.score}%`, backgroundColor: config.color }} />
            </div>
            {/* Components grid */}
            <div className="grid grid-cols-2 gap-x-4 gap-y-1.5">
              {Object.entries(data.components || {}).map(([ck, cv]) => (
                <div key={ck} className="flex items-center justify-between text-xs py-0.5">
                  <span className="text-slate-500 truncate">{ck.replace(/_/g, ' ')}</span>
                  <span className="text-slate-200 font-semibold ml-2">{cv.value}</span>
                </div>
              ))}
            </div>
            {/* Sources for this score */}
            {data.sources && (
              <div className="flex flex-wrap gap-1 mt-2 pt-2 border-t" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
                {data.sources.map((s, i) => (
                  <span key={i} className="text-[9px] px-1.5 py-0.5 rounded" style={{ backgroundColor: `${config.color}10`, color: config.color }}>{s}</span>
                ))}
              </div>
            )}
          </Card>
        );
      })}

      {/* Guide SUPRA Descriptif — Plan Gros Males */}
      <CollapsibleSection icon={TreeDeciduous} title="Plan Gros Males" color={BIONIC.green} badge="GUIDE SUPRA" testId="fiche-plan-males">
        <div className="space-y-2 text-sm text-slate-300">
          <p>Positionnez la saline a proximite des corridors de deplacement identifies par les donnees telemetriques et les observations historiques.</p>
          <p>Les gros males preferent les zones de transition foret-clairiere avec couvert lateral superieur a 60%. Maintenez un acces discret a au moins 150m de l'affut principal.</p>
          <p>Frequence d'entretien recommandee: bi-mensuelle en pre-rut, hebdomadaire pendant le rut actif.</p>
        </div>
      </CollapsibleSection>

      {/* Guide SUPRA — Logistique */}
      <CollapsibleSection icon={MapPin} title="Guide Logistique" color={BIONIC.blue} badge="GUIDE SUPRA" defaultOpen={false} testId="fiche-guide-logistique">
        <div className="space-y-2 text-sm text-slate-300">
          <p>Evaluez l'accessibilite vehiculaire: les chemins forestiers principaux doivent permettre le transport de mineraux (sacs 20-25kg). Distance maximale de portage recommandee: 200m.</p>
          <p>Prevoyez un budget annuel de 150-250$ pour le renouvellement des mineraux selon la taille du site et la frequentation.</p>
        </div>
      </CollapsibleSection>

      {/* Guide SUPRA — ROI */}
      <CollapsibleSection icon={DollarSign} title="Analyse Cout / ROI" color={BIONIC.purple} badge="GUIDE SUPRA" defaultOpen={false} testId="fiche-guide-roi">
        <div className="space-y-2 text-sm text-slate-300">
          <p>Le retour sur investissement d'une saline active se mesure en nombre d'observations qualitatives par saison. Objectif: minimum 15 observations positives par saison active.</p>
          <p>Le cout par observation diminue avec le temps — une saline mature (2+ saisons) reduit le cout/observation de 40-60%.</p>
        </div>
      </CollapsibleSection>

      {/* 20 Sources Scientifiques */}
      <Card testId="fiche-sources-card">
        <button onClick={() => setShowSources(!showSources)}
          className="w-full flex items-center justify-between cursor-pointer"
          data-testid="fiche-toggle-sources">
          <div className="flex items-center gap-2">
            <BookOpen className="h-4 w-4 text-cyan-400" />
            <span className="text-sm font-bold text-white">20 Sources Scientifiques</span>
          </div>
          {showSources ? <ChevronUp className="h-4 w-4 text-slate-500" /> : <ChevronDown className="h-4 w-4 text-slate-500" />}
        </button>
        {showSources && (
          <div className="mt-3 space-y-1">
            {(scientific_sources || []).map((src) => (
              <div key={src.id} className="flex items-start gap-2 py-1.5 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
                <span className="text-[10px] font-bold text-cyan-500 w-5 flex-shrink-0">[{src.id}]</span>
                <div className="min-w-0">
                  <span className="text-xs text-white font-medium">{src.ref}</span>
                  <span className="text-[10px] text-slate-500 block">{src.title}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Integrations badges */}
      <div className="flex flex-wrap gap-1.5 pt-1">
        <span className="text-[10px] px-2 py-1 rounded-lg font-bold" style={{ backgroundColor: '#00BCD415', color: '#00BCD4', border: '1px solid #00BCD430' }}>SUPRA/V6</span>
        <span className="text-[10px] px-2 py-1 rounded-lg font-bold" style={{ backgroundColor: '#22c55e15', color: '#22c55e', border: '1px solid #22c55e30' }}>ACCESS v7</span>
        <span className="text-[10px] px-2 py-1 rounded-lg font-bold" style={{ backgroundColor: '#34d39915', color: '#34d399', border: '1px solid #34d39930' }}>PARTAGER</span>
        <span className="text-[10px] px-2 py-1 rounded-lg font-bold" style={{ backgroundColor: '#f5a62315', color: '#f5a623', border: '1px solid #f5a62330' }}>ADMIN Premium</span>
      </div>
    </div>
  );
};

// ============================================================
// TAB: COMPAREZ
// ============================================================
const ComparezTab = ({ products, compareIds, gc, toggleCompare }) => {
  const compared = (products.products || []).filter(p => compareIds.includes(p.product_id));
  if (compared.length === 0) {
    return (
      <div className="text-center py-12" data-testid="supra-comparez-tab">
        <Scale className="h-10 w-10 text-gray-500 mx-auto mb-4" />
        <div className="text-[16px] text-gray-300 font-semibold">Aucun produit selectionne</div>
        <div className="text-[13px] text-gray-500 mt-2">Allez dans l'onglet INTELLIGENCE et selectionnez 2-4 produits</div>
      </div>
    );
  }
  const best = compared.reduce((a, b) => a.score_global > b.score_global ? a : b);
  return (
    <div data-testid="supra-comparez-tab">
      <div className="text-[15px] text-gray-300 mb-4">{compared.length} produit(s) compares</div>
      <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${Math.min(compared.length, 2)}, 1fr)` }}>
        {compared.map(p => {
          const isBest = p.product_id === best.product_id;
          const sc = p.score_global >= 85 ? BIONIC.green : p.score_global >= 70 ? BIONIC.yellow : p.score_global >= 50 ? BIONIC.orange : BIONIC.red;
          return (
            <Card key={p.product_id} testId={`compare-card-${p.product_id}`} className={isBest ? 'ring-1 ring-green-500/30' : ''}>
              {isBest && <div className="text-[12px] font-bold text-center mb-2" style={{ color: BIONIC.green }}>MEILLEUR CHOIX</div>}
              <div className="text-center mb-3">
                <div className="w-14 h-14 rounded-xl flex items-center justify-center mx-auto" style={{ background: `linear-gradient(135deg, ${sc}22, ${sc}08)`, border: `2px solid ${sc}` }}>
                  <span className="text-[20px] font-black" style={{ color: sc }}>{p.score_global}</span>
                </div>
                <div className="text-[14px] font-bold text-white mt-2">{p.name}</div>
              </div>
              <div className="space-y-1.5">
                {[
                  { label: 'Espece', val: `${p.score_species}%` }, { label: 'Saison', val: `${p.score_season}%` },
                  { label: 'Sol', val: `${p.score_soil}%` }, { label: 'Prix', val: `${p.price_cad}$` },
                ].map((row, i) => (
                  <div key={i} className="flex justify-between py-1 border-b text-[12px]" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
                    <span className="text-gray-400">{row.label}</span>
                    <span className="font-bold text-white">{row.val}</span>
                  </div>
                ))}
              </div>
              <button onClick={() => toggleCompare(p.product_id)} className="w-full mt-2 text-[12px] font-bold py-1.5 rounded-lg" style={{ backgroundColor: `${BIONIC.red}15`, color: BIONIC.red }}>Retirer</button>
            </Card>
          );
        })}
      </div>
    </div>
  );
};

// ============================================================
// TAB: COMMANDEZ — Panier Stripe REEL + Checkout
// ============================================================
const CommandezTab = ({ order, products, recipe, gc, cart, addToCart, cartLoading, handleCheckout, checkoutLoading, fetchCart }) => (
  <div className="space-y-5" data-testid="supra-commandez-tab">
    {/* Pack complet (SUPRA recette) */}
    {order && (
      <Card testId="order-pack-card">
        <div className="flex items-center gap-3 mb-4">
          <Package className="h-5 w-5" style={{ color: SUPRA_CMD_COLOR }} />
          <span className="text-[18px] font-bold text-white">Recette complete</span>
          <span className="text-[16px] font-bold ml-auto" style={{ color: SUPRA_CMD_COLOR }}>{order.summary?.cost_initial_cad}$</span>
        </div>
        <div className="space-y-0">
          {order.items?.map((item, i) => (
            <div key={i} className="flex items-center gap-3 py-2.5 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
              <div className="flex-1 min-w-0">
                <div className="text-[14px] font-bold text-white truncate">{item.name}</div>
                <div className="text-[11px] text-gray-500">{item.brand} | {item.dosage} | Qte: {item.quantity}</div>
              </div>
              <span className="text-[13px] font-bold text-white w-14 text-right">{item.total_price_cad}$</span>
              <SupraButton size="sm" onClick={() => addToCart(item.product_id || `sal_00${i+1}`)} disabled={cartLoading} testId={`order-add-${i}`}>
                <Plus className="h-3 w-3" />
              </SupraButton>
            </div>
          ))}
        </div>
      </Card>
    )}

    {/* Produits individuels avec CMD reel */}
    <div className="text-[14px] font-bold text-gray-300 uppercase tracking-wider mb-2">Produits individuels</div>
    <div className="space-y-2">
      {products?.products?.slice(0, 8).map(p => {
        const sc = p.score_global >= 85 ? BIONIC.green : p.score_global >= 70 ? BIONIC.yellow : p.score_global >= 50 ? BIONIC.orange : BIONIC.red;
        return (
          <div key={p.product_id} className="flex items-center gap-3 px-4 py-2.5 rounded-xl border transition-all hover:border-[#FF980030]"
            style={{ backgroundColor: BIONIC.card, borderColor: BIONIC.cardBorder }} data-testid={`shop-product-${p.product_id}`}>
            <div className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: `${sc}12`, border: `2px solid ${sc}` }}>
              <span className="text-[13px] font-black" style={{ color: sc }}>{p.score_global}</span>
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-[13px] font-bold text-white truncate">{p.name}</div>
              <div className="text-[11px] text-gray-500">{p.type} | {p.weight_kg}kg</div>
            </div>
            <span className="text-[13px] font-bold text-white w-12 text-right">{p.price_cad}$</span>
            <SupraButton size="sm" onClick={() => addToCart(p.product_id)} disabled={cartLoading} testId={`shop-order-${p.product_id}`}>
              <ShoppingCart className="h-3 w-3" /> CMD
            </SupraButton>
          </div>
        );
      })}
    </div>

    {/* PANIER STRIPE REEL */}
    <Card testId="supra-cart-stripe">
      <div className="flex items-center gap-2.5 mb-4">
        <ShoppingCart className="h-5 w-5" style={{ color: SUPRA_CMD_COLOR }} />
        <span className="text-[18px] font-bold text-white">Panier</span>
        <span className="text-[13px] text-gray-400 ml-auto">{cart.item_count || 0} article(s)</span>
      </div>
      {cart.items?.length > 0 ? (
        <>
          <div className="space-y-2">
            {cart.items.map((item) => (
              <div key={item.item_id} className="flex items-center gap-3 py-2 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }} data-testid={`cart-item-${item.product_id}`}>
                <div className="flex-1 min-w-0">
                  <div className="text-[13px] font-semibold text-white truncate">{item.name}</div>
                  <div className="text-[11px] text-gray-500">{item.format} — {item.unit_price}$/u</div>
                </div>
                <span className="text-[12px] font-bold text-gray-300">x{item.quantity}</span>
                <span className="text-[13px] font-bold w-14 text-right" style={{ color: BIONIC.amber }}>{item.subtotal}$</span>
              </div>
            ))}
          </div>
          <div className="flex items-center justify-between mt-4 pt-3 border-t" style={{ borderColor: 'rgba(255,255,255,0.08)' }}>
            <span className="text-[14px] text-gray-400">Total</span>
            <span className="text-[20px] font-bold" style={{ color: BIONIC.amber }}>{cart.total}$ <span className="text-[11px] text-gray-500">CAD</span></span>
          </div>
          <SupraButton size="lg" onClick={handleCheckout} disabled={checkoutLoading} testId="supra-checkout-btn">
            {checkoutLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <ShoppingCart className="h-4 w-4" />}
            {checkoutLoading ? 'Traitement...' : 'Payer avec Stripe'}
            <ArrowRight className="h-4 w-4" />
          </SupraButton>
          <p className="text-[11px] text-gray-600 text-center mt-2">Paiement securise par Stripe</p>
        </>
      ) : (
        <div className="text-center py-6">
          <ShoppingCart className="h-8 w-8 text-gray-600 mx-auto mb-2" />
          <p className="text-[13px] text-gray-500">Votre panier est vide</p>
          <p className="text-[11px] text-gray-600 mt-1">Cliquez CMD pour ajouter des produits</p>
        </div>
      )}
    </Card>
  </div>
);

export default NutritionPointDetailPanel;

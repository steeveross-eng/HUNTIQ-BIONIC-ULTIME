import React, { useState, useEffect, useCallback } from 'react';
import {
  Droplets, FlaskConical, AlertTriangle,
  ShoppingCart,
  Scale, BarChart3,
  X,
  ClipboardList,
} from 'lucide-react';
import axios from 'axios';
import PinnablePanel from './PinnablePanel';
import { ShareBionicButton } from './ui/ShareBionicButton';
import AnalyseTab from './supra/AnalyseTab';
import FicheTab from './supra/FicheTab';
import IntelligenceTab from './supra/IntelligenceTab';
import ComparezTab from './supra/ComparezTab';
import CommandezTab from './supra/CommandezTab';

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

// === SESSION SALINE (Panier Stripe unifie — BCE-4X E03 fix) ===
const getSalineSession = () => {
  let sid = localStorage.getItem('saline_session_id');
  if (!sid || !/^sal_[a-z0-9]{8,16}$/.test(sid)) {
    sid = 'sal_' + Math.random().toString(36).substr(2, 12);
    localStorage.setItem('saline_session_id', sid);
  }
  return sid;
};

// === R3 COMPLETE: Composants UI externalisés → supra/constants.js ===

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

export default NutritionPointDetailPanel;

import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import "@/theme/bionic_theme.css";
import {
  FlaskConical, Beaker, ShoppingCart, ClipboardList, MapPin,
  Droplets, Leaf, Activity, Thermometer, ChevronRight, Plus,
  Minus, X, Loader2, AlertTriangle, CheckCircle, ArrowRight,
  Crosshair, Moon, Wind, Mountain, Package
} from "lucide-react";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const getSessionId = () => {
  let sid = localStorage.getItem("saline_session_id");
  if (!sid) {
    sid = "sal_" + Math.random().toString(36).substr(2, 12);
    localStorage.setItem("saline_session_id", sid);
  }
  return sid;
};

// === GAUGE COMPONENT ===
const Gauge = ({ value, max = 100, label, color = "var(--saline-gold)" }) => {
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const pct = Math.min(value / max, 1);
  const offset = circumference * (1 - pct * 0.75); // 270deg arc

  return (
    <div className="saline-gauge-container" data-testid={`gauge-${label}`}>
      <svg className="saline-gauge-svg" viewBox="0 0 160 160">
        <circle className="saline-gauge-track" cx="80" cy="80" r={radius}
          strokeDasharray={`${circumference * 0.75} ${circumference * 0.25}`} />
        <circle className="saline-gauge-fill" cx="80" cy="80" r={radius}
          stroke={color}
          strokeDasharray={`${circumference * 0.75} ${circumference * 0.25}`}
          strokeDashoffset={offset} />
      </svg>
      <div className="saline-gauge-value">
        <div className="saline-gauge-number" style={{ color }}>{Math.round(value)}</div>
        <div className="saline-gauge-label">{label}</div>
      </div>
    </div>
  );
};

// === BAR COMPONENT ===
const MineralBar = ({ mineral, coverage, status, deficitMg, needMg }) => {
  const colorMap = {
    critical: "var(--saline-red)",
    deficient: "var(--saline-orange)",
    marginal: "var(--saline-blue)",
    sufficient: "var(--saline-green)",
  };
  const color = colorMap[status] || "var(--saline-text-muted)";
  // For visualization: show deficit severity as inverse (how much supplementation needed)
  // 100% = fully covered, 0% = nothing covered
  // Use a scaled view: if coverage < 1%, show the deficit intensity instead
  const displayPct = coverage > 1 ? coverage : Math.max(2, Math.min(95, (deficitMg / Math.max(needMg, 1)) * 100));
  const isDeficit = coverage < 30;

  return (
    <div className="saline-bar-row" data-testid={`mineral-bar-${mineral}`}>
      <span className="saline-bar-label">{mineral}</span>
      <div className="saline-bar-track">
        <div className="saline-bar-fill" style={{ width: `${isDeficit ? displayPct : Math.min(coverage, 100)}%`, background: color }} />
      </div>
      <span className="saline-bar-value" style={{ color }}>
        {isDeficit ? `−${Math.round(deficitMg)}mg` : `${Math.round(coverage)}%`}
      </span>
    </div>
  );
};

// === SECTION: ANALYSE ===
const AnalyseSection = ({ data, loading }) => {
  if (loading) return <SectionSkeleton />;
  if (!data) return null;

  const { engines = {}, analysis = {} } = data;
  const score = analysis.intelligence_score || {};
  const deficits = analysis.adjusted_deficits || {};
  const minerals = deficits.minerals || {};
  const rawDeficiency = engines.deficiency?.coverage || {};
  const soil = engines.soil || {};
  const metabolism = engines.metabolism || {};
  const vegetation = engines.vegetation || {};
  const hydrology = engines.hydrology || {};

  const ratingColor = {
    premium: "var(--saline-gold)",
    optimal: "var(--saline-green)",
    adequat: "var(--saline-blue)",
    insuffisant: "var(--saline-red)",
  }[score.rating] || "var(--saline-text-muted)";

  return (
    <div className="space-y-4 p-4 md:p-6" data-testid="analyse-section">
      {/* Score global + composants */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="saline-card flex flex-col items-center justify-center py-6">
          <Gauge value={score.global_score || 0} label="Score Global" color={ratingColor} />
          <span className={`saline-score-badge ${score.rating || "adequat"} mt-3`}>
            {(score.rating || "N/A").toUpperCase()}
          </span>
        </div>

        <div className="saline-card md:col-span-2">
          <div className="saline-card-title">Composants du Score</div>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {score.components && Object.entries(score.components).map(([key, val]) => (
              <div key={key} className="text-center">
                <div className="text-xl font-bold" style={{ color: val >= 65 ? "var(--saline-green)" : val >= 45 ? "var(--saline-orange)" : "var(--saline-red)" }}>
                  {Math.round(val)}
                </div>
                <div className="text-xs text-neutral-500 mt-0.5">{key.replace(/_/g, " ")}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Carences minerales */}
      <div className="saline-card">
        <div className="saline-card-title flex items-center gap-2">
          <AlertTriangle size={14} className="text-amber-500" />
          Carences Minerales — {deficits.total_critical || 0} critiques, {deficits.total_deficient || 0} deficients
        </div>
        <div className="space-y-1">
          {Object.entries(minerals).map(([mineral, data]) => {
            const rawDef = rawDeficiency[mineral] || {};
            return (
              <MineralBar key={mineral} mineral={mineral}
                coverage={data.adjusted_coverage_pct || 0} status={data.status || "sufficient"}
                deficitMg={rawDef.deficit_mg || data.adjusted_deficit_mg || 0}
                needMg={rawDef.daily_need_mg || 1} />
            );
          })}
        </div>
      </div>

      {/* Info grid: sol, metabolisme, vegetation, hydrologie */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <InfoCard icon={<Mountain size={16} />} title="Sol" items={[
          { label: "Type", value: soil.soil_type },
          { label: "pH", value: soil.pH },
          { label: "Qualite", value: `${soil.quality_index || 0}/100` },
        ]} />
        <InfoCard icon={<Activity size={16} />} title="Metabolisme" items={[
          { label: "Phase", value: (metabolism.metabolic_phase || "").replace(/_/g, " ") },
          { label: "Energie", value: `x${metabolism.energy_demand_factor || 0}` },
          { label: "Activite", value: metabolism.activity_level },
        ]} />
        <InfoCard icon={<Leaf size={16} />} title="Vegetation" items={[
          { label: "Phase", value: vegetation.phenophase },
          { label: "Couvert", value: `${vegetation.couvert_pct || 0}%` },
          { label: "Fourrage", value: `${((vegetation.avg_forage_quality || 0) * 100).toFixed(0)}%` },
        ]} />
        <InfoCard icon={<Droplets size={16} />} title="Hydrologie" items={[
          { label: "Drainage", value: hydrology.drainage },
          { label: "Lessivage", value: hydrology.leaching_risk },
          { label: "Dist. eau", value: `${hydrology.distance_eau_m || 0}m` },
        ]} />
      </div>

      {/* Tips metaboliques */}
      {data.recommendations?.metabolic_tips?.length > 0 && (
        <div className="saline-card">
          <div className="saline-card-title flex items-center gap-2">
            <Moon size={14} className="text-blue-400" />
            Recommandations Metaboliques
          </div>
          <ul className="space-y-1.5">
            {data.recommendations.metabolic_tips.map((tip, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-neutral-300">
                <ChevronRight size={14} className="text-amber-500 mt-0.5 flex-shrink-0" />
                {tip}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

const InfoCard = ({ icon, title, items }) => (
  <div className="saline-card">
    <div className="saline-card-title flex items-center gap-1.5">{icon}{title}</div>
    <div className="space-y-1.5">
      {items.map((item, i) => (
        <div key={i} className="flex justify-between text-xs">
          <span className="text-neutral-500">{item.label}</span>
          <span className="font-semibold text-neutral-200">{item.value || "—"}</span>
        </div>
      ))}
    </div>
  </div>
);

// === SECTION: RECETTES ===
const RecettesSection = ({ data, loading }) => {
  if (loading) return <SectionSkeleton />;
  if (!data) return null;

  const recipe = data.recommendations?.custom_recipe || {};
  const components = recipe.components || [];

  return (
    <div className="space-y-4 p-4 md:p-6" data-testid="recettes-section">
      <div className="saline-card">
        <div className="saline-card-title flex items-center gap-2">
          <Beaker size={14} className="text-amber-500" />
          Recette Personnalisee — {recipe.species || "orignal"} / {(recipe.metabolic_phase || "").replace(/_/g, " ")}
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
          <div className="text-center p-2 rounded-lg" style={{ background: "var(--saline-gold-dim)" }}>
            <div className="text-lg font-bold text-amber-400">{recipe.total_components || 0}</div>
            <div className="text-xs text-neutral-500">Composants</div>
          </div>
          <div className="text-center p-2 rounded-lg" style={{ background: "var(--saline-green-dim)" }}>
            <div className="text-lg font-bold text-emerald-400">{recipe.base_carrier || "—"}</div>
            <div className="text-xs text-neutral-500">Base</div>
          </div>
          <div className="text-center p-2 rounded-lg" style={{ background: "var(--saline-blue-dim)" }}>
            <div className="text-lg font-bold text-blue-400">{recipe.format_recommande || "—"}</div>
            <div className="text-xs text-neutral-500">Format</div>
          </div>
          <div className="text-center p-2 rounded-lg" style={{ background: "var(--saline-orange-dim)" }}>
            <div className="text-lg font-bold text-orange-400">{recipe.renouvellement_jours || 0}j</div>
            <div className="text-xs text-neutral-500">Renouvellement</div>
          </div>
        </div>

        <div className="space-y-1.5">
          {components.map((comp, i) => (
            <div key={i} className={`saline-recipe-item ${comp.priority}`}>
              <div className="flex items-center gap-2">
                <span className="font-bold text-sm">{comp.mineral}</span>
                <span className="text-xs text-neutral-400">couverture {comp.coverage_before}%</span>
              </div>
              <span className="text-sm font-semibold">{comp.supplement_mg_per_kg} mg/kg</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// === SECTION: PRODUITS ===
const ProduitsSection = ({ products, loading, onAddToCart, cartLoading }) => {
  if (loading) return <SectionSkeleton />;

  return (
    <div className="space-y-4 p-4 md:p-6" data-testid="produits-section">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {products.map((product) => (
          <div key={product.id} className="saline-product-card" data-testid={`product-${product.id}`}>
            <div className="saline-product-header">
              <div className="flex items-center justify-between mb-2">
                <span className="saline-product-format">{product.product_format}</span>
                {product.match_score && (
                  <span className="text-xs font-semibold" style={{ color: "var(--saline-green)" }}>
                    Score: {product.match_score}
                  </span>
                )}
              </div>
              <h3 className="font-bold text-sm text-neutral-100 leading-tight">{product.name}</h3>
              <p className="text-xs text-neutral-500 mt-1">{product.description}</p>
            </div>
            <div className="saline-product-body">
              <div className="flex items-end justify-between">
                <div>
                  <span className="saline-product-price">${product.price}</span>
                  <span className="text-xs text-neutral-500 ml-1">CAD</span>
                </div>
                <button
                  className="saline-btn-gold text-xs py-2 px-3"
                  onClick={() => onAddToCart(product.id)}
                  disabled={cartLoading}
                  data-testid={`add-to-cart-${product.id}`}
                >
                  {cartLoading ? <Loader2 size={14} className="animate-spin" /> : <Plus size={14} />}
                  Ajouter
                </button>
              </div>
              {product.targets_addressed?.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {product.targets_addressed.map((t) => (
                    <span key={t} className="text-xs px-1.5 py-0.5 rounded" style={{ background: "var(--saline-red-dim)", color: "var(--saline-red)" }}>
                      {t}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// === SECTION: COMMANDE (CART + CHECKOUT) ===
const CommandeSection = ({ cart, loading, onQuantityChange, onRemove, onCheckout, checkoutLoading }) => {
  if (loading) return <SectionSkeleton />;

  return (
    <div className="space-y-4 p-4 md:p-6" data-testid="commande-section">
      {cart.items?.length > 0 ? (
        <>
          <div className="saline-card">
            <div className="saline-card-title flex items-center gap-2">
              <ShoppingCart size={14} className="text-amber-500" />
              Panier — {cart.item_count} article{cart.item_count > 1 ? "s" : ""}
            </div>
            <div className="space-y-3">
              {cart.items.map((item) => (
                <div key={item.item_id} className="flex items-center gap-3 py-2 border-b border-neutral-800 last:border-0" data-testid={`cart-item-${item.product_id}`}>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-semibold text-neutral-100 truncate">{item.name}</div>
                    <div className="text-xs text-neutral-500">{item.format} — {item.unit_price}$ / unite</div>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <button className="saline-btn-outline p-1" onClick={() => onQuantityChange(item.item_id, -1)}>
                      <Minus size={12} />
                    </button>
                    <span className="w-6 text-center text-sm font-bold">{item.quantity}</span>
                    <button className="saline-btn-outline p-1" onClick={() => onQuantityChange(item.item_id, 1)}>
                      <Plus size={12} />
                    </button>
                  </div>
                  <span className="text-sm font-bold text-amber-400 w-16 text-right">{item.subtotal}$</span>
                  <button className="text-neutral-600 hover:text-red-500 transition-colors" onClick={() => onRemove(item.item_id)}>
                    <X size={14} />
                  </button>
                </div>
              ))}
            </div>
          </div>

          <div className="saline-card">
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm text-neutral-400">Total</span>
              <span className="text-2xl font-bold text-amber-400">{cart.total}$ <span className="text-xs text-neutral-500">CAD</span></span>
            </div>
            <button
              className="saline-btn-gold w-full py-3 text-sm"
              onClick={onCheckout}
              disabled={checkoutLoading}
              data-testid="checkout-button"
            >
              {checkoutLoading ? (
                <><Loader2 size={16} className="animate-spin" /> Traitement...</>
              ) : (
                <>Commander maintenant <ArrowRight size={16} /></>
              )}
            </button>
            <p className="text-xs text-neutral-600 text-center mt-2">Paiement securise par Stripe</p>
          </div>
        </>
      ) : (
        <div className="saline-card text-center py-10">
          <ShoppingCart size={40} className="mx-auto mb-3 text-neutral-700" />
          <p className="text-sm text-neutral-500">Votre panier est vide</p>
          <p className="text-xs text-neutral-600 mt-1">Analysez un territoire et ajoutez des produits recommandes</p>
        </div>
      )}
    </div>
  );
};

// === SKELETON LOADER ===
const SectionSkeleton = () => (
  <div className="space-y-4 p-4 md:p-6">
    <div className="saline-skeleton h-48 w-full" />
    <div className="grid grid-cols-2 gap-3">
      <div className="saline-skeleton h-24" />
      <div className="saline-skeleton h-24" />
    </div>
    <div className="saline-skeleton h-32 w-full" />
  </div>
);

// === LOCATION INPUT ===
const LocationInput = ({ lat, lng, onLatChange, onLngChange, onAnalyze, loading, species, onSpeciesChange, month, onMonthChange }) => (
  <div className="flex flex-wrap items-end gap-3 px-4 md:px-6 py-3" style={{ background: "rgba(245,166,35,0.03)", borderBottom: "1px solid var(--saline-border)" }} data-testid="location-input">
    <div className="flex-1 min-w-[100px]">
      <label className="text-xs text-neutral-500 mb-1 block">Latitude</label>
      <input type="number" step="0.01" value={lat} onChange={e => onLatChange(e.target.value)}
        className="w-full bg-neutral-900 border border-neutral-800 rounded px-2.5 py-1.5 text-sm text-neutral-200 focus:border-amber-500 focus:outline-none" data-testid="input-lat" />
    </div>
    <div className="flex-1 min-w-[100px]">
      <label className="text-xs text-neutral-500 mb-1 block">Longitude</label>
      <input type="number" step="0.01" value={lng} onChange={e => onLngChange(e.target.value)}
        className="w-full bg-neutral-900 border border-neutral-800 rounded px-2.5 py-1.5 text-sm text-neutral-200 focus:border-amber-500 focus:outline-none" data-testid="input-lng" />
    </div>
    <div className="min-w-[100px]">
      <label className="text-xs text-neutral-500 mb-1 block">Espece</label>
      <select value={species} onChange={e => onSpeciesChange(e.target.value)}
        className="w-full bg-neutral-900 border border-neutral-800 rounded px-2.5 py-1.5 text-sm text-neutral-200 focus:border-amber-500 focus:outline-none" data-testid="select-species">
        <option value="orignal">Orignal</option>
        <option value="chevreuil">Chevreuil</option>
        <option value="ours_noir">Ours noir</option>
        <option value="dindon_sauvage">Dindon sauvage</option>
      </select>
    </div>
    <div className="min-w-[70px]">
      <label className="text-xs text-neutral-500 mb-1 block">Mois</label>
      <select value={month} onChange={e => onMonthChange(Number(e.target.value))}
        className="w-full bg-neutral-900 border border-neutral-800 rounded px-2.5 py-1.5 text-sm text-neutral-200 focus:border-amber-500 focus:outline-none" data-testid="select-month">
        {Array.from({length:12},(_,i) => i+1).map(m => (
          <option key={m} value={m}>{["Jan","Fev","Mar","Avr","Mai","Jun","Jul","Aou","Sep","Oct","Nov","Dec"][m-1]}</option>
        ))}
      </select>
    </div>
    <button className="saline-btn-gold py-1.5 px-4" onClick={onAnalyze} disabled={loading} data-testid="analyze-button">
      {loading ? <Loader2 size={16} className="animate-spin" /> : <Crosshair size={16} />}
      Analyser
    </button>
  </div>
);

// === MAIN PAGE ===
export default function SalineIntelligencePage() {
  const [activeTab, setActiveTab] = useState("analyse");
  const [lat, setLat] = useState("47.30");
  const [lng, setLng] = useState("-71.20");
  const [species, setSpecies] = useState("orignal");
  const [month, setMonth] = useState(10);
  const [analysisData, setAnalysisData] = useState(null);
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState({ items: [], item_count: 0, total: 0 });
  const [loading, setLoading] = useState(false);
  const [cartLoading, setCartLoading] = useState(false);
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const [cartCount, setCartCount] = useState(0);

  const seasonMap = { 1:"hiver",2:"hiver",3:"printemps",4:"printemps",5:"ete",6:"ete",7:"ete",8:"pre_rut",9:"pre_rut",10:"rut",11:"post_rut",12:"hiver" };

  const runAnalysis = useCallback(async () => {
    setLoading(true);
    try {
      const season = seasonMap[month] || "automne";
      const [analysisRes, productsRes] = await Promise.all([
        axios.post(`${API}/v1/saline/analyze`, {
          lat: parseFloat(lat), lng: parseFloat(lng), species, sex: "male", age: "adult", month, season,
        }),
        axios.get(`${API}/v1/saline/shop/recommend`, {
          params: { lat: parseFloat(lat), lng: parseFloat(lng), species, month, season },
        }),
      ]);
      setAnalysisData(analysisRes.data);
      setProducts(productsRes.data.recommended_products || []);
    } catch (err) {
      console.error("Analysis error:", err);
    } finally {
      setLoading(false);
    }
  }, [lat, lng, species, month]);

  const fetchCart = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/v1/saline/shop/cart/${getSessionId()}`);
      setCart(res.data);
      setCartCount(res.data.item_count || 0);
    } catch (err) {
      console.error("Cart fetch error:", err);
    }
  }, []);

  const addToCart = useCallback(async (productId) => {
    setCartLoading(true);
    try {
      await axios.post(`${API}/v1/saline/shop/cart/add`, {
        session_id: getSessionId(), product_id: productId, quantity: 1,
      });
      await fetchCart();
    } catch (err) {
      console.error("Add to cart error:", err);
    } finally {
      setCartLoading(false);
    }
  }, [fetchCart]);

  const handleCheckout = useCallback(async () => {
    setCheckoutLoading(true);
    try {
      const res = await axios.post(`${API}/v1/saline/shop/checkout`, {
        session_id: getSessionId(),
        user_id: "guest",
        origin_url: window.location.origin,
      });
      if (res.data.url) {
        window.location.href = res.data.url;
      }
    } catch (err) {
      console.error("Checkout error:", err);
    } finally {
      setCheckoutLoading(false);
    }
  }, []);

  useEffect(() => { fetchCart(); }, [fetchCart]);
  useEffect(() => { runAnalysis(); }, []);

  const tabs = [
    { id: "analyse", label: "Analyse", icon: <FlaskConical size={14} /> },
    { id: "recettes", label: "Recettes", icon: <Beaker size={14} /> },
    { id: "produits", label: "Produits", icon: <Package size={14} /> },
    { id: "commande", label: "Commande", icon: <ShoppingCart size={14} />, badge: cartCount },
  ];

  return (
    <div className="saline-page" data-testid="saline-intelligence-page">
      {/* HERO */}
      <div className="saline-hero">
        <div className="relative z-10 max-w-5xl mx-auto">
          <div className="flex items-center gap-3 mb-2">
            <FlaskConical size={28} style={{ color: "var(--saline-gold)" }} />
            <div>
              <h1 className="saline-hero-title">Saline Intelligence Ultra</h1>
              <p className="saline-hero-subtitle">Analyse scientifique multi-moteurs | 7 engines</p>
            </div>
          </div>
          {analysisData && (
            <div className="flex items-center gap-3 mt-3">
              <span className={`saline-score-badge ${analysisData.analysis?.intelligence_score?.rating || "adequat"}`}>
                <Activity size={14} />
                Score: {analysisData.analysis?.intelligence_score?.global_score || 0} — {(analysisData.analysis?.intelligence_score?.rating || "N/A").toUpperCase()}
              </span>
              <span className="text-xs text-neutral-600">
                <MapPin size={12} className="inline mr-1" />{lat}, {lng}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* LOCATION INPUT */}
      <LocationInput
        lat={lat} lng={lng} onLatChange={setLat} onLngChange={setLng}
        onAnalyze={runAnalysis} loading={loading}
        species={species} onSpeciesChange={setSpecies}
        month={month} onMonthChange={setMonth}
      />

      {/* TABS */}
      <div className="saline-tabs">
        {tabs.map((tab) => (
          <button key={tab.id}
            className={`saline-tab ${activeTab === tab.id ? "active" : ""}`}
            onClick={() => setActiveTab(tab.id)}
            data-testid={`tab-${tab.id}`}
          >
            <span className="flex items-center gap-1.5">
              {tab.icon}
              {tab.label}
              {tab.badge > 0 && (
                <span className="ml-1 px-1.5 py-0.5 rounded-full text-xs font-bold" style={{ background: "var(--saline-gold)", color: "#000", fontSize: "0.625rem" }}>
                  {tab.badge}
                </span>
              )}
            </span>
          </button>
        ))}
      </div>

      {/* CONTENT */}
      <div className="max-w-5xl mx-auto">
        {activeTab === "analyse" && <AnalyseSection data={analysisData} loading={loading} />}
        {activeTab === "recettes" && <RecettesSection data={analysisData} loading={loading} />}
        {activeTab === "produits" && <ProduitsSection products={products} loading={loading} onAddToCart={addToCart} cartLoading={cartLoading} />}
        {activeTab === "commande" && <CommandeSection cart={cart} loading={false} onQuantityChange={() => {}} onRemove={() => {}} onCheckout={handleCheckout} checkoutLoading={checkoutLoading} />}
      </div>
    </div>
  );
}

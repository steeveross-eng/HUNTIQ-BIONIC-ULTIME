/**
 * ProductPage.jsx — MAGASIN v2
 * ============================
 * Fiche produit unifiee — SALINE_PRODUCTS + API
 * CMD branche sur panier saline Stripe
 *
 * BCE-4X / STEEVE-MAX V6 — PHASE P0
 */
import { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import axios from "axios";
import {
  ShoppingCart, ArrowLeft, Package, FlaskConical, Droplets, Shield,
  Star, MapPin, Scale, DollarSign, Activity, Loader2, Leaf,
  TreeDeciduous, Mountain, ChevronDown, ChevronUp
} from "lucide-react";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const BIONIC = {
  green: '#00C853', yellow: '#F9D423', orange: '#FF9800', red: '#D32F2F',
  blue: '#2196F3', purple: '#9C27B0', card: '#111122', border: 'rgba(255,255,255,0.06)',
};

const getSalineSession = () => {
  let sid = localStorage.getItem('saline_session_id');
  if (!sid) {
    sid = 'sal_' + Math.random().toString(36).substr(2, 12);
    localStorage.setItem('saline_session_id', sid);
  }
  return sid;
};

const InfoBlock = ({ icon: Icon, title, children, color = BIONIC.blue }) => (
  <div className="rounded-xl border p-4" style={{ backgroundColor: BIONIC.card, borderColor: BIONIC.border }}>
    <div className="flex items-center gap-2 mb-3">
      <Icon className="h-4 w-4" style={{ color }} />
      <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">{title}</span>
    </div>
    {children}
  </div>
);

export default function ProductPage() {
  const { productId } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [cartLoading, setCartLoading] = useState(false);
  const [showMinerals, setShowMinerals] = useState(false);

  // Fetch product from SALINE API
  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const res = await axios.get(`${API}/v1/saline/shop/products`);
        const p = (res.data.products || []).find(p => p.id === productId);
        setProduct(p || null);
      } catch (e) {
        console.error('[ProductPage]', e);
      } finally {
        setLoading(false);
      }
    };
    fetchProduct();
  }, [productId]);

  // Add to saline cart
  const handleAddToCart = useCallback(async () => {
    setCartLoading(true);
    try {
      await axios.post(`${API}/v1/saline/shop/cart/add`, {
        session_id: getSalineSession(), product_id: productId, quantity: 1,
      });
      toast.success('Produit ajoute au panier SUPRA');
    } catch (e) {
      toast.error("Erreur lors de l'ajout");
    } finally {
      setCartLoading(false);
    }
  }, [productId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a14] flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-[#FF9800]" />
      </div>
    );
  }

  if (!product) {
    return (
      <div className="min-h-screen bg-[#0a0a14] flex flex-col items-center justify-center gap-4 pt-20">
        <Package className="h-16 w-16 text-gray-600" />
        <h2 className="text-xl font-bold text-white">Produit introuvable</h2>
        <Button variant="outline" onClick={() => navigate('/shop')} data-testid="back-to-shop">
          <ArrowLeft className="h-4 w-4 mr-2" /> Retour au catalogue
        </Button>
      </div>
    );
  }

  const p = product;
  const scoreColor = p.score >= 90 ? BIONIC.green : p.score >= 85 ? BIONIC.yellow : BIONIC.orange;

  return (
    <div className="min-h-screen bg-[#0a0a14] pt-20" data-testid="product-page">
      <div className="max-w-3xl mx-auto px-4 py-8 space-y-5">
        {/* Back */}
        <button onClick={() => navigate('/shop')} className="flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors" data-testid="product-back">
          <ArrowLeft className="h-4 w-4" /> Catalogue SUPRA
        </button>

        {/* Header Card */}
        <div className="rounded-xl border p-6 flex items-start gap-5" style={{ backgroundColor: BIONIC.card, borderColor: BIONIC.border }}>
          <div className="w-20 h-20 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: `linear-gradient(135deg, ${scoreColor}22, ${scoreColor}08)`, border: `2.5px solid ${scoreColor}` }}>
            <span className="text-3xl font-black" style={{ color: scoreColor }}>{p.score}</span>
          </div>
          <div className="flex-1 min-w-0">
            <span className="text-[11px] text-[#FF9800] font-bold uppercase tracking-wider">{p.brand}</span>
            <h1 className="text-xl font-black text-white mt-1" data-testid="product-name">{p.name}</h1>
            <p className="text-sm text-gray-400 mt-1">{p.description}</p>
            <div className="flex items-center gap-3 mt-3">
              <span className="text-[11px] font-bold px-2.5 py-1 rounded-lg" style={{ backgroundColor: '#FF980018', color: '#FF9800' }}>{p.product_format}</span>
              <span className="text-[11px] font-bold px-2.5 py-1 rounded-lg" style={{ backgroundColor: `${scoreColor}18`, color: scoreColor }}>SCORE {p.score}/100</span>
              <span className="text-[11px] text-gray-500">{p.weight}</span>
            </div>
          </div>
        </div>

        {/* Animaux cibles */}
        <InfoBlock icon={Leaf} title="Animaux cibles" color={BIONIC.green}>
          <div className="flex flex-wrap gap-2">
            {p.target_animals?.map(a => (
              <span key={a} className="text-sm font-semibold px-3 py-1.5 rounded-lg" style={{ backgroundColor: `${BIONIC.green}12`, color: BIONIC.green }}>{a}</span>
            ))}
          </div>
        </InfoBlock>

        {/* Mineraux */}
        <InfoBlock icon={FlaskConical} title="Composition minerale" color={BIONIC.yellow}>
          <button onClick={() => setShowMinerals(v => !v)} className="flex items-center gap-2 text-sm text-gray-300 mb-2" data-testid="toggle-minerals">
            {showMinerals ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            {Object.keys(p.minerals || {}).length} mineraux
          </button>
          {showMinerals && (
            <div className="grid grid-cols-2 gap-2 mt-2">
              {Object.entries(p.minerals || {}).map(([k, v]) => (
                <div key={k} className="flex justify-between py-1.5 px-3 rounded-lg" style={{ backgroundColor: 'rgba(255,255,255,0.03)' }}>
                  <span className="text-sm text-gray-300">{k}</span>
                  <span className="text-sm font-bold text-white">{v}</span>
                </div>
              ))}
            </div>
          )}
        </InfoBlock>

        {/* Saisons recommandees */}
        <InfoBlock icon={Mountain} title="Saisonnalite" color={BIONIC.orange}>
          <div className="flex flex-wrap gap-2">
            {p.recommended_seasons?.map(s => (
              <span key={s} className="text-sm px-3 py-1 rounded-lg capitalize" style={{ backgroundColor: '#FF980012', color: '#FF9800' }}>{s}</span>
            ))}
          </div>
        </InfoBlock>

        {/* Prix + Commander */}
        <div className="rounded-xl border p-6" style={{ backgroundColor: BIONIC.card, borderColor: BIONIC.border }}>
          <div className="flex items-center justify-between mb-4">
            <div>
              <span className="text-3xl font-black text-white">${p.price}</span>
              <span className="text-sm text-gray-500 ml-2">CAD</span>
            </div>
            <div className="text-right">
              <span className="text-[11px] text-gray-500 uppercase">Format</span>
              <div className="text-sm font-bold text-white">{p.product_format} — {p.weight}</div>
            </div>
          </div>
          <Button
            className="w-full bg-[#FF9800] hover:bg-[#E68900] text-black font-bold h-11"
            onClick={handleAddToCart}
            disabled={cartLoading}
            data-testid="product-order-btn"
          >
            {cartLoading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <ShoppingCart className="h-4 w-4 mr-2" />}
            Ajouter au panier SUPRA
          </Button>
          <p className="text-[11px] text-gray-600 text-center mt-2">Paiement securise Stripe</p>
        </div>

        <div className="text-center text-[10px] text-gray-600 pt-2 pb-6">
          Fiche Produit BIONIC SUPRA v2 | BCE-4X / STEEVE-MAX V6
        </div>
      </div>
    </div>
  );
}

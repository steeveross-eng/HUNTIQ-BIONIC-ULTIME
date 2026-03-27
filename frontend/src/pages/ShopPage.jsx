/**
 * ShopPage.jsx — MAGASIN v2
 * =========================
 * Catalogue unifie SALINE_PRODUCTS — Source unique
 * Panier unifie saline — Stripe Checkout
 *
 * BCE-4X / STEEVE-MAX V6 — PHASE P0 FUSION E-COMMERCE
 */
import { useState, useEffect, useMemo, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useLanguage } from "@/contexts/LanguageContext";
import { toast } from "sonner";
import axios from "axios";
import {
  ShoppingCart, Star, Shield, Droplet, Package, Filter,
  FlaskConical, Search, ArrowRight, Loader2, Crosshair
} from "lucide-react";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const BIONIC = {
  green: '#00C853', yellow: '#F9D423', orange: '#FF9800', red: '#D32F2F',
  blue: '#2196F3', card: '#111122', border: 'rgba(255,255,255,0.06)',
};

// Session saline unifiee
const getSalineSession = () => {
  let sid = localStorage.getItem('saline_session_id');
  if (!sid) {
    sid = 'sal_' + Math.random().toString(36).substr(2, 12);
    localStorage.setItem('saline_session_id', sid);
  }
  return sid;
};

// Format filter badges
const FORMAT_OPTIONS = [
  { value: 'all', label: 'Tous' },
  { value: 'bloc', label: 'Bloc' },
  { value: 'granules', label: 'Granules' },
  { value: 'poudre', label: 'Poudre' },
  { value: 'liquide', label: 'Liquide' },
];

const SPECIES_OPTIONS = [
  { value: 'all', label: 'Toutes especes' },
  { value: 'orignal', label: 'Orignal' },
  { value: 'chevreuil', label: 'Chevreuil' },
  { value: 'ours_noir', label: 'Ours noir' },
  { value: 'dindon_sauvage', label: 'Dindon sauvage' },
];

// Product Card
const SalineProductCard = ({ product, onAddToCart, loading }) => {
  const scoreColor = product.score >= 90 ? BIONIC.green : product.score >= 85 ? BIONIC.yellow : BIONIC.orange;
  const navigate = useNavigate();

  return (
    <Card className="bg-[#111122] border-white/6 overflow-hidden group hover:border-[#FF9800]/30 transition-all duration-300" data-testid={`shop-product-${product.id}`}>
      {/* Image placeholder + Score */}
      <div className="relative h-36 bg-gradient-to-br from-gray-900 to-gray-800 flex items-center justify-center">
        <Package className="h-12 w-12 text-gray-700 group-hover:text-[#FF9800]/30 transition-colors" />
        <div className="absolute top-2 right-2 px-2 py-1 rounded-full text-[11px] font-black" style={{ backgroundColor: `${scoreColor}20`, color: scoreColor, border: `1px solid ${scoreColor}40` }}>
          {product.score}/100
        </div>
        <div className="absolute top-2 left-2 px-2 py-0.5 rounded bg-black/60 text-[10px] font-bold text-[#FF9800] uppercase">
          {product.product_format}
        </div>
        <div className="absolute bottom-2 left-2 px-2 py-0.5 rounded bg-black/60 text-[10px] text-gray-400">
          {product.weight}
        </div>
      </div>

      <CardContent className="p-4 space-y-3">
        <div>
          <p className="text-[#FF9800] text-[11px] font-semibold uppercase tracking-wider">{product.brand}</p>
          <h3 className="text-white font-bold text-sm leading-tight mt-0.5 line-clamp-2 min-h-[2.5rem]">
            {product.name}
          </h3>
        </div>

        <p className="text-gray-400 text-[12px] leading-relaxed line-clamp-2">{product.description}</p>

        {/* Minerals */}
        <div className="flex flex-wrap gap-1">
          {Object.keys(product.minerals || {}).slice(0, 4).map(m => (
            <span key={m} className="text-[10px] px-1.5 py-0.5 rounded" style={{ backgroundColor: `${BIONIC.green}12`, color: BIONIC.green }}>{m}</span>
          ))}
        </div>

        {/* Target animals */}
        <div className="flex flex-wrap gap-1">
          {product.target_animals?.map(a => (
            <span key={a} className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-gray-400">{a}</span>
          ))}
        </div>

        <div className="flex items-center justify-between pt-2 border-t" style={{ borderColor: 'rgba(255,255,255,0.06)' }}>
          <span className="text-white font-black text-lg">${product.price}</span>
          <span className="text-[11px] text-gray-500">CAD</span>
        </div>

        <div className="flex gap-2">
          <Button
            className="flex-1 bg-[#FF9800] hover:bg-[#E68900] text-black text-xs h-9 font-bold"
            onClick={() => onAddToCart(product.id)}
            disabled={loading}
            data-testid={`add-to-cart-${product.id}`}
          >
            {loading ? <Loader2 className="h-3 w-3 animate-spin" /> : <ShoppingCart className="h-3 w-3 mr-1" />}
            CMD
          </Button>
          <Button
            variant="outline"
            className="border-white/10 hover:border-[#FF9800]/30 text-gray-300 text-xs h-9"
            onClick={() => navigate(`/product/${product.id}`)}
            data-testid={`view-product-${product.id}`}
          >
            Fiche
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

// Main Shop Page
export default function ShopPage() {
  const { t } = useLanguage();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [cartLoading, setCartLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [formatFilter, setFormatFilter] = useState('all');
  const [speciesFilter, setSpeciesFilter] = useState('all');
  const navigate = useNavigate();

  // Fetch SALINE_PRODUCTS from API
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const params = {};
        if (speciesFilter !== 'all') params.species = speciesFilter;
        if (formatFilter !== 'all') params.format = formatFilter;
        const res = await axios.get(`${API}/v1/saline/shop/products`, { params });
        setProducts(res.data.products || []);
      } catch (e) {
        console.error('Shop fetch error:', e);
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, [formatFilter, speciesFilter]);

  // Add to saline cart
  const handleAddToCart = useCallback(async (productId) => {
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
  }, []);

  // Filter by search
  const filteredProducts = useMemo(() => {
    if (!search) return products;
    const s = search.toLowerCase();
    return products.filter(p =>
      p.name.toLowerCase().includes(s) ||
      p.description?.toLowerCase().includes(s) ||
      Object.keys(p.minerals || {}).some(m => m.toLowerCase().includes(s))
    );
  }, [products, search]);

  return (
    <main className="min-h-screen bg-[#0a0a14] pt-20" data-testid="shop-page">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: '#FF980015', border: '2px solid #FF980060' }}>
              <FlaskConical className="h-5 w-5" style={{ color: '#FF9800' }} />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white uppercase tracking-tight" data-testid="shop-title">Catalogue SUPRA</h1>
              <p className="text-[12px] text-gray-500 uppercase tracking-wider">Produits salines BIONIC — Source unique certifiee</p>
            </div>
          </div>
          <p className="text-gray-400 text-sm mt-2">
            Supplements mineraux optimises par les 7 moteurs d'intelligence SUPRA. Chaque produit est note scientifiquement.
          </p>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-3 mb-6">
          <div className="relative flex-1 min-w-[200px] max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
            <Input
              placeholder="Rechercher un produit ou mineral..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="pl-10 bg-white/5 border-white/10 text-white text-sm h-9"
              data-testid="shop-search"
            />
          </div>

          {/* Format filter */}
          <div className="flex gap-1">
            {FORMAT_OPTIONS.map(opt => (
              <button key={opt.value} onClick={() => setFormatFilter(opt.value)}
                className={`px-3 py-1.5 rounded-lg text-[11px] font-bold uppercase tracking-wider transition-all ${formatFilter === opt.value ? 'bg-[#FF9800]/20 text-[#FF9800] border border-[#FF9800]/40' : 'bg-white/5 text-gray-400 border border-transparent hover:bg-white/10'}`}
                data-testid={`filter-format-${opt.value}`}>
                {opt.label}
              </button>
            ))}
          </div>

          {/* Species filter */}
          <select value={speciesFilter} onChange={e => setSpeciesFilter(e.target.value)}
            className="bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-xs text-white" data-testid="filter-species">
            {SPECIES_OPTIONS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
          </select>
        </div>

        {/* Results count */}
        <div className="mb-4 text-sm text-gray-400">
          {filteredProducts.length} produit(s) SUPRA
        </div>

        {/* Products Grid */}
        {loading ? (
          <div className="text-center py-16">
            <Loader2 className="h-8 w-8 animate-spin text-[#FF9800] mx-auto" />
            <p className="text-gray-500 text-sm mt-3">Chargement du catalogue...</p>
          </div>
        ) : filteredProducts.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {filteredProducts.map(product => (
              <SalineProductCard key={product.id} product={product} onAddToCart={handleAddToCart} loading={cartLoading} />
            ))}
          </div>
        ) : (
          <div className="text-center py-16">
            <Package className="h-12 w-12 text-gray-600 mx-auto mb-3" />
            <h3 className="text-white font-semibold mb-1">Aucun produit trouve</h3>
            <p className="text-gray-500 text-sm">Essayez un autre filtre</p>
          </div>
        )}

        {/* CTA vers carte */}
        <div className="mt-12 rounded-xl border p-6 text-center" style={{ backgroundColor: '#111122', borderColor: 'rgba(255,255,255,0.06)' }}>
          <Crosshair className="h-8 w-8 text-[#FF9800] mx-auto mb-3" />
          <h3 className="text-white font-bold text-lg mb-2">Analyse personnalisee</h3>
          <p className="text-gray-400 text-sm mb-4">
            Accedez a ANALYSE TERRITOIRE pour obtenir des recommandations SUPRA adaptees a votre site
          </p>
          <Button className="bg-[#FF9800] hover:bg-[#E68900] text-black font-bold" onClick={() => navigate('/mon-territoire-bionic')} data-testid="cta-analyse-territoire">
            <Crosshair className="h-4 w-4 mr-2" /> Analyse Territoire
          </Button>
        </div>
      </div>
    </main>
  );
}

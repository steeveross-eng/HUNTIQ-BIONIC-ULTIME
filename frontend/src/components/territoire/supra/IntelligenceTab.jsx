/**
 * SUPRA v2 — IntelligenceTab (Module Autonome R3.6)
 * ===================================================
 * Extrait de NutritionPointDetailPanel.jsx — Phase R3.6
 * BCE-4X ULTIME ABSOLU x3 / STEEVE-MAX
 *
 * AUCUNE MODIFICATION SANS AUTORISATION COMMANDANT
 * ZERO AJOUT | ZERO SUPPRESSION | EXTRACTION PURE
 */
import React from 'react';
import { FlaskConical, ShoppingCart } from 'lucide-react';
import { BIONIC, GoldenCard, SupraButton } from './constants';
import IconCircle from '../ui/IconCircle';

// ============================================================
// TAB: INTELLIGENCE — 3 COLONNES GOLDEN — BCE-4X STEEVE-MAX
// Produits avec match_score en grille dense
// ============================================================
const IntelligenceTab = ({ products, gc, compareIds, toggleCompare, addToCart, cartLoading }) => {
  const productList = products.products || [];
  // Round-robin distribution for balanced columns (E09 fix)
  const col1 = productList.filter((_, i) => i % 3 === 0);
  const col2 = productList.filter((_, i) => i % 3 === 1);
  const col3 = productList.filter((_, i) => i % 3 === 2);

  const IC = IconCircle;

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

export default IntelligenceTab;

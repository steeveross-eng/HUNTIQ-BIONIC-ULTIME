/**
 * SUPRA v2 — CommandezTab (Module Autonome R3.8)
 * =================================================
 * Extrait de NutritionPointDetailPanel.jsx — Phase R3.8
 * BCE-4X ULTIME ABSOLU / STEEVE-MAX
 *
 * AUCUNE MODIFICATION SANS AUTORISATION COMMANDANT
 * ZERO AJOUT | ZERO SUPPRESSION | EXTRACTION PURE
 */
import React from 'react';
import { Package, ShoppingCart, Plus, ArrowRight, Loader2 } from 'lucide-react';
import { BIONIC, SUPRA_CMD_COLOR, GoldenCard, SupraButton } from './constants';
import IconCircle from '../ui/IconCircle';

// ============================================================
// TAB: COMMANDEZ — 3 COLONNES GOLDEN — BCE-4X STEEVE-MAX
// Panier Stripe REEL + Checkout
// ============================================================
const CommandezTab = ({ order, products, recipe, gc, cart, addToCart, cartLoading, handleCheckout, checkoutLoading, fetchCart }) => {
  const IC = IconCircle;

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
                    {item.product_id ? (
                      <SupraButton size="sm" onClick={() => addToCart(item.product_id)} disabled={cartLoading} testId={`order-add-${i}`}>
                        <Plus className="h-3 w-3" />
                      </SupraButton>
                    ) : (
                      <span className="text-[10px] text-red-400 px-1.5 py-0.5 rounded" style={{ backgroundColor: 'rgba(239,68,68,0.1)' }} data-testid={`order-no-id-${i}`}>ID manquant</span>
                    )}
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

export default CommandezTab;

/**
 * CartSummary — Resume totaux, promos, bouton checkout V2
 * ==========================================================
 * Directive x5400-G — Phase P5-D
 * BCE-4X GOLDEN V6+
 */
import { Button } from '../../../components/ui/button';
import { ShoppingCart, Shield, Loader2 } from 'lucide-react';
import PromoInput from './PromoInput';

export const CartSummary = ({
  subtotal = 0,
  discountTotal = 0,
  total = 0,
  currency = 'CAD',
  promotionsApplied = [],
  onApplyPromo,
  onRemovePromo,
  onCheckout,
  onValidate,
  loading,
  validationResult
}) => {
  return (
    <div className="border-t border-white/10 pt-4 space-y-3" data-testid="cart-summary">
      <PromoInput
        onApply={onApplyPromo}
        onRemove={onRemovePromo}
        appliedPromos={promotionsApplied}
        loading={loading}
      />

      <div className="space-y-1.5 text-sm">
        <div className="flex justify-between text-gray-300">
          <span>Sous-total</span>
          <span data-testid="cart-subtotal">{subtotal.toFixed(2)}$</span>
        </div>
        {discountTotal > 0 && (
          <div className="flex justify-between text-green-400">
            <span>Remises</span>
            <span data-testid="cart-discount">-{discountTotal.toFixed(2)}$</span>
          </div>
        )}
        <div className="flex justify-between text-white font-bold text-base pt-1 border-t border-white/5">
          <span>Total</span>
          <span className="text-[#F5A623]" data-testid="cart-total">
            {total.toFixed(2)}$ {currency}
          </span>
        </div>
      </div>

      {validationResult && !validationResult.valid && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-2.5 text-xs">
          {validationResult.errors?.map((err, i) => (
            <p key={i} className="text-red-400">{err.message}</p>
          ))}
        </div>
      )}

      <Button
        className="w-full bg-[#F5A623] hover:bg-[#d4890e] text-black font-semibold h-11"
        onClick={onCheckout}
        disabled={loading || total <= 0}
        data-testid="cart-checkout-btn"
      >
        {loading ? (
          <Loader2 className="w-4 h-4 animate-spin mr-2" />
        ) : (
          <ShoppingCart className="w-4 h-4 mr-2" />
        )}
        Commander — {total.toFixed(2)}$
      </Button>

      <p className="text-xs text-gray-500 text-center flex items-center justify-center gap-1">
        <Shield className="w-3 h-3" /> Paiement securise par Stripe
      </p>
    </div>
  );
};

export default CartSummary;

/**
 * CartPanel — Panel lateral panier V2
 * ======================================
 * Directive x5400-G — Phase P5-D
 * BCE-4X GOLDEN V6+
 * 
 * Panel Sheet affichant le panier V2 avec:
 * - Liste articles avec +/- quantites
 * - Section promotions
 * - Resume totaux
 * - Bouton checkout
 * - Suggestions upsell
 */
import { useState, useEffect, useCallback } from 'react';
import {
  Sheet, SheetContent, SheetHeader, SheetTitle
} from '../../../components/ui/sheet';
import { Button } from '../../../components/ui/button';
import { ShoppingCart, Trash2, Sparkles, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import CartItem from './CartItem';
import CartSummary from './CartSummary';
import { CartService } from '../CartService';

export const CartPanel = ({ isOpen, onOpenChange, onCartUpdate }) => {
  const [cart, setCart] = useState({ items: [], total: 0, subtotal: 0, discount_total: 0 });
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [validationResult, setValidationResult] = useState(null);

  const userId = CartService.getUserId();

  const fetchCart = useCallback(async () => {
    const data = await CartService.getCartV2(userId);
    setCart(data);
    if (onCartUpdate) onCartUpdate(data.item_count || data.items?.length || 0);
  }, [userId, onCartUpdate]);

  const fetchSuggestions = useCallback(async () => {
    const data = await CartService.getSuggestionsV2(userId);
    setSuggestions(data);
  }, [userId]);

  useEffect(() => {
    if (isOpen) {
      fetchCart();
      fetchSuggestions();
    }
  }, [isOpen, fetchCart, fetchSuggestions]);

  const handleUpdateQuantity = async (itemId, qty) => {
    setLoading(true);
    if (qty <= 0) {
      await CartService.removeItemV2(userId, itemId);
    } else {
      await CartService.updateQuantityV2(userId, itemId, qty);
    }
    await fetchCart();
    setLoading(false);
  };

  const handleRemoveItem = async (itemId) => {
    setLoading(true);
    await CartService.removeItemV2(userId, itemId);
    await fetchCart();
    setLoading(false);
    toast.success('Article retire du panier');
  };

  const handleClear = async () => {
    setLoading(true);
    await CartService.clearCartV2(userId);
    await fetchCart();
    setLoading(false);
    toast.success('Panier vide');
  };

  const handleApplyPromo = async (code) => {
    setLoading(true);
    const result = await CartService.applyPromoV2(userId, code);
    if (result.success) {
      await fetchCart();
      toast.success(`Code ${code} applique`);
    }
    setLoading(false);
    return result;
  };

  const handleRemovePromo = async (code) => {
    setLoading(true);
    await CartService.removePromoV2(userId, code);
    await fetchCart();
    setLoading(false);
    toast.success(`Code ${code} retire`);
  };

  const handleCheckout = async () => {
    setLoading(true);
    const validation = await CartService.validateCartV2(userId);
    if (validation.validation && !validation.validation.valid) {
      setValidationResult(validation.validation);
      setLoading(false);
      toast.error('Veuillez corriger les erreurs avant de commander');
      return;
    }
    setValidationResult(null);

    const result = await CartService.checkoutV2(userId);
    if (result.success) {
      toast.success(`Commande creee: ${result.order_id?.substring(0, 8)}...`);
      await fetchCart();
      onOpenChange(false);
    } else {
      toast.error(result.error || 'Erreur lors du checkout');
    }
    setLoading(false);
  };

  const items = cart.items || [];

  return (
    <Sheet open={isOpen} onOpenChange={onOpenChange}>
      <SheetContent className="bg-[#0a0a1a] border-l border-white/10 w-full sm:max-w-md flex flex-col" data-testid="cart-panel">
        <SheetHeader className="pb-2">
          <SheetTitle className="text-white flex items-center justify-between">
            <span className="flex items-center gap-2">
              <ShoppingCart className="h-5 w-5 text-[#F5A623]" />
              Panier V2
            </span>
            {items.length > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleClear}
                className="text-gray-400 hover:text-red-400 text-xs h-7"
                disabled={loading}
                data-testid="cart-clear-btn"
              >
                <Trash2 className="w-3.5 h-3.5 mr-1" /> Vider
              </Button>
            )}
          </SheetTitle>
        </SheetHeader>

        <div className="flex-1 overflow-auto space-y-2 py-2" data-testid="cart-items-list">
          {items.length === 0 ? (
            <div className="text-center py-12">
              <ShoppingCart className="w-12 h-12 text-gray-600 mx-auto mb-3" />
              <p className="text-gray-400 text-sm">Votre panier est vide</p>
              <p className="text-gray-500 text-xs mt-1">Ajoutez des produits depuis le magasin</p>
            </div>
          ) : (
            items.map((item) => (
              <CartItem
                key={item.item_id}
                item={item}
                onUpdateQuantity={handleUpdateQuantity}
                onRemove={handleRemoveItem}
                loading={loading}
              />
            ))
          )}
        </div>

        {suggestions.length > 0 && items.length > 0 && (
          <div className="border-t border-white/5 pt-3 pb-1" data-testid="cart-suggestions">
            <p className="text-xs text-gray-400 flex items-center gap-1 mb-2">
              <Sparkles className="w-3 h-3 text-[#F5A623]" /> Suggestions
            </p>
            {suggestions.slice(0, 2).map((s, i) => (
              <p key={i} className="text-xs text-gray-300 bg-[#F5A623]/5 rounded px-2 py-1.5 mb-1 border border-[#F5A623]/10">
                {s.message}
              </p>
            ))}
          </div>
        )}

        {items.length > 0 && (
          <CartSummary
            subtotal={cart.subtotal || 0}
            discountTotal={cart.discount_total || 0}
            total={cart.total || 0}
            currency={cart.currency || 'CAD'}
            promotionsApplied={cart.promotions_applied || []}
            onApplyPromo={handleApplyPromo}
            onRemovePromo={handleRemovePromo}
            onCheckout={handleCheckout}
            loading={loading}
            validationResult={validationResult}
          />
        )}
      </SheetContent>
    </Sheet>
  );
};

export default CartPanel;

/**
 * CartBadge — Badge compteur panier navbar V2
 * ==============================================
 * Directive x5400-G — Phase P5-D
 * BCE-4X GOLDEN V6+
 */
import { ShoppingCart } from 'lucide-react';
import { Button } from '../../../components/ui/button';

export const CartBadge = ({ count = 0, onClick }) => {
  return (
    <Button
      variant="outline"
      onClick={onClick}
      className="relative border-white/20 hover:border-[#F5A623]/50 hover:bg-[#F5A623]/10 transition-all"
      data-testid="cart-badge-btn"
      aria-label={`Panier (${count} articles)`}
    >
      <ShoppingCart className="h-5 w-5" />
      {count > 0 && (
        <span
          className="absolute -top-2 -right-2 bg-[#F5A623] text-black text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold shadow-[0_0_10px_rgba(245,166,35,0.4)]"
          data-testid="cart-badge-count"
        >
          {count > 99 ? '99+' : count}
        </span>
      )}
    </Button>
  );
};

export default CartBadge;

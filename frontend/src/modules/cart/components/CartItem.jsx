/**
 * CartItem — Ligne article panier V2
 * ====================================
 * Directive x5400-G — Phase P5-D
 * BCE-4X GOLDEN V6+
 */
import { Minus, Plus, Trash2, Package } from 'lucide-react';
import { Button } from '../../../components/ui/button';

export const CartItem = ({ item, onUpdateQuantity, onRemove, loading }) => {
  const price = item.unit_price || 0;
  const subtotal = (price * (item.quantity || 1)).toFixed(2);

  return (
    <div className="flex items-center gap-3 bg-slate-800/60 rounded-lg p-3 border border-white/5" data-testid={`cart-item-${item.item_id}`}>
      <div className="w-10 h-10 rounded-md bg-[#F5A623]/10 flex items-center justify-center flex-shrink-0">
        <Package className="w-5 h-5 text-[#F5A623]" />
      </div>

      <div className="flex-1 min-w-0">
        <p className="text-white text-sm font-medium truncate">{item.name}</p>
        <p className="text-gray-400 text-xs">{price.toFixed(2)}$ x {item.quantity}</p>
      </div>

      <div className="flex items-center gap-1">
        <Button
          variant="ghost"
          size="icon"
          className="w-7 h-7 text-gray-300 hover:text-white hover:bg-white/10"
          onClick={() => onUpdateQuantity(item.item_id, Math.max(0, item.quantity - 1))}
          disabled={loading}
          data-testid={`cart-item-decrease-${item.item_id}`}
        >
          <Minus className="w-3 h-3" />
        </Button>
        <span className="text-white text-sm w-6 text-center font-medium" data-testid={`cart-item-qty-${item.item_id}`}>
          {item.quantity}
        </span>
        <Button
          variant="ghost"
          size="icon"
          className="w-7 h-7 text-gray-300 hover:text-white hover:bg-white/10"
          onClick={() => onUpdateQuantity(item.item_id, item.quantity + 1)}
          disabled={loading}
          data-testid={`cart-item-increase-${item.item_id}`}
        >
          <Plus className="w-3 h-3" />
        </Button>
      </div>

      <span className="text-[#F5A623] font-bold text-sm w-16 text-right">{subtotal}$</span>

      <Button
        variant="ghost"
        size="icon"
        className="w-7 h-7 text-red-400 hover:text-red-300 hover:bg-red-500/10"
        onClick={() => onRemove(item.item_id)}
        disabled={loading}
        data-testid={`cart-item-remove-${item.item_id}`}
      >
        <Trash2 className="w-3.5 h-3.5" />
      </Button>
    </div>
  );
};

export default CartItem;

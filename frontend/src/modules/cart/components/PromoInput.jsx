/**
 * PromoInput — Champ saisie code promo V2
 * ==========================================
 * Directive x5400-G — Phase P5-D
 * BCE-4X GOLDEN V6+
 */
import { useState } from 'react';
import { Input } from '../../../components/ui/input';
import { Button } from '../../../components/ui/button';
import { Tag, X, Loader2 } from 'lucide-react';

export const PromoInput = ({ onApply, onRemove, appliedPromos = [], loading }) => {
  const [code, setCode] = useState('');
  const [error, setError] = useState('');

  const handleApply = async () => {
    if (!code.trim()) return;
    setError('');
    const result = await onApply(code.trim().toUpperCase());
    if (result && !result.success) {
      setError(result.message || 'Code invalide');
    } else {
      setCode('');
    }
  };

  return (
    <div className="space-y-2" data-testid="promo-input-section">
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Tag className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-500" />
          <Input
            value={code}
            onChange={(e) => { setCode(e.target.value); setError(''); }}
            placeholder="Code promo"
            className="pl-9 bg-slate-800 border-white/10 text-white placeholder:text-gray-500 h-9 text-sm"
            onKeyDown={(e) => e.key === 'Enter' && handleApply()}
            disabled={loading}
            data-testid="promo-code-input"
          />
        </div>
        <Button
          onClick={handleApply}
          disabled={!code.trim() || loading}
          className="bg-[#F5A623] hover:bg-[#d4890e] text-black font-medium h-9 px-4 text-sm"
          data-testid="promo-apply-btn"
        >
          {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : 'Appliquer'}
        </Button>
      </div>

      {error && (
        <p className="text-red-400 text-xs" data-testid="promo-error">{error}</p>
      )}

      {appliedPromos.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {appliedPromos.map((promo) => (
            <span
              key={promo.promo_code}
              className="inline-flex items-center gap-1 bg-green-500/20 text-green-400 text-xs rounded-full px-2.5 py-1 border border-green-500/30"
              data-testid={`promo-badge-${promo.promo_code}`}
            >
              <Tag className="w-3 h-3" />
              {promo.promo_code}
              {promo.discount_type === 'percentage' && ` (-${promo.discount_value}%)`}
              {promo.discount_type === 'fixed' && ` (-${promo.discount_value}$)`}
              <button
                onClick={() => onRemove(promo.promo_code)}
                className="ml-0.5 hover:text-green-200"
                data-testid={`promo-remove-${promo.promo_code}`}
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  );
};

export default PromoInput;

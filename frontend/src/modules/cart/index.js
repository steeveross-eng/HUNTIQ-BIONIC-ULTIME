/**
 * Cart Module — V2 P5-OPTIMIZATION
 * ==================================
 * Directive x5400-G — BCE-4X GOLDEN V6+
 * 
 * V1 exports preserved. V2 exports added.
 * 
 * @module cart
 * @version 2.0.0
 */

export const MODULE_NAME = 'cart';
export const MODULE_VERSION = '2.0.0';
export const MODULE_TYPE = 'business';

// Service
export { CartService } from './CartService';

// V1 Components (ZERO LOSS)
export { CartWidget } from './components/CartWidget';

// V2 Components (P5-OPTIMIZATION)
export { CartPanel } from './components/CartPanel';
export { CartItem } from './components/CartItem';
export { CartSummary } from './components/CartSummary';
export { CartBadge } from './components/CartBadge';
export { PromoInput } from './components/PromoInput';

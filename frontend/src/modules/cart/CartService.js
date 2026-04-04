/**
 * CartService V2 — Client API panier utilisateur
 * ================================================
 * Directive x5400-G — Phase P5-D
 * BCE-4X GOLDEN V6+ | ZERO LOSS, ZERO REGRESSION
 * 
 * V1 methods preserved (session-based).
 * V2 methods added (user_id-based, persistent).
 */

const API_URL = process.env.REACT_APP_BACKEND_URL;

export class CartService {
  // ========================================
  // V1 METHODS (INCHANGES — ZERO LOSS)
  // ========================================

  static async getHealth() {
    try {
      const response = await fetch(`${API_URL}/api/v1/cart/health`);
      if (!response.ok) return { status: 'unavailable' };
      return response.json();
    } catch {
      return { status: 'unavailable' };
    }
  }

  static async getStats() {
    try {
      const response = await fetch(`${API_URL}/api/v1/cart/stats`);
      if (!response.ok) return { total_carts: 0, active_carts: 0 };
      return response.json();
    } catch {
      return { total_carts: 0, active_carts: 0 };
    }
  }

  static async getCart(sessionId) {
    try {
      const response = await fetch(`${API_URL}/api/v1/cart/session/${sessionId}`);
      if (!response.ok) return { items: [], total: 0 };
      const data = await response.json();
      return { items: data.items || [], total: data.total || 0, session_id: sessionId };
    } catch {
      return { items: [], total: 0 };
    }
  }

  static async addItem(sessionId, productId, quantity = 1) {
    try {
      const response = await fetch(`${API_URL}/api/v1/cart/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, product_id: productId, quantity })
      });
      return response.json();
    } catch {
      return { success: false };
    }
  }

  static async updateItem(itemId, quantity) {
    try {
      const response = await fetch(`${API_URL}/api/v1/cart/${itemId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quantity })
      });
      return response.json();
    } catch {
      return { success: false };
    }
  }

  static async removeItem(itemId) {
    try {
      const response = await fetch(`${API_URL}/api/v1/cart/${itemId}`, { method: 'DELETE' });
      return response.json();
    } catch {
      return { success: false };
    }
  }

  static async clearCart(sessionId) {
    try {
      const response = await fetch(`${API_URL}/api/v1/cart/session/${sessionId}/clear`, { method: 'DELETE' });
      return response.json();
    } catch {
      return { success: false };
    }
  }

  static getSessionId() {
    let sessionId = localStorage.getItem('cart_session_id');
    if (!sessionId) {
      sessionId = 'cart_' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('cart_session_id', sessionId);
    }
    return sessionId;
  }

  static calculateTotal(items) {
    return items.reduce((total, item) => {
      const price = item.product?.price || item.price || 0;
      return total + (price * item.quantity);
    }, 0);
  }

  static getItemCount(items) {
    return items.reduce((count, item) => count + item.quantity, 0);
  }

  // ========================================
  // V2 METHODS — P5-OPTIMIZATION (user_id)
  // ========================================

  static getUserId() {
    try {
      const userData = localStorage.getItem('user_data');
      if (userData) {
        const parsed = JSON.parse(userData);
        return parsed.user_id || parsed.id || parsed.email || 'guest';
      }
    } catch { /* ignore */ }
    let guestId = localStorage.getItem('cart_guest_id');
    if (!guestId) {
      guestId = 'guest_' + Math.random().toString(36).substr(2, 12);
      localStorage.setItem('cart_guest_id', guestId);
    }
    return guestId;
  }

  static async getCartV2(userId) {
    try {
      const uid = userId || this.getUserId();
      const response = await fetch(`${API_URL}/api/v1/cart/user/${uid}`);
      if (!response.ok) return { items: [], total: 0, item_count: 0 };
      const data = await response.json();
      return data.cart || { items: [], total: 0, item_count: 0 };
    } catch {
      return { items: [], total: 0, item_count: 0 };
    }
  }

  static async addItemV2(userId, item) {
    try {
      const uid = userId || this.getUserId();
      const response = await fetch(`${API_URL}/api/v1/cart/user/${uid}/items`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(item)
      });
      const data = await response.json();
      return data;
    } catch {
      return { success: false };
    }
  }

  static async updateQuantityV2(userId, itemId, quantity) {
    try {
      const uid = userId || this.getUserId();
      const response = await fetch(`${API_URL}/api/v1/cart/user/${uid}/items/${itemId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quantity })
      });
      return response.json();
    } catch {
      return { success: false };
    }
  }

  static async removeItemV2(userId, itemId) {
    try {
      const uid = userId || this.getUserId();
      const response = await fetch(`${API_URL}/api/v1/cart/user/${uid}/items/${itemId}`, {
        method: 'DELETE'
      });
      return response.json();
    } catch {
      return { success: false };
    }
  }

  static async clearCartV2(userId) {
    try {
      const uid = userId || this.getUserId();
      const response = await fetch(`${API_URL}/api/v1/cart/user/${uid}/clear`, {
        method: 'DELETE'
      });
      return response.json();
    } catch {
      return { success: false };
    }
  }

  static async getSummaryV2(userId) {
    try {
      const uid = userId || this.getUserId();
      const response = await fetch(`${API_URL}/api/v1/cart/user/${uid}/summary`);
      const data = await response.json();
      return data.summary || {};
    } catch {
      return {};
    }
  }

  static async validateCartV2(userId) {
    try {
      const uid = userId || this.getUserId();
      const response = await fetch(`${API_URL}/api/v1/cart/user/${uid}/validate`, {
        method: 'POST'
      });
      return response.json();
    } catch {
      return { success: false };
    }
  }

  static async applyPromoV2(userId, promoCode) {
    try {
      const uid = userId || this.getUserId();
      const response = await fetch(`${API_URL}/api/v1/cart/user/${uid}/promotions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ promo_code: promoCode })
      });
      return response.json();
    } catch {
      return { success: false };
    }
  }

  static async removePromoV2(userId, promoCode) {
    try {
      const uid = userId || this.getUserId();
      const response = await fetch(`${API_URL}/api/v1/cart/user/${uid}/promotions/${promoCode}`, {
        method: 'DELETE'
      });
      return response.json();
    } catch {
      return { success: false };
    }
  }

  static async checkoutV2(userId) {
    try {
      const uid = userId || this.getUserId();
      const response = await fetch(`${API_URL}/api/v1/cart/user/${uid}/checkout`, {
        method: 'POST'
      });
      return response.json();
    } catch {
      return { success: false };
    }
  }

  static async getSuggestionsV2(userId) {
    try {
      const uid = userId || this.getUserId();
      const response = await fetch(`${API_URL}/api/v1/cart/user/${uid}/suggestions`);
      const data = await response.json();
      return data.suggestions || [];
    } catch {
      return [];
    }
  }
}

export default CartService;

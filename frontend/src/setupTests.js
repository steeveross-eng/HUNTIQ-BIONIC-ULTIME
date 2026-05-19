// setupTests.js — CRA setup global pour Jest
// P22ΩΩ_ZEROCOST_PHASE2_R2_CLOUDFLARE_Ω · 2026-02-XX · STEEVE-MAX
//
// Polyfill structuredClone pour JSDOM (utilisé par fake-indexeddb).
// JSDOM v16 (CRA 5) ne l'expose pas dans le global scope.
if (typeof structuredClone === 'undefined') {
  // Polyfill simple basé sur JSON deep clone (suffisant pour les bundles JSON-safe LKG)
  global.structuredClone = (obj) => {
    if (obj === undefined || obj === null) return obj;
    return JSON.parse(JSON.stringify(obj));
  };
}

import React from "react";
import ReactDOM from "react-dom/client";

// BIONIC V7.3 — Suppress benign ResizeObserver loop error.
// This error is non-fatal: the browser caps the loop after one frame.
// Without this handler, React's error overlay displays it as a crash.
const RESIZE_OBSERVER_ERR = 'ResizeObserver loop';
window.addEventListener('error', (e) => {
  if (e.message?.includes(RESIZE_OBSERVER_ERR) || e.error?.message?.includes(RESIZE_OBSERVER_ERR)) {
    e.stopImmediatePropagation();
    e.preventDefault();
  }
});
// Also suppress the unhandledrejection variant (rare but possible)
window.addEventListener('unhandledrejection', (e) => {
  if (e.reason?.message?.includes(RESIZE_OBSERVER_ERR)) {
    e.preventDefault();
  }
});

// BRANCHE 2: Inject Critical CSS BEFORE main styles
import { injectCriticalCSS, removeCriticalCSS } from "@/utils/criticalCSS";
injectCriticalCSS();

import "@/index.css";
import App from "@/App";
import { initWebVitals } from "@/utils/webVitals";
import { initPerformanceOptimizations } from "@/utils/performanceOptimizations";
import { initAccessibilityEnhancements } from "@/utils/accessibilityEnhancements";
import * as serviceWorkerRegistration from "./serviceWorkerRegistration";

// BRANCHE 3: Import advanced optimizations
import { initImageOptimization } from "@/utils/imageCDN";
import { initHTTP3Optimization } from "@/utils/http3Optimization";
import { initSSRConfig } from "@/utils/ssrConfig";
import { preloadCriticalRoutes } from "@/utils/routePreloader";

const root = ReactDOM.createRoot(document.getElementById("root"));

// Phase XI-SUPRA-D : Route de capture institutionnelle — DOIT être rendue
// hors de React.StrictMode pour éliminer les remounts (sinon Playwright
// capture une carte à moitié montée, screenshots < 30 KB).
const IS_CAPTURE_MODE = typeof window !== 'undefined'
  && window.location.pathname.startsWith('/territoire-capture-mode');

if (IS_CAPTURE_MODE) {
  root.render(<App />);
} else {
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>,
  );
}

// BRANCHE 2: Remove Critical CSS after main styles load
removeCriticalCSS();

// PHASE D: Initialize Web Vitals reporting
initWebVitals();

// POLISH FINAL: Performance optimizations
initPerformanceOptimizations();

// POLISH FINAL: Accessibility enhancements (WCAG AAA)
initAccessibilityEnhancements();

// BRANCHE 3: Advanced optimizations
initImageOptimization();
initHTTP3Optimization();
initSSRConfig();
preloadCriticalRoutes();

// PHASE_DESACTIVATION_TOTALE_SW (2026-04-28 · ordre Commandant STEEVE-MAX)
// Toutes les requêtes vont au réseau. Aucun SW. Aucun cache client.
// L'enregistrement n'est PLUS effectué. À la place, on appelle unregister()
// pour désinscrire tout SW résiduel chez les clients existants.
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.getRegistrations()
    .then((regs) => Promise.all(regs.map((r) => r.unregister().catch(() => false))))
    .then(() => {
      console.log('[SW-OFF] tous les SW résiduels ont été désinscrits');
    })
    .catch(() => {});
  if ('caches' in window) {
    caches.keys()
      .then((keys) => Promise.all(keys.map((k) => caches.delete(k).catch(() => false))))
      .then(() => console.log('[SW-OFF] CacheStorage purgé'))
      .catch(() => {});
  }
}

// P22C_FIX_BLANK_SCREEN_Ω · 2026-05-09 · COMMANDANT STEEVE-MAX
// Désactivation TOTALE de l'enregistrement du Service Worker.
// RACINE BLANCHE-ÉCRAN : SW v13 (skipWaiting + clients.claim) avortait
// toutes les requêtes API en cours pendant le mount React → ROOT vide.
// Doctrine : aucun SW ne doit être enregistré côté client.
// Le sw.js public/sw.js est désormais un KILLSWITCH qui s'auto-désinscrit.
// V30_LOCK INVIOLÉ · ANTI-GÉNÉRIQUE STRICT · FUSION ADD-ONLY
// serviceWorkerRegistration.register({...})  ← DISABLED P22C_FIX
void serviceWorkerRegistration;  // mark as intentionally unused
console.log(
  '[BCE-4X · P22C_FIX_BLANK_SCREEN_Ω] '
  + 'serviceWorkerRegistration.register() DESACTIVE par directive STEEVE-MAX');

// P22C · FORCE TERRITOIRE FRONTEND RELOAD Ω · auto-purge AGRESSIF
// Ordre Commandant STEEVE-MAX · 2026-05-09
const BCE_4X_FORCE_PURGE_VERSION = "P22C_TERRITOIRE_FRONTEND_RELOAD_2026_05_09_0030";
try {
  const stored = window.localStorage.getItem("bce4x_purge_version");
  if (stored !== BCE_4X_FORCE_PURGE_VERSION) {
    window.localStorage.setItem(
      "bce4x_purge_version", BCE_4X_FORCE_PURGE_VERSION);

    // P22C · purge AGRESSIVE des keys bionic/territoire/layers
    // Suppression doctrinale - tout key legacy doit disparaître
    const legacyExactKeys = [
      "panel_mode", "show_debug_panel", "analysis_v6_open",
      "legacy_corridors_visible", "show_dev_inspector",
      "old_layers_state", "v6_panel_state",
    ];
    legacyExactKeys.forEach((k) => {
      try { window.localStorage.removeItem(k); } catch (_) {}
      try { window.sessionStorage.removeItem(k); } catch (_) {}
    });

    // P22C · purge keys par préfixe (bionic_*, territoire_*, layers_*, etc.)
    const legacyPrefixes = [
      "bionic_legacy_", "territoire_legacy_", "layers_legacy_",
      "v6_", "debug_", "analysis_v6_", "panel_legacy_",
      "old_corridors_", "old_zones_", "old_affuts_",
    ];
    try {
      const allKeys = Object.keys(window.localStorage);
      allKeys.forEach((k) => {
        if (legacyPrefixes.some((p) => k.startsWith(p))) {
          try { window.localStorage.removeItem(k); } catch (_) {}
        }
      });
      const sessionKeys = Object.keys(window.sessionStorage);
      sessionKeys.forEach((k) => {
        if (legacyPrefixes.some((p) => k.startsWith(p))) {
          try { window.sessionStorage.removeItem(k); } catch (_) {}
        }
      });
    } catch (_) { /* no-op */ }

    // P22C · purge CacheStorage TOUTES versions
    if ('caches' in window) {
      caches.keys().then((keys) =>
        Promise.all(keys.map((k) => caches.delete(k)))
      ).then(() => {
        // eslint-disable-next-line no-console
        console.log(
          '[BCE-4X · P22C FORCE PURGE] CacheStorage cleared · '
          + 'all versions wiped');
      }).catch(() => {});
    }

    // P22C · message au SW pour purge interne
    if ('serviceWorker' in navigator
        && navigator.serviceWorker.controller) {
      try {
        navigator.serviceWorker.controller.postMessage({
          type: 'BCE_4X_FORCE_PURGE',
        });
      } catch (_) { /* no-op */ }
    }

    console.log(
      `[BCE-4X · P22C FORCE PURGE] version=${BCE_4X_FORCE_PURGE_VERSION} `
      + `· legacy keys (exact + prefixes) cleared · CacheStorage purged · `
      + `SW purge message sent`);
  }
} catch (_) {
  /* no-op */
}

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

serviceWorkerRegistration.unregister();

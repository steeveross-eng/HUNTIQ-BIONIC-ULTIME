/**
 * TerritoireFrontendDebugOverlay.jsx — P22C · Diagnostic temporaire
 * ═══════════════════════════════════════════════════════════════
 * COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT
 *
 * Activation : URL `?territoireDebug=on`
 * Affiche overlay bas-droite :
 *   - SW status + version actif
 *   - localStorage keys count + bionic version
 *   - Cache storage names
 *   - Build version + meta tags
 *   - HTTP status canonical/visual/territoire endpoints
 *
 * Anti-générique : utilise UNIQUEMENT les vraies données
 *   (navigator.serviceWorker.controller, caches.keys, fetch réel)
 * V30_LOCK : INVIOLÉ.
 * ═══════════════════════════════════════════════════════════════
 */
import React, { useEffect, useState } from 'react';

const isDebugEnabled = () => {
  try {
    const params = new URLSearchParams(window.location.search);
    return params.get('territoireDebug') === 'on';
  } catch (e) {
    return false;
  }
};

const getMetaContent = (name) => {
  try {
    const el = document.querySelector(`meta[name="${name}"]`);
    return el ? el.getAttribute('content') : null;
  } catch (e) {
    return null;
  }
};

const TerritoireFrontendDebugOverlay = () => {
  const [enabled] = useState(isDebugEnabled());
  const [diag, setDiag] = useState({});

  useEffect(() => {
    if (!enabled) return;
    const collectDiag = async () => {
      const d = {
        ts: new Date().toISOString(),
        url: window.location.href,
        path: window.location.pathname,
        meta: {
          force_purge_version: getMetaContent(
            'bce-4x-force-purge-version'),
          rendu_omega_version: getMetaContent(
            'bionic-rendu-omega-version'),
          territoire_canonical: getMetaContent(
            'bce-4x-territoire-omega-canonical'),
          visual_sync: getMetaContent(
            'bce-4x-canonical-visual-sync'),
          focus_mode: getMetaContent('bce-4x-focus-mode'),
          frontend_resurrection: getMetaContent(
            'bce-4x-frontend-resurrection'),
        },
        sw: {
          supported: 'serviceWorker' in navigator,
          controller: !!(navigator.serviceWorker
            && navigator.serviceWorker.controller),
          state: navigator.serviceWorker
            && navigator.serviceWorker.controller
            ? navigator.serviceWorker.controller.state
            : null,
        },
        localStorage: {
          n_keys: Object.keys(window.localStorage).length,
          bce4x_purge_version: window.localStorage.getItem(
            'bce4x_purge_version'),
          bce4x_commandant_token_set:
            !!window.localStorage.getItem(
              'bce4x_commandant_token'),
        },
        sessionStorage: {
          n_keys: Object.keys(window.sessionStorage).length,
        },
        caches: { names: [] },
        endpoints: {},
      };
      // Caches list
      try {
        if ('caches' in window) {
          const keys = await caches.keys();
          d.caches.names = keys;
          d.caches.count = keys.length;
        }
      } catch (e) {
        d.caches.error = e.message;
      }
      // Endpoint pings (anti-générique : vraies HTTP)
      const base = process.env.REACT_APP_BACKEND_URL || '';
      const ENDPOINTS = [
        ['canonical_status',
         '/api/v30/super-masters/territoire-omega-canonical-status'],
        ['visual_sync',
         '/api/v30/super-masters/canonical-visual-sync-status'],
        ['access_status',
         '/api/v30/super-masters/territoire-access-status'],
        ['force_purge',
         '/api/v30/super-masters/force-purge-doctrine-status'],
      ];
      const results = await Promise.all(
        ENDPOINTS.map(async ([key, path]) => {
          try {
            const r = await fetch(`${base}${path}`, {
              cache: 'no-store',
            });
            return [key, { status: r.status, ok: r.ok }];
          } catch (e) {
            return [key, { error: e.message }];
          }
        }),
      );
      d.endpoints = Object.fromEntries(results);
      setDiag(d);
    };
    collectDiag();
    const t = setInterval(collectDiag, 15000);
    return () => clearInterval(t);
  }, [enabled]);

  const onClearLocal = () => {
    try {
      const keys = Object.keys(window.localStorage);
      keys.forEach((k) => window.localStorage.removeItem(k));
      const skeys = Object.keys(window.sessionStorage);
      skeys.forEach((k) => window.sessionStorage.removeItem(k));
      // eslint-disable-next-line no-alert
      alert(
        `Cleared ${keys.length} localStorage + ${skeys.length} sessionStorage keys.`);
    } catch (e) { /* no-op */ }
  };

  const onPurgeCaches = async () => {
    try {
      const keys = await caches.keys();
      await Promise.all(keys.map((k) => caches.delete(k)));
      // eslint-disable-next-line no-alert
      alert(`Purged ${keys.length} CacheStorage entries.`);
    } catch (e) { /* no-op */ }
  };

  const onUnregisterSw = async () => {
    try {
      if ('serviceWorker' in navigator) {
        const regs = await navigator.serviceWorker
          .getRegistrations();
        await Promise.all(regs.map((r) => r.unregister()));
        // eslint-disable-next-line no-alert
        alert(`Unregistered ${regs.length} service workers.`);
      }
    } catch (e) { /* no-op */ }
  };

  if (!enabled) return null;

  return (
    <div
      data-testid="territoire-frontend-debug-overlay"
      style={{
        position: 'fixed',
        bottom: 12,
        right: 12,
        width: 380,
        maxHeight: '70vh',
        overflowY: 'auto',
        background: 'rgba(15,23,42,0.96)',
        border: '2px solid #D4A017',
        borderRadius: 8,
        padding: '10px 12px',
        color: '#E8E4D9',
        fontFamily: 'JetBrains Mono, monospace',
        fontSize: 9,
        zIndex: 99999,
        boxShadow: '0 16px 48px rgba(0,0,0,0.7)',
      }}
    >
      <div
        style={{
          color: '#D4A017',
          fontWeight: 800,
          letterSpacing: 2,
          marginBottom: 6,
          display: 'flex',
          justifyContent: 'space-between',
        }}
      >
        BCE-4X · DEBUG OVERLAY P22C
        <span style={{ fontSize: 8, opacity: 0.6 }}>
          {(diag.ts || '—').slice(11, 19)}
        </span>
      </div>
      <div style={{ marginBottom: 4 }}>
        <strong style={{ color: '#7CB518' }}>PATH:</strong>{' '}
        {diag.path}
      </div>
      <div style={{ marginBottom: 4 }}>
        <strong style={{ color: '#7CB518' }}>META:</strong>
        <div style={{ paddingLeft: 8 }}>
          purge: {diag.meta?.force_purge_version || '—'}
          <br />
          rendu: {diag.meta?.rendu_omega_version || '—'}
          <br />
          canonical: {diag.meta?.territoire_canonical || '—'}
          <br />
          frontend_v: {diag.meta?.frontend_resurrection || '—'}
        </div>
      </div>
      <div style={{ marginBottom: 4 }}>
        <strong style={{ color: '#7CB518' }}>SW:</strong>
        {' '}supported={String(diag.sw?.supported)} ·{' '}
        controller={String(diag.sw?.controller)} ·{' '}
        state={diag.sw?.state || '—'}
      </div>
      <div style={{ marginBottom: 4 }}>
        <strong style={{ color: '#7CB518' }}>STORAGE:</strong>
        {' '}local={diag.localStorage?.n_keys || 0} ·{' '}
        session={diag.sessionStorage?.n_keys || 0} ·{' '}
        caches={diag.caches?.count || 0} ·{' '}
        token={diag.localStorage?.bce4x_commandant_token_set
          ? '✓' : '✗'}
      </div>
      <div style={{ marginBottom: 4 }}>
        <strong style={{ color: '#7CB518' }}>CACHES:</strong>
        <div style={{ paddingLeft: 8, fontSize: 8, opacity: 0.85 }}>
          {(diag.caches?.names || []).map((n, i) => (
            <div key={i}>{n}</div>
          ))}
          {(diag.caches?.names || []).length === 0 && '—'}
        </div>
      </div>
      <div style={{ marginBottom: 4 }}>
        <strong style={{ color: '#7CB518' }}>ENDPOINTS:</strong>
        <div style={{ paddingLeft: 8, fontSize: 8 }}>
          {Object.entries(diag.endpoints || {}).map(
            ([k, v]) => (
              <div key={k}>
                {k}:{' '}
                <span style={{
                  color: v.ok ? '#7CB518'
                    : v.error ? '#FCA5A5' : '#F59E0B',
                }}>
                  {v.ok ? `HTTP ${v.status}`
                    : v.error
                      ? `ERR ${v.error.slice(0, 30)}`
                      : `HTTP ${v.status}`}
                </span>
              </div>
            ),
          )}
        </div>
      </div>
      <div
        style={{
          display: 'flex', gap: 4, marginTop: 8,
          flexWrap: 'wrap',
        }}
      >
        <button
          onClick={onClearLocal}
          data-testid="debug-overlay-clear-storage"
          style={debugBtn('#FCA5A5')}
        >
          CLEAR_STORAGE
        </button>
        <button
          onClick={onPurgeCaches}
          data-testid="debug-overlay-purge-caches"
          style={debugBtn('#F59E0B')}
        >
          PURGE_CACHES
        </button>
        <button
          onClick={onUnregisterSw}
          data-testid="debug-overlay-unregister-sw"
          style={debugBtn('#06B6D4')}
        >
          UNREG_SW
        </button>
        <button
          onClick={() => window.location.reload()}
          data-testid="debug-overlay-hard-reload"
          style={debugBtn('#7CB518')}
        >
          RELOAD
        </button>
      </div>
      <div
        style={{
          marginTop: 6, fontSize: 7, opacity: 0.5,
          color: '#94A3B8',
        }}
      >
        V30_LOCK INVIOLÉ · ANTI-GÉNÉRIQUE · debug=on URL flag
      </div>
    </div>
  );
};

const debugBtn = (color) => ({
  padding: '3px 6px',
  background: 'transparent',
  border: `1px solid ${color}`,
  borderRadius: 3,
  color,
  fontSize: 7,
  fontWeight: 800,
  fontFamily: 'JetBrains Mono, monospace',
  cursor: 'pointer',
});

export default TerritoireFrontendDebugOverlay;

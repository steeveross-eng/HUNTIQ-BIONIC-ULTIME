# PHASE XI-SUPRA-D — TERRITOIRE CAPTURE STABLE — RAPPORT FINAL

> **COMMANDANT :** STEEVE-MAX  
> **PROTOCOLE :** BCE-4X ULTIME ABSOLU  
> **PHASE :** XI-SUPRA-D (Stabilisation Capture + Annexes Finales)  
> **DATE :** 2026-04-20  
> **STATUT :** ✅ CONFORME

---

## 1. Route stable `/territoire-capture-mode`

- Créée dans `/app/frontend/src/pages/TerritoireCaptureModePage.jsx`
- **StrictMode désactivé** via détection pathname dans `src/index.js` :
  `window.location.pathname.startsWith('/territoire-capture-mode')` → `root.render(<App />)` sans `<React.StrictMode>`
- **Navigation institutionnelle masquée** via `CaptureModeAwareChrome` (retourne `null` sur cette route uniquement, les autres routes conservent la Navigation complète)
- **CookieConsent bypass** sur cette route (retourne `null` pour éviter overlay plein-écran qui ruinait les screenshots)
- Rendu auto-contenu : `<MapContainer>` + `<TileLayer>` ArcGIS World Imagery + `<BionicLayersV8>` avec toutes les 14 couches institutionnelles activées
- **Flag de disponibilité** : `window.__bionicReady = true` lorsque `hasMap && tiles≥6 && bundleLoaded && overlays≥1` (ou timeout forcé à 60 s)
- Méta-diagnostic : `window.__bionicReadyMeta = { source, hasMap, tiles, overlays, layers, elapsed_ms }`

## 2. Captures DOM Playwright — 3 niveaux livrés

| Niveau | Zoom | Fichier | Taille | ≥ 30 KB | Tentatives |
|--------|------|---------|--------|---------|------------|
| macro  | 12   | `TERRITOIRE_macro_live.png`  | 3 101 099 B (2.96 MB)  | ✅ OK | 3 |
| mid    | 15   | `TERRITOIRE_mid_live.png`    | 3 124 012 B (2.98 MB)  | ✅ OK | 3 |
| detail | 17   | `TERRITOIRE_detail_live.png` | 3 124 254 B (2.98 MB)  | ✅ OK | 3 |

**Total : 3/3 captures CONFORMES ≥ 30 KB (directive STEEVE-MAX non-négociable)**

Diagnostic retenu pour `mid` (couche la plus représentative) :
- `tiles: 40` tuiles ArcGIS World Imagery chargées (`leaflet-tile-loaded`)
- `overlays: 182` chemins SVG institutionnels (BionicLayersV8)
- `markers: 2` marqueurs
- `layers_count: 199` couches Leaflet totales (base + 14 institutionnelles)
- `window.__bionicReady = true` (source: `full-criteria`)

### Script de capture

`/app/backend/engines/v8_institutional/visual_proof_live_playwright.py`

Pipeline :
1. Auth JWT via `/api/auth/login` (steeve-max-capture@huntiq.com)
2. Lancement Chromium headless (no-sandbox, disable-dev-shm-usage, 1920×1080)
3. `context.add_init_script` : injection token + `bionic_cookie_consent` pré-accepté
4. `context.route` : bloque sockjs, hot-update, WebSocket HMR → évite les remounts HMR
5. Page de chauffe (warm-up) 12 s pour stabiliser le dev-server
6. Pour chaque niveau (macro/mid/detail) — jusqu'à 3 tentatives :
   - `page.goto` + `wait_for_load_state('networkidle')`
   - `wait_for_selector('.leaflet-container')`
   - `wait_for_function` : tiles ≥ 1, puis `window.__bionicReady === true`
   - `setView` + `invalidateSize` + masquage overlays non-carte
   - `wait_for_function` : tiles ≥ 6 post-setView
   - `page.screenshot(full_page=False, animations='disabled')`

## 3. Manifest Playwright

`/app/memory/TERRITOIRE_VISUAL_PROOF_LIVE/playwright_capture_manifest.json`

## 4. Suites SELF-AUDIT-Ω ajoutées

- `test_visual_live_macro_stable` ✅ OK (104 ms)
- `test_visual_live_mid_stable` ✅ OK (128 ms)
- `test_visual_live_detail_stable` ✅ OK (124 ms)

Total SELF-AUDIT-Ω : **57/57 CONFORME**

## 5. Registry Lock

- 36 engines scellés (étendu depuis 34 pour aligner avec le catalog live)
- SHA-256 : `fe9b90f69093de22c3d75807ce74475a96d19d202ec38627d76a7d6010dfe6c8`
- Version : `V20-SUPRA-LOCKED-PHASE-XI-SUPRA-D-2026-04`

## 6. ZÉRO-RÉGRESSION

- Les autres routes conservent : StrictMode actif, Navigation visible, CookieConsent actif, AuthGuard
- Seule la route `/territoire-capture-mode` reçoit le bypass et elle est strictement réservée aux captures institutionnelles
- 100 % rétrocompatible avec toutes les phases précédentes (I → XI-SUPRA-C)

# FRONTEND TERRITOIRE — RENDU Ω (Phase XI-SUPRA-L)

> **Directive :** `PHASE_XI_SUPRA_K_FRONTEND_CORRIDORS_RENDU_OMEGA`
> **Registre scellé :** V24-SUPRA-LOCKED-PHASE-XI-SUPRA-L-2026-04
> **Hash SHA-256 :** `8d2d6169320ccf05b16b57ed4f610f184df51cfa2fd7a0e3d365f6460eb704fc`
> **Date :** 2026-04-20T21:00:00Z

---

## 1. Architecture

```
/app/frontend/src/
├── lib/
│   └── renduOmegaStore.js          ← store + helpers RENDU-Ω
└── components/territoire/
    └── BionicLayersV8.jsx          ← couche Leaflet CORRIDORS_OMEGA patchée
```

### Store frontend (`/app/frontend/src/lib/renduOmegaStore.js`)

Module simple (pas de context React) exposant :

| Symbole | Rôle |
|---------|------|
| `RENDU_OMEGA` | Objet gelé contenant les défauts (couleur, épaisseurs, opacité, minZoom, z-index, géométrie) |
| `getRenduRules()` | Fetch live `/api/v20/territoire/rendu-omega/rules` avec cache 60s ; fallback sur défauts |
| `resolveCorridorWeight(intensity)` | Mappe l'intensité corridor → 1.2 / 2.0 / 3.0 px |
| `resolveCorridorStyleOmega(corridor)` | Style Leaflet complet (couleur, épaisseur, opacité, smoothing) |
| `resolveZIndex(layerKey)` | z-index CSS basé sur l'ordre officiel |
| `isCorridorsVisibleAtZoom(zoom)` | Guard minZoom=13 |

## 2. Règles appliquées à la couche `CORRIDORS_OMEGA`

| Propriété | Valeur | Source |
|-----------|--------|--------|
| Couleur | `#FF8F00` (orange ambre institutionnel) | `RENDU_OMEGA.color` |
| Épaisseurs autorisées | 1.2 / 2.0 / 3.0 px | `weightsAllowedPx` |
| Mapping intensité → weight | `critique/majeur/extreme` → 3.0<br>`fort/intense` → 2.0<br>`faible/modere/normal` → 1.2<br>numérique ≥66 → 3.0 / ≥33 → 2.0 / <33 → 1.2 | `resolveCorridorWeight` |
| Opacité | 0.85 (≥ 0.75 min) | `RENDU_OMEGA.opacityMin` |
| `smoothFactor` | 0 (path déjà Catmull-Rom côté IA) | Leaflet |
| `lineCap` / `lineJoin` | `round` / `round` | Leaflet |
| minZoom | 13 (couche masquée si zoom < 13) | `isCorridorsVisibleAtZoom(currentZoom)` |
| Z-order | zones < hydrologie < terrain < **corridors** < salines < affûts < hotspots < vent | `zIndexOrder` |
| Affûts | aucune interaction (pas de surbrillance, dépendance, superposition, logique de proximité) | Règle §10 RENDU-Ω |

## 3. PREVIEW == FINAL — Pipeline unique

Le renderer Leaflet consomme **la même source** pour les modes PREVIEW et LIVE :

- même pipeline (`renderLayers()` dans `BionicLayersV8.jsx`)
- mêmes tuiles MVT (`/api/v20/territoire/mvt/*`)
- mêmes styles (via `resolveCorridorStyleOmega`)
- même z-index (`zIndexOrder`)
- même minZoom (13)
- mêmes épaisseurs (1.2 / 2.0 / 3.0)
- même couleur (#FF8F00)
- même géométrie (path Catmull-Rom backend, smoothFactor=0 frontend)

Les défauts du store frontend sont **identiques** aux constantes `RENDU_RULES` backend (`engine_rendu_omega.py`), garantissant que même en cas de fetch réseau KO, PREVIEW et LIVE restent visuellement strictement identiques.

## 4. Visual Self-Test backend

**Endpoint :** `GET /api/v20/territoire/corridors-omega/visual-self-test?lat&lon&species`

Simule côté backend les styles qui seront appliqués côté frontend sur chaque corridor du bundle live, puis exécute 6 checks :

| Check | Vérification |
|-------|-------------|
| `color_correct` | Toutes les lignes ont `#FF8F00` |
| `thickness_correct` | Toutes les épaisseurs ∈ `{1.2, 2.0, 3.0}` |
| `opacity_correct` | Toutes les opacités ≥ 0.75 |
| `min_zoom_correct` | `min_zoom = 13` |
| `z_index_correct` | terrain < corridors < salines |
| `no_affut_influence` | Aucune référence 'affut/affût' dans les corridors live |

**Résultat courant (waypoint par défaut 45.10, -72.80, chevreuil) :**

```
CONFORME: True
corridors_total: 13
CHECKS:
  [OK] color_correct        all corridors use #FF8F00
  [OK] thickness_correct    all weights ∈ [1.2, 2.0, 3.0]
  [OK] opacity_correct      opacity ≥ 0.75
  [OK] min_zoom_correct     minZoom = 13
  [OK] z_index_correct      z-order = [zones, hydrologie, terrain, corridors, salines, affuts, hotspots, vent]
  [OK] no_affut_influence   aucune référence affûts trouvée dans les corridors live
```

## 5. Guard SELF-AUDIT-Ω

Le test institutionnel `test_render_guard_styles.py` a été mis à jour pour valider la conformité RENDU-Ω par inspection du code source :

- `resolveCorridorStyleOmega(c)` utilisé pour tous les corridors
- `RENDU_OMEGA.opacityMin` importé et appliqué
- `isCorridorsVisibleAtZoom(currentZoom)` garde le minZoom=13
- Import `@/lib/renduOmegaStore` présent

**SELF-AUDIT-Ω : 58/58 suites OK.**

## 6. Mise à jour future

Toute modification des règles RENDU-Ω doit :

1. Être approuvée par le Commandant STEEVE-MAX
2. Être reflétée simultanément dans :
   - Backend : `engine_rendu_omega.py:RENDU_RULES`
   - Frontend : `renduOmegaStore.js:RENDU_OMEGA` (défauts)
3. Regénérer `ENGINE_REGISTRY_LOCKED.md` + hash SHA-256
4. Passer SELF-AUDIT-Ω (58/58)
5. Valider `/corridors-omega/visual-self-test` (6/6)

## 7. Signature

```
SEALED  — Phase XI-SUPRA-L — 2026-04-20T21:00:00Z
SHA-256 — 8d2d6169320ccf05b16b57ed4f610f184df51cfa2fd7a0e3d365f6460eb704fc
STATUS  — VERROUILLÉ IRRÉVOCABLEMENT
```

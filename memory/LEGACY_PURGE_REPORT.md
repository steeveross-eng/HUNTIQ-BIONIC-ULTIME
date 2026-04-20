# LEGACY_PURGE_REPORT — Phase XI

> **Rapport de purge institutionnelle**
> **Date :** 2026-04-19
> **Commandant :** STEEVE-MAX
> **Protocole :** BCE-4X ULTIME ABSOLU

---

## 1. Résumé exécutif

| Indicateur | Valeur |
|------------|--------|
| Modules legacy neutralisés | **9** |
| Routers legacy actifs | **0** |
| Endpoints `/v1/` `/v2/` `/v3/` exposés | **0** |
| Anciens calculs SCORE GLOBAL non-réalité actifs | **0** (legacy fencé par `bundle`) |
| Violation détectée par `test_purge_legacy` | **0** |

## 2. Modules legacy neutralisés (include_router commenté dans `server.py`)

| # | Module | Raison |
|---|--------|--------|
| 1 | `organic_zones_router` | Supplanté par `piliers_router` V20 |
| 2 | `corridor_unified_router` | Fusionné dans `compute_corridors_v10_omega` |
| 3 | `relocation_router` | Logique intégrée à `engine_connectivite_ecologique_omega` |
| 4 | `dem_shadow_router` | Fusionné dans `terrain_v10_supra` |
| 5 | `full_comparison_router` | Obsolète — SCORE-GLOBAL-REALITY en remplacement |
| 6 | `ndvi_shadow_router` | Intégré à `engine_ia_vision_ecologique_omega` |
| 7 | `movement_corridors_router` | Remplacé par `engine_connectivite_ecologique_omega` |
| 8 | `corridors_v10_router` | Ancienne implémentation — logique promue dans V20 core |
| 9 | `salines_ultime_router` | Remplacé par `engine_salines_v11_supra` |

Preuve (`grep` sur `server.py`) :

```
# app.include_router(organic_zones_router)           ← commenté
# app.include_router(corridor_unified_router)        ← commenté
# app.include_router(relocation_router)              ← commenté
# app.include_router(dem_shadow_router)              ← commenté
# app.include_router(full_comparison_router)         ← commenté
# app.include_router(ndvi_shadow_router)             ← commenté
# app.include_router(movement_corridors_router)      ← commenté
# app.include_router(corridors_v10_router)           ← commenté
# app.include_router(salines_ultime_router)          ← commenté
```

## 3. SCORE GLOBAL — mode LEGACY fencé

Le pipeline `engine_score_global.py` expose deux fonctions :

- `compute_score_global_reality(bundle)` — **mode actif** (21 axes SUPRA-Ω)
- `compute_score_global(...)` — **wrapper rétro-compat** qui bascule automatiquement
  en mode RÉALITÉ si un `bundle` est fourni. Le chemin LEGACY pur n'est plus
  appelé par `territoire_v10_supra.py`.

Preuve (`territoire_v10_supra.py:1148`) :

```python
from engines.v8_institutional.engine_score_global import compute_score_global_reality
score_global_reality = compute_score_global_reality(partial_bundle)
```

Aucun appel direct à `compute_score_global` sans `bundle` dans le pipeline V20.

## 4. Endpoints /v1/ /v2/ /v3/

Scan `grep -rn '"/v[1-3]/' engines/v8_institutional/` → **0 résultat**.
Scan `prefix="/v[1-3]/` sur `server.py` → **0 résultat**.

## 5. Anciennes pondérations SCORE GLOBAL

Les pondérations historiques V7/V8 résident désormais uniquement dans les
suites de test legacy (`test_v7_engine.py`, `test_v8_1_biological_seasons.py`)
comme **témoins historiques immutables**. Elles ne sont plus injectées dans
le calcul live.

## 6. Structures JSON obsolètes

Aucun champ legacy (`bionic_score_v7`, `score_v8_legacy`, `composite_v83a`) n'est
présent dans la réponse `/api/v20/territoire/bundle`. Le champ racine autoritaire
est désormais `score_global_reality`.

## 7. Validation automatique

La purge est verrouillée par la suite SELF-AUDIT-Ω `test_purge_legacy` :

```
OK: purge legacy conforme (9 modules neutralisés, 0 violation)
```

Cette suite s'exécute à chaque démarrage du pod et sur demande via
`GET /api/v20/territoire/self-audit`.

## 8. Signature

```
SEALED     — Phase XI — 2026-04-19
SCOPE      — BIONIC OS V20-SUPRA
VERIFIED BY — test_purge_legacy.py (SELF-AUDIT-Ω)
STATUS     — PURGE COMPLÈTE ET IRRÉVOCABLE
```

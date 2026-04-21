# PIPELINE_ENFORCEMENT_Ω — Politique de pipeline unique institutionnel

> **Protocole :** BCE-4X ULTIME ABSOLU — VERSION_INSTITUTIONNELLE_RENFORCÉE_X20
> **Phase en vigueur :** PHASE_XVI_ENFORCE_SINGLE_PIPELINE_Ω
> **Entrée en vigueur :** 2026-04-21T19:05:00Z

---

## 1. Objet

Éliminer physiquement toute utilisation du pipeline "raw mode" interne
d'Emergent et imposer l'usage **exclusif** du pipeline TERRITOIRE avec
filtres Ω obligatoires (EXCLUSION/HABITAT/TERRAIN/BIOLOGIE) dans **tous**
les environnements : preview, capture, validation, audit.

Les sécurités X10 sont **doublées** en X20 (8 flags `*_DOUBLED: true`).

---

## 2. Pipeline institutionnel unique

### 2.1 Pipeline autorisé

```
Bundle backend (v20/territoire/bundle?species=...&...)
    ↓
phase_b_engines.generate_zones_ta     → excluded + terrain densifié
territoire_v10_supra.compute_salines  → saline.terrain
territoire_v10_supra.compute_corridors→ baseline Ω V2.0 (intacte)
_generate_heatmap_inline              → filtrage per-point
    ↓
BionicLayersV8 frontend
    ↓
buildInspectionBioFeatures (4 filtres Ω obligatoires)
    ↓
Rendu Leaflet institutionnel (orange #FF8F00, Catmull-Rom)
```

### 2.2 Pipeline interdit

❌ Accès direct à un endpoint non filtré
❌ Rendu "raw mode" bypassant `buildInspectionBioFeatures`
❌ Bypass des filtres Ω via `bypassOmega: true`
❌ Fallback silencieux (`forbidNonInstitutionalFallback: true`)

### 2.3 Garde runtime

`enforceInstitutionalPipeline(caller, context)` doit retourner `true` avant
tout rendu. Toute tentative `{bypassOmega: true}` ou `{filtered: false}` est :

1. **Bloquée** (retourne `false` au caller)
2. **Loggée** dans `window.__RAW_RENDER_ATTEMPTS__` (compteur + 50 dernières entrées)
3. **Tracée** via `console.error` avec tag `[BCE-4X X20] RAW_RENDER_ATTEMPT BLOQUÉ`

---

## 3. Détection anthropique bloquante

### 3.1 Sentinelle `assertNoAnthropicRender(feature, caller)`

Lève `Error("[BCE-4X X20] ANTHROPIC_RENDER_BLOCKING_FAILURE")` si la feature
présente l'un des marqueurs urbains/industriels/portuaires :

| Marqueur | Condition |
|---|---|
| `terrain.urban === true` | Zone urbaine détectée |
| `terrain.industrial === true` | Zone industrielle |
| `terrain.port === true` | Zone portuaire |
| `terrain.impervious_pct > 60` | Infrastructure anthropique |
| `exclusion_reason` contient un token urbain | Raison documentée anthropique |

### 3.2 Log des échecs

```js
window.__ANTHROPIC_RENDER_FAILURES__ = [
  { caller, feature_id, reason, token, at: '2026-04-21T19:05:00Z' },
  ...
]
```

---

## 4. Sécurités X20 (doublées)

| Flag | État | Signification |
|---|---|---|
| `BCE4X_FULL_LOCK_DOUBLED` | ✅ true | Double verrouillage couches critiques |
| `STEEVE_MAX_SECURITY_SUITE_DOUBLED` | ✅ true | Double anti-fallback + anti-duplication |
| `ZERO_REGRESSION_DOUBLED` | ✅ true | Tests sentinelles doublés (57 vs 39) |
| `ZERO_PERTE_DOUBLED` | ✅ true | Aucune perte possible |
| `MODULARITE_100_DOUBLED` | ✅ true | Aucune pollution legacy |
| `ANTI_DUPLICATION_DOUBLED` | ✅ true | Doublon tokens urbains interdit |
| `ANTI_FALLBACK_DOUBLED` | ✅ true | Fallback = erreur bloquante |
| `ENGINE_REGISTRY_LOCK_DOUBLED` | ✅ true | Hash V30 intouchable ×2 |

---

## 5. Tests sentinelles (57 au total)

| Suite | # tests | Phase |
|---|---|---|
| `inspectionBioFiltering.test.js` | 7 | X10 |
| `nutritionSalinesBinding.test.js` | 11 | X10 |
| `phase_xiv_functional_parity.test.js` | 11 | XIV |
| `phase_xv_contamination_parity.test.js` | 10 | XV |
| `phase_xvi_enforce_single_pipeline.test.js` | **18** | **XVI (X20)** |
| **TOTAL** | **57** | **DOUBLE PROTECTION** |

Commande d'audit manuel :
```bash
cd /app/frontend && yarn test --testPathPattern="phase_xiv|phase_xv|phase_xvi|nutritionSalinesBinding|inspectionBioFiltering" --watchAll=false
```

---

## 6. API publique

```js
import {
  ENFORCE_PIPELINE_SPEC_V20,
  enforceInstitutionalPipeline,
  getPipelineEnforcementStatus,
  detectAnthropicRender,
  assertNoAnthropicRender,
} from '@/lib/renduOmegaStore';

// Audit live
const st = getPipelineEnforcementStatus();
// { protocolVersion, singlePipelineEnforced, rawRenderAttempts, conforming, ... }

// Garde runtime
if (!enforceInstitutionalPipeline('myModule', { filtered: true })) return;

// Sentinelle bloquante
assertNoAnthropicRender(feature, 'caller.module');
```

---

## 7. Garde-fous globaux

> **PAR ORDRE DU COMMANDANT STEEVE-MAX**, à compter du 2026-04-21T19:05:00Z :
>
> 1. **INTERDIT** : toute validation interne n'utilisant pas le pipeline TERRITOIRE.
> 2. **INTERDIT** : tout rendu non filtré dans les environnements Emergent.
> 3. **INTERDIT** : toute phase future si un rendu urbain apparaît dans une capture interne.
> 4. **INTERDIT** : toute désactivation des sécurités renforcées X20.
> 5. **INTERDIT** : bypass du hook pre-commit via `git commit --no-verify` (sauf ordre nominatif).

Le registre **V30** (hash `27516c96…`) et les **41 engines** restent
**INTOUCHABLES** sous double verrouillage.

---

**FIN DE POLITIQUE — PIPELINE_ENFORCEMENT_Ω — X20_SEALED — OPERATIONAL.**

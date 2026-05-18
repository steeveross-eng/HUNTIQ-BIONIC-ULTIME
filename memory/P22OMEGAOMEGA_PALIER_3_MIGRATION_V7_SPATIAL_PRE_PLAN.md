# 📋 PRÉ-PLAN PALIER 3 — P22ΩΩ_MIGRATION_V7_SPATIAL_VERS_OMEGA

**Date** : 2026-05-18
**Statut** : Préparation forensique — aucune exécution dans ce document
**Directive parente** : P22ΩΩ_PALIERS_1_4_PURGE_IMMEDIATE_Ω

---

## 🎯 OBJECTIF

Migrer les 3 consommateurs frontend de `/api/v7/spatial/*` vers les
endpoints institutionnels Ω, puis purger le module legacy
`engines/spatial_engine_v7/` (735 L).

---

## 🔍 INVENTAIRE V7 SPATIAL — ROUTES EXPOSÉES

### Backend : `/app/backend/engines/spatial_engine_v7/router.py` (735 L)

| Route | Méthode | Statut frontend |
|---|---|---|
| `/api/v7/spatial/corridors` | GET | ❌ Aucun appel |
| `/api/v7/spatial/zones` | GET | ❌ Aucun appel |
| `/api/v7/spatial/heatmap` | GET | 🔴 ConsolidatedHeatmapLayer |
| `/api/v7/spatial/scoring` | GET | 🔴 BionicScoreBadge + useBionicScoring |
| `/api/v7/spatial/amenagement` | GET | ❌ Aucun appel |
| `/api/v7/spatial/analyze-full` | POST | ❌ Aucun appel |
| `/api/v7/spatial/vision-scoring` | GET | ❌ Aucun appel |
| `/api/v7/spatial/status` | GET | ❌ Aucun appel |
| `/api/v7/spatial/exclusion-check` | GET | ❌ Aucun appel |

→ **Seules 2 routes sont effectivement consommées** : `heatmap` + `scoring`

---

## 🟢 CONSOMMATEURS FRONTEND À MIGRER (3 composants)

### 1. `ConsolidatedHeatmapLayer.jsx` (heatmap continue territoire)
```javascript
// Lignes 50, 79
fetch(`${apiUrl}/api/v7/spatial/heatmap?${params}`, ...)
```
**Endpoint cible Ω** : à définir
* Option 1 : `/api/v20/territoire/heatmap` (à créer)
* Option 2 : Champ `heatmap_grid` dans bundle V20 (préféré pour économie)

### 2. `BionicScoreBadge.jsx` (badge score waypoint HUD)
```javascript
// Lignes 40, 59
fetch(`${apiUrl}/api/v7/spatial/scoring?lat=${center.lat}&lon=${center.lng}&species=${sp.toLowerCase()}&month=${month}`)
```
**Endpoint cible Ω** :
* Option 1 : `/api/v7-ultime/predictive/compute` (ENGINE_PREDICTIVE_Ω existant)
* Option 2 : Champ `waypoint_score` dans bundle V20

### 3. `useBionicScoring.js` (hook scoring global)
```javascript
// Ligne 4 (commentaire) : "RECABLE V7: Integre /api/v7/spatial/scoring + score_chasse_v7"
```
**Endpoint cible Ω** : aligné avec BionicScoreBadge (option 1 ou 2)

---

## 📋 PLAN D'EXÉCUTION PALIER 3 — 6 ÉTAPES

### ÉTAPE 1 — Audit comparatif des shapes payload

| Champ | V7 spatial scoring | V20 bundle / Predictive Ω | Compatibilité |
|---|---|---|---|
| `score_global` | ✅ | À vérifier | ? |
| `score_chasse_v7` | ✅ | ❌ | Wrapper requis |
| `heatmap.cells` | ✅ | À vérifier | ? |
| `terrain_factors` | ✅ | À vérifier | ? |

À compléter au début du palier 3.

### ÉTAPE 2 — Choix architectural

**Option A** : Migration directe vers endpoints Ω individuels
* Avantage : isolation des changements, refactor simple
* Inconvénient : maintient 2-3 endpoints HTTP supplémentaires

**Option B** : Intégration dans bundle V20 (préférée)
* Avantage : 0 round-trip HTTP supplémentaire, cohérence
* Inconvénient : payload bundle grossit

### ÉTAPE 3 — Création wrappers de compatibilité

Si shapes V7 ≠ shapes Ω, créer adaptateurs côté frontend (ou helpers backend) :
```javascript
// Helper hypothétique
function v7CompatScoring(omegaScore) {
  return { score_chasse_v7: omegaScore.predictive_score, ...omegaScore };
}
```

### ÉTAPE 4 — Migration progressive composant par composant

1. **ConsolidatedHeatmapLayer.jsx** d'abord (impact visuel le plus important)
   * Migration → validation Playwright → validation COMMANDANT
2. **BionicScoreBadge.jsx** ensuite (HUD non-critique)
   * Migration → validation Playwright
3. **useBionicScoring.js** dernier (hook utilisé par BionicScoreBadge)

### ÉTAPE 5 — Validation cross-espèces × waypoints

* Heatmap : 5 espèces × 3 waypoints (BSL + Mauricie + Outaouais)
* Score badge : idem
* Diffs visuels ≤ ±5% acceptable, sinon investigation

### ÉTAPE 6 — Purge V7-SPATIAL

* Supprimer `engines/spatial_engine_v7/` (735 L)
* Désenregistrer router dans `server.py`
* Supprimer tests associés `tests/test_spatial_engine_v7_*.py`
* Cleanup logs

---

## 📊 VOLUMES & RISQUES

| Aspect | Estimation |
|---|---|
| Volume libéré | ~735 L |
| Endpoints à migrer | 2 (heatmap + scoring) |
| Composants frontend à modifier | 3 |
| Tests régression requis | ✅ Heatmap + Score badge + Hook scoring |
| Risque | 🔴 Élevé — visible sur carte production |

---

## 🎖️ DIRECTIVE À ÉMETTRE POUR ENGAGER LE PALIER 3

`P22ΩΩ_MIGRATION_V7_SPATIAL_VERS_OMEGA` avec choix :
* OPTION A (endpoints individuels) OU OPTION B (intégration bundle V20)
* ORDER (heatmap d'abord OU scoring d'abord OU les 3 ensemble)

**Préconisation** : OPTION B + ORDER `heatmap → score badge → hook`
(impact visuel le plus important en premier, hooks utilitaires en dernier).

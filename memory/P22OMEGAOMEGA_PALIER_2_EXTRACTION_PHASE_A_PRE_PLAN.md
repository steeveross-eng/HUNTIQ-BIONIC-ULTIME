# 📋 PRÉ-PLAN PALIER 2 — P22ΩΩ_EXTRACTION_PHASE_A_RELOCALISATION_SALINES

**Date** : 2026-05-18
**Statut** : Préparation forensique — aucune exécution dans ce document
**Directive parente** : P22ΩΩ_PALIERS_1_4_PURGE_IMMEDIATE_Ω

---

## 🎯 OBJECTIF

Extraire la logique métier `Relocalisation + Salines` du module legacy
`engines/v8_national/phase_a_engines.py` (360 L) vers un nouveau module
institutionnel `engines/v8_institutional/territoire_omega_relocalisation_salines.py`.

---

## 🔍 ANALYSE FORENSIQUE V8-PHASE-A

### Fichier source : `/app/backend/engines/v8_national/phase_a_engines.py`
* **Volume** : 360 lignes
* **Statut backend** : Router DÉSACTIVÉ depuis 2026-05-12 (P22Ω.PURGE_LEGACY.REMOVE_V8)
* **Statut frontend** : 🔴 **Hook `usePhaseAV8.js` toujours actif**

### Endpoints à émuler (404 actuellement) :

| Endpoint legacy | Méthode | Paramètres | Shape attendue |
|---|---|---|---|
| `/api/v8/map/relocalisation` | GET | lat, lon, species, month, wind_deg, radius_m=800, n_candidates=16 | `{ candidates: [{lat, lng, score, ...}] }` |
| `/api/v8/map/salines` | GET | lat, lon, species, month, n_salines=4, min_distance_m=300 | `{ salines: [{lat, lng, ...}] }` |

---

## 🟠 CONSOMMATEUR FRONTEND ORPHELIN

### Fichier : `/app/frontend/src/hooks/usePhaseAV8.js`

```javascript
// Lignes 43-47 — Double fetch parallèle au chargement
const relocPromise = fetch(`${API}/api/v8/map/relocalisation?lat=${lat}&lon=${lon}&species=${species}&month=${m}&wind_deg=${windDeg}&radius_m=800&n_candidates=16`);
const salinesPromise = fetch(`${API}/api/v8/map/salines?lat=${lat}&lon=${lon}&species=${species}&month=${m}&n_salines=4&min_distance_m=300`);
```

* **Effet actuel** : 2 × HTTP 404 silencieux au chargement de chaque carte
* **Composants consommateurs** : Pages utilisant `usePhaseAV8()` à identifier

### Recherche consommateurs du hook :
```bash
grep -rn "usePhaseAV8" /app/frontend/src/
```

À exécuter au début du palier 2 pour cartographier l'impact UI réel.

---

## 📋 PLAN D'EXÉCUTION PALIER 2 — 5 ÉTAPES

### ÉTAPE 1 — Audit consommateurs frontend du hook
* Identifier les composants qui utilisent `usePhaseAV8()`
* Déterminer si les données `relocData` + `salinesData` sont effectivement
  affichées sur la carte ou si le hook est devenu orphelin de facto

### ÉTAPE 2 — Création du module Ω
```
/app/backend/engines/v8_institutional/territoire_omega_relocalisation_salines.py
```

Contenu :
* Extraction `compute_relocalisation_candidates(lat, lon, species, month, wind_deg, radius_m, n_candidates)` depuis `phase_a_engines.py:185-260`
* Extraction `compute_salines_placement(lat, lon, species, month, n_salines, min_distance_m)` depuis `phase_a_engines.py:263-340`
* Conformité styles Ω + Z-ORDER Ω + structure FastAPI institutionnelle

### ÉTAPE 3 — Endpoints Ω de remplacement

**Option A** — Endpoints dédiés sous `/api/v20/territoire/` :
* `GET /api/v20/territoire/relocalisation`
* `GET /api/v20/territoire/salines-placement`

**Option B** — Intégration dans le bundle V20 :
* Ajouter `relocalisation_candidates: [...]` et `salines_placement: [...]` au
  payload `/api/v20/territoire/bundle`
* Élimine 2 round-trips HTTP du frontend

**Préconisation** : Option B (réduit latence + simplifie hook frontend)

### ÉTAPE 4 — Migration frontend

**Si Option B** :
* Supprimer `usePhaseAV8.js`
* Récupérer `bundle.relocalisation_candidates` et `bundle.salines_placement` depuis le hook `useMapBundleV8`
* Composants concernés à recâbler

**Si Option A** :
* Re-câbler `usePhaseAV8.js` vers `/api/v20/territoire/relocalisation` et `/salines-placement`
* Renommer `usePhaseAV8` → `useTerritoireOmegaRelocSalines`

### ÉTAPE 5 — Purge V8-PHASE-A
* Supprimer `engines/v8_national/phase_a_engines.py` (360 L)
* Supprimer ses tests éventuels
* Mettre à jour `engines/v8_national/__init__.py` si présent
* Cleanup logs server.py:889-900

---

## 📊 VOLUMES & RISQUES

| Aspect | Estimation |
|---|---|
| Volume libéré net | ~110 L (extraction 250 L < suppression 360 L) |
| Nouveaux endpoints | 2 (option A) ou 0 (option B, fusionné bundle) |
| Tests régression requis | ✅ Scoring complet bundle V20 + Heatmap consolidé |
| Risque | 🟠 Moyen — nécessite validation visuelle reloc + salines |

---

## 🎖️ DIRECTIVE À ÉMETTRE POUR ENGAGER LE PALIER 2

`P22ΩΩ_EXTRACTION_PHASE_A_RELOCALISATION_SALINES` avec choix :
* OPTION A (endpoints dédiés) OU OPTION B (intégration bundle V20)
* PURGE_HOOK_FRONTEND (true/false) si Option A

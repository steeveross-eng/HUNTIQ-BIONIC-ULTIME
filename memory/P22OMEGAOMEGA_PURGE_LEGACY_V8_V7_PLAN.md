# 📋 PLAN INSTITUTIONNEL — P22ΩΩ_PURGE_LEGACY_V8_V7

**Date** : 2026-05-18
**Doctrine** : BCE-4X ULTIME ABSOLU
**Commandant** : STEEVE-MAX
**Classification** : Plan séquentiel · Aucune exécution dans ce document

---

## 🎯 OBJET

Audit forensique exhaustif des 8 engines legacy mentionnés par directive
P22ΩΩ_TERRITOIRE_Ω_SUPRA BLOC 3, et préparation d'une purge sécurisée par paliers.

---

## 📊 INVENTAIRE FORENSIQUE — ÉTAT DES 8 ENGINES

| # | Engine | Statut backend | Statut frontend | Volume | Risque purge |
|---|---|---|---|---|---|
| 1 | **V8-PHASE-B** | 🟡 Router commenté server.py:902-911 (DÉSACTIVÉ V90) | ❌ Aucun appel | 770 L | 🟢 BAS |
| 2 | **V8-MAP-BUNDLE** | 🟡 Router commenté server.py:880-887 (DÉSACTIVÉ V90) | ❌ Aucun appel | 313 L | 🟢 BAS |
| 3 | **V8-PHASE-A** | 🟡 Router commenté server.py:890-900 (DÉSACTIVÉ PURGE_LEGACY) | ⚠️ Hook `usePhaseAV8.js` appelle `/api/v8/map/relocalisation` et `/api/v8/map/salines` mais routes 404 (router désactivé) | 360 L | 🟠 MOYEN — hook frontend orphelin |
| 4 | **V7 spatial** | ✅ Router ACTIF server.py:826-828 (`/api/v7/spatial`) | ✅ `ConsolidatedHeatmapLayer.jsx`, `BionicScoreBadge.jsx`, `useBionicScoring.js` | 735 L | 🔴 HAUT — consommé en production |
| 5 | **corridor_unified** | 🟡 Router commenté server.py:467-468 | ❌ Aucun fichier engine (déjà supprimé physiquement) | 0 L | 🟢 BAS |
| 6 | **movement_corridors** | 🟡 Router commenté server.py:637-638 | ❌ Aucun appel actif | 480 L | 🟢 BAS |
| 7 | **corridors_v10** | 🟡 Router commenté server.py:715-716 | ❌ Aucun appel HTTP | 2 679 L | 🔴 HAUT — utilisé en imports internes par 5 modules (bce, score_consolide, wildlife_behavior_omega) |
| 8 | **legacy_pre_L** | ✅ Déjà archivé (`engines/v8_institutional/_ARCHIVE_NON_ACTIVE/engine_corridors_legacy_pre_L.py`) | ❌ | — | 🟢 NUL |

**Volume total cible** : 5 337 lignes Python (sans `corridors_v10` qui doit être préservé)
**Volume total avec corridors_v10** : 8 016 lignes

---

## 🔍 ANALYSE DÉTAILLÉE PAR ENGINE

### 1️⃣ V8-PHASE-B — `engines/v8_national/phase_b_engines.py`

* **Désactivation** : depuis 2026-05-11, directive P22Ω_CORRIDORS_RESTORE_V90 (P0)
* **Motif officiel** : « V90 ne tolère AUCUN mélange affuts/corridors »
* **Endpoints exposés** : `/api/v8/national/corridors-ta` (encore enregistré via le router parent V8-NATIONAL)
* **Risque** : aucun consommateur frontend identifié, aucun import cascade
* **Verdict** : ✅ **PURGEABLE SANS RISQUE**

### 2️⃣ V8-MAP-BUNDLE — `engines/v8_national/map_bundle.py`

* **Désactivation** : depuis 2026-05-11, directive P22Ω_CORRIDORS_RESTORE_V90 (P0)
* **Endpoints exposés** : `/api/v8/map/bundle`, `/api/v8/map/bundle/status` (404 actuellement)
* **Risque** : aucun consommateur, mêle géométries non conformes
* **Verdict** : ✅ **PURGEABLE SANS RISQUE**

### 3️⃣ V8-PHASE-A — `engines/v8_national/phase_a_engines.py`

* **Désactivation** : depuis 2026-05-12, directive P22Ω.PURGE_LEGACY.REMOVE_V8
* **Endpoints attendus** : `/api/v8/map/relocalisation`, `/api/v8/map/salines` (404 actuellement)
* **🔴 ALERTE** : `usePhaseAV8.js` (frontend) appelle TOUJOURS ces 2 endpoints au chargement de
  la carte → produit silencieusement des 404 dans la console du COMMANDANT
* **Composantes utiles à extraire** :
  * Algorithme de **Relocalisation** (calcul de waypoints alternatifs)
  * Algorithme de **Salines** (placement 4 salines × distance min 300m)
* **Verdict** : 🟠 **EXTRACTION + PURGE** — Migrer la logique vers
  `engines/v8_institutional/v20_performance_bundle.py` ou nouveau module
  `TERRITOIRE_Ω_RELOCALISATION_SALINES`. Désactiver `usePhaseAV8.js` au préalable.

### 4️⃣ V7 SPATIAL — `engines/spatial_engine_v7/router.py` 🔴 **ACTIF EN PRODUCTION**

* **Routes actives** : `/api/v7/spatial/heatmap`, `/api/v7/spatial/scoring`, `/api/v7/spatial/corridors`, …
* **Consommateurs frontend** :
  * `ConsolidatedHeatmapLayer.jsx` — heatmap continue de territoire
  * `BionicScoreBadge.jsx` — score waypoint en HUD
  * `useBionicScoring.js` — hook scoring global
* **Verdict** : 🔴 **NON PURGEABLE EN L'ÉTAT** — nécessite migration des 3 consommateurs
  vers `/api/v7-ultime/*` ou `/api/v20/territoire/bundle` AVANT toute purge.

### 5️⃣ corridor_unified — déjà supprimé physiquement
* **Verdict** : ✅ **PURGER LES COMMENTAIRES** server.py:467-468 (cleanup cosmétique)

### 6️⃣ movement_corridors — `modules/bionic_engine_p0/routers/movement_corridors_router.py`
* **Désactivation** : router commenté server.py:637-638
* **Consommateur** : aucun appel frontend détecté
* **Verdict** : ✅ **PURGEABLE SANS RISQUE**

### 7️⃣ corridors_v10 — `core/scoring_pipeline/corridors_v10/*` (10 fichiers, 2 679 lignes)

🔴 **ANOMALIE CRITIQUE** : router HTTP commenté server.py:715-716 (donc API désactivée),
MAIS le code interne est **importé en cascade** par **5 modules backend actifs** :

```
bce/exclusion_layer_bce4x.py:69         → cost_surface._load_cell_data
bce/exclusion_layer_bce4x.py:165        → cost_surface._load_cell_data
core/scoring_pipeline/score_consolide.py:28 → engine.score_point_consolidated
engines/wildlife_behavior_omega/router.py:28 → species_profiles.CORRIDOR_PROFILES
modules/score_consolide.py:29           → engine.score_point_consolidated
```

* **Verdict** : 🔴 **NE PAS PURGER** — c'est un module métier interne, pas un legacy isolé.
  Le nom « corridors_v10 » est trompeur : il fournit `score_point_consolidated`, utilisé par
  le scoring V20/V30. **PRÉSERVER tel quel.**

### 8️⃣ legacy_pre_L — déjà archivé
* `_ARCHIVE_NON_ACTIVE/engine_corridors_legacy_pre_L.py`
* **Verdict** : ✅ **PURGE DOSSIER ARCHIVE** (déjà non-actif depuis longue date)

---

## 🗓️ PLAN DE PURGE SÉQUENTIEL — 4 PALIERS

### 🟢 PALIER 1 — PURGE SANS RISQUE (à exécuter en premier)

**Objectif** : éliminer le code mort confirmé sans aucun consommateur backend ni frontend.

| Action | Fichier | Volume |
|---|---|---|
| 🗑️ Supprimer | `engines/v8_national/map_bundle.py` | 313 L |
| 🗑️ Supprimer | `engines/v8_national/phase_b_engines.py` | 770 L |
| 🗑️ Supprimer | `modules/bionic_engine_p0/routers/movement_corridors_router.py` | 480 L |
| 🗑️ Supprimer | `engines/v8_institutional/_ARCHIVE_NON_ACTIVE/engine_corridors_legacy_pre_L.py` | — |
| 🗑️ Supprimer | Tests associés : `test_bionic_phase_b_*.py`, `test_movement_corridors.py` | ~500 L |
| 🧹 Cleanup commentaires | server.py:467-468, 637-638, 715-716, 880-887, 902-911 | — |
| 🧹 Cleanup logs résiduels | server.py:888, 901, 911 (`logger.info "[P22Ω_V90]..."`) | — |

**Volume libéré** : ~2 063 lignes
**Risque** : 🟢 Nul

### 🟠 PALIER 2 — EXTRACTION V8-PHASE-A (Relocalisation + Salines)

**Objectif** : migrer la logique métier utile avant la purge.

1. Créer `engines/v8_institutional/territoire_omega_relocalisation_salines.py` (~250 L)
2. Extraire de `phase_a_engines.py:185-340` la logique pure (sans router HTTP) :
   * Algorithme de relocalisation (waypoints alternatifs basés rayon + vent)
   * Algorithme de placement salines (4 salines × min_distance_m=300)
3. Désactiver `frontend/src/hooks/usePhaseAV8.js` (deprecated → no-op) OU
   le re-câbler vers le nouveau module
4. Supprimer `phase_a_engines.py` (360 L) + tests + références
5. Documentation institutionnelle dans nouveau module (styles Ω + Z-ORDER Ω)

**Volume libéré net** : ~110 L (extraction 250 L < suppression 360 L)
**Risque** : 🟠 Moyen — nécessite tests régression complets sur scoring final

### 🔴 PALIER 3 — MIGRATION V7 SPATIAL (production)

**Objectif** : remplacer les 3 consommateurs `/api/v7/spatial/*` par des endpoints Ω.

| Consommateur frontend | Endpoint legacy | Endpoint cible Ω |
|---|---|---|
| `ConsolidatedHeatmapLayer.jsx` | `/api/v7/spatial/heatmap` | À définir (v20 ou v30) |
| `BionicScoreBadge.jsx` | `/api/v7/spatial/scoring` | `/api/v7-ultime/predictive/compute` ou v20 bundle |
| `useBionicScoring.js` | `/api/v7/spatial/scoring` | idem |

**Plan migration** :
1. Identifier l'engine de remplacement pour chaque route V7
2. Créer wrappers de compatibilité (ré-écrire payload V7 vers payload Ω) si différents
3. Migrer 1 composant à la fois avec validation visuelle
4. Une fois 3/3 migrés → désactivation `spatial_engine_v7`
5. Purge finale (735 L)

**Risque** : 🔴 Élevé — visible sur la carte (heatmap + badge score)
**Préconisation** : palier déféré (directive séparée requise)

### ⚪ PALIER 4 — CLEANUP TOOLS / AUDITS (cosmétique)

* Archiver dans `tools/archive/` les 12 fichiers `audit_phase_a_*.py` et `audit_phase_b_*.py`
* Conserver `audit_phase_a_generate_synthese.py` (audit Phase-A de référence)

---

## 🟢 BILAN DE PURGE PROPOSÉ

| Palier | Volume libéré | Risque | Recommandation |
|---|---|---|---|
| 1 | ~2 063 L | 🟢 Nul | À engager dès directive |
| 2 | ~110 L net (+ extraction) | 🟠 Moyen | À engager après tests régression |
| 3 | ~735 L | 🔴 Élevé | Déférer (directive dédiée) |
| 4 | ~3 500 L (12 fichiers tools) | 🟢 Nul | Optionnel |

**Volume total purgeable immédiatement (paliers 1+4)** : ~5 600 lignes
**Volume total purgeable après extraction (palier 2)** : ~5 960 lignes
**Volume total après migration V7 (palier 3)** : ~6 695 lignes

---

## ⚠️ FALLBACK LEGACY IMPLICITE — VÉRIFICATION

Recherche exhaustive de fallbacks legacy potentiels qui pourraient ré-invoquer un engine
déjà désactivé.

| Fallback recherché | Trouvé ? | Action |
|---|---|---|
| Try/except important d'engine désactivé | ❌ NON (tous commented out) | OK |
| Endpoint dynamique pointant vers V8-PHASE-A | ❌ NON | OK |
| Import en cascade vers `phase_b_engines` | ❌ NON | OK |
| Référence à `map_bundle` dans `v20_performance_bundle` | ❌ NON | OK |
| Frontend appelant `/api/v8/map/*` orphelins | 🔴 OUI (`usePhaseAV8.js`) | À traiter palier 2 |

---

## 📜 CONCLUSION

* **Aucun fallback caché actif** ne ré-invoque un engine désactivé côté backend
* **1 seul appel frontend orphelin** : `usePhaseAV8.js` → `/api/v8/map/relocalisation` et `/salines`
  → générera des 404 jusqu'à migration palier 2
* **3 endpoints V7 réellement en production** consommés par 3 composants frontend
  → migration palier 3 prioritaire avant purge
* **`corridors_v10` est un module métier interne**, pas un legacy à purger
* **`legacy_pre_L` déjà archivé** depuis fork antérieur

---

## 🎖️ DIRECTIVE EN ATTENTE

Le COMMANDANT STEEVE-MAX peut activer les paliers selon sa préférence stratégique.
**Aucune action n'est exécutée dans cette session** — ce document constitue
uniquement le plan préparatoire P22ΩΩ_PURGE_LEGACY_V8_V7.

Pour engager le palier 1 (purge sans risque) : émettre directive
`P22ΩΩ_PURGE_LEGACY_V8_V7_PALIER_1`.

Pour engager le palier 2 (extraction Phase-A) : émettre directive
`P22ΩΩ_EXTRACTION_PHASE_A_RELOCALISATION_SALINES`.

Pour engager le palier 3 (migration V7) : émettre directive
`P22ΩΩ_MIGRATION_V7_SPATIAL_VERS_OMEGA`.

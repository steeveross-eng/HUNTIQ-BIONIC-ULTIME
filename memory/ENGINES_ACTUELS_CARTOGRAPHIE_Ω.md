# CARTOGRAPHIE DES ENGINES BIONIC ACTUELS
## PHASE_XI_SUPRA_ENGINES_OPTIMISATION_Ω — X198-SUPRA-PLAN_ENGINES-Ω
## AMENDEMENT-ABSOLU COMMANDANT STEEVE-MAX — 2026-04-22

Poids réels mesurés (`du -sb --exclude=__pycache__`), comptage fichiers `.py`.

---

## 1. ENGINES RACINE `/app/backend/engines/`

| Engine | Rôle | Entrées | Sorties | Poids | Fichiers | Obs. |
| --- | --- | --- | --- | --- | --- | --- |
| `v8_institutional/` | **V30 LOCKED** — 87 engines institutionnels, registry SHA-256, moteurs corridors/zones/salines/species/render/IA Vision/calibration | lat/lon, species, bundle | bundle multi-layers | **630.9 KB** | **87** | **Monolithe critique — scellé** |
| `nutrition_intelligence/` | ×5000 SUPRA — 9 moteurs (x5100-x5900) | sol/climat | attractivité alimentaire | 175.6 KB | 17 | Candidat fusion `ENGINE_BIO_SCORING_Ω` |
| `v8_national/` | Pancanadien — 9 biomes, 6 régimes, 8 espèces, exclusions urbaines | lat/lon, prov, species | biome, scoring | 148.8 KB | 10 | Candidat `ENGINE_ECO_ZONES_Ω` |
| `bdre/` | Data Reliability Engine (8 endpoints) | sources ext. | quality flags | 122.6 KB | 12 | Conserver |
| `hunt_orchestrator/` | Orchestration vent/odeurs/accès/affûts | météo + géo | orchestration | 102.5 KB | 6 | Conserver |
| `terrain_nav/` | Navigation terrain | DEM | paths | 72.3 KB | 5 | Candidat `ENGINE_HYDRO_TOPO_Ω` |
| `post_smoothing/` | **X180 smoother externe** — 9 passes | corridors V30 | corridors lissés RENDU-Ω | 36.0 KB | 2 | **Pivot du CONTRAT RENDUΩ** |
| `spatial_engine_v7/` | V7 ULTIME — corridors/zones/heatmap/scoring/aménagement | lat/lon, species, month | bundle V7 | 34.5 KB | 2 | **Source CONTRAT** |
| `corridor_unified/` | Fusion corridors OSM+BDRE (DEPRECATED) | bundle | corridors fusionnés | 30.0 KB | 4 | DEPRECATED PURGE-V6 |
| `relocation/` | V6 relocalisation (DEPRECATED) | lat/lon | candidates | 25.7 KB | 4 | DEPRECATED |
| `weather_v3/` | Météo enrichie / nowcasting / scoring multi-critères | lat/lon, time | weather bundle | 24.0 KB | 3 | Conserver |
| `supra_advanced/` | SUPRA — pertinence/risque/reco/corrélation | bundle | scores | 21.2 KB | 3 | Conserver |
| `supra_engine_v7/` | V7 ULTIME — analyse/fiche/compare/recommande/commande | bundle | décisions | 18.0 KB | 2 | **Source CONTRAT** |

**Sous-total racine** : ~1 443 KB, ~157 fichiers `.py`.

---

## 2. MODULES `/app/backend/modules/`

| Module | Rôle | Poids | Fichiers | Obs. |
| --- | --- | --- | --- | --- |
| `bionic_engine_p0/` | **Routers + moteurs V2/V3 — 210 fichiers** | **3 073.3 KB** | **210** | **MONOLITHE MASSIF** — candidat fractionnement |
| `camera_engine/` | Caméras de chasse (CAM-Oméga) | 102.9 KB | 8 | Conserver |
| `saline_engine/` | SALINE INTELLIGENCE ULTRA (7 moteurs) | 105.5 KB | 14 | Candidat `ENGINE_ECO_ZONES_Ω` (attracteurs) |
| `species_engine/` | Species Engine K3 (12 endpoints) | 51.4 KB | 12 | Candidat `ENGINE_BIO_SCORING_Ω` |
| `vision_engine/` | Vision AI (VIS-A) | 50.2 KB | 4 | Candidat branchement `IA_VISION` |
| `access_clarity_engine_v7/` | Clarté accès affûts V7 | 49.0 KB | 6 | Conserver |
| `guide_pro_engine/` | Guide PRO | 43.8 KB | 7 | Conserver |
| `share_engine/` | PARTAGER BCE-4X | 35.0 KB | 4 | Conserver |
| `nutrition_engine_v7/` | V7 ULTIME — Sol→Nutriments→Fourrage→Gibier | 29.8 KB | 3 | **Source CONTRAT** |
| `api_gateway/` | Routeur unifié v3 | 28.1 KB | 2 | Conserver |
| `canada_v72/` | Canada V7.2 | 22.5 KB | 3 | Fusion avec `v8_national` |
| `soil_engine/` | Pédologie GPS | 19.6 KB | 2 | Candidat `ENGINE_HYDRO_TOPO_Ω` |
| `salines_ultime_engine/` | 5 scores × 20 sources | 18.2 KB | 2 | **Source CONTRAT CRITIQUE** |
| `carte2027_engine/` | Carte 2027 | 17.8 KB | 2 | Conserver |
| `ultra_max_firewall/` | Geo-fencing urbain | 13.0 KB | 2 | Conserver |

**Sous-total modules** : ~3 660 KB, ~279 fichiers.

---

## 3. CORE SCORING PIPELINE `/app/backend/core/scoring_pipeline/`

| Pipeline | Rôle | Poids | Fichiers |
| --- | --- | --- | --- |
| `corridors_v10/` | **V7 ULTIME — scoring 8-facteurs + 5 niveaux** | **119.8 KB** | **12** |
| `alimentation_v2/` | Alimentation V2 multi-espèces | 59.2 KB | 7 |
| `alimentation_v1/` | Alimentation V1 | 44.7 KB | 9 |
| `common/` | Primitives partagées | 44.5 KB | 9 |
| `alimentation_v4/` | V4 terrain-centre SUPRA | 42.9 KB | 5 |
| `repos_v1/` | Repos par espèce | 34.0 KB | 9 |
| `rsf_engine/` | RSF | 17.7 KB | 3 |
| `multi_species_v1/` | Multi-espèces | 9.1 KB | 2 |
| `pression_v1/` | Pression humaine | 9.8 KB | 2 |
| `hydro_v1/` | Hydrologie | 8.8 KB | 2 |
| `scenario_v1/` | Scénario | 8.5 KB | 2 |
| `temporal_v1/` | Temporel | 8.0 KB | 2 |
| `behavior_v1/` | Comportement | 8.3 KB | 2 |
| `risk_v1/` | Risque | 8.2 KB | 2 |
| `thermal_v1/` | Thermique | 8.2 KB | 2 |
| `attractors_v1/` | Attracteurs | 8.0 KB | 2 |
| `trajets_v1/` | Trajets | 8.0 KB | 2 |
| `ndvi_vegetation_v1/` | NDVI | 7.9 KB | 2 |
| `opportunity_v1/` | Opportunité | 7.6 KB | 2 |
| `habitat_v1/` | Habitat | 7.5 KB | 2 |
| `visibility_v1/` | Visibilité | 7.5 KB | 2 |
| `simulation_v1/` | Simulation | 6.8 KB | 2 |
| `ecosystem_v1/` | Écosystème | 6.4 KB | 2 |
| `learning_v1/` | Apprentissage | 6.5 KB | 2 |

**Sous-total core** : ~557 KB, ~86 fichiers (dont `corridors_v10` = 119.8 KB, 12 fichiers).

---

## 4. POIDS TOTAL AGRÉGÉ

| Zone | Poids | Fichiers |
| --- | --- | --- |
| `backend/engines/` | ~1 443 KB | 157 |
| `backend/modules/` | ~3 660 KB | 279 |
| `backend/core/scoring_pipeline/` | ~557 KB | 86 |
| **TOTAL MESURÉ** | **~5 660 KB** | **~522** |

---

## 5. ANALYSE DES REDONDANCES / COUPLAGES

### 5.1 Redondances critiques
- **Corridors** : 3 générations parallèles actives
  - `engine_ia_corridors_organic_omega` (V30 LOCKED)
  - `corridors_v10` (V7, DEPRECATED PURGE-V6 mais source canonique CONTRAT)
  - `corridor_unified` (V6, DEPRECATED)
- **Salines** : `saline_engine` (7 moteurs) + `salines_ultime_engine` (5 scores × 20 sources) + `engine_salines` (v8_institutional)
- **Nutrition** : `nutrition_engine_v7` + `engines/nutrition_intelligence/` (×5000 SUPRA) + `engine_nutrition` (v8_institutional)
- **Alimentation** : `alimentation_v1/v2/v4` en parallèle
- **Canada** : `modules/canada_v72` + `engines/v8_national`

### 5.2 Couplages excessifs
- `modules/bionic_engine_p0/` — monolithe 3 MB / 210 fichiers mélangeant routers + moteurs + services
- `engines/v8_institutional/` — 87 moteurs dans un seul package (cohérence V30 scellé, mais lecture/maintenance difficile)

### 5.3 Zones à alléger
- DEPRECATED actifs à purger définitivement : `corridor_unified`, `relocation`
- Consolidation : `alimentation_v1+v2+v4` → `alimentation_unified`
- Extraction : `bionic_engine_p0/routers/` → répertoire routers dédié

---

## 6. CARTE DES DÉPENDANCES AU SMOOTHER X180

```
             ┌─────────────────────────────┐
             │   engine_ia_corridors_      │
             │     organic_omega (V30)     │  ← SCELLÉ
             └──────────────┬──────────────┘
                            │
                            ▼
             ┌─────────────────────────────┐
             │ post_smoothing/             │
             │ organic_corridor_smoother   │  ← X180-AMENDEMENT-FINAL
             │ (9 passes)                  │
             └─────────────────────────────┘
```

Aujourd'hui le smoother consomme UNIQUEMENT le bundle V30 + quelques `terrain_signals`/`ia_signals` optionnels. Les sources V7 canoniques (`corridors_v10`, `nutrition_engine_v7`, `salines_ultime_engine`, `repos_v1`) **NE SONT PAS** injectées dans le smoother.

---

## 7. CONCLUSIONS

- **Fragmentation excessive** : 23+ moteurs font du "scoring" à divers niveaux sans hiérarchie claire.
- **Monolithes** : `v8_institutional` (V30 scellé) et `bionic_engine_p0` (routers mélangés).
- **Sources V7 ULTIME inutilisées** : `corridors_v10`, `nutrition_engine_v7`, `salines_ultime_engine`, `repos_v1`, `alimentation_v1/v2` présentes physiquement mais non branchées au smoother X180.
- **Pas de CONSTITUTION** formelle : le CONTRAT RENDUΩ doit chapeauter des ENGINES canoniques spécialisés.

La proposition architecturale cible est dans `ENGINES_CIBLES_PLAN_Ω.md`.

— FIN CARTOGRAPHIE —

# PLAN DE RESTAURATION CORRIDORS + ZONES + UI/UX

**Protocole:** BCE-4X ULTIME ABSOLU x3
**Classification:** PLAN D'ACTION CORRECTIVE — COMMANDANT STEEVE-MAX
**Date:** Fevrier 2026
**Branche:** `SUPRA_RECONSTRUCTION`
**Reference:** BIONIC_DIFFERENTIAL_REPORT.md, MULTI_SPECIES_HOTSPOTS_SALINES_AUDIT.md

---

## 1. DIAGNOSTIC PREALABLE — ETAT ACTUEL

### 1.1 Etat des corridors

| Element | Etat actuel | Fichier |
|---|---|---|
| `BionicCorridorsV6Layer.jsx` | **OPERATIONNEL** — 683 lignes, rendering complet (zones, corridors, points) | `components/territoire/BionicCorridorsV6Layer.jsx` |
| Backend `/api/v6/corridors/analyze-full` | **OPERATIONNEL** — GeoJSON retourne avec zones, corridors, points | `corridors_v10/router.py` L128 |
| `MovementCorridorsLayer.jsx` | **PURGE DEFINITIVE** (BCE-4X-UI-003, ORDONNANCE STEEVE-MAX) | `MapContent.jsx` L145 |
| Palette normative 5 niveaux | **OPERATIONNEL** — CRITIQUE/MAJEUR/FORT/MODERE/FAIBLE | `BionicCorridorsV6Layer.jsx` L49-55 |
| Pulsation CRITIQUE | **OPERATIONNEL** — CSS animation 1.5s | `BionicCorridorsV6Layer.jsx` L34-47 |
| Glow 3 couches CRITIQUE | **OPERATIONNEL** — outer/mid/inner | `BionicCorridorsV6Layer.jsx` L237-242 |
| Clip circulaire 780m | **OPERATIONNEL** — clipRingsToCircle + clipCoordsToCircle | `BionicCorridorsV6Layer.jsx` L149-171 |
| Filtrage sous-elements | **OPERATIONNEL** — zoneSubFilters/corridorSubFilters/pointSubFilters | `BionicCorridorsV6Layer.jsx` L252-288 |
| Tooltip hover | **OPERATIONNEL** — Score + espece + type zone | `BionicCorridorsV6Layer.jsx` L337-345 |
| Cache version auto-invalidation | **OPERATIONNEL** — `bce4xmax_v5neutralized` | `BionicCorridorsV6Layer.jsx` L86-91 |

### 1.2 Etat des zones

| Zone | Toggle frontend | Sous-filtre | Backend | Etat |
|---|---|---|---|---|
| Alimentation | `showZonesLayer` | `zoneSubFilters.alimentation` | `corridors_v10/engine.py` | **OPERATIONNEL** |
| Repos | `showZonesLayer` | `zoneSubFilters.repos` | `corridors_v10/engine.py` | **OPERATIONNEL** |
| Rut | `showZonesLayer` | `zoneSubFilters.rut` | `corridors_v10/engine.py` | **OPERATIONNEL** |
| Eau | `showZonesLayer` | `zoneSubFilters.eau` | `corridors_v10/engine.py` | **OPERATIONNEL** |
| Habitat | — | Mappe sur `repos` via `isZoneTypeVisible` | — | **ALIAS** (via repos) |
| Trajets | — | Mappe sur `alimentation` via `isZoneTypeVisible` | — | **ALIAS** (via alimentation) |
| Affuts | — | Mappe sur `rut` via `isZoneTypeVisible` | — | **ALIAS** (via rut) |

### 1.3 Etat des overlays et couches

| Overlay | Toggle frontend | Etat dans MapContent.jsx | Statut |
|---|---|---|---|
| ConsolidatedHeatmapLayer | `showHeatmapV10` (defaut: true) | L180-188 — actif | **OPERATIONNEL** |
| WindFlowLayer | `showWindFlow` (defaut: true) | L142 — actif | **OPERATIONNEL** |
| ExclusionOverlayLayer | `showExclusionOverlay` (defaut: false) | L141 — conditionnel | **OPERATIONNEL** |
| HydrographyOverlayLayer | — | L139 — `enabled={false}` | **DESACTIVE** |
| ContaminationOverlayLayer | `showStands` | L243-251 — lie aux affuts | **OPERATIONNEL** |
| StructureContrastLayer | `classificationToggles.anthropique` | L143 — conditionnel | **OPERATIONNEL** |
| NutritionPointsLayer | `showAlimentationV2 && showNutritionPoints` | L213-223 — actif | **OPERATIONNEL** |
| StandsMapLayer | `showStands` | L227-239 — conditionnel | **OPERATIONNEL** |
| BionicZone2kmLayer | `selectedWaypointForZones` | L156-162 — conditionnel | **OPERATIONNEL** |
| AccessRouteV6Layer | — | L256-261 — **DESACTIVE** (ORDONNANCE STEEVE-MAX) | **DESACTIVE** |
| HuntingPathLayer | — | L150-152 — **DESACTIVE** (ORDONNANCE STEEVE-MAX) | **DESACTIVE** |
| NdviOverlayLayer | — | Non present dans MapContent.jsx | **NON INTEGRE** |
| CursorBionicLayer | `showCursorBionic && classificationToggles.curseurBionic` | L268-270 | **OPERATIONNEL** |

### 1.4 Etat des boutons/toggles

| Toggle | Variable | Defaut | Localisation | Statut |
|---|---|---|---|---|
| Heatmap ON/OFF | `showHeatmapV10` | true | MonTerritoireBionicPage.jsx L606 | **OPERATIONNEL** |
| Corridors V1 toggle | `showCorridorsV1` | false | MonTerritoireBionicPage.jsx L239 | **OPERATIONNEL** (desactive par defaut) |
| Corridors V6 permanent | `showCorridors = true` | true (force) | MonTerritoireBionicPage.jsx L568 | **OPERATIONNEL** |
| Zones layer | `showZonesLayer` | true | MonTerritoireBionicPage.jsx L573 | **OPERATIONNEL** |
| Corridors layer | `showCorridorsLayer` | true | MonTerritoireBionicPage.jsx L574 | **OPERATIONNEL** |
| Points layer | `showPointsLayer` | true | MonTerritoireBionicPage.jsx L575 | **OPERATIONNEL** |
| Alimentation V2 | `showAlimentationV2` | true | MonTerritoireBionicPage.jsx L580 | **OPERATIONNEL** |
| Nutrition Points | `showNutritionPoints` | true | MonTerritoireBionicPage.jsx L581 | **OPERATIONNEL** |
| Wind Flow | `showWindFlow` | true | MonTerritoireBionicPage.jsx L241 | **OPERATIONNEL** |
| Exclusion Overlay | `showExclusionOverlay` | false | MonTerritoireBionicPage.jsx L240 | **OPERATIONNEL** |
| Curseur Bionic | `showCursorBionic` | false | MonTerritoireBionicPage.jsx L550 | **OPERATIONNEL** |
| Stands | `showStands` | Conditionnel | MonTerritoireBionicPage.jsx | **OPERATIONNEL** |
| Layers Panel | `showLayersPanel` | true | MonTerritoireBionicPage.jsx L549 | **OPERATIONNEL** |
| Zone sous-filtres | `zoneSubFilters` | {alimentation:true, repos:true, rut:true, eau:true} | MonTerritoireBionicPage.jsx L620-622 | **OPERATIONNEL** |
| Corridor sous-filtres | `corridorSubFilters` | {normaux:true, intenses:true, extreme:true, saisonniers:false} | MonTerritoireBionicPage.jsx L623-625 | **OPERATIONNEL** |
| Point sous-filtres | `pointSubFilters` | {centroides:true, individuels:false, ...} | MonTerritoireBionicPage.jsx L626-628 | **OPERATIONNEL** |
| Classification toggles | `classificationToggles` | Objet multi-cles | MonTerritoireBionicPage.jsx L634+ | **OPERATIONNEL** |

---

## 2. CONSTATATION GLOBALE

**L'infrastructure corridors + zones + UI/UX est OPERATIONNELLE dans son etat actuel.**

Les elements suivants sont les SEULS elements non-actifs :
1. `HydrographyOverlayLayer` — `enabled={false}` dans MapContent.jsx
2. `AccessRouteV6Layer` — Desactive par ORDONNANCE STEEVE-MAX
3. `HuntingPathLayer` — Desactive par ORDONNANCE STEEVE-MAX
4. `NdviOverlayLayer` — Non integre dans MapContent.jsx

Les corridors, zones, toggles, overlays, heatmaps, vent, et interactions sont **tous fonctionnels**.

---

## 3. PLAN DE RESTAURATION — SECTION B

### 3.1 RESTAURATION CORRIDORS (B.1)

| # | Action | Etat actuel | Action proposee | Priorite |
|---|---|---|---|---|
| B1.1 | Fluidite des corridors | **OPERATIONNEL** — Douglas-Peucker + simplifie | Integration ponderations espece (MS-1) pour varier les corridors | **P1** |
| B1.2 | Continuite visuelle | **OPERATIONNEL** — Clip circulaire 780m + buffer 30% | Aucune action requise | **N/A** |
| B1.3 | Densite et nombre | Depend du backend `analyze_corridors_full` | Integration RSF (MS-2) dans le scoring cellulaire des corridors | **P1** |
| B1.4 | Geometries | **OPERATIONNEL** — Polygones organiques + perturbation terrain | Integration couches ecologiques (MS-3) pour formes realistes | **P1** |
| B1.5 | Rendu CorridorRenderer | **OPERATIONNEL** — 5 niveaux, glow CRITIQUE, pulsation | Aucune action requise | **N/A** |

### 3.2 RESTAURATION ZONES (B.2)

| # | Zone | Etat actuel | Action proposee | Priorite |
|---|---|---|---|---|
| B2.1 | Repos | **OPERATIONNEL** via `zoneSubFilters.repos` | Integration preferences thermiques espece (MS-4 P5) dans le scoring repos | **P1** |
| B2.2 | Eau | **OPERATIONNEL** via `zoneSubFilters.eau` | Integration dependance eau espece (MS-4 P6) pour varier taille/position | **P1** |
| B2.3 | Habitat | **ALIAS** mappe sur repos | Creer un type de zone `habitat` distinct dans `corridors_v10/engine.py` avec scoring RSF | **P1** |
| B2.4 | Trajets | **ALIAS** mappe sur alimentation | Creer un type de zone `trajets` distinct base sur amplitude deplacement espece (MS-4 P4) | **P2** |
| B2.5 | Affuts | **ALIAS** mappe sur rut | **CONFORME** — Les affuts sont lies aux zones de rut, ce qui est biologiquement correct | **N/A** |

### 3.3 REACTIVATION COUCHES (B.3)

| # | Couche | Etat actuel | Action proposee | Priorite | Risque |
|---|---|---|---|---|---|
| B3.1 | HydrographyOverlayLayer | `enabled={false}` | Reactiver avec `enabled={showHydro}` + toggle dedicace | **P1** | Faible |
| B3.2 | NdviOverlayLayer | Non integre dans MapContent.jsx | Ajouter dans MapContent.jsx avec toggle dedicace | **P2** | Faible |
| B3.3 | AccessRouteV6Layer | DESACTIVE (ORDONNANCE STEEVE-MAX) | **ATTENTE ORDRE** — Ne pas reactiver sans autorisation explicite | **BLOQUE** | — |
| B3.4 | HuntingPathLayer | DESACTIVE (ORDONNANCE STEEVE-MAX) | **ATTENTE ORDRE** — Ne pas reactiver sans autorisation explicite | **BLOQUE** | — |
| B3.5 | Boutons/toggles ON/OFF | **TOUS OPERATIONNELS** | Aucune action requise | **N/A** | — |
| B3.6 | Visibilite des couches | **TOUS OPERATIONNELS** | Aucune action requise | **N/A** | — |
| B3.7 | Overlays (heatmaps, vent) | **TOUS OPERATIONNELS** | Aucune action requise | **N/A** | — |
| B3.8 | Rafraichissement dynamique | **OPERATIONNEL** — fetchAndRender sur changement waypoint/espece | Aucune action requise | **N/A** | — |

### 3.4 REPARATIONS (B.4)

| # | Composant | Etat actuel | Action proposee | Priorite |
|---|---|---|---|---|
| B4.1 | LayerController | **N'EXISTE PAS** en tant que composant separe — logique integree dans MonTerritoireBionicPage.jsx via `showZonesLayer`, `showCorridorsLayer`, `showPointsLayer` et sous-filtres | Refactoring optionnel : extraire en composant dedie | **P2** |
| B4.2 | OverlayEngine | **N'EXISTE PAS** en tant que composant separe — logique integree dans MapContent.jsx via les couches individuelles | Refactoring optionnel : creer un gestionnaire d'overlays centralise | **P2** |
| B4.3 | ZoneRenderer | **INTEGRE** dans `BionicCorridorsV6Layer.jsx` (L306-347) — rendu des zones polygonales avec couleurs, tooltips, hover, clipping | **OPERATIONNEL** — Aucune reparation necessaire | **N/A** |
| B4.4 | VisibilityState | **INTEGRE** dans MonTerritoireBionicPage.jsx via 15+ variables `useState` + `classificationToggles` + sous-filtres | **OPERATIONNEL** — Aucune reparation necessaire | **N/A** |

---

## 4. ACTIONS CONCRETES — RECAPITULATIF PAR PRIORITE

### P0 — Aucune action immediate requise
L'infrastructure corridors + zones + UI/UX est **fonctionnelle**. Les ameliorations viendront des phases MS-1 a MS-6 du plan multi-especes.

### P1 — Actions liees aux phases multi-especes

| # | Action | Fichier(s) impacte(s) | Dependance |
|---|---|---|---|
| 1 | Reactiver HydrographyOverlayLayer | `MapContent.jsx` L139 | Aucune |
| 2 | Integrer RSF dans scoring zones/corridors | `corridors_v10/engine.py` | MS-2 (RSF Engine) |
| 3 | Integrer ponderations dynamiques dans heatmap | `score_consolide.py` | MS-1 |
| 4 | Creer type zone `habitat` distinct | `corridors_v10/engine.py` | MS-3 (couches ecologiques) |
| 5 | Integrer dependance eau espece dans zones | `corridors_v10/engine.py` | MS-4 P6 |
| 6 | Integrer preferences thermiques dans zones repos | `corridors_v10/engine.py` | MS-4 P5 |

### P2 — Ameliorations structurelles

| # | Action | Description |
|---|---|---|
| 1 | Integrer NdviOverlayLayer dans MapContent.jsx | Ajouter avec toggle dedie |
| 2 | Creer type zone `trajets` distinct | Base sur amplitude deplacement espece |
| 3 | Extraire LayerController en composant dedie | Refactoring optionnel |
| 4 | Creer OverlayEngine centralise | Refactoring optionnel |

### BLOQUE — En attente d'ordonnance

| # | Action | Raison du blocage |
|---|---|---|
| 1 | Reactiver AccessRouteV6Layer | ORDONNANCE STEEVE-MAX 2026-04-07 |
| 2 | Reactiver HuntingPathLayer | ORDONNANCE STEEVE-MAX 2026-04-07 |

---

## 5. SCHEMA D'INTEGRATION CORRIDORS + MULTI-ESPECES

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (MonTerritoireBionicPage)           │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Toggles/     │  │ Classification│  │ Sous-filtres         │  │
│  │ Visibility   │  │ Toggles      │  │ Zone/Corridor/Point  │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                 │                      │              │
│  ┌──────▼─────────────────▼──────────────────────▼───────────┐  │
│  │                    MapContent.jsx                          │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │ BionicCorridorsV6Layer (ZONES + CORRIDORS + POINTS) │  │  │
│  │  │    ↓ POST /api/v6/corridors/analyze-full            │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │ ConsolidatedHeatmapLayer (HEATMAP = SCORE CONSOLIDE)│  │  │
│  │  │    ↓ GET /api/v1/score-consolide/heatmap            │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐   │  │
│  │  │ WindFlow │ │ Exclusion│ │ Hydro    │ │ Contamina. │   │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────────┘   │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (score_consolide.py)                 │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ compute_consolidated_score(lat, lng, species, month)      │  │
│  │                                                            │  │
│  │  ACTUELLEMENT: weights = ENGINE_WEIGHTS (statique)         │  │
│  │  APRES MS-1:   weights = SPECIES_ENGINE_WEIGHTS[species]   │  │
│  │                                                            │  │
│  │  22 moteurs → score 0-100 par cellule                      │  │
│  │  ACTUELLEMENT: 11 moteurs = hash generique                 │  │
│  │  APRES MS-5:   0 moteurs hash → RSF espece-specifique      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ corridors_v10/engine.py → analyze_corridors_full()        │  │
│  │                                                            │  │
│  │  Zones: alimentation, repos, rut, eau                      │  │
│  │  APRES MS-3: + habitat, trajets (types distincts)          │  │
│  │  Scoring cellulaire → formes organiques → GeoJSON          │  │
│  │  APRES MS-2: + RSF scoring integre                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ NOUVEAU: rsf_engine/ (MS-2)                               │  │
│  │  → Coefficients RSF par espece (13 covariables)            │  │
│  │  → 11 couches ecologiques (MS-3)                           │  │
│  │  → 8 params comportementaux (MS-4)                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. CONTRAINTES DE NON-REGRESSION

| Contrainte | Protection |
|---|---|
| ZERO suppression de composant | Aucun composant frontend supprime |
| ZERO modification de structure GeoJSON | Le frontend recoit le meme format |
| ZERO perte de toggle | Tous les toggles et sous-filtres preserves |
| ZERO regression corridors V6 | Le rendu est preserv, seules les donnees backend changent |
| ZERO merge main | Branche `SUPRA_RECONSTRUCTION` uniquement |
| ZERO rollback global | Restauration ciblee uniquement |
| ZERO reactivation non autorisee | AccessRoute et HuntingPath restent desactives |

---

*PLAN GENERE SOUS PROTOCOLE BCE-4X ULTIME ABSOLU x3*
*ZERO MODIFICATION EXECUTEE — PLAN UNIQUEMENT*
*Autorite : COMMANDANT STEEVE-MAX*
*Agent Operationnel — Fevrier 2026*

# P20_TERRITOIRE_UI_UX_AUDIT_OMEGA.md

**ORDRE** : `P20_TERRITOIRE_UI_UX_AUDIT_Ω`  
**COMMANDANT** : STEEVE-MAX  
**DOCTRINE** : `BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT`  
**MODE** : READ-ONLY · `autonomy: LIMITED` · `V30_LOCK: INVIOLÉ`  
**DATE** : 2026-05-08

═══════════════════════════════════════════════════════════════════

## 1. INVENTAIRE ACTUEL (78 composants `/components/territoire/`)

### 1.1 Composants pilotes (panel/toolbar)
| Composant | LOC | Rôle | État |
|-----------|-----|------|------|
| `ui/TerritoireToolbar.jsx` | 220 | 13 boutons presseur ON/OFF | ✅ Actif |
| `HighFidelityMapsPanel.jsx` | 190 | 7 couches HF + opacity sliders | ✅ Actif |
| `LayersOmegaSyncPanel.jsx` | 316 | Visu status 7 couches Ω + chaînes C1-C6 | ✅ Actif (read-only) |
| `BionicLegend.jsx` | — | Légende permanente | ✅ Actif |
| `EcoforestryLayers.jsx` | **1352** | WMS Québec officiel + fallback polling | ⚠️ Volumineux |

### 1.2 Couches de rendu
| Composant | Rôle | Z-order |
|-----------|------|---------|
| `BionicLayersV8.jsx` | Corridors / zones / salines / hotspots / affûts / contam / nutrition | implicite |
| `WindFlowLayer.jsx` | Flux vent V9 | implicite |
| `CursorBionicLayer.jsx` | Curseur inspection | implicite |
| `EcoforestryLayers.jsx` | WMS forêt MRNF | hardcoded |
| `HighFidelityMapLayers.jsx` | WMS HF (proxy) | `zIndex: 300` |
| `ConsolidatedHeatmapLayer.jsx` | Heatmap consolidée | implicite |
| `NdviOverlayLayer.jsx` | Overlay NDVI | implicite |
| `ContaminationOverlayLayer.jsx` | Contamination zones | implicite |
| `HydrographyOverlayLayer.jsx` | Hydrographie | implicite |
| `NutritionPointsLayer.jsx` | Points nutrition | implicite |
| `StandsMapLayer.jsx` | Affûts (610 LOC) | implicite |
| `AlphaHotspotsLayer.jsx` | Hotspots Alpha | implicite |
| `GuidedRouteLayer.jsx` | Route guidée | implicite |
| `RoutePlannerLayer.jsx` | Planificateur | implicite |
| `RouteReplayLayer.jsx` | Replay routes | implicite |
| `BionicPrecisionZonesLayer.jsx` | Zones précision | implicite |
| `BionicZone600m.jsx` / `BionicZone2km.jsx` | Zones rayon | implicite |
| `BionicMicroZones.jsx` | Microzones | implicite |
| `CameraMarkersLayer.jsx` | Caméras | implicite |
| `CursorBionicLayer.jsx` | Curseur | implicite |
| `ExclusionOverlayLayer.jsx` | Exclusions BCE-4X | implicite |
| `StructureContrastLayer.jsx` | Contraste sol | implicite |
| `TrajectoriesLayer.jsx` | Trajectoires | implicite |

### 1.3 Composants neutralisés (dead-code conservé)
- `TerritoryShell.jsx` (10 LOC, retourne `null`)
- `BionicMapOverlay.jsx` (27 LOC, retourne `null`)
- `_PURGED_LEGACY_LAYERS_OMEGA.js` (registre de 3 fichiers supprimés)

═══════════════════════════════════════════════════════════════════

## 2. DUPLICATIONS DOCTRINALES IDENTIFIÉES (priorité décroissante)

### 🔴 D1 — HF LAYERS vs ECOFORESTRY (CRITIQUE)
- `HighFidelityMapsPanel.jsx` expose **7 couches HF** (LIDAR HD, Canopy, Orthophoto HR, Hydro, Chemins forestiers, Neige/Sol, Pente DEM).
- `EcoforestryLayers.jsx` (1352 LOC) couvre LiDAR dendrométrique, ortho, courbes, peuplements, hauteur — **chevauchement direct** sur LIDAR + ortho + canopy.
- Les deux interrogent NFIS-QC + MERN/MRNF ; risque de double-fetch et de toggle conflict.
- **Recommandation** : factoriser en un registre unique `LAYER_CATALOG_OMEGA` (source de vérité) consommé par HF et Ecoforestry.

### 🟠 D2 — HEATMAP triple
- `ConsolidatedHeatmapLayer.jsx` (orphan — aucun import détecté ailleurs)
- `showHeatmapV10` flag dans toolbar → "Hotspots" → ConsolidatedHeatmapLayer ?
- `AlphaHotspotsLayer.jsx` séparé
- **Recommandation** : audit du flux `showHeatmapV10` et fusion sous `HotspotsLayerOmega` unique.

### 🟠 D3 — ZONES multiples
- `BionicZone600m`, `BionicZone2km`, `BionicMicroZones`, `BionicPrecisionZonesLayer`, `BionicLayersV8.zones`
- **Recommandation** : registre `ZONES_OMEGA_REGISTRY` avec sélecteur radius (600/2k/precision).

### 🟡 D4 — Stubs neutralisés
- `TerritoryShell.jsx` + `BionicMapOverlay.jsx` retournent `null` mais sont importés par `WaypointMap` / `MapContent`.
- **Recommandation** : conserver tant que les imports ne sont pas tracés et nettoyés (V30_LOCK : pas de suppression sans validation).

═══════════════════════════════════════════════════════════════════

## 3. PROBLÈMES UI/UX

### 3.1 Z-ORDER non centralisé
- Aucun registre `LAYER_Z_INDEX_OMEGA`.
- `HighFidelityMapLayers` hardcode `zIndex: 300` ; les autres composants n'ont **pas de zIndex défini** → ordre dépend de l'ordre d'insertion DOM.
- **Risque** : couches HF masquent zones/corridors selon montage.

### 3.2 Opacity asymétrique
- Seul `HighFidelityMapsPanel` expose des sliders d'opacité (10-100%, step 5).
- Toolbar = ON/OFF brut → pas de granularité visuelle pour Vent / Contam / Hotspots.
- **Recommandation** : opacity tier (FULL=100, MEDIUM=70, LOW=40) sur chaque couche toggleable.

### 3.3 Couleurs incohérentes
- TerritoireToolbar utilise `activeColor` ad hoc (#2E7D32, #FF9800, #FDD835, #E53935, #90CAF9, etc.)
- HighFidelityMapsPanel utilise palette différente (#F59E0B, #22C55E, #3B82F6, etc.)
- LayersOmegaSyncPanel utilise palette Ω (#FFD600, #00A676, #33B787, #A78BFA, #F59E0B, #DC2626, #06B6D4)
- **Risque** : conflits visuels (ex: orange = Corridors **et** Salines selon panneau).
- **Recommandation** : créer `/styles/territoire-omega-palette.json` doctrinal unique.

### 3.4 Icons fragmentés
- `lucide-react` partout, mais sélection par composant (Mountain, TreePine, Layers, Navigation, Crosshair, Droplets, Flame, Wind, Eye, Brain, Microscope, etc.) — **18 icons distincts**.
- Pas de table de mapping fonction→icon.
- **Recommandation** : `LAYER_ICON_REGISTRY_OMEGA` unique.

### 3.5 Performance
- `EcoforestryLayers` 1352 LOC + polling fallback → re-render risqué sur changement opacity.
- `LayersOmegaSyncPanel` re-calcule `counts` et `flagsRow` à chaque render (pas de `useMemo`).
- `MonTerritoireBionicPage.jsx` 1722 LOC = god component.
- **Recommandation** : memoize calculs panel + lazy import EcoforestryLayers.

### 3.6 Grouping absent
- Toolbar mélange tabs (waypoints/lieux), filtres (espèce), couches Ω, couches diag (curseur, inspec) **sur la même barre**.
- 13 boutons en flat = scrollbar horizontal forcé sur mobile.
- **Recommandation** : 5 groupes doctrinaux (cf §4).

═══════════════════════════════════════════════════════════════════

## 4. RECOMMANDATIONS DOCTRINALES (groupage Ω)

### 4.1 Proposition 5 groupes hiérarchiques
| Groupe | Couches | Couleur Ω | z-base |
|--------|---------|-----------|--------|
| **A · BASE** | Carte fond, Ortho HR, Topo | `#64748B` | 100 |
| **B · BIO-Ω** | Zones, Corridors, Affûts, Salines, Hotspots | `#00A676` | 200 |
| **C · ENVIRONNEMENT** | Vent, Contamination, Sensoriel | `#06B6D4` | 300 |
| **D · HF SPECIALISÉ** | LIDAR HD, Canopy, Hydro, Forest Roads, DEM, Neige | `#F59E0B` | 400 |
| **E · INSPECTION** | Curseur Bionic, Inspec Bio, NDVI | `#A78BFA` | 500 |

### 4.2 Composant cible : `LayersPanelOmegaUnified.jsx` (P21 Visualizer18)
Spécification minimale anti-générique :
```jsx
<LayersPanelOmegaUnified
  layers={LAYER_CATALOG_OMEGA}      // 18 entrées doctrinales
  groupSpec={5_GROUPS_ABCDE}
  zIndexBase={GROUP_Z_BASE}
  opacityRegistry={LAYER_OPACITY_REGISTRY}
  iconRegistry={LAYER_ICON_REGISTRY_OMEGA}
  paletteRegistry={TERRITOIRE_OMEGA_PALETTE}
  onToggle={(layerId) => ...}
  onOpacityChange={(layerId, value) => ...}
/>
```
Avantages :
- Un seul render path (vs 4 panneaux actuels)
- Z-order **explicite et figé** par groupe
- Opacity uniformisée 0-100% par couche
- Palette/icon registries = source unique vérité doctrinale

═══════════════════════════════════════════════════════════════════

## 5. CLEANUP DOCTRINAL PROPOSÉ (FUSION ADD-ONLY ; réversible)

### 5.1 ❎ NE PAS supprimer (V30_LOCK)
- `TerritoryShell.jsx` / `BionicMapOverlay.jsx` (stubs neutralisés ; imports actifs)
- `_PURGED_LEGACY_LAYERS_OMEGA.js` (registre archives doctrinal)

### 5.2 ✅ Convertir vers registre doctrinal (overlays nouveaux, fichiers existants intacts)
- Créer `/components/territoire/registry/layer_catalog_omega.js` (18 layers + groupes + z-order + couleur + icon + opacity defaults)
- Créer `/components/territoire/registry/territoire_palette_omega.js`
- Créer `/components/territoire/registry/layer_icon_registry_omega.js`
- Créer `/components/territoire/LayersPanelOmegaUnified.jsx` (panneau unifié)
- Brancher `LayersPanelOmegaUnified` **en parallèle** des panneaux actuels (FUSION ADD-ONLY) ; toggle via flag `panelMode = 'unified' | 'legacy'`.

### 5.3 ⏳ Phase ultérieure (sous validation Commandant)
- Marquer `HighFidelityMapsPanel.jsx` comme legacy après 1 cycle de validation
- Migration progressive Toolbar vers `LayersPanelOmegaUnified`
- Lazy-load `EcoforestryLayers.jsx` (1352 LOC)

═══════════════════════════════════════════════════════════════════

## 6. PRÉPARATION P21 VISUALIZER18

### 6.1 Mapping 18 couches doctrinales (cf P18 Manual)
Le manual P18 expose 18 couches **back-end** (`L01_NDVI_DENSE_GRID` à `L18_OTS_UPGRADE_AUTOMATION`). Le **front-end actuel** expose ~24 couches dont 7 HF + 8 Ω + autres.

**Stratégie de réconciliation** :
- L01-L05 (NDVI, Habitat, Anthropogenic, Rut, Trend) → couche `Intel-Ω` du toolbar (déjà présent)
- L06-L12 (Soil, Topo, GBIF, OWM, Canopy, RSF, GLAD) → groupe **D · HF**
- L13 (BP135) → badge dans `BionicScoreBadge`
- L14-L18 (Merkle, MultiSig, Validation, Messaging, OTS) → **nouveau panneau** `MerkleAuditPage` (P21)

### 6.2 Endpoints back-end utilisables (déjà actifs via P15/P17/P18)
- `GET /api/v30/super-masters/territoire-omega-report-status` → métadonnées rapports
- `GET /api/v30/super-masters/layer-interpretation-manual-status` → catalogue 18 couches
- `GET /api/v30/super-masters/merkle-tree-anchor-hook-status` → preuves Bitcoin
- `GET /api/v30/super-masters/ots-upgrade-automation-status` → état automation 6h

═══════════════════════════════════════════════════════════════════

## 7. VERDICT AUDIT P20

| Critère | Score | Verdict |
|---------|-------|---------|
| **Cohérence palette** | 4/10 | ❌ Trois palettes en concurrence |
| **Z-order** | 3/10 | ❌ Quasi-absent, hardcoded local |
| **Opacity** | 5/10 | ⚠️ HF only, autres ON/OFF brut |
| **Performance** | 6/10 | ⚠️ Re-render non memoizé sur sync panel |
| **Duplications** | 5/10 | ⚠️ HF↔Ecoforestry + Heatmap orphan |
| **Iconographie** | 7/10 | ✅ lucide-react bien adopté |
| **Architecture** | 6/10 | ⚠️ Page 1722 LOC ; 78 composants |
| **Doctrine V30** | 9/10 | ✅ Stubs neutralisés correctement |

**SCORE GLOBAL** : **5.6 / 10** — Optimisation requise avant P21.

═══════════════════════════════════════════════════════════════════

## 8. ACTION ITEMS (priorité décroissante)

| # | Action | Priorité | Effort | Risque |
|---|--------|----------|--------|--------|
| 1 | Créer `layer_catalog_omega.js` (18 entrées) | P0 | S | Faible |
| 2 | Créer `territoire_palette_omega.js` | P0 | XS | Faible |
| 3 | Créer `layer_icon_registry_omega.js` | P0 | XS | Faible |
| 4 | Créer `LayersPanelOmegaUnified.jsx` | P0 | M | Moyen |
| 5 | Brancher en mode `panelMode='unified'` opt-in | P1 | S | Faible |
| 6 | Mémoizer `LayersOmegaSyncPanel` calculs | P1 | S | Faible |
| 7 | Lazy-load `EcoforestryLayers` | P2 | S | Faible |
| 8 | Audit flux heatmap `showHeatmapV10` | P2 | M | Moyen |
| 9 | Stratégie z-order centralisée | P0 | S | Faible |
| 10 | Doc préfacée `/docs/territoire_layers_omega.md` | P3 | S | Faible |

═══════════════════════════════════════════════════════════════════

## 9. CONFORMITÉ DOCTRINALE

- ✅ **V30_LOCK** : INVIOLÉ — aucun fichier maître muté
- ✅ **FUSION ADD-ONLY** : recommandations en overlay (registres + composant unifié), pas de remplacement direct
- ✅ **ANTI-GÉNÉRIQUE STRICT** : audit basé sur lecture réelle des 78 fichiers (pas de fabrication)
- ✅ **AUTONOMIE LIMITÉE** : aucune mutation effectuée pendant l'audit ; recommandations soumises à approbation
- ✅ **READ-ONLY** : le pipeline TERRITOIRE/MapContent reste inchangé tant que validation Commandant non reçue

═══════════════════════════════════════════════════════════════════

**Audit doctrinal scellé.**  
**Manifest SHA-256** : *(à calculer post-validation Commandant)*  
**COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · 2026-05-08**

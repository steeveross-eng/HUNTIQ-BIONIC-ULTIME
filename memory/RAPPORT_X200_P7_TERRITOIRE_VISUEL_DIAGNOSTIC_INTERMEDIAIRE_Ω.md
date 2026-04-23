# RAPPORT INTERMÉDIAIRE — PHASE_X200_P7 (SECTIONS 1 & 2)
**Commandant** : STEEVE-MAX
**Protocole** : BCE-4X ULTIME ABSOLU — TOP-ABSOLU
**Date** : 2026-04-23
**Waypoint officiel** : LAT `48.206657` / LNG `-68.382422`
**Zoom testé** : 14
**Espèce** : cerf (par défaut)

---

## SECTION 1 — INVENTAIRE DES COUCHES (Backend ↔ Frontend)

### 1.1 — Mesures quantitatives au waypoint officiel

| Couche | Backend (bundle V20) | Frontend rendu live | Δ | Statut |
|---|---:|---:|---:|---|
| **Zones** | 5 `zones` | Cercles buffer 600 m + 2 km visibles, contours polygonaux présents | ~OK | ✅ OK |
| **Corridors** | 12 `corridors` | 24 SVG paths dans pane `renduOmega-corridors-pane` (2 paths/corridor : ligne + halo) | OK | ✅ OK (RenduΩ appliqué) |
| **Affûts** | 6 `affuts` | Marqueurs présents dans `leaflet-marker-pane` | ~OK | ✅ OK |
| **Salines** | 6 `salines` | Non distinctement identifiables à l'écran (pas d'icône cristal sel visible) | ⚠ | ⚠ PARTIEL |
| **Hotspots** | 11 `hotspots` | Non distinctement identifiables (marqueurs circulaires rouges mêlés aux affuts ?) | ⚠ | ⚠ PARTIEL |
| **Vent** | 8 `wind_vectors` (backend) | **0 canvas** dans tous les panes Leaflet, aucune particule visible | -8 | ❌ ABSENT |
| **Contamination** | 18 `contamination` | Aucun polygone rouge/orange visible au-delà du centre | ⚠ | ⚠ PARTIEL/ABSENT |
| **Inspection bio** | spec 4 sous-couches (attracteurs, exclusions, pentes, couvert) | 4 panes créés (`leaflet-leaflet-inspection-bio-*-pane-pane`) MAIS **0 svg_paths** dans chacun | ⚠ | ⚠ INACTIF (mode DÉSACTIVÉ par défaut) |
| **Waypoint central** | pin officiel 48.206657/-68.382422 | Pin vert avec score visible | OK | ✅ OK |

### 1.2 — Classification

- **Présent backend ET invisible frontend** : `wind_vectors` (8 items, 0 rendu).
- **Partiellement visible** : `salines`, `hotspots`, `contamination` (données présentes backend, absence d'une distinction visuelle nette).
- **Totalement absent/inactif** : `inspection_bio` (4 panes vides, toggle PRO/EXPERT désactivé par défaut).

### 1.3 — Panes Leaflet inventoriés (capture live)

```
leaflet-map-pane                                     : 133 paths, 8 markers
leaflet-overlay-pane                                 :  88 paths
leaflet-marker-pane                                  :  21 paths, 8 markers
leaflet-renduOmega-corridors-pane                    :  24 paths   ← corridors Ω ✅
leaflet-leaflet-inspection-bio-attracteurs-pane-pane :   0 paths   ← INSPEC vide
leaflet-leaflet-inspection-bio-exclusions-pane-pane  :   0 paths   ← INSPEC vide
leaflet-leaflet-inspection-bio-pentes-pane-pane      :   0 paths   ← INSPEC vide
leaflet-leaflet-inspection-bio-couvert-pane-pane     :   0 paths   ← INSPEC vide
Total canvas elements                                :   0         ← VENT absent
```

---

## SECTION 2 — ANALYSE DES CAUSES (par couche)

### 2.1 VENT (CRITIQUE — couche entièrement absente)

- **Cause probable** : `WindFlowLayer.jsx` est bien présent dans le code mais le toggle `toggle-wind-flow` n'initialise pas de `<canvas>` (`total_canvas=0` même après clic).
- **Fichiers impactés** :
  - `/app/frontend/src/components/territoire/WindFlowLayer.jsx`
  - `/app/frontend/src/components/territoire/BionicLayersV8.jsx` (délégation VENT)
  - `/app/frontend/src/hooks/useBionicLayers.js` (état toggle)
- **Hypothèses à valider** :
  1. `showWindFlow` reste `false` après clic (event binding défectueux).
  2. `wind_vectors` du bundle non consommé par `WindFlowLayer`.
  3. Canvas non attaché au DOM Leaflet (map instance non transmise).

### 2.2 INSPECTION BIO (INACTIF par design mais vide même en PRO/EXPERT ?)

- **Cause probable** : 4 sous-panes créés mais aucun `<path>` injecté. Le panneau affiche `STATUT DÉSACTIVÉ`. Les boutons PRO/EXPERT ne semblent pas injecter de données. Règle "FALLBACK VISUEL NON INSTITUTIONNEL — INTERDIT" peut bloquer tout rendu si les flux d'attracteurs/exclusions ne sont pas reçus.
- **Fichiers impactés** :
  - `/app/frontend/src/components/territoire/InspectionBiologiquePanel.jsx`
  - `/app/frontend/src/components/territoire/BionicLayersV8.jsx` (INSPECTION_BIO_SPEC.overlayLayers)
- **Hypothèses** : source de données `inspection` absente du bundle (`inspection: ABSENT` confirmé dans l'inventaire backend).

### 2.3 CONTAMINATION (partiel)

- **Cause probable** : 18 items dans `contamination` mais `ContaminationOverlayLayer.jsx` ne les rend peut-être que sous certains filtres/toggles, ou les polygones sont trop petits / opacité trop faible.
- **Fichiers impactés** :
  - `/app/frontend/src/components/territoire/ContaminationOverlayLayer.jsx`
  - `/app/frontend/src/components/territoire/BionicLayersV8.jsx` (flags `contamination_layers_visible`)

### 2.4 SALINES / HOTSPOTS (partiel/confusion visuelle)

- **Cause probable** : icônes non différenciées (cercles similaires pour salines / hotspots / affuts). Backend fournit bien les 6 salines + 11 hotspots mais aucun marqueur spécifique (cristal de sel, punaise chaude) n'est rendu.
- **Fichiers impactés** :
  - `/app/frontend/src/components/territoire/AlphaHotspotsLayer.jsx`
  - `/app/frontend/src/components/territoire/NutritionPointsLayer.jsx` (salines)
  - `/app/frontend/src/components/territoire/BionicLayersV8.jsx`

### 2.5 CORRIDORS (✅ CONFORME)

- 12 corridors backend → 24 paths frontend = 2 paths/corridor (ligne centrale + halo institutionnel).
- Pane dédié `renduOmega-corridors-pane` respecté (zIndex institutionnel strict).
- RenduΩ appliqué : couleur #FF8F00, CatmullRom, 25-30 points, 1.2/2.0/3.0 px.
- Aucune action corrective requise.

### 2.6 ZONES / AFFÛTS / WAYPOINT (✅ CONFORME)

- Rendu conforme aux spécifications institutionnelles observées.

### 2.7 CI / runtime_beacon

- `CI_STATUS_Ω.runtime_beacon.conforming = true` (X200-P4 fermé).
- Le beacon rapporte `panels_clickable_count=6`, `corridors_style_conforme=true`, `filters_omega_active=true`. Conforme.
- Aucun blocage CI observé pour P7.

---

## ÉTAT DES LIEUX — AUTORISATION REQUISE POUR SECTION 3

Conformément au protocole BCE-4X (ordre du COMMANDANT), **aucune
modification frontend/backend ne sera entreprise sans confirmation
explicite** de la priorité et du scope des corrections.

### Priorités proposées à votre validation

| # | Priorité | Couche | Cause | Effort estimé |
|---|---|---|---|---|
| P0-A | 🔴 CRITIQUE | **VENT** (0 canvas, 0 particule) | WindFlowLayer non initialisé | moyen |
| P0-B | 🔴 CRITIQUE | **INSPECTION BIO** (4 panes vides) | Source de données `inspection` manquante au bundle, mode DÉSACTIVÉ par défaut | moyen-élevé |
| P1 | 🟠 HAUTE | **CONTAMINATION** (18 items mais non visibles) | Styles/opacité/filtre | faible-moyen |
| P1 | 🟠 HAUTE | **SALINES + HOTSPOTS** (icônes non distinctives) | Marqueurs dédiés manquants | faible |
| P2 | 🟡 FINITION | Confirmer corridors halo (24/12 = 2×) conforme | Aucune action | nulle |

---

*Captures d'écran : `/tmp/x200p7_map_waypoint.png`, `/tmp/x200p7_map_all_on.png` (hors dépôt, piece-jointe interne).*
*Fin du rapport intermédiaire — en attente d'ordre SECTION 3.*

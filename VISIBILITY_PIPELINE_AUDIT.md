# AUDIT DU PIPELINE DE VISIBILITE

**Protocole:** BCE-4X ULTIME ABSOLU x3
**Classification:** AUDIT PIPELINE — COMMANDANT STEEVE-MAX
**Date:** Fevrier 2026

---

## 1. ARCHITECTURE DU PIPELINE

```
UIState (MonTerritoireBionicPage.jsx)
  → useState: showZonesLayer, showCorridorsLayer, showPointsLayer
  → useState: showHeatmapV10, showWindFlow, showHydro, showExclusionOverlay
  → useState: showAlimentationV2, showNutritionPoints, showStands
  → useState: zoneSubFilters, corridorSubFilters, pointSubFilters
  → useState: classificationToggles
      ↓
VisibilityState (Props propagees)
      ↓
MapContent.jsx (Distribution des props aux couches)
      ↓
BionicCorridorsV6Layer.jsx (Zones + Corridors + Points)
  → isZoneTypeVisible(zoneType)
  → isCorridorLevelVisible(niveau)
  → isPointTypeVisible(zoneType, isChaudMode)
```

## 2. BUGS IDENTIFIES ET CORRIGES

### BUG 1 — multiEngines court-circuit (CRITIQUE)

| Aspect | Detail |
|---|---|
| Localisation | `BionicCorridorsV6Layer.jsx` L252 |
| Symptome | TOUS les sous-filtres zone COURT-CIRCUITES |
| Cause | `if (zoneSubFilters.multiEngines) return true;` — defaut `true` |
| Impact | Toggle OFF alimentation → zone TOUJOURS visible |
| Correction | Suppression de la ligne `multiEngines` — chaque type controle independamment |
| Statut | **CORRIGE** |

### BUG 2 — saisonniers court-circuit (CRITIQUE)

| Aspect | Detail |
|---|---|
| Localisation | `BionicCorridorsV6Layer.jsx` L265 |
| Symptome | TOUS les sous-filtres corridor COURT-CIRCUITES |
| Cause | `if (corridorSubFilters.saisonniers) return true;` — defaut `true` |
| Impact | Toggle OFF normaux → corridors TOUJOURS visibles |
| Correction | Suppression de la ligne `saisonniers` — chaque niveau controle independamment |
| Statut | **CORRIGE** |

### BUG 3 — Aliasing zone/point (MODERE)

| Aspect | Detail |
|---|---|
| Localisation | `BionicCorridorsV6Layer.jsx` L253, L281 |
| Symptome | Alimentation visible quand trajets ON et alimentation OFF |
| Cause | `alimentation: zoneSubFilters.alimentation || zoneSubFilters.trajets` |
| Impact | Desynchronisation toggle/affichage |
| Correction | Chaque type mappe directement sur son propre filtre — ZERO aliasing |
| Statut | **CORRIGE** |

## 3. ETAT POST-CORRECTION

| Composant | Etat |
|---|---|
| UIState | **SYNCHRONISE** — 15+ toggles operationnels |
| VisibilityState | **SYNCHRONISE** — Props correctement propagees |
| isZoneTypeVisible | **CORRIGE** — 7 types controles independamment |
| isCorridorLevelVisible | **CORRIGE** — 3 niveaux sans court-circuit |
| isPointTypeVisible | **CORRIGE** — 7 types sans aliasing |

## 4. GARANTIES

| Garantie | Statut |
|---|---|
| Bouton OFF = couche invisible | **GARANTI** |
| Bouton ON = couche visible | **GARANTI** |
| Aucun override non autorise | **GARANTI** |
| Alimentation OFF = invisible | **GARANTI** |

---

*BCE-4X ULTIME ABSOLU x3 — COMMANDANT STEEVE-MAX*

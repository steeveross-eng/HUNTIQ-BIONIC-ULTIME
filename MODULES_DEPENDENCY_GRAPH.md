# MODULES_DEPENDENCY_GRAPH.md
## BCE-4X ULTIME — GRAPHE DE DEPENDANCES MODULAIRE
### COMMANDANT STEEVE-MAX

---

## GRAPHE

```
                    ┌─────────────────┐
                    │  M5 — REGLES    │
                    │  METIER         │
                    │  (max_salines,  │
                    │   seuils, etc.) │
                    └────────┬────────┘
                             │ configure
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  M1 — SCORING   │ │  M2 — SELECTION │ │  M3 — GENERATION│
│  score_cell()   │ │  select_top_n() │ │  generate_zones()│
│                 │ │                 │ │                  │
│  Entree: grille │ │  Entree: cands  │ │  Entree: clusters│
│  Sortie: scores │ │  Sortie: top-N  │ │  Sortie: GeoJSON │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         │ scores            │ salines           │ geojson
         ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────┐
│                    API ENDPOINTS                        │
│  /api/v2/alimentation/analyze                           │
│  /api/v6/corridors/analyze-full                         │
│  /api/v1/hunt/orchestrate                               │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP JSON
                         ▼
              ┌─────────────────┐
              │  M4 — RENDU     │
              │  UI/UX          │
              │                 │
              │  BionicCorridorsV6Layer │
              │  NutritionPointsLayer   │
              │  StandsMapLayer         │
              └─────────────────┘
```

## FLUX DE DONNEES

1. M5 → M1: Regles metier configurent les seuils de scoring
2. M1 → M2: Scores alimentent la selection des salines
3. M1 → M3: Scores alimentent la generation des zones
4. M2 → API: Salines selectionnees retournees au frontend
5. M3 → API: GeoJSON des zones retourne au frontend
6. API → M4: Frontend recoit et rend les donnees

## ZERO DEPENDANCE CIRCULAIRE CONFIRMEE

**Date:** 2026-02-01
**Auteur:** Agent BCE-4X sous ordres COMMANDANT STEEVE-MAX
